"""
Views for the subscriptions app.
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import stripe


class SubscriptionPlansView(APIView):
    """View for subscription plans."""
    
    def get(self, request):
        plans = [
            {
                'id': 'free',
                'name': 'Free',
                'price': 0,
                'messages_limit': 100,
                'contacts_limit': 50,
                'features': ['Basic messaging', '50 contacts', '100 messages/month']
            },
            {
                'id': 'basic',
                'name': 'Basic',
                'price': 29,
                'messages_limit': 5000,
                'contacts_limit': 1000,
                'features': ['5,000 messages', '1,000 contacts', 'Email support']
            },
            {
                'id': 'pro',
                'name': 'Pro',
                'price': 79,
                'messages_limit': 25000,
                'contacts_limit': 10000,
                'features': ['25,000 messages', '10,000 contacts', 'Priority support', 'Analytics']
            },
            {
                'id': 'enterprise',
                'name': 'Enterprise',
                'price': 199,
                'messages_limit': -1,  # Unlimited
                'contacts_limit': -1,
                'features': ['Unlimited messages', 'Unlimited contacts', 'Dedicated support', 'Custom integrations']
            }
        ]
        return Response({
            'success': True,
            'plans': plans
        })


class SubscriptionView(APIView):
    """View for current subscription."""
    
    def get(self, request):
        from apps.tenants.models import Tenant
        tenant = Tenant.objects.get(id=request.user.tenant_id)
        return Response({
            'success': True,
            'data': {
                'status': tenant.subscription_status,
                'trial_ends_at': tenant.trial_ends_at
            }
        })


class CreateCheckoutView(APIView):
    """View for creating Stripe checkout session."""
    
    def post(self, request):
        plan_id = request.data.get('plan_id')
        
        # TODO: Implement Stripe checkout session creation
        
        return Response({
            'success': True,
            'checkout_url': 'https://checkout.stripe.com/...'  # Placeholder
        })


class CancelSubscriptionView(APIView):
    """View for cancelling subscription."""
    
    def post(self, request):
        from apps.tenants.models import Tenant
        tenant = Tenant.objects.get(id=request.user.tenant_id)
        tenant.subscription_status = 'cancelled'
        tenant.save()
        
        return Response({
            'success': True,
            'message': 'Subscription cancelled successfully.'
        })
