from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class IssueReport(models.Model):
    """A service delivery issue reported by a resident."""

    CATEGORY_CHOICES = [
        ('water', '💧 Water (Leaks / No Water)'),
        ('electricity', '⚡ Electricity (Outage / Fault)'),
        ('roads', '🚧 Roads (Potholes / Damage)'),
        ('waste', '🗑️ Waste Collection'),
        ('sewage', '🚽 Sewage / Drainage'),
        ('parks', '🌳 Parks & Public Spaces'),
        ('street_lights', '💡 Street Lights'),
        ('other', '📋 Other'),
    ]

    STATUS_CHOICES = [
        ('submitted', 'Submitted'),
        ('under_review', 'Under Review'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    ]

    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]

    # Core fields
    reporter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reports')
    title = models.CharField(max_length=200)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    description = models.TextField()
    location = models.CharField(max_length=300, help_text="Street address or description of location")
    ward_number = models.CharField(max_length=10, blank=True)
    photo = models.ImageField(upload_to='report_photos/', blank=True, null=True)

    # Status tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='submitted')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                     related_name='assigned_reports')

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    # Reference number
    reference_number = models.CharField(max_length=20, unique=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        # Auto-generate reference number
        if not self.reference_number:
            import random, string
            self.reference_number = 'MUN-' + ''.join(random.choices(string.digits, k=6))
        # Set resolved_at timestamp
        if self.status == 'resolved' and not self.resolved_at:
            self.resolved_at = timezone.now()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"[{self.reference_number}] {self.title}"

    def get_status_badge_class(self):
        classes = {
            'submitted': 'bg-secondary',
            'under_review': 'bg-info',
            'in_progress': 'bg-warning text-dark',
            'resolved': 'bg-success',
            'closed': 'bg-dark',
        }
        return classes.get(self.status, 'bg-secondary')

    def get_priority_badge_class(self):
        classes = {
            'low': 'bg-success',
            'medium': 'bg-info text-dark',
            'high': 'bg-warning text-dark',
            'urgent': 'bg-danger',
        }
        return classes.get(self.priority, 'bg-secondary')


class Message(models.Model):
    """Messages between residents and municipal officials about a report."""

    report = models.ForeignKey(IssueReport, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_official_response = models.BooleanField(default=False)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"Message from {self.sender.username} on {self.report.reference_number}"


class Notification(models.Model):
    """System notifications for users."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=200)
    message = models.TextField()
    report = models.ForeignKey(IssueReport, on_delete=models.CASCADE, null=True, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Notification for {self.user.username}: {self.title}"
