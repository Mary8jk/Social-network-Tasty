from rest_framework import routers
from django.urls import include, path
from rest_framework_simplejwt.views import (TokenObtainPairView,
                                            TokenRefreshView,
                                            TokenVerifyView,)
from api.views import CustomUserViewSet


app_name = 'api'

router = routers.DefaultRouter()
router.register('users', CustomUserViewSet)

# urlpatterns = [
#     path('api/auth/token/login/', TokenObtainPairView.as_view(),
#          name='token_obtain_pair'),
#     path('api/auth/token/refresh/', TokenRefreshView.as_view(),
#          name='token_refresh'),
#     path('api/auth/token/verify/', TokenVerifyView.as_view(),
#          name='token_verify'),
# ]

urlpatterns = [
    path('', include(router.urls)),
]
