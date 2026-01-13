"""
Celery tasks for campaigns and message sending.
"""
import logging
from celery import shared_task
from django.utils import timezone
from django.db import models, transaction
from apps.tenants.models import Tenant
from apps.contacts.models import Contact
from apps.messages.models import Message, ScheduledMessage
from apps.green_api.service import get_green_api_service

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_single_message(self, message_id):
    """Send a single message via Green API."""
    try:
        message = Message.objects.get(id=message_id)
        tenant = Tenant.objects.get(id=message.tenant_id)
        
        # Check if tenant can send messages
        if not tenant.can_send_messages:
            message.status = 'failed'
            message.status_description = 'Tenant cannot send messages'
            message.save()
            return {'status': 'error', 'message': 'Tenant cannot send messages'}
        
        # Get Green API service
        service = get_green_api_service(tenant)
        
        # Send message based on type
        if message.media_url:
            if message.media_type == 'image':
                service.send_image(message.phone_to, message.media_url, message.content)
            elif message.media_type == 'video':
                service.send_video(message.phone_to, message.media_url, message.content)
            else:
                service.send_file(message.phone_to, message.media_url, 
                                 message.media_id or 'file', message.content)
        else:
            service.send_message(message.phone_to, message.content)
        
        # Update message status
        message.status = 'sent'
        message.sent_at = timezone.now()
        message.save()
        
        # Update contact stats
        Contact.objects.filter(tenant_id=message.tenant_id, 
                              phone_number=message.phone_to).update(
            messages_sent=models.F('messages_sent') + 1,
            last_message_at=timezone.now()
        )
        
        logger.info(f"Message sent successfully: {message_id}")
        return {'status': 'success', 'message_id': message_id}
        
    except Message.DoesNotExist:
        logger.error(f"Message not found: {message_id}")
        return {'status': 'error', 'message': 'Message not found'}
    except Exception as e:
        logger.error(f"Error sending message {message_id}: {e}")
        raise self.retry(exc=e)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def process_campaign(self, campaign_id):
    """Process a bulk messaging campaign."""
    try:
        from apps.campaigns.models import Campaign
        campaign = Campaign.objects.get(id=campaign_id)
        
        if campaign.status != 'running':
            return {'status': 'skipped', 'reason': 'Campaign not running'}
        
        # Get target contacts
        contacts = Contact.objects.filter(
            tenant_id=campaign.tenant_id,
            is_blocked=False,
            is_subscribed=True
        )
        
        # Apply tag filter if specified
        if campaign.target_tags:
            contacts = contacts.filter(tags__overlap=campaign.target_tags)
        
        # Get unprocessed contacts
        sent_message_ids = set(
            Message.objects.filter(
                campaign_id=campaign_id
            ).values_list('contact_id', flat=True)
        )
        
        pending_contacts = contacts.exclude(id__in=sent_message_ids)
        
        if not pending_contacts.exists():
            # Campaign complete
            campaign.status = 'completed'
            campaign.completed_at = timezone.now()
            campaign.save()
            return {'status': 'complete', 'campaign_id': campaign_id}
        
        # Process in batches with rate limiting
        batch_size = campaign.messages_per_minute
        throttle_seconds = 60 // batch_size if batch_size > 0 else 1
        
        for contact in pending_contacts[:batch_size]:
            # Personalize message
            content = campaign.message_template
            variables = campaign.message_variables or {}
            for var, value in variables.items():
                content = content.replace(f'{{{var}}}', str(getattr(contact, var, value)))
            
            # Create message
            message = Message.objects.create(
                tenant_id=campaign.tenant_id,
                contact_id=contact.id,
                campaign_id=campaign_id,
                direction='outbound',
                message_type='text',
                content=content,
                phone_from='self',
                phone_to=contact.phone_number,
                status='queued'
            )
            
            # Queue sending task
            send_single_message.delay(message.id)
            
            # Update campaign stats
            campaign.total_recipients += 1
            campaign.save()
        
        return {'status': 'processing', 'campaign_id': campaign_id, 
                'processed': min(batch_size, pending_contacts.count())}
        
    except Exception as e:
        logger.error(f"Error processing campaign {campaign_id}: {e}")
        raise self.retry(exc=e)


@shared_task
def process_scheduled_messages():
    """Process due scheduled messages."""
    now = timezone.now()
    due_messages = ScheduledMessage.objects.filter(
        status='pending',
        scheduled_at__lte=now
    )[:100]
    
    for scheduled in due_messages:
        # Create message
        message = Message.objects.create(
            tenant_id=scheduled.tenant_id,
            direction='outbound',
            message_type='text' if not scheduled.media_type else scheduled.media_type,
            content=scheduled.message,
            media_url=scheduled.media_url,
            phone_from='self',
            phone_to=scheduled.phone_number,
            status='queued'
        )
        
        # Queue sending task
        send_single_message.delay(message.id)
        
        # Update scheduled message
        scheduled.status = 'sent'
        scheduled.save()
    
    return {'processed': due_messages.count()}


@shared_task
def update_message_delivery_status(message_id, status):
    """Update message delivery status from webhook."""
    try:
        message = Message.objects.get(id=message_id)
        message.status = status
        
        if status == 'delivered':
            message.delivered_at = timezone.now()
        elif status == 'read':
            message.read_at = timezone.now()
        
        message.save()
        return {'status': 'success'}
    except Message.DoesNotExist:
        return {'status': 'error', 'message': 'Message not found'}


@shared_task
def check_and_start_scheduled_campaigns():
    """Check for campaigns that need to start."""
    from apps.campaigns.models import Campaign
    now = timezone.now()
    
    campaigns = Campaign.objects.filter(
        status='scheduled',
        scheduled_at__lte=now
    )
    
    for campaign in campaigns:
        campaign.status = 'running'
        campaign.started_at = now
        campaign.save()
        process_campaign.delay(campaign.id)
    
    return {'started': campaigns.count()}
