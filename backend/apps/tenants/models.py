"""
Tenant models for multi-tenant architecture.
"""
import uuid
from django.db import models
from django.utils import timezone
from django.conf import settings


class Tenant(models.Model):
    """Model representing a tenant (organization/company)."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=100, unique=True)
    logo = models.URLField(blank=True)
    website = models.URLField(blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    
    # Subscription status
    SUBSCRIPTION_STATUS = [
        ('active', 'Active'),
        ('trial', 'Trial'),
        ('past_due', 'Past Due'),
        ('cancelled', 'Cancelled'),
        ('suspended', 'Suspended'),
    ]
    subscription_status = models.CharField(
        max_length=20, choices=SUBSCRIPTION_STATUS, default='trial'
    )
    
    # Green API credentials (for this tenant)
    green_api_id = models.CharField(max_length=100, blank=True)
    green_api_token = models.CharField(max_length=200, blank=True)
    green_api_instance_id = models.CharField(max_length=100, blank=True)
    
    # Status fields
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    trial_ends_at = models.DateTimeField(null=True, blank=True)
    
    # Settings (JSON field for flexible configuration)
    settings = models.JSONField(default=dict, blank=True)
    
    class Meta:
        db_table = 'tenants'
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['subscription_status']),
        ]
    
    def __str__(self):
        return self.name
    
    @property
    def is_on_trial(self):
        """Check if the tenant is on trial."""
        if self.trial_ends_at and timezone.now() < self.trial_ends_at:
            return True
        return False
    
    @property
    def can_send_messages(self):
        """Check if the tenant can send messages based on subscription."""
        if not self.is_active:
            return False
        if self.subscription_status in ('past_due', 'suspended'):
            return False
        return True
    
    def get_green_api_credentials(self):
        """Return Green API credentials for this tenant."""
        return {
            'id': self.green_api_id,
            'token': self.green_api_token,
            'instance_id': self.green_api_instance_id,
        }


class TenantSettings(models.Model):
    """Model for tenant-specific settings."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.OneToOneField(
        Tenant, on_delete=models.CASCADE, related_name='settings_model'
    )
    
    # General settings
    timezone = models.CharField(max_length=50, default='UTC')
    language = models.CharField(max_length=10, default='en')
    date_format = models.CharField(max_length=20, default='YYYY-MM-DD')
    time_format = models.CharField(max_length=20, default='24h')
    
    # Message settings
    default_country_code = models.CharField(max_length=10, default='')
    message_footer = models.CharField(max_length=200, blank=True)
    signature = models.TextField(blank=True)
    auto_save_contacts = models.BooleanField(default=True)
    
    # Notification settings
    email_notifications = models.BooleanField(default=True)
    browser_notifications = models.BooleanField(default=True)
    
    # Integration settings
    webhook_url = models.URLField(blank=True)
    webhook_secret = models.CharField(max_length=200, blank=True)
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'tenant_settings'
    
    def __str__(self):
        return f"Settings for {self.tenant.name}"
    
    def to_dict(self):
        """Convert settings to dictionary."""
        return {
            'timezone': self.timezone,
            'language': self.language,
            'date_format': self.date_format,
            'time_format': self.time_format,
            'default_country_code': self.default_country_code,
            'message_footer': self.message_footer,
            'signature': self.signature,
            'auto_save_contacts': self.auto_save_contacts,
            'email_notifications': self.email_notifications,
            'browser_notifications': self.browser_notifications,
            'webhook_url': self.webhook_url,
        }


class TenantUsage(models.Model):
    """Model for tracking tenant resource usage."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.OneToOneField(
        Tenant, on_delete=models.CASCADE, related_name='usage'
    )
    
    # Current month usage
    messages_sent = models.IntegerField(default=0)
    messages_limit = models.IntegerField(default=0)
    contacts_count = models.IntegerField(default=0)
    contacts_limit = models.IntegerField(default=0)
    campaigns_count = models.IntegerField(default=0)
    campaigns_limit = models.IntegerField(default=0)
    
    # Storage usage (in bytes)
    storage_used = models.BigIntegerField(default=0)
    storage_limit = models.BigIntegerField(default=0)
    
    # Users
    users_count = models.IntegerField(default=1)
    users_limit = models.IntegerField(default=5)
    
    # Period tracking
    period_start = models.DateField()
    period_end = models.DateField()
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'tenant_usage'
    
    def __str__(self):
        return f"Usage for {self.tenant.name}"
    
    def get_messages_usage_percent(self):
        """Calculate messages usage percentage."""
        if self.messages_limit == 0:
            return 0
        return (self.messages_sent / self.messages_limit) * 100
    
    def get_contacts_usage_percent(self):
        """Calculate contacts usage percentage."""
        if self.contacts_limit == 0:
            return 0
        return (self.contacts_count / self.contacts_limit) * 100
    
    def get_storage_usage_percent(self):
        """Calculate storage usage percentage."""
        if self.storage_limit == 0:
            return 0
        return (self.storage_used / self.storage_limit) * 100
    
    def is_over_limit(self):
        """Check if tenant is over any limit."""
        if self.messages_limit > 0 and self.messages_sent >= self.messages_limit:
            return True
        if self.contacts_limit > 0 and self.contacts_count >= self.contacts_limit:
            return True
        if self.storage_limit > 0 and self.storage_used >= self.storage_limit:
            return True
        return False
