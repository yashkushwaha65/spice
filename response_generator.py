# Natural Response Generator
# Generates varied, context-aware responses instead of static templates

import random
from typing import Dict, Any, List, Optional

# Response templates for different scenarios
RESPONSE_TEMPLATES = {
    "news": {
        "success": [
            "Here's what's happening right now:\n\n{content}",
            "Fresh off the press! 📰\n\n{content}",
            "Top stories today:\n\n{content}",
            "Here are the latest headlines:\n\n{content}",
            "Breaking news and updates:\n\n{content}",
        ],
        "cached": [
            "Here's the latest (from my recent check):\n\n{content}",
            "Just pulled this for you:\n\n{content}",
        ],
        "error": [
            "Hmm, couldn't fetch the news right now. Try again in a moment?",
            "News sources are being slow. Mind trying again?",
            "Having trouble getting the headlines. Give it another shot?",
        ]
    },
    "weather": {
        "success": [
            "🌦️ Weather in {location}:\n\n{content}",
            "Here's the forecast for {location}:\n\n{content}",
            "{location} right now:\n\n{content}",
            "Weather update for {location}:\n\n{content}",
        ],
        "cached": [
            "Recent weather for {location}:\n\n{content}",
        ],
        "error": [
            "Couldn't get the weather for {location}. Check the spelling?",
            "Weather data unavailable for {location} right now.",
            "Having trouble reaching weather services. Try again?",
        ],
        "fallback": [
            "I'll check {location} for you.",
            "Let me grab the weather for {location}.",
        ]
    },
    "market": {
        "success": [
            "📈 {symbol} Price:\n\n{content}",
            "Here's the latest for {symbol}:\n\n{content}",
            "{symbol} market data:\n\n{content}",
            "Stock update for {symbol}:\n\n{content}",
        ],
        "cached": [
            "Recent price for {symbol}:\n\n{content}",
        ],
        "error": [
            "Couldn't find market data for {symbol}. Is that the right symbol?",
            "Having trouble fetching {symbol}. Try again?",
            "Market data unavailable for {symbol} right now.",
        ]
    },
    "trends": {
        "success": [
            "🔥 What's trending right now:\n\n{content}",
            "Here's what's hot today:\n\n{content}",
            "Top trending topics:\n\n{content}",
            "Everyone's talking about:\n\n{content}",
        ],
        "cached": [
            "Recent trending topics:\n\n{content}",
        ],
        "error": [
            "Can't get trending data right now. Try again?",
            "Having trouble fetching trends. Give it a moment?",
        ]
    },
    "hello": {
        "greeting": [
            "Hey there! 👋 What can I help you with?",
            "Hello! I'm here to help with news, weather, markets, or trends.",
            "Hi! 👋 Ask me about news, weather, stock prices, or what's trending!",
            "Welcome! What would you like to know? I can help with news, weather, markets, or trends.",
        ]
    },
    "contextual_followup": {
        "same_intent": [
            "Sure, let me check that for you.",
            "On it! 🚀",
            "Let me grab that info...",
            "Right away!",
        ],
        "different_intent": [
            "Switching gears! Let me get that for you.",
            "Got it, checking now...",
            "Sure thing!",
        ]
    }
}

SUGGESTION_TEMPLATES = {
    "news": [
        "Weather Update",
        "Trending Topics",
        "Market Prices",
    ],
    "weather": [
        "Check News",
        "What's Trending",
        "Stock Prices",
    ],
    "market": [
        "Latest News",
        "Weather Forecast",
        "Trending Now",
    ],
    "trends": [
        "Breaking News",
        "Weather Update",
        "Market Data",
    ]
}

