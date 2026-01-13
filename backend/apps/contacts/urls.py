"""
URL configuration for the contacts app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ContactViewSet, TagViewSet, ContactNoteViewSet, ContactActivityView,
    BulkContactView, ContactImportView
)

router = DefaultRouter()
router.register(r'contacts', ContactViewSet, basename='contact')
router.register(r'tags', TagViewSet, basename='tag')

urlpatterns = [
    path('', include(router.urls)),
    path('contacts/bulk/', BulkContactView.as_view(), name='bulk-contacts'),
    path('contacts/import/', ContactImportView.as_view(), name='contact-import'),
    path('contacts/<uuid:pk>/activities/', ContactActivityView.as_view(), name='contact-activities'),
    path('contacts/<uuid:contact_pk>/notes/', ContactNoteViewSet.as_view({
        'get': 'list',
        'post': 'create'
    }), name='contact-notes'),
]
