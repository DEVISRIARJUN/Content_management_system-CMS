from datetime import timedelta
from django.utils import timezone
from django.db.models import Count, Sum
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from apps.posts.models import Post, Category
from .models import PageView


class AnalyticsDashboardView(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get(self, request):
        now = timezone.now()
        seven_days_ago = now - timedelta(days=7)

        # Post counts
        total_posts = Post.objects.count()
        published_posts = Post.objects.filter(status='published').count()
        draft_posts = Post.objects.filter(status='draft').count()
        total_views = Post.objects.aggregate(total=Sum('view_count'))['total'] or 0

        # Top 5 performing posts
        top_posts = Post.objects.filter(status='published').order_by('-view_count')[:5].values(
            'id', 'title', 'slug', 'view_count', 'reading_time_minutes', 'published_at'
        )

        # Views past 7 days breakdown
        views_timeline = []
        for i in range(6, -1, -1):
            day_start = (now - timedelta(days=i)).replace(hour=0, minute=0, second=0, microsecond=0)
            day_end = day_start + timedelta(days=1)
            count = PageView.objects.filter(timestamp__gte=day_start, timestamp__lt=day_end).count()
            views_timeline.append({
                "date": day_start.strftime("%b %d"),
                "views": count
            })

        # Category distribution
        categories_data = []
        for cat in Category.objects.all():
            count = cat.posts.count()
            if count > 0:
                categories_data.append({
                    "name": cat.name,
                    "color": cat.color_hex,
                    "count": count
                })

        return Response({
            "metrics": {
                "total_posts": total_posts,
                "published_posts": published_posts,
                "draft_posts": draft_posts,
                "total_views": total_views,
                "avg_views_per_post": round(total_views / max(published_posts, 1), 1)
            },
            "views_timeline": views_timeline,
            "top_posts": list(top_posts),
            "categories_distribution": categories_data
        })
