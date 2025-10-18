"""
Signals for the users application.

This module defines signal handlers for user-related events.
"""

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import UserPreference

User = get_user_model()


@receiver(post_save, sender=User)
def create_user_preference(sender, instance, created, **kwargs):
    """
    Create UserPreference instance when a new user is created.
    
    Args:
        sender: Model class that sent the signal
        instance: User instance that was saved
        created: Boolean indicating if this is a new instance
        **kwargs: Additional keyword arguments
    """
    if created:
        UserPreference.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_preference(sender, instance, **kwargs):
    """
    Save UserPreference when user is saved.
    
    Args:
        sender: Model class that sent the signal
        instance: User instance that was saved
        **kwargs: Additional keyword arguments
    """
    if hasattr(instance, 'preferences'):
        instance.preferences.save()
