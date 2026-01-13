"""
URL configuration for the authentication app.
"""
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenRefreshView, TokenVerifyView, TokenBlacklistView
)
from rest_framework.routers import DefaultRouter

from .views import (
    RegisterView, CustomTokenObtainPairView, UserProfileView,
    ChangePasswordView, UserViewSet, UserInvitationViewSet, AcceptInvitationView
)

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'invitations', UserInvitationViewSet, basename='invitation')

urlpatterns = [
    # Authentication endpoints
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('token/logout/', TokenBlacklistView.as_view(), name='token_blacklist'),
    
    # User profile
    path('me/', UserProfileView.as_view(), name='user_profile'),
    path('change-password/', ChangePasswordView.as_view(), name='change_password'),
    
    # Invitations
    path('invitations/accept/', AcceptInvitationView.as_view(), name='accept_invitation'),
    
    # User management (admin)
    path('', include(router.urls)),
]
