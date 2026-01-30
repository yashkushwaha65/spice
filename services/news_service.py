import requests
from config import NEWS_API_KEY
from cache import get_cache, set_cache

def get_news():
    cached = get_cache("news")
    if cached:
        return cached

    url = f"https://gnews.io/api/v4/top-headlines?token={NEWS_API_KEY}&lang=en"
    res = requests.get(url).json()

    articles = res.get("articles", [])[:5]

    headlines = [a["title"] for a in articles]

    data = "📰 Top News:\n" + "\n".join(f"- {h}" for h in headlines)

    set_cache("news", data, 300)
    return data
