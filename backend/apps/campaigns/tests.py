"""
Unit tests for the campaigns app.
"""
import pytest
from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from rest_framework.test import APITestCase
from rest_framework import status
from apps.campaigns.models import Campaign, CampaignSchedule, MessageTemplate


class CampaignModelTests(TestCase):
    """Tests for the Campaign model."""
    
    def test_create_campaign(self):
        """Test creating a campaign."""
        campaign = Campaign.objects.create(
            tenant_id='test-tenant-id',
            name='Test Campaign',
            message_template='Hello {name}!',
            message_variables={'name': 'Contact Name'},
            created_by='test-user-id'
        )
        
        self.assertEqual(campaign.name, 'Test Campaign')
        self.assertEqual(campaign.status, 'draft')
        self.assertEqual(campaign.message_template, 'Hello {name}!')
        self.assertTrue(campaign.throttle_enabled)
    
    def test_delivery_rate(self):
        """Test the delivery_rate property."""
        campaign = Campaign.objects.create(
            tenant_id='test-tenant-id',
            name='Test Campaign',
            message_template='Test message',
            created_by='test-user-id',
            total_recipients=100,
            sent_count=80,
            delivered_count=60
        )
        
        self.assertEqual(campaign.delivery_rate, 75.0)
    
    def test_delivery_rate_zero(self):
        """Test delivery_rate when no messages sent."""
        campaign = Campaign.objects.create(
            tenant_id='test-tenant-id',
            name='Test Campaign',
            message_template='Test message',
            created_by='test-user-id',
            total_recipients=0,
            sent_count=0
        )
        
        self.assertEqual(campaign.delivery_rate, 0)
    
    def test_read_rate(self):
        """Test the read_rate property."""
        campaign = Campaign.objects.create(
            tenant_id='test-tenant-id',
            name='Test Campaign',
            message_template='Test message',
            created_by='test-user-id',
            delivered_count=100,
            read_count=40
        )
        
        self.assertEqual(campaign.read_rate, 40.0)
    
    def test_progress_percent(self):
        """Test the progress_percent property."""
        campaign = Campaign.objects.create(
            tenant_id='test-tenant-id',
            name='Test Campaign',
            message_template='Test message',
            created_by='test-user-id',
            total_recipients=100,
            sent_count=50,
            failed_count=10,
            blocked_count=5
        )
        
        self.assertEqual(campaign.progress_percent, 65.0)
    
    def test_string_representation(self):
        """Test campaign string representation."""
        campaign = Campaign.objects.create(
            tenant_id='test-tenant-id',
            name='My Campaign',
            message_template='Test',
            created_by='test-user-id'
        )
        
        self.assertEqual(str(campaign), 'My Campaign')


class MessageTemplateTests(TestCase):
    """Tests for the MessageTemplate model."""
    
    def test_create_template(self):
        """Test creating a message template."""
        template = MessageTemplate.objects.create(
            tenant_id='test-tenant-id',
            name='Welcome Template',
            content='Welcome {name} to our service!',
            category='marketing'
        )
        
        self.assertEqual(template.name, 'Welcome Template')
        self.assertEqual(template.category, 'marketing')
    
    def test_parse_variables(self):
        """Test parsing variables from template."""
        template = MessageTemplate.objects.create(
            tenant_id='test-tenant-id',
            name='Test Template',
            content='Hello {name}, your order {order_id} is confirmed.'
        )
        
        variables = template.parse_variables()
        
        self.assertIn('name', variables)
        self.assertIn('order_id', variables)
        self.assertEqual(len(variables), 2)


