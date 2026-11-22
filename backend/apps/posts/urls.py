from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet, TagViewSet, PostViewSet, PublicPostListView, PublicPostDetailView

router = DefaultRouter()
router.register(r'categories', CategoryViewSet)
router.register(r'tags', TagViewSet)
router.register(r'posts', PostViewSet, basename='post')

urlpatterns = [
    path('public/posts/', PublicPostListView.as_view(), name='public-post-list'),
    path('public/posts/<slug:slug>/', PublicPostDetailView.as_view(), name='public-post-detail'),
    path('', include(router.urls)),
]
