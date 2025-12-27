"""
Job models for the job board application.
Jobs are posted by companies and can receive applications.
"""

from django.db import models
from django.conf import settings
from companies.models import Company


class Job(models.Model):
    """
    Job model representing job postings.
    Each job belongs to a company and is created by a user.
    """
    
    # Job type choices
    JOB_TYPE_CHOICES = [
        ('full_time', 'Full Time'),
        ('part_time', 'Part Time'),
        ('contract', 'Contract'),
        ('internship', 'Internship'),
    ]
    
    # Basic job information
    title = models.CharField(max_length=200)
    description = models.TextField()
    location = models.CharField(max_length=200)
    job_type = models.CharField(max_length=20, choices=JOB_TYPE_CHOICES, default='full_time')
    salary = models.CharField(max_length=100, blank=True, null=True)
    
    # Foreign key relationships
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='jobs'
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='posted_jobs'
    )
    
    # Status and timestamps
    is_active = models.BooleanField(default=True)
    posted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        """String representation of the job."""
        return f"{self.title} at {self.company.name}"
    
    class Meta:
        """Metadata options for the Job model."""
        ordering = ['-posted_at']