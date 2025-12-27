"""
Views for the users app.
Handles user registration, login, and profile management.
"""

from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from .serializers import (
    UserSerializer, RegisterSerializer, LoginSerializer, UserProfileSerializer
)


class RegisterView(generics.CreateAPIView):
    """
    View for user registration.
    Allows anyone to create a new user account.
    """
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]
    
    def create(self, request, *args, **kwargs):
        """Handle user registration."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Log the user in after registration
        login(request, user)
        
        return Response({
            'user': UserSerializer(user, context=self.get_serializer_context()).data,
            'message': 'User registered successfully'
        }, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    """
    View for user login.
    Uses Django's built-in authentication system.
    """
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        """Handle user login."""
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        username = serializer.validated_data['username']
        password = serializer.validated_data['password']
        
        # Authenticate user
        user = authenticate(username=username, password=password)
        
        if user is not None:
            # Log the user in
            login(request, user)
            return Response({
                'user': UserSerializer(user).data,
                'message': 'Login successful'
            })
        else:
            return Response(
                {'error': 'Invalid credentials'},
                status=status.HTTP_401_UNAUTHORIZED
            )


class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    View for user profile.
    Allows authenticated users to view and update their profile.
    """
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        """Get the current user's profile."""
        return self.request.user
    
    def update(self, request, *args, **kwargs):
        """Update user profile."""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        
        # Update user fields
        user_serializer = self.get_serializer(
            instance, data=request.data, partial=partial
        )
        user_serializer.is_valid(raise_exception=True)
        self.perform_update(user_serializer)
        
        # Update profile fields if provided
        if 'is_employer' in request.data:
            profile_serializer = UserProfileSerializer(
                instance.profile,
                data={'is_employer': request.data['is_employer']},
                partial=True
            )
            profile_serializer.is_valid(raise_exception=True)
            profile_serializer.save()
        
        return Response(user_serializer.data)


class LogoutView(APIView):
    """
    View for user logout.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """Handle user logout."""
        # Django automatically handles session logout
        return Response({'message': 'Logout successful'})