from django.contrib import admin
from .models import NewsArticle

@admin.register(NewsArticle)
class NewsArticleAdmin(admin.ModelAdmin):
    list_display = ['title', 'source', 'category', 'published_at', 'created_at']
    list_filter = ['category', 'source']
    search_fields = ['title', 'description']
    readonly_fields = ['created_at']