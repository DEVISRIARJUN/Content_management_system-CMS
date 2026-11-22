import os
from django.db import models
from django.contrib.auth.models import User


def media_upload_path(instance, filename):
    return f"uploads/{filename}"


class MediaAsset(models.Model):
    TYPE_CHOICES = [
        ('image', 'Image'),
        ('video', 'Video'),
        ('document', 'Document'),
        ('audio', 'Audio'),
        ('other', 'Other'),
    ]

    title = models.CharField(max_length=255, blank=True)
    file = models.FileField(upload_to=media_upload_path)
    file_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='image')
    file_size_bytes = models.BigIntegerField(default=0)
    mime_type = models.CharField(max_length=100, blank=True, default='')
    alt_text = models.CharField(max_length=255, blank=True, default='')
    s3_key = models.CharField(max_length=500, blank=True, default='')
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.title and self.file:
            self.title = os.path.basename(self.file.name)
        if self.file and hasattr(self.file, 'size') and not self.file_size_bytes:
            self.file_size_bytes = self.file.size
        
        # Detect type
        ext = os.path.splitext(self.file.name)[1].lower() if self.file else ''
        if ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg']:
            self.file_type = 'image'
        elif ext in ['.mp4', '.webm', '.mov', '.avi']:
            self.file_type = 'video'
        elif ext in ['.pdf', '.doc', '.docx', '.txt', '.csv']:
            self.file_type = 'document'
        elif ext in ['.mp3', '.wav', '.ogg']:
            self.file_type = 'audio'
        else:
            self.file_type = 'other'

        super().save(*args, **kwargs)

    def __str__(self):
        return self.title or str(self.file)
