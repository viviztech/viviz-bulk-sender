"""
Serializers for the messages app.
"""
from rest_framework import serializers
from .models import Message, ScheduledMessage


class MessageSerializer(serializers.ModelSerializer):
    """Serializer for the Message model."""
    
    class Meta:
        model = Message
        fields = [
            'id', 'tenant_id', 'direction', 'message_type', 'content',
            'media_url', 'media_id', 'media_mime_type', 'phone_from',
            'phone_to', 'status', 'status_description', 'green_api_message_id',
            'green_api_chat_id', 'sent_at', 'delivered_at', 'read_at', 'created_at'
        ]
        read_only_fields = ['id', 'tenant_id', 'green_api_message_id',
                          'sent_at', 'delivered_at', 'read_at', 'created_at']


class SendMessageSerializer(serializers.Serializer):
    """Serializer for sending a message."""
    
    phone_number = serializers.CharField(max_length=20)
    message = serializers.CharField()
    media_url = serializers.URLField(required=False, allow_blank=True)
    media_type = serializers.CharField(max_length=50, required=False)


class ScheduledMessageSerializer(serializers.ModelSerializer):
    """Serializer for the ScheduledMessage model."""
    
    class Meta:
        model = ScheduledMessage
        fields = [
            'id', 'tenant_id', 'phone_number', 'message', 'media_url',
            'media_type', 'scheduled_at', 'timezone', 'status', 'error_message',
            'created_at'
        ]
        read_only_fields = ['id', 'tenant_id', 'status', 'error_message', 'created_at']
