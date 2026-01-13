"""
Chat models for inbox functionality.
"""
import uuid
from django.db import models
from django.utils import timezone


class Chat(models.Model):
    """Model for chat conversations."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant_id = models.UUIDField()
    
    # Phone numbers
    phone_number = models.CharField(max_length=20)
    contact_name = models.CharField(max_length=200, blank=True)
    
    # Status
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('closed', 'Closed'),
        ('archived', 'Archived'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    
    # Assignment
    assigned_to = models.UUIDField(null=True, blank=True)
    
    # Unread count
    unread_count = models.IntegerField(default=0)
    
    # Last message preview
    last_message_preview = models.CharField(max_length=200, blank=True)
    last_message_at = models.DateTimeField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'chats'
        indexes = [
            models.Index(fields=['tenant_id']),
            models.Index(fields=['status']),
            models.Index(fields=['phone_number']),
            models.Index(fields=['assigned_to']),
            models.Index(fields=['last_message_at']),
        ]
        unique_together = [['tenant_id', 'phone_number']]
    
    def __str__(self):
        return self.contact_name or self.phone_number


class AutoReply(models.Model):
    """Model for auto-reply rules."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant_id = models.UUIDField()
    
    # Rule info
    name = models.CharField(max_length=200)
    is_active = models.BooleanField(default=True)
    
    # Trigger
    TRIGGER_CHOICES = [
        ('keyword', 'Contains Keyword'),
        ('exact', 'Exact Match'),
        ('regex', 'Regex Pattern'),
        ('always', 'Always'),
    ]
    trigger_type = models.CharField(max_length=20, choices=TRIGGER_CHOICES)
    trigger_value = models.CharField(max_length=200)
    
    # Response
    message = models.TextField()
    media_url = models.URLField(blank=True)
    
    # Priority (higher = checked first)
    priority = models.IntegerField(default=0)
    
    # Timestamps
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        db_table = 'auto_replies'
        indexes = [
            models.Index(fields=['tenant_id']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return self.name
