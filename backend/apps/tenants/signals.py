"""
Signals for the tenants app.
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import Tenant, TenantSettings, TenantUsage
import logging

logger = logging.getLogger(__name__)
User = get_user_model()


@receiver(post_save, sender=Tenant)
def tenant_post_save(sender, instance, created, **kwargs):
    """Handle post-save operations for Tenant model."""
    if created:
        logger.info(f"New tenant created: {instance.name}")
        # Create default settings
        TenantSettings.objects.get_or_create(tenant=instance)
        # Create usage tracking
        from django.utils import timezone
        from datetime import timedelta
        TenantUsage.objects.get_or_create(
            tenant=instance,
            defaults={
                'period_start': timezone.now().replace(day=1),
                'period_end': (timezone.now().replace(day=1) + timedelta(days=32)).replace(day=1)
            }
        )
