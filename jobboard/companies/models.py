"""
Company models for the job board application.
Companies are created by employers and can post jobs.
"""

from django.db import models
from django.conf import settings


class Company(models.Model):
    """
    Company model representing organizations that post jobs.
    Each company is created by a user (employer).
    """
    name = models.CharField(max_length=200)
    description = models.TextField()
    location = models.CharField(max_length=200)
    website = models.URLField(max_length=200, blank=True, null=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='companies'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        """String representation of the company."""
        return self.name
    
    class Meta:
        """Metadata options for the Company model."""
        verbose_name_plural = "Companies"
        ordering = ['-created_at']