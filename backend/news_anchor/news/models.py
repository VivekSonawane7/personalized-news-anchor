# models.py
from django.db import models

class NewsArticle(models.Model):
    title = models.CharField(max_length=500)
    description = models.TextField(null=True, blank=True)
    url = models.URLField(max_length=500, unique=True)
    source = models.CharField(max_length=100, null=True, blank=True)
    category = models.CharField(max_length=50, null=True, blank=True)
    published_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class AnchoringScript(models.Model):
    news = models.OneToOneField(NewsArticle, on_delete=models.CASCADE, related_name='script')
    script = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Script for: {self.news.title}"