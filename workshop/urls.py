from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import WorkshopViewSet, WorkshopRatingViewSet

router = DefaultRouter()
router.register(r'workshops', WorkshopViewSet, basename='workshop')
router.register(r'workshops/(?P<workshop_pk>\d+)/ratings', WorkshopRatingViewSet, basename='workshop-ratings')

urlpatterns = [
    path('', include(router.urls)),
]