"""
Admin configuration for the tenants app.
"""
from django.contrib import admin
from .models import Tenant, TenantSettings, TenantUsage


@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    """Admin configuration for the Tenant model."""
    
    list_display = ('name', 'slug', 'subscription_status', 'is_active', 'created_at')
    list_filter = ('subscription_status', 'is_active', 'created_at')
    search_fields = ('name', 'slug', 'email')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        (None, {'fields': ('name', 'slug', 'logo')}),
        ('Contact Info', {'fields': ('website', 'email', 'phone', 'address')}),
        ('Subscription', {'fields': ('subscription_status', 'trial_ends_at')}),
        ('Green API', {'fields': ('green_api_id', 'green_api_instance_id')}),
        ('Status', {'fields': ('is_active', 'is_verified')}),
        ('Settings', {'fields': ('settings',)}),
        ('Dates', {'fields': ('created_at', 'updated_at')}),
    )


@admin.register(TenantSettings)
class TenantSettingsAdmin(admin.ModelAdmin):
    """Admin configuration for the TenantSettings model."""
    
    list_display = ('tenant', 'timezone', 'language', 'created_at')
    list_filter = ('timezone', 'language')
    search_fields = ('tenant__name',)


@admin.register(TenantUsage)
class TenantUsageAdmin(admin.ModelAdmin):
    """Admin configuration for the TenantUsage model."""
    
    list_display = ('tenant', 'messages_sent', 'messages_limit', 'contacts_count', 'period_start')
    list_filter = ('period_start',)
    search_fields = ('tenant__name',)
