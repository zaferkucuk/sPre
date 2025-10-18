"""
Admin configuration for users application.

This module defines the admin interface for User and related models.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User, UserPreference


class UserPreferenceInline(admin.StackedInline):
    """
    Inline admin for UserPreference model.
    
    Allows editing user preferences directly from the user admin page.
    """
    model = UserPreference
    can_delete = False
    verbose_name_plural = 'Preferences'
    fields = ['favorite_sports', 'default_currency', 'timezone', 'language']


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Admin interface for User model.
    
    Customizes the Django admin interface for user management.
    """
    
    inlines = [UserPreferenceInline]
    
    # List display configuration
    list_display = [
        'email',
        'first_name',
        'last_name',
        'is_active',
        'is_staff',
        'date_joined',
    ]
    
    list_filter = [
        'is_active',
        'is_staff',
        'is_superuser',
        'date_joined',
    ]
    
    search_fields = ['email', 'first_name', 'last_name']
    
    ordering = ['-date_joined']
    
    # Fieldsets for user detail page
    fieldsets = (
        (None, {
            'fields': ('email', 'password')
        }),
        (_('Personal Info'), {
            'fields': (
                'first_name',
                'last_name',
                'username',
                'phone_number',
                'bio',
                'avatar',
            )
        }),
        (_('Permissions'), {
            'fields': (
                'is_active',
                'is_staff',
                'is_superuser',
                'groups',
                'user_permissions',
            )
        }),
        (_('Settings'), {
            'fields': ('notification_enabled',)
        }),
        (_('Important dates'), {
            'fields': ('last_login', 'date_joined', 'updated_at')
        }),
    )
    
    # Fieldsets for user creation page
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email',
                'password1',
                'password2',
                'first_name',
                'last_name',
                'is_active',
                'is_staff',
            ),
        }),
    )
    
    readonly_fields = ['date_joined', 'updated_at', 'last_login']


@admin.register(UserPreference)
class UserPreferenceAdmin(admin.ModelAdmin):
    """
    Admin interface for UserPreference model.
    """
    
    list_display = [
        'user',
        'default_currency',
        'timezone',
        'language',
        'updated_at',
    ]
    
    list_filter = ['default_currency', 'language']
    
    search_fields = ['user__email']
    
    readonly_fields = ['created_at', 'updated_at']
