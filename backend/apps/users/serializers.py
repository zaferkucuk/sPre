"""
Serializers for the users application.

This module defines serializers for User and related models.
"""

from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .models import User, UserPreference


class UserPreferenceSerializer(serializers.ModelSerializer):
    """
    Serializer for UserPreference model.
    
    Handles serialization and deserialization of user preferences.
    """
    
    class Meta:
        model = UserPreference
        fields = [
            'favorite_sports',
            'default_currency',
            'timezone',
            'language',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at']


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User model.
    
    Provides detailed user information including preferences.
    """
    
    preferences = UserPreferenceSerializer(read_only=True)
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'full_name',
            'phone_number',
            'bio',
            'avatar',
            'notification_enabled',
            'is_active',
            'date_joined',
            'updated_at',
            'preferences',
        ]
        read_only_fields = ['id', 'date_joined', 'updated_at']
        extra_kwargs = {
            'password': {'write_only': True},
        }


class UserCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.
    
    Handles user creation with password validation.
    """
    
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        validators=[validate_password]
    )
    password_confirm = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )
    
    class Meta:
        model = User
        fields = [
            'email',
            'password',
            'password_confirm',
            'first_name',
            'last_name',
            'phone_number',
        ]
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
        }
    
    def validate(self, attrs):
        """
        Validate that passwords match.
        
        Args:
            attrs (dict): Serializer data
            
        Returns:
            dict: Validated data
            
        Raises:
            ValidationError: If passwords don't match
        """
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({
                'password_confirm': 'Passwords do not match.'
            })
        return attrs
    
    def create(self, validated_data):
        """
        Create a new user with validated data.
        
        Args:
            validated_data (dict): Validated user data
            
        Returns:
            User: Created user instance
        """
        # Remove password_confirm from data
        validated_data.pop('password_confirm')
        
        # Create user
        user = User.objects.create_user(**validated_data)
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating user information.
    
    Allows partial updates to user profile.
    """
    
    class Meta:
        model = User
        fields = [
            'first_name',
            'last_name',
            'phone_number',
            'bio',
            'avatar',
            'notification_enabled',
        ]


class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializer for changing user password.
    
    Validates old password and ensures new passwords match.
    """
    
    old_password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )
    new_password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'},
        validators=[validate_password]
    )
    new_password_confirm = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )
    
    def validate_old_password(self, value):
        """
        Validate that old password is correct.
        
        Args:
            value (str): Old password
            
        Returns:
            str: Validated old password
            
        Raises:
            ValidationError: If old password is incorrect
        """
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('Old password is incorrect.')
        return value
    
    def validate(self, attrs):
        """
        Validate that new passwords match.
        
        Args:
            attrs (dict): Serializer data
            
        Returns:
            dict: Validated data
            
        Raises:
            ValidationError: If new passwords don't match
        """
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({
                'new_password_confirm': 'New passwords do not match.'
            })
        return attrs
    
    def save(self, **kwargs):
        """
        Save the new password.
        
        Args:
            **kwargs: Additional arguments
            
        Returns:
            User: Updated user instance
        """
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user
