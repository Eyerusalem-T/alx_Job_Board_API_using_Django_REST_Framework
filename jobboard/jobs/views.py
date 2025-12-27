"""
Views for the jobs app.
Handles job CRUD operations with filtering and search.
"""

from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import models
from .models import Job
from .serializers import JobSerializer, JobListSerializer


class JobViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Job model.
    Provides CRUD operations for jobs with filtering and search.
    """
    queryset = Job.objects.filter(is_active=True)
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description', 'company__name']
    ordering_fields = ['posted_at', 'title']
    ordering = ['-posted_at']
    
    def get_serializer_class(self):
        """
        Use different serializers for list and detail views.
        - List: JobListSerializer (lightweight)
        - Other: JobSerializer (full details)
        """
        if self.action == 'list':
            return JobListSerializer
        return JobSerializer
    
    def get_permissions(self):
        """
        Set permissions based on action.
        - List and retrieve: Anyone can view
        - Create: Only authenticated users who are employers
        - Update/Delete: Only job creator
        """
        if self.action == 'create':
            permission_classes = [permissions.IsAuthenticated]
        elif self.action in ['update', 'partial_update', 'destroy']:
            permission_classes = [permissions.IsAuthenticated]
        else:
            permission_classes = [permissions.AllowAny]
        return [permission() for permission in permission_classes]
    
    def perform_create(self, serializer):
        """
        Create a new job.
        Check if user is an employer before creating.
        """
        if not self.request.user.profile.is_employer:
            raise permissions.PermissionDenied("Only employers can create jobs.")
        
        serializer.save(created_by=self.request.user)
    
    def perform_update(self, serializer):
        """
        Update a job.
        Check if user is the job creator before updating.
        """
        instance = self.get_object()
        if instance.created_by != self.request.user:
            raise permissions.PermissionDenied("You can only update your own jobs.")
        serializer.save()
    
    def perform_destroy(self, instance):
        """
        Delete a job.
        Check if user is the job creator before deleting.
        """
        if instance.created_by != self.request.user:
            raise permissions.PermissionDenied("You can only delete your own jobs.")
        instance.delete()
    
    @action(detail=False, methods=['get'])
    def my_jobs(self, request):
        """Get jobs posted by the current user."""
        if not request.user.is_authenticated:
            return Response(
                {'detail': 'Authentication required'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        jobs = Job.objects.filter(created_by=request.user)
        serializer = self.get_serializer(jobs, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        """
        Advanced job search endpoint.
        Supports multiple search criteria.
        """
        queryset = self.filter_queryset(self.get_queryset())
        
        # Get search parameters
        location = request.query_params.get('location', None)
        job_type = request.query_params.get('job_type', None)
        keyword = request.query_params.get('keyword', None)
        
        # Apply filters
        if location:
            queryset = queryset.filter(location__icontains=location)
        if job_type:
            queryset = queryset.filter(job_type=job_type)
        if keyword:
            queryset = queryset.filter(
                models.Q(title__icontains=keyword) |
                models.Q(description__icontains=keyword) |
                models.Q(company__name__icontains=keyword)
            )
        
        # Paginate results
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)