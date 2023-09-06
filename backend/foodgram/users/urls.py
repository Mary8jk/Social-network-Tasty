from django.contrib import admin
from django.urls import include, path
from rest_framework_simplejwt.views import (TokenObtainPairView,
                                            TokenRefreshView, TokenVerifyView)

# urlpatterns = [
#     path('api/v1/jwt/create/', TokenObtainPairView.as_view(),
#          name='token_obtain_pair'),
#     path('api/v1/jwt/refresh/', TokenRefreshView.as_view(),
#          name='token_refresh'),
#     path('api/v1/jwt/verify/', TokenVerifyView.as_view(),
#          name='token_verify'),
# ]
