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



# openrouter_summarizer.py
import requests

OPENROUTER_API_KEY = "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"  # <-- Replace with your API key
MODEL_ID = "nvidia/nemotron-nano-9b-v2:free"  # <-- Free OpenRouter model for summarization

def summarize_text(text, max_length=50, min_length=20):
    """
    Summarize a news article using OpenRouter's free model.
    """
    if not text:
        return "No content to summarize."

    prompt = f"Deliver a news anchor-style summary of this article in 2-3 concise sentences, highlighting key developments.:\n\n{text}"

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }

    data = {
        "model": MODEL_ID,
        "messages": [{"role": "user", "content": prompt}],
    }

    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            json=data,
            headers=headers,
            timeout=10
        )
        response.raise_for_status()
        summary = response.json().get("choices", [{}])[0].get("message", {}).get("content", "")
        return summary if summary else "No summary available."
    except requests.exceptions.RequestException as e:
        return f"Error: {e}"
