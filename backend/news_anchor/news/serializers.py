# api/serializers.py
from rest_framework import serializers
from .models import NewsArticle
from .summerizer import generate_summary

class NewsArticleSerializer(serializers.ModelSerializer):
    summary = serializers.SerializerMethodField()

    class Meta:
        model = NewsArticle
        fields = "__all__"  # includes title, description, url, source, category, etc.

    def get_summary(self, obj):
        return generate_summary(obj.description or obj.title)
