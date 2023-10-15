from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path
from recipes.views import (FavoriteViewSet, IngredientViewSet, RecipeViewSet,
                           SubscribeListViewSet, SubscribeViewSet, TagViewSet)
from rest_framework import routers
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView
from users.views import (CustomTokenObtainPairView, CustomUserMeViewSet,
                         CustomUserUpdateViewSet, CustomUserViewSet,
                         ResetTokenAPIView)

app_name = 'api'

router = routers.DefaultRouter()
router.register('users', CustomUserViewSet)
router.register('tags', TagViewSet)
router.register('recipes', RecipeViewSet)
router.register('ingredients', IngredientViewSet)

urlpatterns = [
    path('auth/token/login/', CustomTokenObtainPairView.as_view(),
         name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(),
         name='token_refresh'),
    path('auth/token/verify/', TokenVerifyView.as_view(),
         name='token_verify'),
    path('auth/token/logout/', ResetTokenAPIView.as_view(), name='logout'),
    path('users/me/', CustomUserMeViewSet.as_view(),
         name='users-me'),
    path('users/set_password/', CustomUserUpdateViewSet.as_view(),
         name='set_password'),
    path('users/subscriptions/',
         SubscribeListViewSet.as_view({'get': 'subscriptions'}),
         name='subscriptions'),
    path('users/<int:id>/subscribe/',
         SubscribeViewSet.as_view({'post': 'subscribe',
                                   'delete': 'unsubscribe'}),
         name='subscribe'),
    path('recipes/<int:id>/favorite/',
         FavoriteViewSet.as_view({'post': 'add_favorite',
                                  'delete': 'del_favorite'}),
         name='favorite'),

    path('', include(router.urls)),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
