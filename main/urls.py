from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    BannerViewSet, 
    CraftsmanshipViewSet, 
    OurteamViewSet, 
    SocialMediaLinkViewSet, 
    CraftsmanshipListViewSet, 
    AboutUsViewSet, 
    CraftsmenStatsView,
    CraftmanDetailView,
    CategoryStatsView
)
router = DefaultRouter()
router.register(r'banner', BannerViewSet)
router.register(r'craftsmanship', CraftsmanshipViewSet)
router.register(r'craftsmanshiplists', CraftsmanshipListViewSet)
router.register(r'socialmedialink', SocialMediaLinkViewSet)
router.register(r'aboutus', AboutUsViewSet)
router.register(r'ourteam', OurteamViewSet)


urlpatterns = [
    path('', include(router.urls)),
    path('craftsmens/', CraftsmenStatsView.as_view(), name='craftmens-stats'),
    path('craftsmens/<int:id>/', CraftmanDetailView.as_view(), name='craftman-detail'),
    path('category/', CategoryStatsView.as_view(), name='category-stats'),
]