def generate_response(
    intent: str,
    data: Any,
    is_cached: bool = False,
    is_error: bool = False,
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Generate a natural, varied response based on intent and data.
    
    Args:
        intent: Detected intent (news, weather, market, trends, hello)
        data: Response data from service (could be dict or string)
        is_cached: Whether data came from cache
        is_error: Whether an error occurred
        context: Additional context (location, symbol, etc.)
    
    Returns:
        Dict with reply, image, and suggestions
    """
    if context is None:
        context = {}
    
    # Handle hello/greeting
    if intent == "hello":
        return {
            "reply": random.choice(RESPONSE_TEMPLATES["hello"]["greeting"]),
            "image": None,
            "suggestions": ["Latest News", "Weather Delhi", "Bitcoin Price", "What's Trending"]
        }
    
    # Handle errors
    if is_error:
        return _generate_error_response(intent, context)
    
    # Extract text and image from data
    reply_text, image_url = _extract_data(data)
    
    # Generate appropriate response
    if intent in RESPONSE_TEMPLATES:
        template_key = "cached" if is_cached else "success"
        templates = RESPONSE_TEMPLATES[intent].get(template_key, RESPONSE_TEMPLATES[intent]["success"])
        
        template = random.choice(templates)
        
        # Format template with context
        formatted_reply = template.format(
            content=reply_text,
            location=context.get("city", "your location"),
            symbol=context.get("symbol", "the symbol")
        )
        
        # Generate contextual suggestions
        suggestions = _generate_suggestions(intent, context)
        
        return {
            "reply": formatted_reply,
            "image": image_url,
            "suggestions": suggestions
        }
    
    # Fallback for unknown intents
    return {
        "reply": reply_text,
        "image": image_url,
        "suggestions": ["Latest News", "Weather", "Market Prices"]
    }

def _extract_data(data: Any) -> tuple:
    """Extract text and image from service response data."""
    reply_text = ""
    image_url = None
    
    if isinstance(data, dict):
        reply_text = data.get("text", "No information available")
        image_url = data.get("image")
    else:
        reply_text = str(data) if data else "No information available"
    
    return reply_text, image_url

def _generate_error_response(intent: str, context: Dict[str, Any]) -> Dict[str, Any]:
    """Generate error response for a given intent."""
    if intent in RESPONSE_TEMPLATES and "error" in RESPONSE_TEMPLATES[intent]:
        template = random.choice(RESPONSE_TEMPLATES[intent]["error"])
        reply = template.format(
            location=context.get("city", "that location"),
            symbol=context.get("symbol", "that symbol")
        )
    else:
        reply = "Something went wrong. Mind trying again?"
    
    return {
        "reply": reply,
        "image": None,
        "suggestions": ["Retry", "Latest News", "Try Something Else"]
    }

def _generate_suggestions(intent: str, context: Dict[str, Any]) -> List[str]:
    """Generate contextual suggestions based on intent and context."""
    base_suggestions = SUGGESTION_TEMPLATES.get(intent, [])
    
    # Add some contextual variety
    suggestions = base_suggestions.copy()
    
    # Add location-based suggestions for weather
    if intent == "weather" and context.get("city"):
        other_cities = ["Mumbai", "Delhi", "Bangalore", "New York"]
        current_city = context.get("city")
        other_cities = [c for c in other_cities if c.lower() != current_city.lower()]
        if other_cities:
            suggestions.insert(1, f"Weather {random.choice(other_cities)}")
    
    # Add stock suggestions for market
    if intent == "market":
        popular_stocks = ["Tesla", "Apple", "Bitcoin", "Gold", "Ethereum"]
        current_symbol = context.get("symbol", "").upper()
        # Filter out current symbol
        other_stocks = [s for s in popular_stocks if s.upper() not in current_symbol]
        if other_stocks:
            suggestions.insert(1, random.choice(other_stocks))
    
    return suggestions[:4]  # Limit to 4 suggestions

def generate_followup_acknowledgment(intent: str, last_intent: Optional[str]) -> Optional[str]:
    """
    Generate a quick acknowledgment for follow-up queries.
    
    Args:
        intent: Current intent
        last_intent: Previous intent
    
    Returns:
        Acknowledgment text or None
    """
    if not last_intent:
        return None
    
    if intent == last_intent:
        return random.choice(RESPONSE_TEMPLATES["contextual_followup"]["same_intent"])
    else:
        return random.choice(RESPONSE_TEMPLATES["contextual_followup"]["different_intent"])

def format_contextual_response(base_response: str, is_followup: bool = False, entity_changed: bool = False) -> str:
    """
    Add contextual prefixes to responses based on conversation flow.
    
    Args:
        base_response: Base response text
        is_followup: Whether this is a follow-up query
        entity_changed: Whether user changed the entity (e.g., different city)
    
    Returns:
        Formatted response with appropriate prefix
    """
    if not is_followup:
        return base_response
    
    if entity_changed:
        prefixes = ["Sure!", "Got it!", "Switching to that...", "Let me check..."]
        prefix = random.choice(prefixes)
        return f"{prefix}\n\n{base_response}"
    
    return base_response
