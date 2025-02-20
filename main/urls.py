from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BannerViewSet, CraftsmanshipViewSet, OurteamViewSet, SocialMediaLinkViewSet, CraftsmanshipListViewSet, AboutUsViewSet

router = DefaultRouter()
router.register(r'banner', BannerViewSet)
router.register(r'craftsmanship', CraftsmanshipViewSet)
router.register(r'craftsmanshiplists', CraftsmanshipListViewSet)
router.register(r'socialmedialink', SocialMediaLinkViewSet)
router.register(r'aboutus', AboutUsViewSet)
router.register(r'ourteam', OurteamViewSet)


urlpatterns = [
    path('', include(router.urls)),
]
