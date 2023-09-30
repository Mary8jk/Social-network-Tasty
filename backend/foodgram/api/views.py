from rest_framework import viewsets
from rest_framework import generics
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
from django.db.models import Sum
from django.http.response import HttpResponse
from rest_framework import status
from rest_framework.pagination import LimitOffsetPagination
from django.shortcuts import get_object_or_404
from rest_framework.decorators import action
from django.db import IntegrityError

from users.models import User
from recipes.models import (Tag, Recipe, Subscribe, Ingredient,
                            Favorite, RecipeIngredient, TagRecipe,
                            ShoppingCart)
from .serializers import (CustomUserSerializer, TagSerializer,
                          RecipeListSerializer, SubscribeSerializer,
                          IngredientListSerializer,
                          FavoriteSerializer, RecipeSerializer,
                          ShoppingCartSerializer)
from .filters import IngredientFilter, RecipeFilter
from .permissions import AdminOrAuthorOrReadOnly
from .paginations import CustomPagination


class CustomUserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination

    def list(self, request, *args, **kwargs):
        users = User.objects.all()
        user = request.user
        data = []
        for user_to_check in users:
            is_subscribed = user.follower.filter(
                following=user_to_check).exists()
            serializer = self.get_serializer(user_to_check)
            user_data = serializer.data
            user_data['is_subscribed'] = is_subscribed
            data.append(user_data)
        return Response(data)


