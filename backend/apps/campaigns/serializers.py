"""
Serializers for the campaigns app.
"""
from rest_framework import serializers
from .models import Campaign, CampaignSchedule, MessageTemplate


class CampaignSerializer(serializers.ModelSerializer):
    """Serializer for the Campaign model."""
    
    delivery_rate = serializers.ReadOnlyField()
    read_rate = serializers.ReadOnlyField()
    progress_percent = serializers.ReadOnlyField()
    
    class Meta:
        model = Campaign
        fields = [
            'id', 'name', 'description', 'message_template', 'message_variables',
            'media_url', 'media_type', 'contact_filter', 'target_tags', 'target_count',
            'status', 'scheduled_at', 'started_at', 'completed_at',
            'total_recipients', 'sent_count', 'delivered_count', 'read_count',
            'failed_count', 'blocked_count', 'messages_per_minute', 'throttle_enabled',
            'created_by', 'created_at', 'updated_at', 'delivery_rate', 'read_rate',
            'progress_percent'
        ]
        read_only_fields = ['id', 'status', 'sent_count', 'delivered_count',
                          'read_count', 'failed_count', 'created_at', 'updated_at']


class CampaignCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating a campaign."""
    
    class Meta:
        model = Campaign
        fields = ['name', 'description', 'message_template', 'message_variables',
                  'media_url', 'media_type', 'contact_filter', 'target_tags',
                  'scheduled_at', 'messages_per_minute', 'throttle_enabled']
    
    def validate(self, attrs):
        # Parse variables from template
        import re
        content = attrs.get('message_template', '')
        variables = re.findall(r'\{(\w+)\}', content)
        attrs['message_variables'] = list(set(variables))
        return attrs


class CampaignUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating a campaign."""
    
    class Meta:
        model = Campaign
        fields = ['name', 'description', 'message_template', 'message_variables',
                  'media_url', 'media_type', 'contact_filter', 'target_tags',
                  'messages_per_minute', 'throttle_enabled']


class CampaignStatsSerializer(serializers.ModelSerializer):
    """Serializer for campaign statistics."""
    
    delivery_rate = serializers.ReadOnlyField()
    read_rate = serializers.ReadOnlyField()
    progress_percent = serializers.ReadOnlyField()
    
    class Meta:
        model = Campaign
        fields = [
            'id', 'name', 'status', 'total_recipients', 'sent_count',
            'delivered_count', 'read_count', 'failed_count', 'blocked_count',
            'started_at', 'completed_at', 'delivery_rate', 'read_rate',
            'progress_percent'
        ]
        read_only_fields = fields


class CampaignScheduleSerializer(serializers.ModelSerializer):
    """Serializer for the CampaignSchedule model."""
    
    class Meta:
        model = CampaignSchedule
        fields = [
            'id', 'campaign', 'scheduled_at', 'timezone', 'is_recurring',
            'recurrence_type', 'recurrence_end_date', 'is_active', 'last_run_at',
            'next_run_at', 'created_at'
        ]
        read_only_fields = ['id', 'last_run_at', 'next_run_at', 'created_at']


class MessageTemplateSerializer(serializers.ModelSerializer):
    """Serializer for the MessageTemplate model."""
    
    class Meta:
        model = MessageTemplate
        fields = [
            'id', 'name', 'description', 'content', 'variables', 'category',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'variables', 'created_at', 'updated_at']


class MessageTemplateCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating a message template."""
    
    class Meta:
        model = MessageTemplate
        fields = ['name', 'description', 'content', 'category']
    
    def validate_content(self, value):
        # Parse variables from template
        import re
        variables = re.findall(r'\{(\w+)\}', value)
        return value
