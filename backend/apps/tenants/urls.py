"""
URL configuration for the tenants app.
"""
from django.urls import path
from .views import (
    TenantViewSet, TenantSettingsView, TenantUsageView,
    TenantGreenAPIView, TenantInviteView
)

urlpatterns = [
    path('tenants/', TenantViewSet.as_view({
        'get': 'list',
        'post': 'create'
    }), name='tenant-list'),
    
    path('tenants/me/', TenantViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update'
    }), name='tenant-detail'),
    
    path('tenants/settings/', TenantSettingsView.as_view(), name='tenant-settings'),
    path('tenants/usage/', TenantUsageView.as_view(), name='tenant-usage'),
    path('tenants/green-api/', TenantGreenAPIView.as_view(), name='tenant-green-api'),
    path('tenants/invite/', TenantInviteView.as_view(), name='tenant-invite'),
]
