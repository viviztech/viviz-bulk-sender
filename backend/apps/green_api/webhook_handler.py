"""
Webhook handler for Green API messages.
"""
import json
import logging
from django.utils import timezone
from django.db import transaction
from apps.tenants.models import Tenant
from apps.contacts.models import Contact, ContactActivity
from apps.messages.models import Message
from apps.chats.models import Chat, AutoReply
from apps.campaigns.tasks import update_message_delivery_status

logger = logging.getLogger(__name__)


class GreenAPIWebhookHandler:
    """Handler for Green API webhook events."""
    
    def __init__(self, webhook_data):
        self.data = webhook_data
        self.event_type = webhook_data.get('type', '')
    
    def process(self):
        """Process the webhook based on event type."""
        handlers = {
            'messageReceived': self.handle_message_received,
            'messageSent': self.handle_message_sent,
            'messageRead': self.handle_message_read,
            'instanceStatusChanged': self.handle_status_changed,
            'contactAdded': self.handle_contact_added,
        }
        
        handler = handlers.get(self.event_type)
        if handler:
            return handler()
        else:
            logger.warning(f"Unknown webhook event type: {self.event_type}")
            return {'status': 'unknown', 'event': self.event_type}
    
    def handle_message_received(self):
        """Handle incoming messages."""
        try:
            message_data = self.data.get('messageData', {})
            sender = message_data.get('sender', '')
            message_type = message_data.get('type', 'text')
            text = message_data.get('textMessage', {}).get('text', '')
            media = message_data.get('fileMessage', {})
            
            # Normalize phone number
            phone = sender.replace('@c.us', '').replace('@g.us', '')
            
            # Find or create contact
            tenant = self._find_tenant_by_phone(phone)
            if not tenant:
                logger.warning(f"No tenant found for phone: {phone}")
                return {'status': 'skipped', 'reason': 'No tenant'}
            
            contact, created = Contact.objects.get_or_create(
                tenant_id=tenant.id,
                phone_number=phone,
                defaults={
                    'wa_id': sender,
                    'source': 'chat'
                }
            )
            
            # Create message
            message = Message.objects.create(
                tenant_id=tenant.id,
                direction='inbound',
                message_type=message_type,
                content=text,
                media_url=media.get('fileUrl', ''),
                media_id=media.get('fileUniqueId', ''),
                phone_from=phone,
                phone_to='self',
                green_api_chat_id=sender,
                green_api_message_id=self.data.get('idMessage', ''),
                status='received'
            )
            
            # Update contact stats
            contact.messages_received += 1
            contact.last_message_at = timezone.now()
            contact.save()
            
            # Log activity
            ContactActivity.objects.create(
                contact=contact,
                activity_type='message_received',
                description=f"Received: {text[:100]}"
            )
            
            # Update or create chat
            chat, _ = Chat.objects.get_or_create(
                tenant_id=tenant.id,
                phone_number=phone,
                defaults={'contact_name': contact.name}
            )
            chat.last_message_preview = text[:200]
            chat.last_message_at = timezone.now()
            chat.unread_count += 1
            chat.save()
            
            # Check for auto-reply
            self._process_auto_reply(tenant.id, phone, text, message.id)
            
            logger.info(f"Incoming message processed: {message.id}")
            return {'status': 'success', 'message_id': message.id}
            
        except Exception as e:
            logger.error(f"Error handling message received: {e}")
            return {'status': 'error', 'message': str(e)}
    
    def handle_message_sent(self):
        """Handle outgoing message delivery confirmation."""
        try:
            message_id = self.data.get('idMessage', '')
            chat_id = self.data.get('chatId', '')
            
            # Find message by Green API ID
            message = Message.objects.filter(
                green_api_message_id=message_id
            ).first()
            
            if message:
                message.status = 'delivered'
                message.delivered_at = timezone.now()
                message.save()
                
                # Update campaign stats
                if message.campaign_id:
                    from apps.campaigns.tasks import update_campaign_stats
                    update_campaign_stats.delay(message.campaign_id)
            
            return {'status': 'success'}
            
        except Exception as e:
            logger.error(f"Error handling message sent: {e}")
            return {'status': 'error', 'message': str(e)}
    
    def handle_message_read(self):
        """Handle message read confirmation."""
        try:
            message_id = self.data.get('idMessage', '')
            
            message = Message.objects.filter(
                green_api_message_id=message_id
            ).first()
            
            if message:
                message.status = 'read'
                message.read_at = timezone.now()
                message.save()
            
            return {'status': 'success'}
            
        except Exception as e:
            logger.error(f"Error handling message read: {e}")
            return {'status': 'error', 'message': str(e)}
    
    def handle_status_changed(self):
        """Handle instance status changes."""
        try:
            instance_data = self.data.get('instanceData', {})
            status = instance_data.get('state', '')
            chat_id = instance_data.get('chatId', '')
            
            # Find tenant by Green API instance
            phone = chat_id.replace('@c.us', '') if chat_id else ''
            tenant = self._find_tenant_by_phone(phone)
            
            if tenant:
                # Update instance status
                # This could trigger notifications or logging
                logger.info(f"Tenant {tenant.id} instance status: {status}")
            
            return {'status': 'success'}
            
        except Exception as e:
            logger.error(f"Error handling status change: {e}")
            return {'status': 'error', 'message': str(e)}
    
    def handle_contact_added(self):
        """Handle contact added event."""
        try:
            contact_data = self.data.get('contact', {})
            phone = contact_data.get('id', '').replace('@c.us', '')
            
            contact = Contact.objects.filter(phone_number=phone).first()
            if contact:
                contact.wa_id = contact_data.get('id', '')
                contact.save()
            
            return {'status': 'success'}
            
        except Exception as e:
            logger.error(f"Error handling contact added: {e}")
            return {'status': 'error', 'message': str(e)}
    
    def _process_auto_reply(self, tenant_id, phone, message_text, message_id):
        """Process auto-reply rules for incoming message."""
        try:
            rules = AutoReply.objects.filter(
                tenant_id=tenant_id,
                is_active=True
            ).order_by('-priority')
            
            for rule in rules:
                matched = False
                
                if rule.trigger_type == 'keyword':
                    matched = rule.trigger_value.lower() in message_text.lower()
                elif rule.trigger_type == 'exact':
                    matched = message_text.lower() == rule.trigger_value.lower()
                elif rule.trigger_type == 'always':
                    matched = True
                
                if matched:
                    # Create and queue reply message
                    reply_message = Message.objects.create(
                        tenant_id=tenant_id,
                        direction='outbound',
                        message_type='text',
                        content=rule.message,
                        media_url=rule.media_url,
                        phone_from='self',
                        phone_to=phone,
                        status='queued'
                    )
                    
                    # Queue sending task
                    from apps.campaigns.tasks import send_single_message
                    send_single_message.delay(reply_message.id)
                    
                    logger.info(f"Auto-reply sent to {phone}: {rule.name}")
                    break
                    
        except Exception as e:
            logger.error(f"Error processing auto-reply: {e}")
    
    def _find_tenant_by_phone(self, phone):
        """Find tenant associated with a phone number."""
        # In a multi-tenant system, we need another way to identify the tenant
        # This could be done by:
        # 1. Matching with tenant's configured phone number
        # 2. Using a mapping table
        # 3. Using the first active tenant (for single-tenant scenarios)
        
        # For now, return the first active tenant
        return Tenant.objects.filter(is_active=True).first()


def process_webhook(webhook_data):
    """Main entry point for processing webhooks."""
    handler = GreenAPIWebhookHandler(webhook_data)
    return handler.process()
