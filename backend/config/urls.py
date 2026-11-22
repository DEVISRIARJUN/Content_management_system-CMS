from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from django.http import JsonResponse


def api_root(request):
    return JsonResponse({
        "name": "NovaCMS API",
        "version": "1.0.0",
        "status": "operational",
        "endpoints": {
            "auth": "/api/auth/",
            "posts": "/api/posts/",
            "categories": "/api/categories/",
            "tags": "/api/tags/",
            "media": "/api/media/",
            "analytics": "/api/analytics/dashboard/",
            "ai_assistant": "/api/ai/",
            "public_reader": "/api/public/posts/"
        }
    })


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', api_root, name='api-root'),
    path('api/auth/', include('apps.accounts.urls')),
    path('api/', include('apps.posts.urls')),
    path('api/', include('apps.media_manager.urls')),
    path('api/analytics/', include('apps.analytics.urls')),
    path('api/ai/', include('apps.ai_assistant.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Frontend client routes (Single Page Application fallback)
urlpatterns += [
    re_path(r'^(?!api/|admin/|media/|static/).*$', TemplateView.as_view(template_name='index.html'), name='app-frontend'),
]
