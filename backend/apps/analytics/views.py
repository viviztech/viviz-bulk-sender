"""
Views for the analytics app.
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Count, Sum
from django.utils import timezone
from datetime import timedelta
from apps.messages.models import Message
from apps.contacts.models import Contact
from apps.campaigns.models import Campaign


class AnalyticsOverviewView(APIView):
    """View for analytics overview."""
    
    def get(self, request):
        tenant_id = request.user.tenant_id
        today = timezone.now().date()
        
        # Message stats
        total_messages = Message.objects.filter(tenant_id=tenant_id).count()
        today_messages = Message.objects.filter(
            tenant_id=tenant_id,
            created_at__date=today
        ).count()
        
        # Contact stats
        total_contacts = Contact.objects.filter(tenant_id=tenant_id).count()
        blocked_contacts = Contact.objects.filter(
            tenant_id=tenant_id, is_blocked=True
        ).count()
        
        # Campaign stats
        total_campaigns = Campaign.objects.filter(tenant_id=tenant_id).count()
        active_campaigns = Campaign.objects.filter(
            tenant_id=tenant_id, status='running'
        ).count()
        
        return Response({
            'success': True,
            'data': {
                'messages': {
                    'total': total_messages,
                    'today': today_messages,
                },
                'contacts': {
                    'total': total_contacts,
                    'blocked': blocked_contacts,
                },
                'campaigns': {
                    'total': total_campaigns,
                    'active': active_campaigns,
                }
            }
        })


class MessageStatsView(APIView):
    """View for message statistics."""
    
    def get(self, request):
        tenant_id = request.user.tenant_id
        days = int(request.query_params.get('days', 30))
        
        start_date = timezone.now() - timedelta(days=days)
        
        # Group by date
        from django.db.models.functions import TruncDate
        messages_by_date = Message.objects.filter(
            tenant_id=tenant_id,
            created_at__gte=start_date
        ).annotate(
            date=TruncDate('created_at')
        ).values('date').annotate(
            count=Count('id'),
            sent=Count('id', filter={'direction': 'outbound'}),
            received=Count('id', filter={'direction': 'inbound'})
        ).order_by('date')
        
        return Response({
            'success': True,
            'data': {
                'period': f'Last {days} days',
                'messages': list(messages_by_date)
            }
        })


class CampaignStatsView(APIView):
    """View for campaign statistics."""
    
    def get(self, request):
        tenant_id = request.user.tenant_id
        
        campaigns = Campaign.objects.filter(
            tenant_id=tenant_id
        ).values('id', 'name', 'status', 'total_recipients',
                'sent_count', 'delivered_count', 'read_count',
                'failed_count', 'created_at')
        
        return Response({
            'success': True,
            'data': list(campaigns)
        })