class CustomUserMeViewSet(generics.RetrieveAPIView):
    serializer_class = CustomUserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class CustomUserUpdateViewSet(generics.UpdateAPIView):
    serializer_class = CustomUserSerializer
    permission_classes = (AdminOrAuthorOrReadOnly,)

    def update(self, request):
        user = self.request.user
        current_password = request.data.get('current_password', None)
        new_password = request.data.get('new_password', None)

        if not current_password or not new_password:
            return Response({'error': r'Both current_password '
                             r'and new_password are required.'},
                            status=status.HTTP_400_BAD_REQUEST)

        if not user.check_password(current_password):
            return Response({'error': 'Current password is incorrect.'},
                            status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save()
        return Response({'message': 'Password updated successfully.'},
                        status=status.HTTP_200_OK)


class CustomUserDeleteApiView(generics.DestroyAPIView):
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [AdminOrAuthorOrReadOnly]


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class SubscribeListViewSet(viewsets.ModelViewSet):
    queryset = Subscribe.objects.all()
    serializer_class = SubscribeSerializer
    pagination_class = CustomPagination

    @action(detail=False, methods=['GET'])
    def subscriptions(self, request):
        user = request.user
        subscriptions = Subscribe.objects.filter(user=user)
        serializer = self.get_serializer(subscriptions, many=True)
        return Response(serializer.data)


class SubscribeViewSet(viewsets.GenericViewSet):
    serializer_class = SubscribeSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user_id = self.kwargs['id']
        queryset = Subscribe.objects.filter(user=user_id)
        return queryset

    @action(detail=False, methods=['POST'])
    def subscribe(self, request, id=None):
        user_id = self.kwargs['id']
        user = self.request.user
        if user_id == user.id:
            return Response({'error': 'You cannot subscribe to yourself'},
                            status=status.HTTP_400_BAD_REQUEST)
        try:
            Subscribe.objects.create(user=user, following_id=user_id)
            serializer = self.serializer_class(
                Subscribe.objects.get(user=user, following_id=user_id))
            return Response(serializer.data)
        except IntegrityError:
            return Response({'error': 'Subscription already exists'},
                            status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['DELETE'])
    def unsubscribe(self, request, id=None):
        user_id = self.kwargs['id']
        user = self.request.user
        try:
            subscription = Subscribe.objects.get(user=user,
                                                 following_id=user_id)
            subscription.delete()
            return Response({'message': 'Unsubscribed successfully'})
        except Subscribe.DoesNotExist:
            return Response({'message': 'Subscription not found'})


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = [AdminOrAuthorOrReadOnly]
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.action == 'list' or self.action == 'retrieve':
            return RecipeListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return RecipeSerializer

    @staticmethod
    def send_message(ingredients):
        shopping_list = 'Shopping list:'
        for ingredient in ingredients:
            shopping_list += (
                f"\n{ingredient['ingredient__name']} "
                f"({ingredient['ingredient__measurement_unit']}) - "
                f"{ingredient['amount']}")
        file = 'shopping_list.txt'
        response = HttpResponse(shopping_list,
                                content_type='text/plain; charset=utf-8')
        response['Content-Disposition'] = f'attachment; filename="{file}.txt"'
        return response

    @action(detail=False, methods=['GET'])
    def download_shopping_cart(self, request):
        recipes = Recipe.objects.filter(shopping_carts__user=request.user)
        ingredients = RecipeIngredient.objects.filter(
            recipe__in=recipes).order_by('ingredient__name').values(
            'ingredient__name', 'ingredient__measurement_unit').annotate(
            amount=Sum('amount'))
        return self.send_message(ingredients)

    @action(detail=True, methods=['POST'],
            permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, pk):
        context = {'request': request}
        recipe = get_object_or_404(Recipe, id=pk)
        data = {
            'user': request.user.id,
            'recipe': recipe.id}
        serializer = ShoppingCartSerializer(data=data, context=context)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @shopping_cart.mapping.delete
    def destroy_shopping_cart(self, request, pk):
        get_object_or_404(
            ShoppingCart,
            user=request.user.id,
            recipe=get_object_or_404(Recipe, id=pk)
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_create(self, serializer):
        if serializer.is_valid(raise_exception=True):
            recipe = serializer.save(author=self.request.user)
            ingredients_data = self.request.data.get('ingredients', [])
            tags_data = self.request.data.get('tags', [])

            for ingredient_data in ingredients_data:
                ingredient_id = ingredient_data.get('id')
                amount = ingredient_data.get('amount')
                ingredient = get_object_or_404(Ingredient, id=ingredient_id)
                RecipeIngredient.objects.create(recipe=recipe,
                                                ingredient=ingredient,
                                                amount=amount)

            for tag_id in tags_data:
                tag = get_object_or_404(Tag, id=tag_id)
                TagRecipe.objects.create(tag=tag, recipe=recipe)

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance,
                                         data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        if 'ingredients' in request.data:
            ingredients_data = request.data.get('ingredients', [])
            instance.ingredients.clear()
            for ingredient_data in ingredients_data:
                ingredient_id = ingredient_data.get('id')
                amount = ingredient_data.get('amount')
                ingredient = get_object_or_404(Ingredient, id=ingredient_id)
                RecipeIngredient.objects.create(recipe=instance,
                                                ingredient=ingredient,
                                                amount=amount)
        if 'tags' in request.data:
            tags_data = request.data.get('tags', [])
            instance.tag.clear()
            for tag_id in tags_data:
                tag = get_object_or_404(Tag, id=tag_id)
                instance.tag.add(tag)
            return Response(serializer.data)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientListSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [IngredientFilter]
    pagination_class = LimitOffsetPagination


class FavoriteViewSet(viewsets.GenericViewSet):
    queryset = Favorite.objects.all()
    serializer_class = FavoriteSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['POST'])
    def add_favorite(self, request, id=None):
        recipes_id = self.kwargs['id']
        user = self.request.user
        existing_favorite = Favorite.objects.filter(
            user=user, recipes_id=recipes_id)
        if existing_favorite:
            return Response({'error': 'Recipe already add'},
                            status=status.HTTP_400_BAD_REQUEST)
        try:
            Favorite.objects.create(user=user, recipes_id=recipes_id)
            serializer = self.serializer_class(
                Favorite.objects.get(user=user, recipes_id=recipes_id))
            return Response(serializer.data)
        except IntegrityError:
            return Response({'message': 'Recipe does not exist'})

    @action(detail=False, methods=['DELETE'])
    def del_favorite(self, request, id=None):
        recipes_id = self.kwargs['id']
        user = self.request.user
        favorite_to_delete = Favorite.objects.filter(
            user=user, recipes_id=recipes_id)
        if favorite_to_delete.exists():
            favorite_to_delete.delete()
            return Response({'message': 'Recipe removed successfully'})
        else:
            return Response({'message': 'Recipe not found'})
