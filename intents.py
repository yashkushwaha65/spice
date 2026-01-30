# intents.py

def detect_intent(text: str) -> str:
    t = text.lower()

    if "weather" in t:
        return "weather"
    if "price" in t or "stock" in t or "bitcoin" in t or "market" in t:
        return "market"
    if "news" in t:
        return "news"
    if "trend" in t or "trending" in t:
        return "trends"

    return "unknown"
