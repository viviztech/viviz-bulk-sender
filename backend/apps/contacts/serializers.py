"""
Serializers for the contacts app.
"""
from rest_framework import serializers
from .models import Contact, Tag, ContactActivity, ContactNote


class ContactSerializer(serializers.ModelSerializer):
    """Serializer for the Contact model."""
    
    display_name = serializers.ReadOnlyField()
    engagement_score = serializers.ReadOnlyField()
    
    class Meta:
        model = Contact
        fields = [
            'id', 'phone_number', 'name', 'email', 'company', 'position',
            'tags', 'metadata', 'is_blocked', 'is_subscribed', 'source',
            'wa_id', 'wa_business_id', 'messages_received', 'messages_sent',
            'last_message_at', 'created_at', 'updated_at', 'display_name',
            'engagement_score'
        ]
        read_only_fields = ['id', 'wa_id', 'wa_business_id', 'messages_received',
                          'messages_sent', 'last_message_at', 'created_at', 'updated_at']


class ContactCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating a contact."""
    
    class Meta:
        model = Contact
        fields = ['phone_number', 'name', 'email', 'company', 'position',
                  'tags', 'metadata', 'is_blocked', 'is_subscribed', 'source']
    
    def validate_phone_number(self, value):
        """Validate and normalize phone number."""
        # Remove any non-digit characters except leading +
        import re
        phone = re.sub(r'[^\d+]', '', value)
        
        # Ensure it starts with country code
        if not phone.startswith('+'):
            phone = '+' + phone
        
        return phone


class ContactUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating a contact."""
    
    class Meta:
        model = Contact
        fields = ['name', 'email', 'company', 'position', 'tags', 'metadata',
                  'is_blocked', 'is_subscribed']


class TagSerializer(serializers.ModelSerializer):
    """Serializer for the Tag model."""
    
    contacts_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Tag
        fields = ['id', 'name', 'color', 'description', 'contacts_count', 'created_at']
        read_only_fields = ['id', 'created_at']
    
    def get_contacts_count(self, obj):
        return obj.contact_set.count()


class TagCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating a tag."""
    
    class Meta:
        model = Tag
        fields = ['name', 'color', 'description']


class ContactActivitySerializer(serializers.ModelSerializer):
    """Serializer for the ContactActivity model."""
    
    class Meta:
        model = ContactActivity
        fields = ['id', 'contact', 'activity_type', 'description', 'metadata',
                  'performed_by', 'created_at']
        read_only_fields = ['id', 'contact', 'activity_type', 'metadata',
                          'performed_by', 'created_at']


class ContactNoteSerializer(serializers.ModelSerializer):
    """Serializer for the ContactNote model."""
    
    class Meta:
        model = ContactNote
        fields = ['id', 'contact', 'content', 'added_by', 'created_at', 'updated_at']
        read_only_fields = ['id', 'contact', 'added_by', 'created_at', 'updated_at']


class ContactNoteCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating a contact note."""
    
    class Meta:
        model = ContactNote
        fields = ['content']


class BulkContactSerializer(serializers.Serializer):
    """Serializer for bulk contact operations."""
    
    phone_numbers = serializers.ListField(
        child=serializers.CharField(),
        min_length=1,
        max_length=1000
    )
    tags = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        default=list
    )
    metadata = serializers.JSONField(required=False, default=dict)


class ContactImportSerializer(serializers.Serializer):
    """Serializer for contact import."""
    
    file = serializers.FileField()
    mapping = serializers.JSONField()
    tags = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        default=list
    )
