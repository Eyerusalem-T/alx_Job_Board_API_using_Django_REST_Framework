"""
Views for the applications app.
Handles job application operations.
"""

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend # type: ignore
from .models import Application
from .serializers import ApplicationSerializer, ApplicationStatusSerializer


class ApplicationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Application model.
    Provides CRUD operations for job applications.
    """
    serializer_class = ApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'job']
    
    def get_queryset(self):
        """
        Get applications based on user role.
        - Employers: See applications for their jobs
        - Job Seekers: See their own applications
        """
        user = self.request.user
        
        if user.profile.is_employer:
            # Employers see applications for jobs they posted
            return Application.objects.filter(job__created_by=user)
        else:
            # Job seekers see their own applications
            return Application.objects.filter(applicant=user)
    
    def perform_create(self, serializer):
        """Check if user is a job seeker before creating application."""
        if self.request.user.profile.is_employer:
            raise permissions.PermissionDenied("Employers cannot apply for jobs.")
        
        serializer.save(applicant=self.request.user)
    
    def perform_update(self, serializer):
        """Check permissions before updating application."""
        instance = self.get_object()
        
        # Only applicants can update their own applications
        if instance.applicant != self.request.user:
            raise permissions.PermissionDenied(
                "You can only update your own applications."
            )
        
        serializer.save()
    
    def perform_destroy(self, instance):
        """Check permissions before deleting application."""
        # Only applicants can delete their own applications
        if instance.applicant != self.request.user:
            raise permissions.PermissionDenied(
                "You can only delete your own applications."
            )
        
        instance.delete()
    
    @action(detail=True, methods=['patch'])
    def status(self, request, pk=None):
        """
        Update application status.
        Only job creators can update application status.
        """
        application = self.get_object()
        
        # Check if user is the job creator
        if application.job.created_by != request.user:
            return Response(
                {'error': 'Only job creators can update application status'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = ApplicationStatusSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        application.status = serializer.validated_data['status']
        application.save()
        
        return Response(ApplicationSerializer(application).data)
    
    @action(detail=False, methods=['get'])
    def my_applications(self, request):
        """Get applications submitted by the current user."""
        applications = Application.objects.filter(applicant=request.user)
        serializer = self.get_serializer(applications, many=True)
        return Response(serializer.data)