"""
URL configuration for the messages app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MessageViewSet, SendMessageView, ScheduledMessageViewSet

router = DefaultRouter()
router.register(r'messages', MessageViewSet, basename='message')
router.register(r'scheduled', ScheduledMessageViewSet, basename='scheduled')

urlpatterns = [
    path('', include(router.urls)),
    path('send/', SendMessageView.as_view(), name='send-message'),
]
