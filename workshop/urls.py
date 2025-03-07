from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import WorkshopViewSet

router = DefaultRouter()
router.register(r'workshops', WorkshopViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
