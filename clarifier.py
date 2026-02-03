# Progressive Clarification Module
# Handles ambiguous queries and generates clarification questions

import random
from typing import List, Dict, Optional, Any
from intents import calculate_intent_scores, CONFIDENCE_THRESHOLD

# Confidence thresholds
HIGH_CONFIDENCE = 15
MEDIUM_CONFIDENCE = 8
LOW_CONFIDENCE = CONFIDENCE_THRESHOLD

# Clarification templates for different ambiguity types
CLARIFICATION_TEMPLATES = {
    "ambiguous_intent": [
        "I'm not quite sure what you're looking for. Are you interested in {options}?",
        "Could you clarify? Would you like {options}?",
        "I found a few possibilities. Did you mean {options}?",
        "Not sure I got that right. Are you asking about {options}?",
    ],
    "missing_entity": [
        "Which {entity_type} are you interested in?",
        "Could you specify which {entity_type}?",
        "I'd love to help! Which {entity_type} should I look up?",
        "Sure thing! Which {entity_type} would you like to know about?",
    ],
    "ambiguous_entity": [
        "Did you mean {options}?",
        "I found multiple matches. Are you looking for {options}?",
        "Could you be more specific? Did you mean {options}?",
    ]
}

def needs_clarification(intent: str, confidence: int, entities: Dict[str, Any]) -> bool:
    """
    Determine if a query needs clarification.
    
    Args:
        intent: Detected intent
        confidence: Confidence score
        entities: Extracted entities
    
    Returns:
        True if clarification is needed
    """
    # Unknown intent always needs clarification
    if intent == "unknown" or confidence < LOW_CONFIDENCE:
        return True
    
    # Medium confidence might need clarification
    if confidence < MEDIUM_CONFIDENCE:
        return True
    
    # Check for required entities based on intent
    if intent == "weather" and not entities.get("city"):
        return False  # Will use default/preference
    
    if intent == "market" and not entities.get("symbol"):
        return False  # Will use default/preference
    
    return False

def generate_clarification(
    query: str, 
    intent: str, 
    confidence: int, 
    entities: Dict[str, Any],
    scores: Optional[Dict[str, int]] = None
) -> Dict[str, Any]:
    """
    Generate a clarification question and options.
    
    Args:
        query: Original user query
        intent: Detected intent
        confidence: Confidence score
        entities: Extracted entities
        scores: Intent scores (optional)
    
    Returns:
        Dict with clarification text and suggested options
    """
    if scores is None:
        from intents import calculate_intent_scores, normalize_input
        scores = calculate_intent_scores(normalize_input(query))
    
    # Case 1: Completely unknown or very low confidence
    if intent == "unknown" or confidence < LOW_CONFIDENCE:
        return _generate_intent_clarification(scores)
    
    # Case 2: Medium confidence - multiple possible intents
    if confidence < MEDIUM_CONFIDENCE:
        return _generate_ambiguous_intent_clarification(intent, scores)
    
    # Case 3: Missing required entity
    if intent == "weather" and not entities.get("city"):
        return _generate_entity_clarification("weather", "city")
    
    if intent == "market" and not entities.get("symbol"):
        return _generate_entity_clarification("market", "symbol")
    
    # Default: no clarification needed
    return {
        "needs_clarification": False,
        "text": None,
        "options": []
    }

def _generate_intent_clarification(scores: Dict[str, int]) -> Dict[str, Any]:
    """Generate clarification when intent is completely unknown."""
    # Filter out hello and unknown intents
    valid_intents = {k: v for k, v in scores.items() if k not in ["hello", "unknown"] and v > 0}
    
    if not valid_intents:
        # Truly unknown - suggest all main features
        options = [
            {"label": "Latest News 📰", "action": "news"},
            {"label": "Weather Forecast 🌦️", "action": "weather"},
            {"label": "Market Prices 📈", "action": "market"},
            {"label": "Trending Topics 🔥", "action": "trends"},
        ]
        text = random.choice([
            "I'm here to help! What would you like to know?",
            "I can help with news, weather, markets, or trends. What interests you?",
            "Not sure what you're looking for. Try asking about news, weather, stocks, or what's trending!",
            "I didn't quite get that. Would you like news, weather updates, market info, or trending topics?",
        ])
    else:
        # Has some signals - suggest top intents
        top_intents = sorted(valid_intents.items(), key=lambda x: x[1], reverse=True)[:3]
        
        intent_labels = {
            "news": "News 📰",
            "weather": "Weather 🌦️",
            "market": "Stock Prices 📈",
            "trends": "Trending Topics 🔥"
        }
        
        options = [
            {"label": intent_labels.get(intent, intent.title()), "action": intent}
            for intent, _ in top_intents
        ]
        
        option_text = " or ".join([opt["label"] for opt in options])
        template = random.choice(CLARIFICATION_TEMPLATES["ambiguous_intent"])
        text = template.format(options=option_text)
    
    return {
        "needs_clarification": True,
        "text": text,
        "options": options
    }

def _generate_ambiguous_intent_clarification(primary_intent: str, scores: Dict[str, int]) -> Dict[str, Any]:
    """Generate clarification when there are multiple likely intents."""
    # Get top 2-3 intents
    sorted_intents = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    top_intents = [i for i, s in sorted_intents if s >= LOW_CONFIDENCE][:3]
    
    if len(top_intents) <= 1:
        return {"needs_clarification": False, "text": None, "options": []}
    
    intent_labels = {
        "news": "Latest News 📰",
        "weather": "Weather Forecast 🌦️",
        "market": "Stock/Crypto Prices 📈",
        "trends": "What's Trending 🔥"
    }
    
    options = [
        {"label": intent_labels.get(intent, intent.title()), "action": intent}
        for intent in top_intents
    ]
    
    option_text = " or ".join([opt["label"] for opt in options])
    template = random.choice(CLARIFICATION_TEMPLATES["ambiguous_intent"])
    text = template.format(options=option_text)
    
    return {
        "needs_clarification": True,
        "text": text,
        "options": options
    }

def _generate_entity_clarification(intent: str, entity_type: str) -> Dict[str, Any]:
    """Generate clarification for missing entities."""
    entity_suggestions = {
        "city": [
            {"label": "Delhi", "action": "weather delhi"},
            {"label": "Mumbai", "action": "weather mumbai"},
            {"label": "Bangalore", "action": "weather bangalore"},
            {"label": "New York", "action": "weather new york"},
        ],
        "symbol": [
            {"label": "Bitcoin (BTC)", "action": "market btc"},
            {"label": "Apple (AAPL)", "action": "market aapl"},
            {"label": "Tesla (TSLA)", "action": "market tsla"},
            {"label": "Gold", "action": "market gold"},
        ]
    }
    
    template = random.choice(CLARIFICATION_TEMPLATES["missing_entity"])
    text = template.format(entity_type=entity_type)
    
    return {
        "needs_clarification": True,
        "text": text,
        "options": entity_suggestions.get(entity_type, [])
    }

def get_clarification_response(query: str, intent: str, confidence: int, entities: Dict[str, Any]) -> Dict[str, Any]:
    """
    Main entry point for clarification.
    
    Returns:
        Complete response dict with needs_clarification, text, and options
    """
    from intents import calculate_intent_scores, normalize_input
    scores = calculate_intent_scores(normalize_input(query))
    
    return generate_clarification(query, intent, confidence, entities, scores)
