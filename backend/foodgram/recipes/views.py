from django.db.models import Sum
from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            ShoppingCart, Subscribe, Tag, TagRecipe)
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from users.models import User

from .filters import IngredientFilter, RecipeFilter
from .paginations import CustomPagination
from .permissions import AdminOrAuthorOrReadOnly
from .serializers import (FavoriteSerializer, IngredientListSerializer,
                          RecipeListSerializer, RecipeSerializer,
                          ShoppingCartSerializer, SubscribeListSerializer,
                          SubscribeSerializer, TagSerializer)


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly]
    serializer_class = TagSerializer
    pagination_class = None


class SubscribeListViewSet(viewsets.ModelViewSet):
    serializer_class = SubscribeListSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = CustomPagination

    @action(detail=False, methods=['GET'],)
    def subscriptions(self, request):
        queryset = User.objects.filter(
            following__user=request.user).prefetch_related('follower__recipes')
        pages = self.paginate_queryset(queryset)
        serializer = self.get_serializer(pages, many=True)
        return self.get_paginated_response(serializer.data)


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
        data = {'user': user.id, 'following': user_id}
        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['DELETE'])
    def unsubscribe(self, request, id=None):
        user_id = self.kwargs['id']
        user = self.request.user
        subscription = get_object_or_404(Subscribe, user=user,
                                         following_id=user_id)
        subscription.delete()
        return Response({'message': 'Unsubscribed successfully'})


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = [AdminOrAuthorOrReadOnly]
    pagination_class = CustomPagination
    filter_backends = (DjangoFilterBackend, )
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
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
        serializer.is_valid(raise_exception=True)
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

        for tags_id in tags_data:
            tags = get_object_or_404(Tag, id=tags_id)
            TagRecipe.objects.create(tags=tags, recipe=recipe)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

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
            instance.tags.clear()
            for tags_id in tags_data:
                tag = get_object_or_404(Tag, id=tags_id)
                instance.tags.add(tag)
            return Response(serializer.data)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientListSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
    pagination_class = None


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
        Favorite.objects.create(user=user, recipes_id=recipes_id)
        serializer = self.serializer_class(
            Favorite.objects.get(user=user, recipes_id=recipes_id))
        return Response(serializer.data)

    @action(detail=False, methods=['DELETE'])
    def del_favorite(self, request, id=None):
        recipes_id = self.kwargs['id']
        user = self.request.user
        favorite_to_delete = get_object_or_404(Favorite, user=user.id,
                                               recipes=recipes_id)
        favorite_to_delete.delete()
        return Response({'message': 'Recipe removed successfully'})
