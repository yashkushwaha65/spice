import requests
import xml.etree.ElementTree as ET
from cache import get_cache, set_cache

def get_trends(geo="IN"):
    # Check cache first
    cached = get_cache("trends_global")
    if cached:
        return cached

    # Use Google Trends Daily RSS Feed (Much more stable than scraping)
    # geo="IN" for India, "US" for USA
    url = f"https://trends.google.com/trends/trendingsearches/daily/rss?geo={geo}"
    
    try:
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            return {"text": "Unable to fetch trends right now. 📉", "image": None}

        # Parse XML
        root = ET.fromstring(response.content)
        
        # Extract items
        items = root.findall(".//item")
        
        text = "🔥 **Trending Now**\n"
        count = 0
        
        for item in items:
            if count >= 5: break # Top 5 trends
            title = item.find("title").text
            traffic = item.find(".//ht:approx_traffic", namespaces={'ht': 'https://trends.google.com.br/trends/trendingsearches/daily'})
            traffic_text = f" ({traffic.text}+)" if traffic is not None else ""
            
            text += f"\n• {title}{traffic_text}"
            count += 1

        data = {"text": text, "image": None}
        set_cache("trends_global", data, 3600) # Cache for 1 hour
        return data

    except Exception as e:
        print(f"Trends Error: {e}")
        return {"text": "I'm having trouble seeing what's trending. 😕", "image": None}
