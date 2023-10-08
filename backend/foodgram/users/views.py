from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework_simplejwt.token_blacklist.models import (OutstandingToken,
                                                             BlacklistedToken)
from rest_framework import generics
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from users.models import User
from .serializers import CustomUserSerializer, CustomUserUpdateSerializer
from recipes.permissions import AdminOrAuthorOrReadOnly


class CustomUserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = PageNumberPagination

    def list(self, request, *args, **kwargs):
        users = self.get_queryset()
        user = request.user
        data = []
        user_followers = user.follower.values_list('following', flat=True)
        for user_to_check in users:
            is_subscribed = user_to_check.id in user_followers
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


class CustomUserUpdateViewSet(generics.CreateAPIView):
    serializer_class = CustomUserUpdateSerializer
    permission_classes = (AdminOrAuthorOrReadOnly,)


class ResetTokenAPIView(APIView):
    permission_classes = (IsAuthenticated,)
    """
    Adding all refresh tokens in black list
    """
    def post(self, request):
        tokens = OutstandingToken.objects.filter(user_id=request.user.id)
        for token in tokens:
            t, _ = BlacklistedToken.objects.get_or_create(token=token)
        return Response('Successful Logout',
                        status=status.HTTP_205_RESET_CONTENT)
