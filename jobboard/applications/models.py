"""
Application models for the job board application.
Applications are submitted by job seekers for specific jobs.
"""

from django.db import models
from django.conf import settings
from jobs.models import Job


class Application(models.Model):
    """
    Application model representing job applications.
    Each application is for a specific job and by a specific user.
    """
    
    # Application status choices
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('reviewed', 'Reviewed'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ]
    
    # Foreign key relationships
    job = models.ForeignKey(
        Job,
        on_delete=models.CASCADE,
        related_name='applications'
    )
    applicant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='applications'
    )
    
    # Application details
    resume = models.TextField()  # Storing resume as text (can be extended to file upload)
    cover_letter = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Timestamps
    applied_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        """String representation of the application."""
        return f"{self.applicant.username} - {self.job.title}"
    
    class Meta:
        """Metadata options for the Application model."""
        # Prevent duplicate applications
        unique_together = ['job', 'applicant']
        ordering = ['-applied_at']