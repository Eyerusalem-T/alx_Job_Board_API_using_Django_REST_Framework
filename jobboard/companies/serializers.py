"""
Serializers for the companies app.
Handles company data serialization.
"""

from rest_framework import serializers
from .models import Company


class CompanySerializer(serializers.ModelSerializer):
    """Serializer for Company model."""
    
    # Read-only fields
    created_by = serializers.StringRelatedField(read_only=True)
    jobs_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Company
        fields = ['id', 'name', 'description', 'location', 'website',
                'created_by', 'jobs_count', 'created_at', 'updated_at']
        read_only_fields = ['created_by', 'created_at', 'updated_at', 'jobs_count']
    
    def get_jobs_count(self, obj):
        """Get count of active jobs for this company."""
        return obj.jobs.filter(is_active=True).count()
    
    def create(self, validated_data):
        """Create a new company with the current user as creator."""
        # Set created_by to current user from request context
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class CompanyDetailSerializer(CompanySerializer):
    """Detailed serializer for Company with all fields."""
    
    class Meta(CompanySerializer.Meta):
        fields = CompanySerializer.Meta.fields