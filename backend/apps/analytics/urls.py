"""
URL configuration for the analytics app.
"""
from django.urls import path
from .views import AnalyticsOverviewView, MessageStatsView, CampaignStatsView

urlpatterns = [
    path('analytics/overview/', AnalyticsOverviewView.as_view(), name='analytics-overview'),
    path('analytics/messages/', MessageStatsView.as_view(), name='analytics-messages'),
    path('analytics/campaigns/', CampaignStatsView.as_view(), name='analytics-campaigns'),
]
