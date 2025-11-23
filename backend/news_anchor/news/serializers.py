from rest_framework import serializers
from .models import NewsArticle, AnchoringScript


class NewsArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsArticle
        fields = '__all__'


class AnchoringScriptSerializer(serializers.ModelSerializer):
    news_title = serializers.CharField(source='news.title', read_only=True)
    news_category = serializers.CharField(source='news.category', read_only=True)

    class Meta:
        model = AnchoringScript
        fields = ['id', 'news', 'news_title', 'news_category', 'script', 'created_at']
