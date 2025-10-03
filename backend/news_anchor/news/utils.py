import requests
import logging
from django.utils.dateparse import parse_datetime
from django.conf import settings
from .models import NewsArticle

logger = logging.getLogger(__name__)

def fetch_and_store_news(category="general"):
    """
    Simple function to fetch news and store in database
    """
    if not settings.NEWS_API_KEY:
        logger.error("NEWS_API_KEY not found in environment variables")
        return 0

    url = "https://newsapi.org/v2/top-headlines"
    params = {
        "apiKey": settings.NEWS_API_KEY,
        "country": "us",  # You can change this
        "pageSize": 20
    }

    if category and category != "all":
        params["category"] = category

    try:
        print(f"Fetching news for category: {category}")
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
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
                        title=article_data.get('title', '')[:500],
                        description=article_data.get('description'),
                        url=article_data.get('url'),
                        source=article_data.get('source', {}).get('name'),
                        category=category,
                        published_at=published_at
                    )
                    articles_created += 1

            print(f"✅ Created {articles_created} new articles for category: {category}")
            return articles_created
        else:
            print(f"❌ API Error: {data.get('message', 'Unknown error')}")
            return 0

    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching news: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

    return 0