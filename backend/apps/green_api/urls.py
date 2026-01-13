"""
URL configuration for the green_api app.
"""
from django.urls import path
from .views import InstanceStatusView, QRCodeView, WebhookView

urlpatterns = [
    path('green-api/status/', InstanceStatusView.as_view(), name='green-api-status'),
    path('green-api/qr-code/', QRCodeView.as_view(), name='green-api-qr'),
    path('green-api/webhook/', WebhookView.as_view(), name='green-api-webhook'),
]
