"""
User models for the job board application.
Extends Django's built-in User model with a profile.
"""

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserProfile(models.Model):
    """
    Extended user profile with additional information.
    Links to Django's built-in User model.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    is_employer = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        """String representation of the user profile."""
        return f"{self.user.username}'s Profile"


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Signal to automatically create a UserProfile when a new User is created.
    """
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """
    Signal to save UserProfile when User is saved.
    """
    instance.profile.save()