import requests
from config import YOUTUBE_API_KEY
from cache import get_cache, set_cache

def search_youtube(query: str, max_results: int = 5):
    """
    Search YouTube for videos related to a query.
    
    Args:
        query: Search query
        max_results: Maximum number of results (default 5)
    
    Returns:
        Dict with text and image (thumbnail)
    """
    cache_key = f"youtube:{query.lower()}"
    cached = get_cache(cache_key)
    if cached:
        return cached
    
    if not YOUTUBE_API_KEY:
        return {
            "text": "YouTube search is not configured.",
            "image": None,
            "videos": []
        }
    
    url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        "part": "snippet",
        "q": query,
        "type": "video",
        "maxResults": max_results,
        "key": YOUTUBE_API_KEY,
        "order": "relevance"  # Most relevant first
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code != 200:
            return {
                "text": f"Couldn't fetch YouTube results right now.",
                "image": None,
                "videos": []
            }
        
        data = response.json()
        items = data.get("items", [])
        
        if not items:
            return {
                "text": f"No YouTube videos found for '{query}'.",
                "image": None,
                "videos": []
            }
        
        # Build response
        text = f"🎥 **YouTube Results for '{query}'**\n"
        videos = []
        thumbnail_url = None
        
        for idx, item in enumerate(items, 1):
            snippet = item.get("snippet", {})
            video_id = item.get("id", {}).get("videoId")
            title = snippet.get("title", "No title")
            channel = snippet.get("channelTitle", "Unknown")
            
            # Get thumbnail (use first video's thumbnail as main image)
            if idx == 1 and "thumbnails" in snippet:
                thumbnail_url = snippet["thumbnails"].get("medium", {}).get("url")
            
            video_url = f"https://www.youtube.com/watch?v={video_id}"
            
            text += f"\n{idx}. **{title}**\n   by {channel}\n   {video_url}\n"
            
            videos.append({
                "title": title,
                "channel": channel,
                "video_id": video_id,
                "url": video_url,
                "thumbnail": snippet.get("thumbnails", {}).get("default", {}).get("url")
            })
        
        result = {
            "text": text,
            "image": thumbnail_url,
            "videos": videos
        }
        
        set_cache(cache_key, result, 600)  # Cache for 10 minutes
        return result
    
    except Exception as e:
        print(f"YouTube API Error: {e}")
        return {
            "text": "Having trouble reaching YouTube right now. 📺",
            "image": None,
            "videos": []
        }
