"""
URL configuration for users application.

This module defines URL patterns for user-related endpoints.
"""

from django.urls import path
from .views import (
    RegisterView,
    UserProfileView,
    ChangePasswordView,
    UserPreferenceView,
    DeleteAccountView,
    current_user,
)

app_name = 'users'

urlpatterns = [
    # Registration
    path('register/', RegisterView.as_view(), name='register'),
    
    # Current user
    path('me/', current_user, name='current-user'),
    
    # Profile management
    path('profile/', UserProfileView.as_view(), name='profile'),
    
    # Password management
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
    
    # Preferences
    path('preferences/', UserPreferenceView.as_view(), name='preferences'),
    
    # Account deletion
    path('delete-account/', DeleteAccountView.as_view(), name='delete-account'),
]
