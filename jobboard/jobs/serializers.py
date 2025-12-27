"""
Serializers for the jobs app.
Handles job data serialization and filtering.
"""

from rest_framework import serializers

from jobboard.companies.models import Company
from .models import Job
from companies.serializers import CompanySerializer


class JobSerializer(serializers.ModelSerializer):
    """Serializer for Job model."""
    
    # Read-only fields
    company = CompanySerializer(read_only=True)
    created_by = serializers.StringRelatedField(read_only=True)
    company_id = serializers.PrimaryKeyRelatedField(
        queryset=Company.objects.all(),
        source='company',
        write_only=True
    )
    applications_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Job
        fields = ['id', 'title', 'description', 'location', 'job_type', 'salary',
                'company', 'company_id', 'created_by', 'is_active',
                'posted_at', 'updated_at', 'applications_count']
        read_only_fields = ['created_by', 'posted_at', 'updated_at', 'applications_count']
    
    def get_applications_count(self, obj):
        """Get count of applications for this job."""
        return obj.applications.count()
    
    def create(self, validated_data):
        """Create a new job with the current user as creator."""
        # Set created_by to current user from request context
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class JobListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for job listings."""
    
    company_name = serializers.CharField(source='company.name', read_only=True)
    
    class Meta:
        model = Job
        fields = ['id', 'title', 'location', 'job_type', 'salary',
                'company_name', 'posted_at', 'is_active']