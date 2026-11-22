from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('admin', 'Administrator'),
        ('editor', 'Editor'),
        ('author', 'Author'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='author')
    avatar_url = models.URLField(blank=True, default='')
    bio = models.TextField(blank=True, default='')
    website = models.URLField(blank=True, default='')
    twitter_handle = models.CharField(max_length=60, blank=True, default='')
    github_handle = models.CharField(max_length=60, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"
