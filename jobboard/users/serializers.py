"""
Serializers for the users app.
Handles user registration, login, and profile serialization.
"""

from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model."""
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
        read_only_fields = ['id']


class UserProfileSerializer(serializers.Serializer):
    """Serializer for UserProfile with extended fields."""
    is_employer = serializers.BooleanField(default=False)


class RegisterSerializer(serializers.ModelSerializer):
    """Serializer for user registration."""
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)
    is_employer = serializers.BooleanField(default=False)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password2', 'is_employer']
    
    def validate(self, attrs):
        """Validate registration data."""
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        
        if User.objects.filter(email=attrs.get('email', '')).exists():
            raise serializers.ValidationError({"email": "Email is already in use."})
        
        return attrs
    
    def create(self, validated_data):
        """Create a new user with profile."""
        # Remove password2 and is_employer from validated data
        password2 = validated_data.pop('password2')
        is_employer = validated_data.pop('is_employer')
        
        # Create user
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data.get('email', '')
        )
        user.set_password(validated_data['password'])
        user.save()
        
        # Update user profile
        user.profile.is_employer = is_employer
        user.profile.save()
        
        return user


class LoginSerializer(serializers.Serializer):
    """Serializer for user login."""
    username = serializers.CharField(required=True)
    password = serializers.CharField(write_only=True, required=True)