"""
Views for the chats app.
"""
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Chat, AutoReply


class ChatViewSet(viewsets.ModelViewSet):
    """ViewSet for chat management."""
    
    def get_queryset(self):
        return Chat.objects.filter(tenant_id=self.request.user.tenant_id)
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        # Filter by status
        status_filter = request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        data = [{'id': chat.id, 'phone_number': chat.phone_number,
                 'contact_name': chat.contact_name, 'status': chat.status,
                 'unread_count': chat.unread_count, 'last_message_at': chat.last_message_at}
                for chat in queryset]
        return Response({
            'success': True,
            'chats': data,
            'count': queryset.count()
        })


class AutoReplyViewSet(viewsets.ModelViewSet):
    """ViewSet for auto-reply rules."""
    
    def get_queryset(self):
        return AutoReply.objects.filter(tenant_id=self.request.user.tenant_id)
    
    def perform_create(self, serializer):
        serializer.save(tenant_id=self.request.user.tenant_id)
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        data = [{'id': ar.id, 'name': ar.name, 'trigger_type': ar.trigger_type,
                 'trigger_value': ar.trigger_value, 'message': ar.message,
                 'is_active': ar.is_active, 'priority': ar.priority}
                for ar in queryset]
        return Response({
            'success': True,
            'auto_replies': data,
            'count': queryset.count()
        })
