import requests
from config import NEWS_API_KEY
from cache import get_cache, set_cache

def get_news():
    """Get general top headlines."""
    cached = get_cache("news")
    if cached:
        return cached

    url = f"https://gnews.io/api/v4/top-headlines?token={NEWS_API_KEY}&lang=en"
    try:
        res = requests.get(url).json()
        articles = res.get("articles", [])[:4] 

        text = "📰 **Top Headlines Today**\n"
        image_url = None
        
        # Use the image from the first/top article
        if articles and "image" in articles[0]:
            image_url = articles[0]["image"]

        for article in articles:
            title = article["title"]
            text += f"\n• {title}"

        data = {"text": text, "image": image_url}
        set_cache("news", data, 300)
        return data
    except Exception:
        return {
            "text": "I'm having trouble loading the news feed right now. 🗞️",
            "image": None
        }

def search_news(query: str, max_results: int = 5):
    """Search for news articles about a specific topic."""
    cache_key = f"news_search:{query.lower()}"
    cached = get_cache(cache_key)
    if cached:
        return cached
    
    url = f"https://gnews.io/api/v4/search?q={query}&token={NEWS_API_KEY}&lang=en&max={max_results}"
    try:
        res = requests.get(url, timeout=10).json()
        articles = res.get("articles", [])
        
        if not articles:
            return {
                "text": f"No news articles found for '{query}'.",
                "image": None,
                "articles": []
            }
        
        text = f"📰 **News: {query}**\n"
        image_url = None
        
        # Use the image from the first article
        if articles and "image" in articles[0]:
            image_url = articles[0]["image"]
        
        article_list = []
        for idx, article in enumerate(articles, 1):
            title = article.get("title", "No title")
            source = article.get("source", {}).get("name", "Unknown")
            url_link = article.get("url", "")
            
            text += f"\n{idx}. **{title}**\n   Source: {source}\n"
            
            article_list.append({
                "title": title,
                "source": source,
                "url": url_link,
                "image": article.get("image")
            })
        
        data = {
            "text": text,
            "image": image_url,
            "articles": article_list
        }
        set_cache(cache_key, data, 300)
        return data
    
    except Exception as e:
        print(f"News Search Error: {e}")
        return {
            "text": f"Couldn't fetch news for '{query}' right now. 🗞️",
            "image": None,
            "articles": []
        }