class CampaignAPITests(APITestCase):
    """Tests for the campaigns API endpoints."""
    
    def setUp(self):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        self.user = User.objects.create_user(
            email='test@example.com',
            password='test123',
            tenant_id='test-tenant-id'
        )
        self.client.force_authenticate(self.user)
    
    def test_list_campaigns(self):
        """Test listing campaigns."""
        Campaign.objects.create(
            tenant_id=self.user.tenant_id,
            name='Campaign 1',
            message_template='Test 1',
            created_by=self.user.id
        )
        Campaign.objects.create(
            tenant_id=self.user.tenant_id,
            name='Campaign 2',
            message_template='Test 2',
            created_by=self.user.id
        )
        
        url = '/api/campaigns/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['campaigns']), 2)
    
    def test_create_campaign(self):
        """Test creating a campaign."""
        url = '/api/campaigns/'
        data = {
            'name': 'New Campaign',
            'message_template': 'Hello {name}!',
            'target_tags': ['vip'],
            'messages_per_minute': 20
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['success'])
        self.assertEqual(Campaign.objects.count(), 1)
    
    def test_start_campaign(self):
        """Test starting a campaign."""
        campaign = Campaign.objects.create(
            tenant_id=self.user.tenant_id,
            name='Test Campaign',
            message_template='Test message',
            created_by=self.user.id
        )
        
        url = f'/api/campaigns/{campaign.id}/action/'
        data = {'action': 'start'}
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        campaign.refresh_from_db()
        self.assertEqual(campaign.status, 'running')
    
    def test_pause_campaign(self):
        """Test pausing a running campaign."""
        campaign = Campaign.objects.create(
            tenant_id=self.user.tenant_id,
            name='Test Campaign',
            message_template='Test message',
            created_by=self.user.id,
            status='running',
            started_at=timezone.now()
        )
        
        url = f'/api/campaigns/{campaign.id}/action/'
        data = {'action': 'pause'}
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        campaign.refresh_from_db()
        self.assertEqual(campaign.status, 'paused')
    
    def test_cancel_campaign(self):
        """Test cancelling a campaign."""
        campaign = Campaign.objects.create(
            tenant_id=self.user.tenant_id,
            name='Test Campaign',
            message_template='Test message',
            created_by=self.user.id,
            status='running',
            started_at=timezone.now()
        )
        
        url = f'/api/campaigns/{campaign.id}/action/'
        data = {'action': 'cancel'}
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        campaign.refresh_from_db()
        self.assertEqual(campaign.status, 'cancelled')
        self.assertIsNotNone(campaign.completed_at)
    
    def test_delete_campaign(self):
        """Test deleting a campaign."""
        campaign = Campaign.objects.create(
            tenant_id=self.user.tenant_id,
            name='To Delete',
            message_template='Test',
            created_by=self.user.id
        )
        
        url = f'/api/campaigns/{campaign.id}/'
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(Campaign.objects.filter(id=campaign.id).exists())
    
    def test_get_campaign_stats(self):
        """Test getting campaign statistics."""
        campaign = Campaign.objects.create(
            tenant_id=self.user.tenant_id,
            name='Test Campaign',
            message_template='Test',
            created_by=self.user.id,
            status='completed',
            total_recipients=1000,
            sent_count=950,
            delivered_count=900,
            read_count=400
        )
        
        url = f'/api/campaigns/{campaign.id}/stats/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['stats']['sent_count'], 950)
        self.assertEqual(response.data['stats']['delivery_rate'], 94.74)


class MessageTemplateAPITests(APITestCase):
    """Tests for the message templates API."""
    
    def setUp(self):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        self.user = User.objects.create_user(
            email='test@example.com',
            password='test123',
            tenant_id='test-tenant-id'
        )
        self.client.force_authenticate(self.user)
    
    def test_list_templates(self):
        """Test listing message templates."""
        MessageTemplate.objects.create(
            tenant_id=self.user.tenant_id,
            name='Template 1',
            content='Hello {name}!',
            category='marketing'
        )
        MessageTemplate.objects.create(
            tenant_id=self.user.tenant_id,
            name='Template 2',
            content='Your order {order_id}',
            category='transactional'
        )
        
        url = '/api/templates/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['templates']), 2)
    
    def test_create_template(self):
        """Test creating a message template."""
        url = '/api/templates/'
        data = {
            'name': 'New Template',
            'content': 'Hello {name}, welcome!',
            'category': 'marketing'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['success'])
