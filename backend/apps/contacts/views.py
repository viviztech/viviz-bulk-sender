"""
Views for the contacts app.
"""
from rest_framework import viewsets, status, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db import transaction

from .models import Contact, Tag, ContactActivity, ContactNote
from .serializers import (
    ContactSerializer, ContactCreateSerializer, ContactUpdateSerializer,
    TagSerializer, TagCreateSerializer, ContactActivitySerializer,
    ContactNoteSerializer, ContactNoteCreateSerializer, BulkContactSerializer,
    ContactImportSerializer
)


class ContactViewSet(viewsets.ModelViewSet):
    """ViewSet for contact management."""
    
    serializer_class = ContactSerializer
    permission_classes = []
    
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['is_blocked', 'is_subscribed', 'tags', 'source']
    search_fields = ['phone_number', 'name', 'email', 'company']
    ordering_fields = ['created_at', 'name', 'phone_number']
    ordering = ['-created_at']
    
    def get_queryset(self):
        return Contact.objects.filter(tenant_id=self.request.user.tenant_id)
    
    def get_serializer_class(self):
        if self.action == 'create':
            return ContactCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return ContactUpdateSerializer
        return ContactSerializer
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['tenant_id'] = self.request.user.tenant_id
        return context
    
    def perform_create(self, serializer):
        serializer.save(tenant_id=self.request.user.tenant_id)
        # Log activity
        ContactActivity.objects.create(
            contact=serializer.instance,
            activity_type='imported',
            description='Contact created',
            performed_by=self.request.user.id
        )
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'success': True,
            'contacts': serializer.data,
            'count': queryset.count()
        })
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        # Get activities
        activities = ContactActivity.objects.filter(
            contact=instance
        )[:20]
        return Response({
            'success': True,
            'contact': serializer.data,
            'activities': ContactActivitySerializer(activities, many=True).data
        })
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response({
            'success': True,
            'message': 'Contact deleted successfully.'
        })


class BulkContactView(APIView):
    """View for bulk contact operations."""
    
    def post(self, request):
        serializer = BulkContactSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        tenant_id = request.user.tenant_id
        phone_numbers = serializer.validated_data['phone_numbers']
        tags = serializer.validated_data.get('tags', [])
        metadata = serializer.validated_data.get('metadata', {})
        
        created = 0
        existing = 0
        
        with transaction.atomic():
            for phone in phone_numbers:
                phone = phone.strip()
                if not phone:
                    continue
                
                contact, was_created = Contact.objects.get_or_create(
                    tenant_id=tenant_id,
                    phone_number=phone,
                    defaults={
                        'metadata': metadata,
                        'source': 'import'
                    }
                )
                
                if was_created:
                    created += 1
                else:
                    existing += 1
                
                # Add tags
                if tags:
                    contact.tags.extend(tags)
                    contact.save()
        
        return Response({
            'success': True,
            'message': f'Contacts processed: {created} created, {existing} existing.',
            'created': created,
            'existing': existing
        })


class ContactImportView(APIView):
    """View for importing contacts from file."""
    
    parser_classes = [MultiPartParser]
    
    def post(self, request):
        serializer = ContactImportSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # TODO: Implement CSV/Excel import logic
        # This would use pandas or csv module to parse the file
        
        return Response({
            'success': True,
            'message': 'Import started. You will be notified when complete.'
        })


class TagViewSet(viewsets.ModelViewSet):
    """ViewSet for tag management."""
    
    serializer_class = TagSerializer
    permission_classes = []
    
    def get_queryset(self):
        return Tag.objects.filter(tenant_id=self.request.user.tenant_id)
    
    def get_serializer_class(self):
        if self.action == 'create':
            return TagCreateSerializer
        return TagSerializer
    
    def perform_create(self, serializer):
        serializer.save(tenant_id=self.request.user.tenant_id)
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'success': True,
            'tags': serializer.data,
            'count': queryset.count()
        })
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response({
            'success': True,
            'message': 'Tag deleted successfully.'
        })


class ContactNoteViewSet(viewsets.ModelViewSet):
    """ViewSet for contact notes."""
    
    serializer_class = ContactNoteSerializer
    permission_classes = []
    
    def get_queryset(self):
        contact_id = self.kwargs.get('contact_pk')
        if contact_id:
            return ContactNote.objects.filter(contact_id=contact_id)
        return ContactNote.objects.none()
    
    def get_serializer_class(self):
        if self.action == 'create':
            return ContactNoteCreateSerializer
        return ContactNoteSerializer
    
    def perform_create(self, serializer):
        contact_id = self.kwargs.get('contact_pk')
        contact = Contact.objects.get(id=contact_id, tenant_id=self.request.user.tenant_id)
        serializer.save(contact=contact, added_by=self.request.user.id)


class ContactActivityView(generics.ListAPIView):
    """View for contact activities."""
    
    serializer_class = ContactActivitySerializer
    permission_classes = []
    
    def get_queryset(self):
        contact_id = self.kwargs.get('pk')
        return ContactActivity.objects.filter(contact_id=contact_id)[:50]
