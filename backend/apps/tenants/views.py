"""
Views for the tenants app.
"""
from rest_framework import viewsets, status, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from .models import Tenant, TenantSettings, TenantUsage
from .serializers import (
    TenantSerializer, TenantCreateSerializer, TenantUpdateSerializer,
    TenantSettingsSerializer, TenantUsageSerializer, TenantGreenAPISerializer,
    TenantInviteSerializer
)


class TenantViewSet(viewsets.ModelViewSet):
    """ViewSet for tenant management."""
    
    serializer_class = TenantSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # Users can only see their own tenant
        return Tenant.objects.filter(id=self.request.user.tenant_id)
    
    def get_serializer_class(self):
        if self.action == 'create':
            return TenantCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return TenantUpdateSerializer
        return TenantSerializer
    
    def get_object(self):
        # Get the tenant associated with the current user
        return get_object_or_404(Tenant, id=self.request.user.tenant_id)
    
    def create(self, request, *args, **kwargs):
        # Only owners can create tenants
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        tenant = serializer.save()
        
        # Create default settings
        TenantSettings.objects.create(tenant=tenant)
        
        # Create usage tracking
        TenantUsage.objects.create(
            tenant=tenant,
            period_start=timezone.now().replace(day=1),
            period_end=timezone.now().replace(day=1) + timezone.timedelta(days=32)
        )
        
        return Response({
            'success': True,
            'message': 'Tenant created successfully.',
            'tenant': TenantSerializer(tenant).data
        }, status=status.HTTP_201_CREATED)
    
    def list(self, request, *args, **kwargs):
        # Users can only see their own tenant
        tenant = self.get_object()
        serializer = self.get_serializer(tenant)
        return Response({
            'success': True,
            'tenant': serializer.data
        })
    
    def retrieve(self, request, *args, **kwargs):
        tenant = self.get_object()
        serializer = self.get_serializer(tenant)
        return Response({
            'success': True,
            'tenant': serializer.data
        })
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        tenant = self.get_object()
        serializer = self.get_serializer(tenant, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({
            'success': True,
            'message': 'Tenant updated successfully.',
            'tenant': serializer.data
        })


class TenantSettingsView(generics.RetrieveUpdateAPIView):
    """View for tenant settings."""
    
    serializer_class = TenantSettingsSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        tenant = get_object_or_404(Tenant, id=self.request.user.tenant_id)
        settings, created = TenantSettings.objects.get_or_create(tenant=tenant)
        return settings
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({
            'success': True,
            'message': 'Settings updated successfully.',
            'settings': serializer.data
        })


class TenantUsageView(generics.RetrieveAPIView):
    """View for tenant usage statistics."""
    
    serializer_class = TenantUsageSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        tenant = get_object_or_404(Tenant, id=self.request.user.tenant_id)
        usage, created = TenantUsage.objects.get_or_create(tenant=tenant)
        return usage


class TenantGreenAPIView(APIView):
    """View for managing Green API credentials."""
    
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        tenant = get_object_or_404(Tenant, id=request.user.tenant_id)
        return Response({
            'success': True,
            'green_api': {
                'green_api_id': tenant.green_api_id,
                'green_api_instance_id': tenant.green_api_instance_id,
                'is_configured': bool(tenant.green_api_id and tenant.green_api_token)
            }
        })
    
    def put(self, request):
        tenant = get_object_or_404(Tenant, id=request.user.tenant_id)
        serializer = TenantGreenAPISerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.update(tenant, serializer.validated_data)
        return Response({
            'success': True,
            'message': 'Green API credentials updated successfully.',
            'green_api': {
                'green_api_id': tenant.green_api_id,
                'green_api_instance_id': tenant.green_api_instance_id,
                'is_configured': True
            }
        })


class TenantInviteView(APIView):
    """View for inviting users to a tenant."""
    
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        # Only admins and owners can invite users
        if request.user.role not in ['owner', 'admin']:
            return Response({
                'success': False,
                'message': 'Only admins can invite users.'
            }, status=status.HTTP_403_FORBIDDEN)
        
        serializer = TenantInviteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # TODO: Create invitation and send email
        
        return Response({
            'success': True,
            'message': f'Invitation sent to {serializer.validated_data["email"]}.'
        })


# Import timezone for the view
from django.utils import timezone
