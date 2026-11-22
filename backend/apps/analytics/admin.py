from django.contrib import admin
from .models import PageView

@admin.register(PageView)
class PageViewAdmin(admin.ModelAdmin):
    list_display = ('path', 'post', 'ip_address', 'timestamp')
    list_filter = ('timestamp',)
    search_fields = ('path', 'ip_address', 'user_agent')
