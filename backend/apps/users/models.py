"""
User models for the sPre application.

This module defines the custom User model and related profile models.
"""

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    """
    Custom user manager for the User model.
    
    This manager handles user creation with email as the primary identifier.
    """
    
    def create_user(self, email, password=None, **extra_fields):
        """
        Create and save a regular user with the given email and password.
        
        Args:
            email (str): User's email address
            password (str): User's password
            **extra_fields: Additional fields for the user
            
        Returns:
            User: Created user instance
            
        Raises:
            ValueError: If email is not provided
        """
        if not email:
            raise ValueError(_('The Email field must be set'))
        
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        """
        Create and save a superuser with the given email and password.
        
        Args:
            email (str): Superuser's email address
            password (str): Superuser's password
            **extra_fields: Additional fields for the superuser
            
        Returns:
            User: Created superuser instance
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
        
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    """
    Custom User model for the sPre application.
    
    This model extends Django's AbstractUser and uses email as the primary
    identifier instead of username.
    
    Attributes:
        email (EmailField): User's email address (unique)
        username (CharField): Optional username
        first_name (CharField): User's first name
        last_name (CharField): User's last name
        is_active (BooleanField): Whether the user account is active
        is_staff (BooleanField): Whether the user can access admin site
        date_joined (DateTimeField): When the user joined
        updated_at (DateTimeField): Last update timestamp
    """
    
    # Override username field to make it optional
    username = models.CharField(
        _('username'),
        max_length=150,
        unique=True,
        blank=True,
        null=True,
        help_text=_('Optional. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'),
    )
    
    # Email is the primary identifier
    email = models.EmailField(
        _('email address'),
        unique=True,
        help_text=_('Required. Enter a valid email address.')
    )
    
    # Additional fields
    phone_number = models.CharField(
        _('phone number'),
        max_length=20,
        blank=True,
        null=True,
        help_text=_('Optional. Phone number with country code.')
    )
    
    bio = models.TextField(
        _('biography'),
        blank=True,
        null=True,
        max_length=500,
        help_text=_('Optional. Brief description about the user.')
    )
    
    avatar = models.URLField(
        _('avatar URL'),
        blank=True,
        null=True,
        help_text=_('Optional. URL to user avatar image.')
    )
    
    # Preferences
    notification_enabled = models.BooleanField(
        _('notifications enabled'),
        default=True,
        help_text=_('Whether user wants to receive notifications.')
    )
    
    # Timestamps
    updated_at = models.DateTimeField(
        _('updated at'),
        auto_now=True,
        help_text=_('Last time user information was updated.')
    )
    
    # Set email as the username field
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    
    objects = UserManager()
    
    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        ordering = ['-date_joined']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['date_joined']),
        ]
    
    def __str__(self):
        """
        String representation of the user.
        
        Returns:
            str: User's email address
        """
        return self.email
    
    def get_full_name(self):
        """
        Get user's full name.
        
        Returns:
            str: Full name (first_name + last_name) or email if names are not set
        """
        full_name = f"{self.first_name} {self.last_name}".strip()
        return full_name if full_name else self.email
    
    def get_short_name(self):
        """
        Get user's short name.
        
        Returns:
            str: First name or email if first name is not set
        """
        return self.first_name if self.first_name else self.email


class UserPreference(models.Model):
    """
    User preferences and settings.
    
    This model stores user-specific preferences for the application.
    
    Attributes:
        user (OneToOneField): Related user
        favorite_sports (JSONField): List of favorite sports
        default_currency (CharField): Preferred currency for odds display
        timezone (CharField): User's timezone
        language (CharField): Preferred language
    """
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='preferences',
        verbose_name=_('user')
    )
    
    favorite_sports = models.JSONField(
        _('favorite sports'),
        default=list,
        blank=True,
        help_text=_('List of favorite sports (e.g., ["football", "basketball"])')
    )
    
    default_currency = models.CharField(
        _('default currency'),
        max_length=3,
        default='USD',
        help_text=_('Currency code (e.g., USD, EUR, GBP)')
    )
    
    timezone = models.CharField(
        _('timezone'),
        max_length=50,
        default='UTC',
        help_text=_('User timezone (e.g., America/New_York)')
    )
    
    language = models.CharField(
        _('language'),
        max_length=10,
        default='en',
        help_text=_('Language code (e.g., en, tr)')
    )
    
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('user preference')
        verbose_name_plural = _('user preferences')
    
    def __str__(self):
        """
        String representation of user preferences.
        
        Returns:
            str: User's email with 'preferences' suffix
        """
        return f"{self.user.email} preferences"
