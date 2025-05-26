from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions



schema_view = get_schema_view(
    openapi.Info(
        title="NatCraft Shopping API",
        default_version='v1',
        description="API for NatCraft Shopping Backend. Provides endpoints for user management, products, workshops, chats, and notifications.",
        terms_of_service="https://www.example.com/terms/",
        contact=openapi.Contact(email="support@natcraft.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,  # Hammaga ochiq bo‘lishi uchun
    permission_classes=(permissions.AllowAny,),  # Autentifikatsiyasiz kirish uchun
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('products.urls')),
    path('accounts/', include('accounts.urls')),
    path("main/", include('main.urls')),
    path("workshop/", include('workshop.urls')),
    path("chat/", include('chat.urls')),
    path("notifications/", include('notifications.urls')),
    # Swagger va ReDoc URL-lari
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]  

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)      