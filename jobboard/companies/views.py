"""
Views for the companies app.
Handles company CRUD operations.
"""

from rest_framework import viewsets, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Company
from .serializers import CompanySerializer


class CompanyViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Company model.
    Provides CRUD operations for companies.
    """
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'location']
    
    def get_permissions(self):
        """
        Set permissions based on action.
        - List and retrieve: Anyone can view
        - Create: Only authenticated users
        - Update/Delete: Only company creator
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [permissions.IsAuthenticated]
        else:
            permission_classes = [permissions.AllowAny]
        return [permission() for permission in permission_classes]
    
    def perform_create(self, serializer):
        """Set the current user as the company creator."""
        serializer.save(created_by=self.request.user)
    
    def perform_update(self, serializer):
        """Check if user is the company creator before updating."""
        instance = self.get_object()
        if instance.created_by != self.request.user:
            raise permissions.PermissionDenied("You can only update your own companies.")
        serializer.save()
    
    def perform_destroy(self, instance):
        """Check if user is the company creator before deleting."""
        if instance.created_by != self.request.user:
            raise permissions.PermissionDenied("You can only delete your own companies.")
        instance.delete()
    
    @action(detail=False, methods=['get'])
    def my_companies(self, request):
        """Get companies created by the current user."""
        if not request.user.is_authenticated:
            return Response(
                {'detail': 'Authentication required'},
                status=status.HTTP_401_UNAUTHORIZED # type: ignore
            )
        
        companies = Company.objects.filter(created_by=request.user)
        serializer = self.get_serializer(companies, many=True)
        return Response(serializer.data)