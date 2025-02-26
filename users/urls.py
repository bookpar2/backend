from django.urls import path
from .views import (
    SendVerificationEmailView,
    VerifyEmailCodeView,
    UserRegistrationView,
    UserLoginView,
    UserLogoutView,
    PasswordResetConfirmView,
)
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('send-verification-email/', SendVerificationEmailView.as_view(), name='send-verification-email'),
    path('verify-email-code/', VerifyEmailCodeView.as_view(), name='verify-email-code'),
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', UserLogoutView.as_view(), name='logout'),
    path('password-reset-confirm/', PasswordResetConfirmView.as_view(), name='password-reset-confirm'),
]