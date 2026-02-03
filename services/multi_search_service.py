"""
Multi-Source Search Aggregator
Searches across News, YouTube, Reddit, and other platforms for a topic.
"""

from typing import Dict, List, Any
from services.news_service import search_news
from services.youtube_service import search_youtube
from services.reddit_service import search_reddit
from cache import get_cache, set_cache

def search_all_sources(query: str, sources: List[str] = None) -> Dict[str, Any]:
    """
    Search multiple platforms for a topic and aggregate results.
    
    Args:
        query: Search topic/keyword
        sources: List of sources to search. If None, searches all.
                 Options: ['news', 'youtube', 'reddit']
    
    Returns:
        Aggregated results with text and metadata
    """
    if sources is None:
        sources = ['news', 'youtube', 'reddit']
    
    cache_key = f"multi_search:{query.lower()}:{'_'.join(sorted(sources))}"
    cached = get_cache(cache_key)
    if cached:
        return cached
    
    results = {
        "query": query,
        "sources": {},
        "combined_text": f"🔍 **Search Results for '{query}'**\n\n",
        "primary_image": None
    }
    
    # Search each source
    if 'news' in sources:
        news_result = search_news(query, max_results=3)
        results["sources"]["news"] = news_result
        if news_result.get("articles"):
            results["combined_text"] += f"📰 **News Articles**\n{news_result['text']}\n\n"
            if not results["primary_image"] and news_result.get("image"):
                results["primary_image"] = news_result["image"]
    
    if 'youtube' in sources:
        youtube_result = search_youtube(query, max_results=3)
        results["sources"]["youtube"] = youtube_result
        if youtube_result.get("videos"):
            results["combined_text"] += f"🎥 **YouTube Videos**\n{youtube_result['text']}\n\n"
            if not results["primary_image"] and youtube_result.get("image"):
                results["primary_image"] = youtube_result["image"]
    
    if 'reddit' in sources:
        reddit_result = search_reddit(query, max_results=3)
        results["sources"]["reddit"] = reddit_result
        if reddit_result.get("posts"):
            results["combined_text"] += f"🔴 **Reddit Discussions**\n{reddit_result['text']}\n\n"
    
    # Check if we got any results
    has_results = any(
        results["sources"].get(source, {}).get("articles") or
        results["sources"].get(source, {}).get("videos") or
        results["sources"].get(source, {}).get("posts")
        for source in sources
    )
    
    if not has_results:
        results["combined_text"] = f"No results found for '{query}' across any platform. 😕\n\nTry:\n• Different keywords\n• More specific terms\n• Check spelling"
    
    # Build final response
    response = {
        "text": results["combined_text"].strip(),
        "image": results["primary_image"],
        "metadata": {
            "query": query,
            "sources_searched": sources,
            "sources_data": results["sources"]
        }
    }
    
    set_cache(cache_key, response, 300)  # Cache for 5 minutes
    return response

def get_topic_summary(query: str) -> Dict[str, Any]:
    """
    Get a comprehensive summary for a topic across all sources.
    Alias for search_all_sources with better naming.
    """
    return search_all_sources(query, sources=['news', 'youtube', 'reddit'])
