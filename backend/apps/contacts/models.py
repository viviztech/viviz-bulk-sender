"""
Contact models for CRM functionality.
"""
import uuid
from django.db import models
from django.utils import timezone


class Contact(models.Model):
    """Model representing a contact in the CRM."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant_id = models.UUIDField()  # For multi-tenancy
    
    # Basic info
    phone_number = models.CharField(max_length=20)
    name = models.CharField(max_length=200, blank=True)
    email = models.EmailField(blank=True)
    company = models.CharField(max_length=200, blank=True)
    position = models.CharField(max_length=100, blank=True)
    
    # Tags for segmentation
    tags = models.JSONField(default=list, blank=True)
    
    # Custom fields (flexible metadata)
    metadata = models.JSONField(default=dict, blank=True)
    
    # Status
    is_blocked = models.BooleanField(default=False)
    is_subscribed = models.BooleanField(default=True)
    
    # Source tracking
    SOURCE_CHOICES = [
        ('manual', 'Manual Entry'),
        ('import', 'Import'),
        ('chat', 'From Chat'),
        ('campaign', 'From Campaign'),
        ('api', 'API'),
    ]
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES, default='manual')
    
    # WhatsApp-specific
    wa_id = models.CharField(max_length=100, blank=True)  # WhatsApp ID
    wa_business_id = models.CharField(max_length=100, blank=True)
    
    # Engagement stats
    messages_received = models.IntegerField(default=0)
    messages_sent = models.IntegerField(default=0)
    last_message_at = models.DateTimeField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'contacts'
        indexes = [
            models.Index(fields=['tenant_id']),
            models.Index(fields=['phone_number']),
            models.Index(fields=['tags']),
            models.Index(fields=['is_blocked']),
            models.Index(fields=['created_at']),
        ]
        unique_together = [['tenant_id', 'phone_number']]
    
    def __str__(self):
        return self.name or self.phone_number
    
    @property
    def display_name(self):
        """Return the contact's display name."""
        if self.name:
            return self.name
        return self.phone_number
    
    @property
    def engagement_score(self):
        """Calculate a simple engagement score."""
        return self.messages_received + self.messages_sent


class Tag(models.Model):
    """Model for managing contact tags."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant_id = models.UUIDField()
    name = models.CharField(max_length=100)
    color = models.CharField(max_length=7, default='#3498db')  # Hex color
    
    # Description
    description = models.CharField(max_length=200, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        db_table = 'tags'
        indexes = [
            models.Index(fields=['tenant_id']),
        ]
        unique_together = [['tenant_id', 'name']]
    
    def __str__(self):
        return self.name


class ContactActivity(models.Model):
    """Model for tracking contact activities."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    contact = models.ForeignKey(
        Contact, on_delete=models.CASCADE, related_name='activities'
    )
    
    # Activity type
    ACTIVITY_TYPES = [
        ('message_sent', 'Message Sent'),
        ('message_received', 'Message Received'),
        ('tag_added', 'Tag Added'),
        ('tag_removed', 'Tag Removed'),
        ('note_added', 'Note Added'),
        ('blocked', 'Blocked'),
        ('unblocked', 'Unblocked'),
        ('imported', 'Imported'),
        ('exported', 'Exported'),
    ]
    activity_type = models.CharField(max_length=30, choices=ACTIVITY_TYPES)
    
    # Activity details
    description = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    
    # User who performed the activity
    performed_by = models.UUIDField(null=True, blank=True)
    
    # Timestamp
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        db_table = 'contact_activities'
        indexes = [
            models.Index(fields=['contact']),
            models.Index(fields=['activity_type']),
            models.Index(fields=['created_at']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.activity_type} - {self.contact.display_name}"


class ContactNote(models.Model):
    """Model for contact notes."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    contact = models.ForeignKey(
        Contact, on_delete=models.CASCADE, related_name='notes'
    )
    
    content = models.TextField()
    
    # User who added the note
    added_by = models.UUIDField()
    
    # Timestamp
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'contact_notes'
        indexes = [
            models.Index(fields=['contact']),
            models.Index(fields=['created_at']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Note for {self.contact.display_name}"
