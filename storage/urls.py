"""
URL configuration for storage project.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.permissions import IsAdminUser
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# Swagger / ReDoc — réservé aux administrateurs
schema_view = get_schema_view(
    openapi.Info(
        title="MuraStorage API",
        default_version='v1',
        description="API de gestion multi-boutiques",
    ),
    public=False,
    permission_classes=(IsAdminUser,),
    patterns=[
        path('api/', include('core.urls')),
    ],
)

urlpatterns = [
    path('swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('admin/', admin.site.urls),
    path('api/', include('core.urls')),
]

# JWT : routes déjà définies dans core/urls.py
#   /api/auth/jwt/login|refresh|verify/
#   /api/token/refresh|verify/

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
