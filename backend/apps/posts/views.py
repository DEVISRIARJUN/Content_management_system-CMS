from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone
from django.db.models import Q
from .models import Category, Tag, Post, PostRevision
from .serializers import (
    CategorySerializer, TagSerializer, PostListSerializer,
    PostDetailSerializer, PostCreateUpdateSerializer, PostRevisionSerializer
)


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'slug'


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'slug'


class PostViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.AllowAny]
    lookup_field = 'id'

    def get_queryset(self):
        qs = Post.objects.select_related('author', 'author__profile').prefetch_related('categories', 'tags').all()
        
        # Filtering by status
        status_param = self.request.query_params.get('status')
        if status_param and status_param != 'all':
            qs = qs.filter(status=status_param)

        # Filtering by category
        category = self.request.query_params.get('category')
        if category:
            qs = qs.filter(categories__slug=category)

        # Filtering by tag
        tag = self.request.query_params.get('tag')
        if tag:
            qs = qs.filter(tags__slug=tag)

        # Search query
        search = self.request.query_params.get('search')
        if search:
            qs = qs.filter(Q(title__icontains=search) | Q(excerpt__icontains=search) | Q(content_html__icontains=search))

        # Ordering
        ordering = self.request.query_params.get('ordering', '-created_at')
        return qs.order_by(ordering)

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return PostCreateUpdateSerializer
        if self.action == 'retrieve':
            return PostDetailSerializer
        return PostListSerializer

    @action(detail=True, methods=['post'])
    def publish(self, request, id=None):
        post = self.get_object()
        post.status = 'published'
        post.published_at = timezone.now()
        post.save()
        return Response({"message": f"Post '{post.title}' published successfully.", "status": post.status})

    @action(detail=True, methods=['post'])
    def duplicate(self, request, id=None):
        original = self.get_object()
        user = request.user if request.user.is_authenticated else original.author
        duplicated = Post.objects.create(
            title=f"Copy of {original.title}",
            author=user,
            status='draft',
            content_format=original.content_format,
            blocks_data=original.blocks_data,
            content_html=original.content_html,
            excerpt=original.excerpt,
            featured_image=original.featured_image,
            seo_title=original.seo_title,
            seo_description=original.seo_description,
            seo_keywords=original.seo_keywords
        )
        duplicated.categories.set(original.categories.all())
        duplicated.tags.set(original.tags.all())
        duplicated.create_revision(user=user, summary="Duplicated from original post")
        return Response(PostDetailSerializer(duplicated).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get'])
    def revisions(self, request, id=None):
        post = self.get_object()
        revs = post.revisions.all().order_by('-version_number')
        return Response(PostRevisionSerializer(revs, many=True).data)

    @action(detail=True, methods=['post'])
    def rollback(self, request, id=None):
        post = self.get_object()
        version = request.data.get('version')
        if not version:
            return Response({"error": "Version number required."}, status=status.HTTP_400_BAD_REQUEST)

        revision = post.revisions.filter(version_number=version).first()
        if not revision:
            return Response({"error": "Revision version not found."}, status=status.HTTP_404_NOT_FOUND)

        post.title = revision.title_snapshot
        post.excerpt = revision.excerpt_snapshot
        post.blocks_data = revision.blocks_data_snapshot
        post.content_html = revision.content_html_snapshot
        post.save()

        user = request.user if request.user.is_authenticated else post.author
        post.create_revision(user=user, summary=f"Restored to revision v{version}")
        return Response({
            "message": f"Restored post to revision v{version}.",
            "post": PostDetailSerializer(post).data
        })

    @action(detail=True, methods=['post'], permission_classes=[permissions.AllowAny])
    def track_view(self, request, id=None):
        post = self.get_object()
        post.view_count += 1
        post.save(update_fields=['view_count'])
        
        # Also log to PageView model if analytics app is loaded
        try:
            from apps.analytics.models import PageView
            PageView.objects.create(
                post=post,
                path=request.path,
                ip_address=request.META.get('REMOTE_ADDR', '127.0.0.1'),
                user_agent=request.META.get('HTTP_USER_AGENT', '')[:250],
                referrer=request.META.get('HTTP_REFERER', '')[:250]
            )
        except Exception:
            pass

        return Response({"views": post.view_count})


class PublicPostListView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        qs = Post.objects.filter(status='published').select_related('author', 'author__profile').prefetch_related('categories', 'tags')
        
        category = request.query_params.get('category')
        if category:
            qs = qs.filter(categories__slug=category)

        tag = request.query_params.get('tag')
        if tag:
            qs = qs.filter(tags__slug=tag)

        search = request.query_params.get('search')
        if search:
            qs = qs.filter(Q(title__icontains=search) | Q(excerpt__icontains=search) | Q(content_html__icontains=search))

        qs = qs.order_by('-published_at')
        return Response(PostListSerializer(qs, many=True).data)


class PublicPostDetailView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, slug):
        post = Post.objects.filter(slug=slug, status='published').select_related('author', 'author__profile').prefetch_related('categories', 'tags').first()
        if not post:
            return Response({"error": "Article not found."}, status=status.HTTP_404_NOT_FOUND)
        
        # Auto increment view count
        post.view_count += 1
        post.save(update_fields=['view_count'])
        return Response(PostDetailSerializer(post).data)
