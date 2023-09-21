from rest_framework import viewsets
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import LimitOffsetPagination, PageNumberPagination
from django.shortcuts import get_object_or_404
from rest_framework.decorators import action
from api.mixins import MixinSet
from rest_framework import status
from django.db import IntegrityError

from users.models import User
from recipes.models import Tag, Recipe, Subscribe
from .serializers import CustomUserSerializer, TagSerializer, RecipeSerializer, SubscribeSerializer


class CustomUserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = LimitOffsetPagination

    def list(self, request, *args, **kwargs):
        users = User.objects.all()
        user = request.user
        data = []
        for user_to_check in users:
            is_subscribed = user.follower.filter(following=user_to_check).exists()
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
    permission_classes = [IsAuthenticated]

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
    permission_classes = [IsAuthenticated]


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class SubscribeListViewSet(viewsets.ModelViewSet):
    queryset = Subscribe.objects.all()
    serializer_class = SubscribeSerializer
    pagination_class = LimitOffsetPagination

    @action(detail=False, methods=['GET'])
    def subscriptions(self, request):
        user = request.user
        subscriptions = Subscribe.objects.filter(user=user)
        serializer = self.get_serializer(subscriptions, many=True)
        return Response(serializer.data)


class SubscribeViewSet(viewsets.GenericViewSet):
    serializer_class = SubscribeSerializer

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
            serializer = self.serializer_class(Subscribe.objects.get(user=user, following_id=user_id))
            return Response(serializer.data)
        except IntegrityError:
            return Response({'error': 'Subscription already exists'}, status=status.HTTP_400_BAD_REQUEST)

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









# class SubscribeViewSet(viewsets.ViewSet):

#     def list(self, request):
#         queryset = Subscribe.objects.all()
#         serializer = SubscribeSerializer(queryset, many=True)
#         return Response(serializer.data)






# class SubscribeViewSet(viewsets.ModelViewSet):
#     queryset = Subscribe.objects.all()
#     serializer_class = SubscribeSerializer

    # @action(detail=False, methods=['GET'], url_path='subscriptions')
    # def subscriptions(self, request):
    #     user = request.user
    #     subscriptions = Subscribe.objects.filter(user=user)
    #     serializer = self.get_serializer(subscriptions, many=True)
    #     return Response(serializer.data)

    # @action(detail=True, methods=['POST', ], url_path='subscribe', url_name='subscribe')
    # def manage_subscription(self, request, pk=None):
    #     if request.method == 'POST':
    #         user_to_check = get_object_or_404(User, id=pk)
    #         subscription, created = Subscribe.objects.get_or_create(user=request.user, following=user_to_check)
    #         if created:
    #             is_subscribed = True
    #             return Response({'is_subscribed': is_subscribed}, status=status.HTTP_201_CREATED)
    #         else:
    #             is_subscribed = False
    #             return Response({'detail': 'Subscription already exists'}, status=status.HTTP_200_OK)

    # @action(detail=True, methods=['DELETE'], url_path='subscribe', url_name='subscribe-delete')
    # def delete_subscription(self, request, pk=None):
    #     if request.method == 'DELETE':
    #         user_to_check = get_object_or_404(User, id=pk)
    #         subscription = Subscribe.objects.filter(user=request.user, following=user_to_check).first()
    #         if subscription:
    #             subscription.delete()
    #             return Response({'detail': 'Subscription deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
    #         else:
    #             return Response({'detail': 'Subscription not found'}, status=status.HTTP_404_NOT_FOUND)

      
      


        # elif request.method == 'DELETE':
        #     user_to_check = get_object_or_404(User, id=pk)
        #     subscription = Subscribe.objects.filter(user=request.user, following=user_to_check).first()
        #     if subscription:
        #         subscription.delete()
        #         return Response({'detail': 'Subscription deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
        #     else:
        #         return Response({'detail': 'Subscription not found'}, status=status.HTTP_404_NOT_FOUND)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    pagination_class = LimitOffsetPagination

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
