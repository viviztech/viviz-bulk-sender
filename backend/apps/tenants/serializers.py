"""
Serializers for the tenants app.
"""
from rest_framework import serializers
from .models import Tenant, TenantSettings, TenantUsage


class TenantSerializer(serializers.ModelSerializer):
    """Serializer for the Tenant model."""
    
    is_on_trial = serializers.ReadOnlyField()
    can_send_messages = serializers.ReadOnlyField()
    
    class Meta:
        model = Tenant
        fields = [
            'id', 'name', 'slug', 'logo', 'website', 'email', 'phone', 'address',
            'subscription_status', 'is_active', 'is_verified', 'green_api_id',
            'green_api_instance_id', 'created_at', 'updated_at', 'trial_ends_at',
            'settings', 'is_on_trial', 'can_send_messages'
        ]
        read_only_fields = ['id', 'is_active', 'is_verified', 'created_at', 'updated_at']


class TenantCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating a new tenant."""
    
    class Meta:
        model = Tenant
        fields = ['name', 'slug', 'logo', 'website', 'email', 'phone', 'address']
    
    def validate_slug(self, value):
        """Ensure slug is unique."""
        if Tenant.objects.filter(slug=value).exists():
            raise serializers.ValidationError('This slug is already taken.')
        return value


class TenantUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating a tenant."""
    
    class Meta:
        model = Tenant
        fields = ['name', 'logo', 'website', 'email', 'phone', 'address', 'settings']
    
    def validate_slug(self, value):
        """Ensure slug is unique (excluding current instance)."""
        instance = getattr(self, 'instance', None)
        if instance and Tenant.objects.filter(slug=value).exclude(pk=instance.pk).exists():
            raise serializers.ValidationError('This slug is already taken.')
        return value


class TenantSettingsSerializer(serializers.ModelSerializer):
    """Serializer for the TenantSettings model."""
    
    class Meta:
        model = TenantSettings
        fields = [
            'id', 'timezone', 'language', 'date_format', 'time_format',
            'default_country_code', 'message_footer', 'signature',
            'auto_save_contacts', 'email_notifications', 'browser_notifications',
            'webhook_url', 'webhook_secret', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class TenantUsageSerializer(serializers.ModelSerializer):
    """Serializer for the TenantUsage model."""
    
    messages_usage_percent = serializers.ReadOnlyField()
    contacts_usage_percent = serializers.ReadOnlyField()
    storage_usage_percent = serializers.ReadOnlyField()
    is_over_limit = serializers.ReadOnlyField()
    
    class Meta:
        model = TenantUsage
        fields = [
            'id', 'messages_sent', 'messages_limit', 'contacts_count', 'contacts_limit',
            'campaigns_count', 'campaigns_limit', 'storage_used', 'storage_limit',
            'users_count', 'users_limit', 'period_start', 'period_end',
            'messages_usage_percent', 'contacts_usage_percent', 'storage_usage_percent',
            'is_over_limit'
        ]
        read_only_fields = ['id', 'period_start', 'period_end']


class TenantGreenAPISerializer(serializers.Serializer):
    """Serializer for updating Green API credentials."""
    
    green_api_id = serializers.CharField(max_length=100)
    green_api_token = serializers.CharField(max_length=200)
    green_api_instance_id = serializers.CharField(max_length=100)
    
    def validate(self, attrs):
        # TODO: Validate credentials with Green API
        return attrs
    
    def update(self, instance, validated_data):
        instance.green_api_id = validated_data.get('green_api_id')
        instance.green_api_token = validated_data.get('green_api_token')
        instance.green_api_instance_id = validated_data.get('green_api_instance_id')
        instance.save()
        return instance


class TenantInviteSerializer(serializers.Serializer):
    """Serializer for inviting users to a tenant."""
    
    email = serializers.EmailField()
    role = serializers.ChoiceField(
        choices=['admin', 'manager', 'agent', 'viewer'],
        default='agent'
    )
