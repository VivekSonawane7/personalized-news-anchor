from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import viewsets, status
from .models import NewsArticle
from .serializers import NewsArticleSerializer
from .utils import fetch_and_store_news

class FetchNewsAPIView(APIView):
    """
    Fetch latest news from API and store in DB
    """
    def get(self, request):
        category = request.GET.get("category", "general")
        created = fetch_and_store_news(category)
        return Response({
            "status": "success",
            "message": f"Fetched {created} new articles",
            "category": category,
            "articles_created": created
        })

    def post(self, request):
        category = request.data.get("category", "general")
        created = fetch_and_store_news(category)
        return Response({
            "status": "success",
            "message": f"Fetched {created} new articles",
            "category": category,
            "articles_created": created
        })

class NewsArticleViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Simple view to list all news articles
    """
    queryset = NewsArticle.objects.all().order_by('-published_at')
    serializer_class = NewsArticleSerializer

    def get_queryset(self):
        queryset = NewsArticle.objects.all().order_by('-published_at')

        # Filter by category if provided
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category=category)

        # Search by keyword if provided
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(title__icontains=search)

        return queryset

class CategoryListView(APIView):
    """
    Get all available categories from news articles
    """
    def get(self, request):
        categories = NewsArticle.objects.values_list('category', flat=True).distinct()
        return Response({
            "categories": [cat for cat in categories if cat]
        })

class ClearNewsAPIView(APIView):
    """
    Clear all news articles from database
    """
    def delete(self, request):
        count = NewsArticle.objects.count()
        NewsArticle.objects.all().delete()
        return Response({
            "status": "success",
            "message": f"Cleared {count} articles from database"
        })



# views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import NewsArticle
from .utils import summarize_text
from django.db.models import Count
import random

class RandomSummarizeNewsAPIView(APIView):
    """
    API to get a random news article from the database and summarize it.
    """

    def get(self, request):
        total_articles = NewsArticle.objects.count()
        if total_articles == 0:
            return Response({"error": "No articles in the database"}, status=404)

        # Get a random article
        random_index = random.randint(0, total_articles - 1)
        article = NewsArticle.objects.all()[random_index]

        # Summarize description or title if description is empty
        summary = summarize_text(article.description or article.title)

        return Response({
            "id": article.id,
            "title": article.title,
            "url": article.url,
            "category": article.category,
            "published_at": article.published_at,
            "summary": summary
        })
