"""
Message models for WhatsApp messaging.
"""
import uuid
from django.db import models
from django.utils import timezone


class Message(models.Model):
    """Model for WhatsApp messages."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant_id = models.UUIDField()
    
    # Message direction
    DIRECTION_CHOICES = [
        ('outbound', 'Outbound'),
        ('inbound', 'Inbound'),
    ]
    direction = models.CharField(max_length=20, choices=DIRECTION_CHOICES)
    
    # Message type
    MESSAGE_TYPES = [
        ('text', 'Text'),
        ('image', 'Image'),
        ('video', 'Video'),
        ('document', 'Document'),
        ('audio', 'Audio'),
        ('location', 'Location'),
        ('contact', 'Contact'),
    ]
    message_type = models.CharField(max_length=20, choices=MESSAGE_TYPES, default='text')
    
    # Content
    content = models.TextField(blank=True)
    media_url = models.URLField(blank=True)
    media_id = models.CharField(max_length=100, blank=True)
    media_mime_type = models.CharField(max_length=100, blank=True)
    
    # Phone numbers
    phone_from = models.CharField(max_length=20)
    phone_to = models.CharField(max_length=20)
    
    # Status
    STATUS_CHOICES = [
        ('queued', 'Queued'),
        ('sent', 'Sent'),
        ('delivered', 'Delivered'),
        ('read', 'Read'),
        ('failed', 'Failed'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='queued')
    status_description = models.CharField(max_length=200, blank=True)
    
    # Green API message ID
    green_api_message_id = models.CharField(max_length=100, blank=True)
    green_api_chat_id = models.CharField(max_length=100, blank=True)
    
    # Timestamps
    sent_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    read_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        db_table = 'messages'
        indexes = [
            models.Index(fields=['tenant_id']),
            models.Index(fields=['direction']),
            models.Index(fields=['status']),
            models.Index(fields=['phone_from']),
            models.Index(fields=['phone_to']),
            models.Index(fields=['created_at']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.direction} - {self.phone_from} -> {self.phone_to}"


class ScheduledMessage(models.Model):
    """Model for scheduled messages."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant_id = models.UUIDField()
    
    # Message content
    phone_number = models.CharField(max_length=20)
    message = models.TextField()
    media_url = models.URLField(blank=True)
    media_type = models.CharField(max_length=50, blank=True)
    
    # Scheduling
    scheduled_at = models.DateTimeField()
    timezone = models.CharField(max_length=50, default='UTC')
    
    # Status
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('cancelled', 'Cancelled'),
        ('failed', 'Failed'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Error tracking
    error_message = models.CharField(max_length=500, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        db_table = 'scheduled_messages'
        indexes = [
            models.Index(fields=['tenant_id']),
            models.Index(fields=['scheduled_at']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"Scheduled: {self.phone_number} at {self.scheduled_at}"
