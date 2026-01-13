"""
URL configuration for the campaigns app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CampaignViewSet, CampaignActionView, CampaignStatsView, MessageTemplateViewSet

router = DefaultRouter()
router.register(r'campaigns', CampaignViewSet, basename='campaign')
router.register(r'templates', MessageTemplateViewSet, basename='template')

urlpatterns = [
    path('', include(router.urls)),
    path('campaigns/<uuid:pk>/action/', CampaignActionView.as_view(), name='campaign-action'),
    path('campaigns/<uuid:pk>/stats/', CampaignStatsView.as_view(), name='campaign-stats'),
]
