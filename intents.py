import re
import difflib
from typing import Tuple, Optional, Dict, List

# =============================================================================
# CONFIGURATION
# =============================================================================

# Keyword clusters with weights (higher = stronger signal)
INTENT_CLUSTERS: Dict[str, Dict[str, int]] = {
    "weather": {
        # Primary keywords (high confidence)
        "weather": 10, "forecast": 10, "temperature": 10,
        # Secondary keywords
        "temp": 8, "rain": 7, "raining": 7, "sunny": 7, "cloudy": 7,
        "humidity": 6, "climate": 5, "hot": 4, "cold": 4,
        # Phrases (checked separately)
        "how hot": 8, "how cold": 8, "will it rain": 9,
    },
    "news": {
        "news": 10, "headlines": 10, "breaking": 9,
        "latest": 7, "updates": 6, "happening": 6, "events": 5,
        "report": 5, "world": 4,
        # Phrases
        "what's happening": 9, "whats happening": 9, "tell me news": 10,
    },
    "market": {
        "price": 10, "stock": 10, "market": 8, "crypto": 9,
        "bitcoin": 10, "btc": 10, "eth": 10, "ethereum": 10,
        "gold": 8, "nifty": 8, "sensex": 8, "nasdaq": 8,
        "value": 5, "rate": 4, "cost": 4, "share": 6, "shares": 6,
        # Common tickers/companies
        "aapl": 10, "tsla": 10, "googl": 10, "amzn": 10, "msft": 10,
        "apple": 8, "tesla": 8, "google": 8, "amazon": 8, "microsoft": 8, "meta": 8,
        "reliance": 8, "tcs": 8, "infosys": 8,
        # Phrases
        "how much": 6, "what is the price": 10, "stock price": 10,
    },
    "trends": {
        "trend": 10, "trending": 10, "viral": 9, "popular": 8,
        "hot": 5, "buzz": 7,
        # Phrases
        "what's trending": 10, "whats trending": 10, "hot topics": 9,
        "what's hot": 8, "whats hot": 8,
    },
    "hello": {
        "hello": 10, "hi": 10, "hey": 10, "help": 8,
        "start": 7, "menu": 7, "greetings": 6,
    },
}

# Known entities for extraction
COMMON_CITIES = {
    "delhi", "mumbai", "bangalore", "chennai", "kolkata", "hyderabad", "pune",
    "ahmedabad", "jaipur", "lucknow", "kanpur", "nagpur", "indore", "bhopal",
    "surat", "vapi", "vadodara", "rajkot", "gandhinagar",  # Gujarat cities
    "new york", "london", "tokyo", "paris", "dubai", "singapore", "sydney",
    "los angeles", "chicago", "san francisco", "seattle", "boston",
}

STOCK_SYMBOLS = {
    # US Stocks
    "aapl": "AAPL", "apple": "AAPL",
    "tsla": "TSLA", "tesla": "TSLA",
    "googl": "GOOGL", "google": "GOOGL", "goog": "GOOGL",
    "amzn": "AMZN", "amazon": "AMZN",
    "msft": "MSFT", "microsoft": "MSFT",
    "meta": "META", "facebook": "META",
    "nvda": "NVDA", "nvidia": "NVDA",
    "nflx": "NFLX", "netflix": "NFLX",
    # Crypto
    "btc": "BTC-USD", "bitcoin": "BTC-USD",
    "eth": "ETH-USD", "ethereum": "ETH-USD",
    # Indian Stocks
    "reliance": "RELIANCE.NS", "tcs": "TCS.NS", "infosys": "INFY.NS",
    # Commodities
    "gold": "GC=F", "silver": "SI=F", "oil": "CL=F",
}

CONFIDENCE_THRESHOLD = 5  # Minimum score to return an intent

# =============================================================================
# INPUT NORMALIZATION
# =============================================================================

def normalize_input(text: str) -> str:
    """Clean and normalize user input."""
    # Lowercase and strip
    text = text.lower().strip()
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    # Remove punctuation except apostrophes (for contractions like "what's")
    text = re.sub(r"[^\w\s']", '', text)
    return text

