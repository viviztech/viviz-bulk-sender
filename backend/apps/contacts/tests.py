"""
Unit tests for the contacts app.
"""
import pytest
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APITestCase
from rest_framework import status
from apps.contacts.models import Contact, Tag, ContactActivity, ContactNote

from unittest.mock import patch


class ContactModelTests(TestCase):
    """Tests for the Contact model."""
    
    def test_create_contact(self):
        """Test creating a contact."""
        contact = Contact.objects.create(
            tenant_id='test-tenant-id',
            phone_number='+1234567890',
            name='John Doe',
            email='john@example.com'
        )
        
        self.assertEqual(contact.phone_number, '+1234567890')
        self.assertEqual(contact.name, 'John Doe')
        self.assertEqual(contact.email, 'john@example.com')
        self.assertFalse(contact.is_blocked)
        self.assertTrue(contact.is_subscribed)
    
    def test_display_name_property(self):
        """Test the display_name property."""
        contact = Contact.objects.create(
            tenant_id='test-tenant-id',
            phone_number='+1234567890',
            name='Jane Doe'
        )
        
        self.assertEqual(contact.display_name, 'Jane Doe')
    
    def test_display_name_without_name(self):
        """Test display_name when name is empty."""
        contact = Contact.objects.create(
            tenant_id='test-tenant-id',
            phone_number='+1234567890'
        )
        
        self.assertEqual(contact.display_name, '+1234567890')
    
    def test_engagement_score(self):
        """Test the engagement_score property."""
        contact = Contact.objects.create(
            tenant_id='test-tenant-id',
            phone_number='+1234567890',
            messages_sent=10,
            messages_received=5
        )
        
        self.assertEqual(contact.engagement_score, 15)
    
    def test_phone_normalization(self):
        """Test that phone number is normalized on save."""
        contact = Contact(
            tenant_id='test-tenant-id',
            phone_number='1234567890'
        )
        contact.save()
        
        self.assertTrue(contact.phone_number.startswith('+'))
    
    def test_tags_field(self):
        """Test the tags JSON field."""
        contact = Contact.objects.create(
            tenant_id='test-tenant-id',
            phone_number='+1234567890',
            tags=['vip', 'customer', 'newsletter']
        )
        
        self.assertEqual(contact.tags, ['vip', 'customer', 'newsletter'])
    
    def test_metadata_field(self):
        """Test the metadata JSON field."""
        contact = Contact.objects.create(
            tenant_id='test-tenant-id',
            phone_number='+1234567890',
            metadata={
                'company': 'Acme Inc',
                'position': 'Manager',
                'custom_field': 'value'
            }
        )
        
        self.assertEqual(contact.metadata['company'], 'Acme Inc')


class TagModelTests(TestCase):
    """Tests for the Tag model."""
    
    def test_create_tag(self):
        """Test creating a tag."""
        tag = Tag.objects.create(
            tenant_id='test-tenant-id',
            name='VIP Customer',
            color='#ff0000'
        )
        
        self.assertEqual(tag.name, 'VIP Customer')
        self.assertEqual(tag.color, '#ff0000')
    
    def test_tag_string_representation(self):
        """Test tag string representation."""
        tag = Tag.objects.create(
            tenant_id='test-tenant-id',
            name='Newsletter'
        )
        
        self.assertEqual(str(tag), 'Newsletter')


class ContactActivityTests(TestCase):
    """Tests for the ContactActivity model."""
    
    def setUp(self):
        self.contact = Contact.objects.create(
            tenant_id='test-tenant-id',
            phone_number='+1234567890',
            name='Test Contact'
        )
    
    def test_create_activity(self):
        """Test creating a contact activity."""
        activity = ContactActivity.objects.create(
            contact=self.contact,
            activity_type='message_sent',
            description='Test message sent'
        )
        
        self.assertEqual(activity.contact, self.contact)
        self.assertEqual(activity.activity_type, 'message_sent')
        self.assertTrue(activity.created_at)


class ContactAPITests(APITestCase):
    """Tests for the contacts API endpoints."""
    
    def setUp(self):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        self.user = User.objects.create_user(
            email='test@example.com',
            password='test123',
            tenant_id='test-tenant-id'
        )
        self.client.force_authenticate(self.user)
    
    def test_list_contacts(self):
        """Test listing contacts."""
        Contact.objects.create(
            tenant_id=self.user.tenant_id,
            phone_number='+1111111111',
            name='Contact 1'
        )
        Contact.objects.create(
            tenant_id=self.user.tenant_id,
            phone_number='+2222222222',
            name='Contact 2'
        )
        
        url = '/api/contacts/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(len(response.data['contacts']), 2)
    
    def test_create_contact(self):
        """Test creating a contact."""
        url = '/api/contacts/'
        data = {
            'phone_number': '+1234567890',
            'name': 'New Contact',
            'email': 'contact@example.com',
            'tags': ['vip']
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['success'])
        self.assertEqual(Contact.objects.count(), 1)
    
    def test_get_contact(self):
        """Test getting a single contact."""
        contact = Contact.objects.create(
            tenant_id=self.user.tenant_id,
            phone_number='+1234567890',
            name='Test Contact'
        )
        
        url = f'/api/contacts/{contact.id}/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['contact']['name'], 'Test Contact')
    
    def test_update_contact(self):
        """Test updating a contact."""
        contact = Contact.objects.create(
            tenant_id=self.user.tenant_id,
            phone_number='+1234567890',
            name='Old Name'
        )
        
        url = f'/api/contacts/{contact.id}/'
        data = {'name': 'New Name'}
        
        response = self.client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        contact.refresh_from_db()
        self.assertEqual(contact.name, 'New Name')
    
    def test_delete_contact(self):
        """Test deleting a contact."""
        contact = Contact.objects.create(
            tenant_id=self.user.tenant_id,
            phone_number='+1234567890',
            name='To Delete'
        )
        
        url = f'/api/contacts/{contact.id}/'
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(Contact.objects.filter(id=contact.id).exists())
    
    def test_bulk_create_contacts(self):
        """Test bulk contact creation."""
        url = '/api/contacts/bulk/'
        data = {
            'phone_numbers': ['+1111111111', '+2222222222', '+3333333333'],
            'tags': ['bulk']
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(Contact.objects.count(), 3)
    
    def test_filter_contacts_by_blocked(self):
        """Test filtering contacts by blocked status."""
        Contact.objects.create(
            tenant_id=self.user.tenant_id,
            phone_number='+1111111111',
            is_blocked=False
        )
        Contact.objects.create(
            tenant_id=self.user.tenant_id,
            phone_number='+2222222222',
            is_blocked=True
        )
        
        url = '/api/contacts/?is_blocked=true'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['contacts']), 1)
    
    def test_search_contacts(self):
        """Test searching contacts."""
        Contact.objects.create(
            tenant_id=self.user.tenant_id,
            phone_number='+1111111111',
            name='John Doe'
        )
        Contact.objects.create(
            tenant_id=self.user.tenant_id,
            phone_number='+2222222222',
            name='Jane Smith'
        )
        
        url = '/api/contacts/?search=John'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['contacts']), 1)
        self.assertEqual(response.data['contacts'][0]['name'], 'John Doe')
