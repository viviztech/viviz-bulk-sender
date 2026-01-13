"""
Admin configuration for the contacts app.
"""
from django.contrib import admin
from .models import Contact, Tag, ContactActivity, ContactNote


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    """Admin configuration for the Contact model."""
    
    list_display = ('display_name', 'phone_number', 'tenant_id', 'is_blocked',
                   'messages_sent', 'messages_received', 'created_at')
    list_filter = ('is_blocked', 'is_subscribed', 'source', 'created_at')
    search_fields = ('phone_number', 'name', 'email', 'company')
    readonly_fields = ('wa_id', 'wa_business_id', 'messages_received',
                      'messages_sent', 'created_at', 'updated_at')
    raw_id_fields = ('tenant_id',)
    
    fieldsets = (
        (None, {'fields': ('tenant_id', 'phone_number', 'wa_id')}),
        ('Personal Info', {'fields': ('name', 'email', 'company', 'position')}),
        ('Status', {'fields': ('is_blocked', 'is_subscribed', 'tags')}),
        ('WhatsApp', {'fields': ('wa_business_id',)}),
        ('Engagement', {'fields': ('messages_sent', 'messages_received', 'last_message_at')}),
        ('Additional', {'fields': ('metadata', 'source')}),
        ('Dates', {'fields': ('created_at', 'updated_at')}),
    )


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Admin configuration for the Tag model."""
    
    list_display = ('name', 'color', 'tenant_id', 'created_at')
    list_filter = ('tenant_id', 'created_at')
    search_fields = ('name', 'description')


@admin.register(ContactActivity)
class ContactActivityAdmin(admin.ModelAdmin):
    """Admin configuration for the ContactActivity model."""
    
    list_display = ('contact', 'activity_type', 'performed_by', 'created_at')
    list_filter = ('activity_type', 'created_at')
    search_fields = ('contact__phone_number', 'contact__name', 'description')


@admin.register(ContactNote)
class ContactNoteAdmin(admin.ModelAdmin):
    """Admin configuration for the ContactNote model."""
    
    list_display = ('contact', 'added_by', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('contact__phone_number', 'contact__name', 'content')
