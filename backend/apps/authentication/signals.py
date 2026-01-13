"""
Signals for the authentication app.
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
import logging

logger = logging.getLogger(__name__)
User = get_user_model()


@receiver(post_save, sender=User)
def user_post_save(sender, instance, created, **kwargs):
    """Handle post-save operations for User model."""
    if created:
        logger.info(f"New user created: {instance.email}")
        # Add any post-creation logic here
        # e.g., send welcome email, create default settings, etc.
