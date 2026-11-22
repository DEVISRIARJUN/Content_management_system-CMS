from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Category, Tag, Post, PostRevision
from apps.accounts.serializers import UserSerializer


class CategorySerializer(serializers.ModelSerializer):
    posts_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'color_hex', 'icon', 'is_featured', 'posts_count', 'created_at']

    def get_posts_count(self, obj):
        return obj.posts.filter(status='published').count()


class TagSerializer(serializers.ModelSerializer):
    posts_count = serializers.SerializerMethodField()

    class Meta:
        model = Tag
        fields = ['id', 'name', 'slug', 'posts_count', 'created_at']

    def get_posts_count(self, obj):
        return obj.posts.filter(status='published').count()


class PostRevisionSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)

    class Meta:
        model = PostRevision
        fields = [
            'id', 'version_number', 'title_snapshot', 'excerpt_snapshot',
            'blocks_data_snapshot', 'content_html_snapshot', 'author',
            'change_summary', 'created_at'
        ]


class PostListSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    categories = CategorySerializer(many=True, read_only=True)
    tags = TagSerializer(many=True, read_only=True)

    class Meta:
        model = Post
        fields = [
            'id', 'title', 'slug', 'author', 'status', 'content_format',
            'excerpt', 'featured_image', 'categories', 'tags',
            'reading_time_minutes', 'view_count', 'published_at',
            'created_at', 'updated_at'
        ]


class PostDetailSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    categories = CategorySerializer(many=True, read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    revisions_count = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            'id', 'title', 'slug', 'author', 'status', 'content_format',
            'blocks_data', 'content_html', 'excerpt', 'featured_image',
            'categories', 'tags', 'reading_time_minutes', 'view_count',
            'seo_title', 'seo_description', 'seo_keywords',
            'revisions_count', 'published_at', 'scheduled_for',
            'created_at', 'updated_at'
        ]

    def get_revisions_count(self, obj):
        return obj.revisions.count()


class PostCreateUpdateSerializer(serializers.ModelSerializer):
    category_ids = serializers.ListField(child=serializers.IntegerField(), required=False, write_only=True)
    tag_names = serializers.ListField(child=serializers.CharField(), required=False, write_only=True)
    revision_summary = serializers.CharField(required=False, write_only=True, default="Content update")

    class Meta:
        model = Post
        fields = [
            'id', 'title', 'slug', 'status', 'content_format', 'blocks_data',
            'content_html', 'excerpt', 'featured_image', 'category_ids',
            'tag_names', 'seo_title', 'seo_description', 'seo_keywords',
            'scheduled_for', 'revision_summary'
        ]

    def create(self, validated_data):
        category_ids = validated_data.pop('category_ids', [])
        tag_names = validated_data.pop('tag_names', [])
        summary = validated_data.pop('revision_summary', 'Initial draft')
        
        request = self.context.get('request')
        author = request.user if request and request.user.is_authenticated else User.objects.first()

        post = Post.objects.create(author=author, **validated_data)

        if category_ids:
            post.categories.set(Category.objects.filter(id__in=category_ids))

        if tag_names:
            tag_objs = []
            for name in tag_names:
                t, _ = Tag.objects.get_or_create(name=name.strip())
                tag_objs.append(t)
            post.tags.set(tag_objs)

        # Snapshot first revision
        post.create_revision(user=author, summary=summary)
        return post

    def update(self, instance, validated_data):
        category_ids = validated_data.pop('category_ids', None)
        tag_names = validated_data.pop('tag_names', None)
        summary = validated_data.pop('revision_summary', 'Updated content')
        request = self.context.get('request')
        user = request.user if request and request.user.is_authenticated else instance.author

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if category_ids is not None:
            instance.categories.set(Category.objects.filter(id__in=category_ids))

        if tag_names is not None:
            tag_objs = []
            for name in tag_names:
                t, _ = Tag.objects.get_or_create(name=name.strip())
                tag_objs.append(t)
            instance.tags.set(tag_objs)

        # Auto create revision on significant changes
        instance.create_revision(user=user, summary=summary)
        return instance
