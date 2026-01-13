"""
Views for the campaigns app.
"""
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.utils import timezone

from .models import Campaign, CampaignSchedule, MessageTemplate
from .serializers import (
    CampaignSerializer, CampaignCreateSerializer, CampaignUpdateSerializer,
    CampaignStatsSerializer, CampaignScheduleSerializer,
    MessageTemplateSerializer, MessageTemplateCreateSerializer
)


class CampaignViewSet(viewsets.ModelViewSet):
    """ViewSet for campaign management."""
    
    def get_queryset(self):
        return Campaign.objects.filter(tenant_id=self.request.user.tenant_id)
    
    def get_serializer_class(self):
        if self.action == 'create':
            return CampaignCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return CampaignUpdateSerializer
        elif self.action == 'stats':
            return CampaignStatsSerializer
        return CampaignSerializer
    
    def perform_create(self, serializer):
        serializer.save(tenant_id=self.request.user.tenant_id, created_by=self.request.user.id)
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'success': True,
            'campaigns': serializer.data,
            'count': queryset.count()
        })
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({
            'success': True,
            'campaign': serializer.data
        })
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.status == 'running':
            return Response({
                'success': False,
                'message': 'Cannot delete a running campaign. Pause it first.'
            }, status=status.HTTP_400_BAD_REQUEST)
        instance.delete()
        return Response({
            'success': True,
            'message': 'Campaign deleted successfully.'
        })


class CampaignActionView(APIView):
    """View for campaign actions (start, pause, cancel)."""
    
    def post(self, request, pk):
        campaign = Campaign.objects.get(
            id=pk, tenant_id=request.user.tenant_id
        )
        
        action = request.data.get('action')
        
        if action == 'start':
            if campaign.status not in ['draft', 'scheduled', 'paused']:
                return Response({
                    'success': False,
                    'message': f'Cannot start campaign with status: {campaign.status}'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            campaign.status = 'running'
            campaign.started_at = timezone.now()
            campaign.save()
            
            # TODO: Queue campaign execution task
            
            return Response({
                'success': True,
                'message': 'Campaign started successfully.'
            })
        
        elif action == 'pause':
            if campaign.status != 'running':
                return Response({
                    'success': False,
                    'message': 'Can only pause running campaigns.'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            campaign.status = 'paused'
            campaign.save()
            
            return Response({
                'success': True,
                'message': 'Campaign paused successfully.'
            })
        
        elif action == 'cancel':
            if campaign.status == 'completed':
                return Response({
                    'success': False,
                    'message': 'Cannot cancel a completed campaign.'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            campaign.status = 'cancelled'
            campaign.completed_at = timezone.now()
            campaign.save()
            
            return Response({
                'success': True,
                'message': 'Campaign cancelled successfully.'
            })
        
        return Response({
            'success': False,
            'message': 'Invalid action.'
        }, status=status.HTTP_400_BAD_REQUEST)


class CampaignStatsView(APIView):
    """View for campaign statistics."""
    
    def get(self, request, pk):
        campaign = Campaign.objects.get(
            id=pk, tenant_id=request.user.tenant_id
        )
        serializer = CampaignStatsSerializer(campaign)
        return Response({
            'success': True,
            'stats': serializer.data
        })


class MessageTemplateViewSet(viewsets.ModelViewSet):
    """ViewSet for message templates."""
    
    def get_queryset(self):
        return MessageTemplate.objects.filter(tenant_id=self.request.user.tenant_id)
    
    def get_serializer_class(self):
        if self.action == 'create':
            return MessageTemplateCreateSerializer
        return MessageTemplateSerializer
    
    def perform_create(self, serializer):
        serializer.save(tenant_id=self.request.user.tenant_id)
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'success': True,
            'templates': serializer.data,
            'count': queryset.count()
        })