# =============================================================================
# INTENT DETECTION WITH CONFIDENCE SCORING
# =============================================================================

def calculate_intent_scores(text: str) -> Dict[str, int]:
    """Calculate confidence scores for each intent."""
    scores = {intent: 0 for intent in INTENT_CLUSTERS}
    words = text.split()
    
    for intent, keywords in INTENT_CLUSTERS.items():
        for keyword, weight in keywords.items():
            # Check for phrase match (multi-word keywords)
            if ' ' in keyword and keyword in text:
                scores[intent] += weight
            # Check for word match
            elif keyword in words:
                scores[intent] += weight
    
    return scores

def detect_intent(q: str) -> str:
    """
    Detect user intent using confidence scoring.
    Returns the intent with highest score above threshold, or 'unknown'.
    """
    normalized = normalize_input(q)
    scores = calculate_intent_scores(normalized)
    
    # Get intent with highest score
    best_intent = max(scores, key=scores.get)
    best_score = scores[best_intent]
    
    # Return intent only if above threshold
    if best_score >= CONFIDENCE_THRESHOLD:
        return best_intent
    
    # Fuzzy matching fallback for typos
    all_keywords = []
    keyword_to_intent = {}
    for intent, keywords in INTENT_CLUSTERS.items():
        for k in keywords:
            if ' ' not in k:  # Only single words for fuzzy matching
                all_keywords.append(k)
                keyword_to_intent[k] = intent
    
    for word in normalized.split():
        matches = difflib.get_close_matches(word, all_keywords, n=1, cutoff=0.8)
        if matches:
            return keyword_to_intent[matches[0]]
    
    return "unknown"

def get_intent_with_confidence(q: str) -> Tuple[str, int]:
    """Returns intent and its confidence score."""
    normalized = normalize_input(q)
    scores = calculate_intent_scores(normalized)
    best_intent = max(scores, key=scores.get)
    return (best_intent, scores[best_intent]) if scores[best_intent] >= CONFIDENCE_THRESHOLD else ("unknown", 0)

# =============================================================================
# ENTITY EXTRACTION
# =============================================================================

def extract_city(text: str) -> Optional[str]:
    """Extract city name from text."""
    normalized = normalize_input(text)
    
    # Check for known cities (including multi-word cities)
    for city in COMMON_CITIES:
        if city in normalized:
            return city.title()
    
    # Remove trigger words and take remaining as potential city
    triggers = {"weather", "forecast", "temp", "temperature", "in", "at", "for", "of", "the", "whats", "what"}
    words = [w for w in normalized.split() if w not in triggers]
    
    if words:
        # Return the last word(s) as city name
        return " ".join(words).title()
    
    return None

def extract_symbol(text: str) -> Optional[str]:
    """Extract stock/crypto symbol from text."""
    normalized = normalize_input(text)
    words = normalized.split()
    
    # Check for known symbols/names
    for word in words:
        if word in STOCK_SYMBOLS:
            return STOCK_SYMBOLS[word]
    
    # Check if entire normalized text is a symbol
    if normalized in STOCK_SYMBOLS:
        return STOCK_SYMBOLS[normalized]
    
    # Remove trigger words and take remaining as potential symbol
    triggers = {"price", "stock", "market", "value", "quote", "of", "is", "for", "check", "whats", "what", "the", "show", "me"}
    symbol_candidates = [w for w in words if w not in triggers]
    
    if symbol_candidates:
        candidate = symbol_candidates[-1].upper()
        # Validate: typical symbols are 1-5 chars
        if 1 <= len(candidate) <= 5:
            return candidate
    
    return None

def extract_topic(text: str, intent: str) -> Optional[str]:
    """Extract topic/subject from a query based on intent."""
    normalized = normalize_input(text)
    words = normalized.split()
    
    if intent == "news":
        # Remove news-related trigger words
        triggers = {"news", "headlines", "breaking", "latest", "updates", "about", "on", "of", "for", "whats", "what", "tell", "me", "show", "the"}
        topic_words = [w for w in words if w not in triggers]
        
        if topic_words:
            # Return all remaining words as topic
            return " ".join(topic_words)
    
    return None
