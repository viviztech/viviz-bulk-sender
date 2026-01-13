"""
Views for the green_api app.
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from apps.tenants.models import Tenant
from .service import get_green_api_service
import json
import logging

logger = logging.getLogger(__name__)


class InstanceStatusView(APIView):
    """View for checking instance status."""
    
    def get(self, request):
        tenant = Tenant.objects.get(id=request.user.tenant_id)
        try:
            service = get_green_api_service(tenant)
            result = service.get_instance_status()
            return Response({
                'success': True,
                'data': result
            })
        except Exception as e:
            return Response({
                'success': False,
                'message': str(e)
            }, status=status.HTTP_502_BAD_GATEWAY)


class QRCodeView(APIView):
    """View for getting QR code."""
    
    def get(self, request):
        tenant = Tenant.objects.get(id=request.user.tenant_id)
        try:
            service = get_green_api_service(tenant)
            result = service.get_qr_code()
            return Response({
                'success': True,
                'data': result
            })
        except Exception as e:
            return Response({
                'success': False,
                'message': str(e)
            }, status=status.HTTP_502_BAD_GATEWAY)


@method_decorator(csrf_exempt, name='dispatch')
class WebhookView(APIView):
    """View for handling Green API webhooks."""
    
    def post(self, request):
        """Handle incoming webhook from Green API."""
        try:
            data = json.loads(request.body)
            logger.info(f"Received webhook: {data}")
            
            # TODO: Process webhook based on type
            # - messageReceived: Handle incoming message
            # - messageSent: Update message status
            # - instanceStatusChanged: Update instance status
            
            return Response({'success': True})
        except Exception as e:
            logger.error(f"Webhook error: {e}")
            return Response(
                {'success': False, 'message': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
