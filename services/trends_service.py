from pytrends.request import TrendReq
import requests
from cache import get_cache, set_cache

def get_trends():
    cached = get_cache("trends")
    if cached:
        return cached

    pytrends = TrendReq()
    trends = pytrends.trending_searches(pn="india").head(5)[0].tolist()

    reddit = requests.get("https://www.reddit.com/r/popular.json", headers={"User-Agent": "Mozilla/5.0"}).json()
    reddit_titles = [p["data"]["title"] for p in reddit["data"]["children"][:5]]

    data = "🔥 Trending Now:\n\nGoogle Searches:\n"
    for t in trends:
        data += f"- {t}\n"

    data += "\nReddit:\n"
    for r in reddit_titles:
        data += f"- {r}\n"

    set_cache("trends", data, 900)
    return data
