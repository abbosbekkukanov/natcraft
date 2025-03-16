from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ( 
    RegisterView, 
    EmailConfirmationView, 
    CustomTokenObtainPairView,
    PasswordResetRequestView, 
    PasswordResetVerifyView,
    PasswordResetConfirmView,
    LogoutView ,
    UserProfileViewSet,
    CraftsmenListView,
    GetUserProfileView
)

router = DefaultRouter()
router.register(r'profiles', UserProfileViewSet, basename='userprofile')

from rest_framework_simplejwt.views import (
    TokenRefreshView,
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('confirm-email/', EmailConfirmationView.as_view(), name='confirm-email'),
    path('login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('password-reset-request/', PasswordResetRequestView.as_view(), name='password_reset_request'),
    path('password-reset-verify/', PasswordResetVerifyView.as_view(), name='password_reset_verify'),
    path('password-reset-confirm/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('profile/me/', GetUserProfileView.as_view(), name='get_user_profile'),
    path('', include(router.urls)),
    path('craftsmen/', CraftsmenListView.as_view(), name='craftsmen-list'),
]