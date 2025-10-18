"""
Views for the users application.

This module defines API views for user management and authentication.
"""

from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from .serializers import (
    UserSerializer,
    UserCreateSerializer,
    UserUpdateSerializer,
    ChangePasswordSerializer,
    UserPreferenceSerializer,
)
from .models import UserPreference

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    """
    API view for user registration.
    
    POST /api/users/register/
    - Create a new user account
    - No authentication required
    """
    
    queryset = User.objects.all()
    serializer_class = UserCreateSerializer
    permission_classes = [permissions.AllowAny]
    
    def create(self, request, *args, **kwargs):
        """
        Create a new user and return user data with success message.
        
        Args:
            request: HTTP request object
            
        Returns:
            Response: User data and success message
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Return user data with success message
        user_data = UserSerializer(user).data
        return Response(
            {
                'user': user_data,
                'message': 'User registered successfully.'
            },
            status=status.HTTP_201_CREATED
        )


class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    API view for retrieving and updating user profile.
    
    GET /api/users/profile/
    - Get current user profile
    
    PUT/PATCH /api/users/profile/
    - Update current user profile
    
    Authentication required.
    """
    
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        """
        Return the current authenticated user.
        
        Returns:
            User: Current user instance
        """
        return self.request.user
    
    def get_serializer_class(self):
        """
        Use different serializer for update operations.
        
        Returns:
            Serializer: Appropriate serializer class
        """
        if self.request.method in ['PUT', 'PATCH']:
            return UserUpdateSerializer
        return UserSerializer


class ChangePasswordView(APIView):
    """
    API view for changing user password.
    
    POST /api/users/change-password/
    - Change current user's password
    
    Authentication required.
    """
    
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """
        Change user password.
        
        Args:
            request: HTTP request object
            
        Returns:
            Response: Success or error message
        """
        serializer = ChangePasswordSerializer(
            data=request.data,
            context={'request': request}
        )
        
        if serializer.is_valid():
            serializer.save()
            return Response(
                {'message': 'Password changed successfully.'},
                status=status.HTTP_200_OK
            )
        
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class UserPreferenceView(generics.RetrieveUpdateAPIView):
    """
    API view for user preferences.
    
    GET /api/users/preferences/
    - Get current user preferences
    
    PUT/PATCH /api/users/preferences/
    - Update current user preferences
    
    Authentication required.
    """
    
    serializer_class = UserPreferenceSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        """
        Get or create user preferences.
        
        Returns:
            UserPreference: User preferences instance
        """
        preferences, created = UserPreference.objects.get_or_create(
            user=self.request.user
        )
        return preferences


class DeleteAccountView(APIView):
    """
    API view for account deletion.
    
    DELETE /api/users/delete-account/
    - Delete current user account (soft delete)
    
    Authentication required.
    """
    
    permission_classes = [permissions.IsAuthenticated]
    
    def delete(self, request):
        """
        Deactivate user account (soft delete).
        
        Args:
            request: HTTP request object
            
        Returns:
            Response: Success message
        """
        user = request.user
        user.is_active = False
        user.save()
        
        return Response(
            {'message': 'Account deactivated successfully.'},
            status=status.HTTP_200_OK
        )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def current_user(request):
    """
    Get current authenticated user information.
    
    GET /api/users/me/
    
    Args:
        request: HTTP request object
        
    Returns:
        Response: User data
    """
    serializer = UserSerializer(request.user)
    return Response(serializer.data)
