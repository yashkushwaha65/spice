import requests
from cache import get_cache, set_cache

def search_reddit(query: str, max_results: int = 5):
    """
    Search Reddit for posts related to a query.
    Uses Reddit's public JSON API (no auth required).
    
    Args:
        query: Search query
        max_results: Maximum number of results
    
    Returns:
        Dict with text and posts
    """
    cache_key = f"reddit:{query.lower()}"
    cached = get_cache(cache_key)
    if cached:
        return cached
    
    url = "https://www.reddit.com/search.json"
    headers = {
        "User-Agent": "Spice Bot/1.0"
    }
    params = {
        "q": query,
        "limit": max_results,
        "sort": "relevance"
    }
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        
        if response.status_code != 200:
            return {
                "text": "Couldn't fetch Reddit results right now.",
                "image": None,
                "posts": []
            }
        
        data = response.json()
        posts_data = data.get("data", {}).get("children", [])
        
        if not posts_data:
            return {
                "text": f"No Reddit posts found for '{query}'.",
                "image": None,
                "posts": []
            }
        
        # Build response
        text = f"🔴 **Reddit: {query}**\n"
        posts = []
        
        for idx, post in enumerate(posts_data, 1):
            post_data = post.get("data", {})
            title = post_data.get("title", "No title")
            subreddit = post_data.get("subreddit", "unknown")
            score = post_data.get("score", 0)
            permalink = post_data.get("permalink", "")
            url_link = f"https://www.reddit.com{permalink}"
            
            text += f"\n{idx}. **{title}**\n   r/{subreddit} • ⬆️ {score}\n   {url_link}\n"
            
            posts.append({
                "title": title,
                "subreddit": subreddit,
                "score": score,
                "url": url_link
            })
        
        result = {
            "text": text,
            "image": None,
            "posts": posts
        }
        
        set_cache(cache_key, result, 600)  # Cache for 10 minutes
        return result
    
    except Exception as e:
        print(f"Reddit API Error: {e}")
        return {
            "text": "Having trouble reaching Reddit right now. 🔴",
            "image": None,
            "posts": []
        }
