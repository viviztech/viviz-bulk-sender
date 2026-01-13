"""
Serializers for the authentication app.
"""
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import UserInvitation

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the User model."""
    
    full_name = serializers.ReadOnlyField()
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name', 'full_name', 'phone',
            'avatar', 'role', 'is_active', 'is_staff', 'email_verified',
            'two_factor_enabled', 'date_joined', 'last_login', 'timezone',
            'language', 'updated_at'
        ]
        read_only_fields = ['id', 'email', 'is_staff', 'date_joined', 'last_login']


class UserCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating new users."""
    
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = [
            'email', 'password', 'password_confirm', 'first_name', 'last_name',
            'phone', 'role'
        ]
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({
                'password_confirm': 'Passwords do not match.'
            })
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Custom token serializer with additional user info."""
    
    def validate(self, attrs):
        data = super().validate(attrs)
        data['user'] = UserSerializer(self.user).data
        return data


class ChangePasswordSerializer(serializers.Serializer):
    """Serializer for password change."""
    
    old_password = serializers.CharField()
    new_password = serializers.CharField(min_length=8)
    
    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('Old password is incorrect.')
        return value


class PasswordResetRequestSerializer(serializers.Serializer):
    """Serializer for password reset request."""
    
    email = serializers.EmailField()


class PasswordResetConfirmSerializer(serializers.Serializer):
    """Serializer for password reset confirmation."""
    
    token = serializers.CharField()
    new_password = serializers.CharField(min_length=8)
    new_password_confirm = serializers.CharField()
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({
                'new_password_confirm': 'Passwords do not match.'
            })
        return attrs


class UserInvitationSerializer(serializers.ModelSerializer):
    """Serializer for user invitations."""
    
    invited_by_email = serializers.ReadOnlyField(source='invited_by.email')
    is_expired = serializers.ReadOnlyField()
    
    class Meta:
        model = UserInvitation
        fields = [
            'id', 'email', 'role', 'token', 'invited_by_email', 'is_accepted',
            'created_at', 'expires_at', 'is_expired'
        ]
        read_only_fields = ['id', 'token', 'invited_by_email', 'created_at', 'is_expired']


class UserInvitationCreateSerializer(serializers.Serializer):
    """Serializer for creating invitations."""
    
    email = serializers.EmailField()
    role = serializers.ChoiceField(choices=User.ROLE_CHOICES)
    
    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('A user with this email already exists.')
        return value


class AcceptInvitationSerializer(serializers.Serializer):
    """Serializer for accepting invitations."""
    
    token = serializers.CharField()
    password = serializers.CharField(min_length=8)
    password_confirm = serializers.CharField()
    first_name = serializers.CharField(max_length=100)
    last_name = serializers.CharField(max_length=100)
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({
                'password_confirm': 'Passwords do not match.'
            })
        return attrs
    
    def validate_token(self, value):
        try:
            invitation = UserInvitation.objects.get(token=value, is_accepted=False)
            if invitation.is_expired():
                raise serializers.ValidationError('Invitation has expired.')
            self.invitation = invitation
        except UserInvitation.DoesNotExist:
            raise serializers.ValidationError('Invalid or expired invitation.')
        return value
