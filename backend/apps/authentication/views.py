"""
Views for the authentication app.
"""
from rest_framework import status, viewsets, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import get_user_model
from django.utils import timezone

from .models import UserInvitation
from .serializers import (
    UserSerializer, UserCreateSerializer, CustomTokenObtainPairSerializer,
    ChangePasswordSerializer, PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer, UserInvitationSerializer,
    UserInvitationCreateSerializer, AcceptInvitationSerializer
)

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    """View for user registration."""
    
    serializer_class = UserCreateSerializer
    permission_classes = [AllowAny]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({
            'success': True,
            'message': 'User registered successfully.',
            'user': UserSerializer(user).data
        }, status=status.HTTP_201_CREATED)


class CustomTokenObtainPairView(TokenObtainPairView):
    """Custom token view with additional user info."""
    serializer_class = CustomTokenObtainPairSerializer


class UserProfileView(generics.RetrieveUpdateAPIView):
    """View for user profile."""
    
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        return self.request.user
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({
            'success': True,
            'user': serializer.data
        })


class ChangePasswordView(APIView):
    """View for changing password."""
    
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        serializer = ChangePasswordSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        
        user = request.user
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        
        return Response({
            'success': True,
            'message': 'Password changed successfully.'
        })


class UserViewSet(viewsets.ModelViewSet):
    """ViewSet for user management (admin only)."""
    
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # Only return users from the same tenant
        return User.objects.filter(tenant_id=self.request.user.tenant_id)
    
    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        return UserSerializer
    
    def perform_create(self, serializer):
        # Set the tenant_id from the current user
        serializer.save(tenant_id=self.request.user.tenant_id)
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'success': True,
            'users': serializer.data,
            'count': queryset.count()
        })
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({
            'success': True,
            'user': serializer.data
        })
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({
            'success': True,
            'user': serializer.data
        })
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        # Prevent deleting yourself
        if instance == request.user:
            return Response({
                'success': False,
                'message': 'You cannot delete your own account.'
            }, status=status.HTTP_400_BAD_REQUEST)
        instance.delete()
        return Response({
            'success': True,
            'message': 'User deleted successfully.'
        })


class UserInvitationViewSet(viewsets.ModelViewSet):
    """ViewSet for managing user invitations."""
    
    serializer_class = UserInvitationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return UserInvitation.objects.filter(
            tenant_id=self.request.user.tenant_id,
            is_accepted=False
        )
    
    def get_serializer_class(self):
        if self.action == 'create':
            return UserInvitationCreateSerializer
        return UserInvitationSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        invitation = UserInvitation.objects.create(
            tenant_id=request.user.tenant_id,
            email=serializer.validated_data['email'],
            role=serializer.validated_data['role'],
            invited_by=request.user
        )
        
        # TODO: Send invitation email
        
        return Response({
            'success': True,
            'message': 'Invitation sent successfully.',
            'invitation': UserInvitationSerializer(invitation).data
        }, status=status.HTTP_201_CREATED)
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'success': True,
            'invitations': serializer.data,
            'count': queryset.count()
        })


class AcceptInvitationView(APIView):
    """View for accepting invitations."""
    
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = AcceptInvitationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        invitation = serializer.invitation
        
        # Create the user
        user = User.objects.create_user(
            email=invitation.email,
            password=serializer.validated_data['password'],
            first_name=serializer.validated_data['first_name'],
            last_name=serializer.validated_data['last_name'],
            role=invitation.role,
            tenant_id=invitation.tenant_id
        )
        
        # Mark invitation as accepted
        invitation.is_accepted = True
        invitation.save()
        
        return Response({
            'success': True,
            'message': 'Invitation accepted successfully. You can now log in.',
            'user': UserSerializer(user).data
        })
