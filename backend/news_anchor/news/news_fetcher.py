import requests
from .models import NewsArticle
from django.utils.dateparse import parse_datetime
from django.conf import settings
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

def fetch_and_store_news(category=None):
    url = "https://newsapi.org/v2/top-headlines"
    params = {
        "apiKey": settings.NEWS_API_KEY,
        "country": "in",  # India
        "pageSize": 20
    }

    if category:
        params["category"] = category

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()  # Raises an HTTPError for bad responses
        data = response.json()

        if data.get("status") == "ok":
            articles_created = 0
            for article_data in data.get("articles", []):
                # Skip articles with missing essential data
                if not article_data.get('url') or not article_data.get('title'):
                    continue

                # Avoid duplicates based on URL
                if not NewsArticle.objects.filter(url=article_data['url']).exists():
                    published_at = parse_datetime(article_data.get('publishedAt'))

                    NewsArticle.objects.create(
                        title=article_data.get('title', '')[:500],  # Ensure it fits in CharField
                        description=article_data.get('description'),
                        url=article_data.get('url'),
                        source=article_data.get('source', {}).get('name'),
                        category=category,
                        published_at=published_at
                    )
                    articles_created += 1

            logger.info(f"Created {articles_created} new articles for category: {category}")
            return articles_created

    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching news: {e}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")

    return 0