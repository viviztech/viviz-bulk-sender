"""
Admin configuration for the authentication app.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User, UserInvitation


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin configuration for the User model."""
    
    list_display = ('email', 'full_name', 'tenant_id', 'role', 'is_active', 'date_joined')
    list_filter = ('is_active', 'is_staff', 'role', 'date_joined')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('-date_joined',)
    
    fieldsets = (
        (_('Account Info'), {'fields': ('email', 'password')}),
        (_('Personal Info'), {'fields': ('first_name', 'last_name', 'phone', 'avatar')}),
        (_('Tenant'), {'fields': ('tenant_id',)}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'role', 'groups', 'user_permissions')}),
        (_('Dates'), {'fields': ('date_joined', 'last_login')}),
        (_('Preferences'), {'fields': ('timezone', 'language')}),
    )
    
    add_fieldsets = (
        (_('Account Info'), {'fields': ('email', 'password1', 'password2')}),
        (_('Personal Info'), {'fields': ('first_name', 'last_name', 'phone')}),
        (_('Tenant'), {'fields': ('tenant_id',)}),
        (_('Permissions'), {'fields': ('role',)}),
    )
    
    readonly_fields = ('date_joined', 'last_login')
    
    def get_readonly_fields(self, request, obj=None):
        readonly = super().get_readonly_fields(request, obj)
        if obj:
            readonly += ('tenant_id',)
        return readonly


@admin.register(UserInvitation)
class UserInvitationAdmin(admin.ModelAdmin):
    """Admin configuration for the UserInvitation model."""
    
    list_display = ('email', 'role', 'invited_by', 'is_accepted', 'created_at', 'expires_at')
    list_filter = ('role', 'is_accepted', 'created_at')
    search_fields = ('email', 'invited_by__email')
    ordering = ('-created_at',)
    readonly_fields = ('token', 'created_at')
