from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('products.urls')),
    path('accounts/', include('accounts.urls')),
    path("main/", include('main.urls')),
    path("workshop/", include('workshop.urls')),
    path("chat/", include('chat.urls'))
]  

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)      