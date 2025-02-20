from django.urls import path
from .views import ( 
    RegisterView, 
    EmailConfirmationView, 
    PasswordResetRequestView, 
    PasswordResetView, 
    LogoutView 
)

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('confirm-email/', EmailConfirmationView.as_view(), name='confirm-email'),
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('password-reset-request/', PasswordResetRequestView.as_view(), name='password_reset_request'),
    path('password-reset/', PasswordResetView.as_view(), name='password_reset'),
    path('logout/', LogoutView.as_view(), name='logout'),
]