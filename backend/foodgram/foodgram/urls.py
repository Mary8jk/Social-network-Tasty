from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import (TokenObtainPairView,
                                            TokenRefreshView,
                                            TokenVerifyView,)

urlpatterns = [
     path('admin/', admin.site.urls),
     path('api/', include('api.urls')),
     path('api/auth/token/login/', TokenObtainPairView.as_view(),
          name='token_obtain_pair'),
     path('api/auth/token/refresh/', TokenRefreshView.as_view(),
          name='token_refresh'),
     path('api/auth/token/verify/', TokenVerifyView.as_view(),
          name='token_verify'),
]





# handler404 = 'core.views.page_not_found' # хандлеры добавить в приложение кор
# handler403 = 'core.views.permission_denied'

# if settings.DEBUG:
#     urlpatterns += static(settings.MEDIA_URL,
#                           document_root=settings.MEDIA_ROOT)