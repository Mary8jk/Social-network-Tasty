from recipes.permissions import AdminOrAuthorOrReadOnly
from rest_framework import generics, status, viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.token_blacklist.models import (BlacklistedToken,
                                                             OutstandingToken)
from rest_framework_simplejwt.tokens import AccessToken
from users.models import User

from .serializers import (CustomTokenObtainSerializer, CustomUserSerializer,
                          CustomUserUpdateSerializer)


class CustomUserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    pagination_class = PageNumberPagination

    def get_permissions(self):
        if self.action == 'list':
            permission_classes = [IsAuthenticated]
        elif self.action == 'create':
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

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

    def post(self, request, *args, **kwargs):
        serializer = CustomUserSerializer(data=request.data)
        serializer.is_valid()
        user = serializer.save()
        response_data = {
            'email': user.email,
            'id': user.id,
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name
        }
        return Response(response_data, status=status.HTTP_201_CREATED)


class CustomTokenObtainPairView(generics.CreateAPIView):
    serializer_class = CustomTokenObtainSerializer
    queryset = User.objects.all()
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        user = User.objects.get(email=email)
        access = AccessToken.for_user(user)
        access_token = str(access)
        response_data = {"auth_token": access_token}
        return Response(response_data, status=status.HTTP_201_CREATED)


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
