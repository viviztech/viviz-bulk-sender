"""
URL configuration for the subscriptions app.
"""
from django.urls import path
from .views import SubscriptionPlansView, SubscriptionView, CreateCheckoutView, CancelSubscriptionView

urlpatterns = [
    path('subscriptions/plans/', SubscriptionPlansView.as_view(), name='subscription-plans'),
    path('subscriptions/', SubscriptionView.as_view(), name='subscription'),
    path('subscriptions/checkout/', CreateCheckoutView.as_view(), name='subscription-checkout'),
    path('subscriptions/cancel/', CancelSubscriptionView.as_view(), name='subscription-cancel'),
]
