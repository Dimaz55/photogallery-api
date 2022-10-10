from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from rest_framework import routers


from app.views import AlbumViewSet, PhotoViewSet
from config import settings
from users import urls

router = routers.SimpleRouter()
router.register(r'albums', AlbumViewSet, 'albums')
router.register(r'photos', PhotoViewSet, 'photos')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include([
        path('users/', include(urls)),
        path('app/', include(router.urls)),
        path('docs/', include([
            path('schema/', SpectacularAPIView.as_view(), name='schema'),
            path('swagger/', SpectacularSwaggerView.as_view(), name='schema-ui'),
            path('redoc/', SpectacularRedocView.as_view())
            ]))
        ])
    )
]

urlpatterns += static(settings.MEDIA_URL,
                      document_root=settings.MEDIA_ROOT)
