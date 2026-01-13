"""
URL configuration for the chats app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ChatViewSet, AutoReplyViewSet

router = DefaultRouter()
router.register(r'chats', ChatViewSet, basename='chat')
router.register(r'auto-replies', AutoReplyViewSet, basename='auto-reply')

urlpatterns = [
    path('', include(router.urls)),
]
