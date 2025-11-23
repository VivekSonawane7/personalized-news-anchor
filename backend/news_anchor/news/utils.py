from .news_fetcher import fetch_and_store_news

def update_news(category=None):
    fetch_and_store_news(category)
