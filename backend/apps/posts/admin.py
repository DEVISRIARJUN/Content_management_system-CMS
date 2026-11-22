from django.contrib import admin
from .models import Category, Tag, Post, PostRevision


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'color_hex', 'is_featured', 'created_at')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name', 'description')


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'created_at')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)


class PostRevisionInline(admin.TabularInline):
    model = PostRevision
    extra = 0
    readonly_fields = ('version_number', 'title_snapshot', 'author', 'change_summary', 'created_at')
    can_delete = False


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'status', 'view_count', 'published_at', 'created_at')
    list_filter = ('status', 'content_format', 'categories', 'created_at')
    search_fields = ('title', 'excerpt', 'content_html')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [PostRevisionInline]


@admin.register(PostRevision)
class PostRevisionAdmin(admin.ModelAdmin):
    list_display = ('post', 'version_number', 'author', 'change_summary', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('post__title', 'title_snapshot', 'change_summary')
