from rest_framework import routers
from django.urls import include, path
from rest_framework_simplejwt.views import (TokenObtainPairView,
                                            TokenRefreshView,
                                            TokenVerifyView,)
from api.views import (CustomUserViewSet, CustomUserDeleteApiView,
                       CustomUserMeViewSet, CustomUserUpdateViewSet,
                       TagViewSet, RecipeViewSet, SubscribeViewSet,
                       SubscribeListViewSet)


app_name = 'api'

router = routers.DefaultRouter()
router.register('users', CustomUserViewSet)
router.register('tags', TagViewSet)
router.register('recipes', RecipeViewSet)
#router.register('users/subscriptions', SubscribeListViewSet)

urlpatterns = [
     path('auth/token/logout/', CustomUserDeleteApiView.as_view(),
          name='token_logout'),
     path('users/me/', CustomUserMeViewSet.as_view(),
          name='users-me'),
     path('users/set_password/', CustomUserUpdateViewSet.as_view(),
          name='users-me'),
     path('users/subscriptions/',
          SubscribeListViewSet.as_view({'get': 'subscriptions'}),
          name='subscriptions'),
     path('users/<int:id>/subscribe/',
          SubscribeViewSet.as_view({'post': 'subscribe',
                                    'delete': 'unsubscribe'}),
          name='subscribe'),

     path('', include(router.urls)),
]
