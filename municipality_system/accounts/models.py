from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    """Extended profile for municipality system users."""
    ROLE_CHOICES = [
        ('resident', 'Resident'),
        ('official', 'Municipal Official'),
        ('admin', 'Administrator'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='resident')
    phone_number = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True, help_text="Your residential/street address")
    ward_number = models.CharField(max_length=10, blank=True, help_text="e.g. Ward 5")
    id_number = models.CharField(max_length=13, blank=True, help_text="SA ID Number (optional)")
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} ({self.get_role_display()})"

    def is_official(self):
        return self.role in ['official', 'admin']
