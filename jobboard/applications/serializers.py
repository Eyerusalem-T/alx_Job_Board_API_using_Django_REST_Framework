"""
Serializers for the applications app.
Handles job application data serialization.
"""

from rest_framework import serializers

from jobboard.jobs.models import Job
from .models import Application
from jobs.serializers import JobListSerializer


class ApplicationSerializer(serializers.ModelSerializer):
    """Serializer for Application model."""
    
    # Read-only fields
    job = JobListSerializer(read_only=True)
    applicant = serializers.StringRelatedField(read_only=True)
    job_id = serializers.PrimaryKeyRelatedField(
        queryset=Job.objects.filter(is_active=True),
        source='job',
        write_only=True
    )
    
    class Meta:
        model = Application
        fields = ['id', 'job', 'job_id', 'applicant', 'resume', 'cover_letter',
                'status', 'applied_at', 'updated_at']
        read_only_fields = ['applicant', 'status', 'applied_at', 'updated_at']
    
    def validate(self, data):
        """Validate application data."""
        user = self.context['request'].user
        job = data.get('job')
        
        # Check if user has already applied for this job
        if Application.objects.filter(job=job, applicant=user).exists():
            raise serializers.ValidationError(
                {"job": "You have already applied for this job."}
            )
        
        # Check if job is active
        if not job.is_active:
            raise serializers.ValidationError(
                {"job": "This job is no longer active."}
            )
        
        return data
    
    def create(self, validated_data):
        """Create a new application with the current user as applicant."""
        # Set applicant to current user from request context
        validated_data['applicant'] = self.context['request'].user
        return super().create(validated_data)


class ApplicationStatusSerializer(serializers.Serializer):
    """Serializer for updating application status."""
    status = serializers.ChoiceField(choices=Application.STATUS_CHOICES)