"""
Views for the messages app.
"""
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Message, ScheduledMessage
from .serializers import MessageSerializer, ScheduledMessageSerializer
import uuid


class MessageViewSet(viewsets.ModelViewSet):
    """ViewSet for message management."""
    
    serializer_class = MessageSerializer
    
    def get_queryset(self):
        return Message.objects.filter(tenant_id=self.request.user.tenant_id)
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'success': True,
            'messages': serializer.data,
            'count': queryset.count()
        })


class SendMessageView(APIView):
    """View for sending individual messages."""
    
    def post(self, request):
        phone_number = request.data.get('phone_number')
        message = request.data.get('message')
        media_url = request.data.get('media_url')
        media_type = request.data.get('media_type')
        
        if not phone_number or not message:
            return Response({
                'success': False,
                'message': 'phone_number and message are required.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Create message record
        msg = Message.objects.create(
            tenant_id=request.user.tenant_id,
            direction='outbound',
            phone_from='self',
            phone_to=phone_number,
            content=message,
            media_url=media_url,
            media_type=media_type,
            status='queued'
        )
        
        # TODO: Queue message sending task via Celery
        
        return Response({
            'success': True,
            'message': 'Message queued successfully.',
            'data': MessageSerializer(msg).data
        }, status=status.HTTP_201_CREATED)


class ScheduledMessageViewSet(viewsets.ModelViewSet):
    """ViewSet for scheduled messages."""
    
    serializer_class = ScheduledMessageSerializer
    
    def get_queryset(self):
        return ScheduledMessage.objects.filter(tenant_id=self.request.user.tenant_id)
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'success': True,
            'scheduled_messages': serializer.data,
            'count': queryset.count()
        })
