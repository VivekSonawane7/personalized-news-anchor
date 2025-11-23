import requests
from datetime import datetime
from django.conf import settings
from .models import NewsArticle

def fetch_and_store_news(category=None):
    """
    Fetches news articles from NewsAPI and stores them in MySQL.
    Tries top-headlines first; if no articles, falls back to everything endpoint.
    """
    # --- Step 1: Try top-headlines ---
    url = "https://newsapi.org/v2/top-headlines"
    params = {
        "apiKey": settings.NEWS_API_KEY,
        "country": "in",
    }
    if category:
        params["category"] = category

    try:
        response = requests.get(url, params=params)
        data = response.json()

        if data.get("status") != "ok":
            print("❌ Error fetching news:", data.get("message"))
            return

        articles = data.get("articles", [])
        print(f"🔍 Top-headlines returned {len(articles)} articles.")

        # --- Step 2: Fallback to everything if no articles ---
        if len(articles) == 0:
            url = "https://newsapi.org/v2/everything"
            params = {
                "apiKey": settings.NEWS_API_KEY,
                "q": "India",
                "language": "en",
                "pageSize": 50,
            }
            response = requests.get(url, params=params)
            data = response.json()
            articles = data.get("articles", [])
            print(f"🔍 Everything endpoint returned {len(articles)} articles.")

        # --- Step 3: Save articles to database ---
        saved_count = 0
        for i, article in enumerate(articles, start=1):
            title = article.get("title")
            description = article.get("description")
            url = article.get("url")
            source = article.get("source", {}).get("name")
            published_at = article.get("publishedAt")

            # Convert string date to datetime
            if published_at:
                try:
                    published_at = datetime.fromisoformat(published_at.replace("Z", "+00:00"))
                except Exception:
                    published_at = None

            try:
                obj, created = NewsArticle.objects.get_or_create(
                    url=url,
                    defaults={
                        "title": title,
                        "description": description,
                        "source": source,
                        "category": category,
                        "published_at": published_at,
                    }
                )
                if created:
                    saved_count += 1
            except Exception as e:
                print(f"❌ Error saving article {i}: {e}")

        print(f"✅ Stored {saved_count} new articles successfully.")

    except Exception as e:
        print("⚠️ Error while fetching news:", e)
