import math
from django.db import models
from django.utils.text import slugify
from django.utils import timezone
from django.contrib.auth.models import User


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    description = models.TextField(blank=True, default='')
    color_hex = models.CharField(max_length=10, default='#3B82F6')
    icon = models.CharField(max_length=40, default='Folder')
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=60, unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Post(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('scheduled', 'Scheduled'),
        ('archived', 'Archived'),
    ]

    FORMAT_CHOICES = [
        ('blocks', 'Block Builder (JSON)'),
        ('markdown', 'Markdown'),
        ('html', 'Rich HTML'),
    ]

    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=280, unique=True, blank=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    content_format = models.CharField(max_length=20, choices=FORMAT_CHOICES, default='blocks')
    
    # Block-based JSON representation for drag & drop visual editor
    blocks_data = models.JSONField(default=list, blank=True)
    # Rendered HTML representation for instant caching and public delivery
    content_html = models.TextField(blank=True, default='')
    
    excerpt = models.TextField(blank=True, default='')
    featured_image = models.CharField(max_length=500, blank=True, default='')
    
    categories = models.ManyToManyField(Category, blank=True, related_name='posts')
    tags = models.ManyToManyField(Tag, blank=True, related_name='posts')
    
    reading_time_minutes = models.PositiveIntegerField(default=1)
    view_count = models.PositiveIntegerField(default=0)
    
    # SEO fields
    seo_title = models.CharField(max_length=160, blank=True, default='')
    seo_description = models.CharField(max_length=255, blank=True, default='')
    seo_keywords = models.CharField(max_length=255, blank=True, default='')
    
    published_at = models.DateTimeField(null=True, blank=True)
    scheduled_for = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def calculate_reading_time(self):
        # Estimate based on 200 words per minute
        text = self.content_html or ""
        words = len(text.split())
        return max(1, math.ceil(words / 200))

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title) or 'untitled'
            slug = base_slug
            counter = 1
            while Post.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug

        self.reading_time_minutes = self.calculate_reading_time()

        if self.status == 'published' and not self.published_at:
            self.published_at = timezone.now()

        super().save(*args, **kwargs)

    def create_revision(self, user=None, summary="Auto snapshot"):
        next_ver = self.revisions.count() + 1
        return PostRevision.objects.create(
            post=self,
            version_number=next_ver,
            title_snapshot=self.title,
            excerpt_snapshot=self.excerpt,
            blocks_data_snapshot=self.blocks_data,
            content_html_snapshot=self.content_html,
            author=user or self.author,
            change_summary=summary
        )

    def __str__(self):
        return f"{self.title} [{self.status}]"


class PostRevision(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='revisions')
    version_number = models.PositiveIntegerField()
    title_snapshot = models.CharField(max_length=255)
    excerpt_snapshot = models.TextField(blank=True, default='')
    blocks_data_snapshot = models.JSONField(default=list)
    content_html_snapshot = models.TextField(blank=True, default='')
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    change_summary = models.CharField(max_length=255, default='Updated content')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-version_number']

    def __str__(self):
        return f"{self.post.title} v{self.version_number} ({self.created_at.strftime('%Y-%m-%d %H:%M')})"
