"""
Signals for the contacts app.
"""
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import Contact
import logging

logger = logging.getLogger(__name__)


@receiver(pre_save, sender=Contact)
def contact_pre_save(sender, instance, **kwargs):
    """Handle pre-save operations for Contact model."""
    # Normalize phone number
    if instance.phone_number:
        import re
        phone = re.sub(r'[^\d+]', '', instance.phone_number)
        if not phone.startswith('+'):
            phone = '+' + phone
        instance.phone_number = phone


@receiver(post_save, sender=Contact)
def contact_post_save(sender, instance, created, **kwargs):
    """Handle post-save operations for Contact model."""
    if created:
        logger.info(f"New contact created: {instance.phone_number}")
