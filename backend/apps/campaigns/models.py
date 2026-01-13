"""
Campaign models for bulk messaging.
"""
import uuid
from django.db import models
from django.utils import timezone


class Campaign(models.Model):
    """Model for bulk messaging campaigns."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant_id = models.UUIDField()
    
    # Campaign info
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    
    # Message content
    message_template = models.TextField()
    message_variables = models.JSONField(default=dict, blank=True)  # For personalization
    
    # Media (optional)
    media_url = models.URLField(blank=True)
    media_type = models.CharField(max_length=50, blank=True)  # image, video, document, audio
    
    # Targeting
    contact_filter = models.JSONField(default=dict, blank=True)  # Filter criteria
    target_tags = models.JSONField(default=list, blank=True)
    target_count = models.IntegerField(default=0)
    
    # Status
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('scheduled', 'Scheduled'),
        ('running', 'Running'),
        ('paused', 'Paused'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('failed', 'Failed'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Scheduling
    scheduled_at = models.DateTimeField(null=True, blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Statistics
    total_recipients = models.IntegerField(default=0)
    sent_count = models.IntegerField(default=0)
    delivered_count = models.IntegerField(default=0)
    read_count = models.IntegerField(default=0)
    failed_count = models.IntegerField(default=0)
    blocked_count = models.IntegerField(default=0)
    
    # Throttling
    messages_per_minute = models.IntegerField(default=20)  # Rate limiting
    throttle_enabled = models.BooleanField(default=True)
    
    # Created by
    created_by = models.UUIDField()
    
    # Timestamps
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'campaigns'
        indexes = [
            models.Index(fields=['tenant_id']),
            models.Index(fields=['status']),
            models.Index(fields=['scheduled_at']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return self.name
    
    @property
    def delivery_rate(self):
        """Calculate delivery rate percentage."""
        if self.total_recipients == 0:
            return 0
        return (self.delivered_count / self.sent_count) * 100 if self.sent_count > 0 else 0
    
    @property
    def read_rate(self):
        """Calculate read rate percentage."""
        if self.delivered_count == 0:
            return 0
        return (self.read_count / self.delivered_count) * 100
    
    @property
    def progress_percent(self):
        """Calculate campaign progress percentage."""
        if self.total_recipients == 0:
            return 0
        return ((self.sent_count + self.failed_count + self.blocked_count) / self.total_recipients) * 100


class CampaignSchedule(models.Model):
    """Model for scheduled campaigns."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    campaign = models.ForeignKey(
        Campaign, on_delete=models.CASCADE, related_name='schedules'
    )
    
    # Schedule info
    scheduled_at = models.DateTimeField()
    timezone = models.CharField(max_length=50, default='UTC')
    
    # Recurring settings
    is_recurring = models.BooleanField(default=False)
    RECURRENCE_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
    ]
    recurrence_type = models.CharField(max_length=20, choices=RECURRENCE_CHOICES, blank=True)
    recurrence_end_date = models.DateField(null=True, blank=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    last_run_at = models.DateTimeField(null=True, blank=True)
    next_run_at = models.DateTimeField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        db_table = 'campaign_schedules'
        indexes = [
            models.Index(fields=['scheduled_at']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"Schedule for {self.campaign.name}"


class MessageTemplate(models.Model):
    """Model for reusable message templates."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant_id = models.UUIDField()
    
    # Template info
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    
    # Content
    content = models.TextField()
    variables = models.JSONField(default=list)  # List of variable names
    
    # Category
    CATEGORY_CHOICES = [
        ('marketing', 'Marketing'),
        ('transactional', 'Transactional'),
        ('notification', 'Notification'),
        ('support', 'Support'),
        ('custom', 'Custom'),
    ]
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='custom')
    
    # Status
    is_active = models.BooleanField(default=True)
    
    # Timestamps
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'message_templates'
        indexes = [
            models.Index(fields=['tenant_id']),
            models.Index(fields=['category']),
        ]
    
    def __str__(self):
        return self.name
    
    def parse_variables(self):
        """Extract variables from template content."""
        import re
        pattern = r'\{(\w+)\}'
        variables = re.findall(pattern, self.content)
        self.variables = list(set(variables))
        return self.variables
