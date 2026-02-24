
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save    # ← ADD THIS!
from django.dispatch import receiver              # ← ADD THIS!


class Profile(models.Model):    
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE,
        related_name='profile'
    )
    avatar = models.ImageField(
        upload_to='avatars/',
        blank=True,
        null=True
    )
    bio = models.TextField(
        max_length=500,
        blank=True
    )
    
    def __str__(self):
        return f"{self.user.username}'s profile"
    
# ============================================
# SIGNALS: Auto-create profile for new users
# ============================================

@receiver(post_save, sender=User)                               # ← ADD THIS!
def create_user_profile(sender, instance, created, **kwargs):
    """Create a Profile when a new User is created"""
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)                               # ← ADD THIS!
def save_user_profile(sender, instance, **kwargs):
    """Save the Profile when User is saved"""
    # Check if profile exists before saving
    if hasattr(instance, 'profile'):
        instance.profile.save()

