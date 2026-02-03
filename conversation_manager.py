# Conversation Manager
# Manages conversation state, follow-ups, and contextual understanding

from typing import Dict, Any, Optional, Tuple
from intents import detect_intent, get_intent_with_confidence, extract_city, extract_symbol, extract_topic
from context import (
    get_conversation_history, 
    get_last_intent, 
    get_entity, 
    update_entity,
    update_last_intent,
    add_to_history
)

# Keywords that indicate reference to previous context
REFERENCE_KEYWORDS = {
    "there", "that", "it", "this", "same",
    "what about", "how about", "also", "and"
}

def detect_contextual_query(query: str, user_id: str) -> Dict[str, Any]:
    """
    Detect if query references previous context and resolve it.
    
    Examples:
        - "what about Mumbai?" after "weather Delhi" -> weather intent with Mumbai
        - "how about Apple?" after "price Tesla" -> market intent with Apple
        - "and there?" after "weather Delhi" and user asking about news -> news intent (no entity carry-over)
    
    Returns:
        Dict with resolved intent, entities, and context flags
    """
    query_lower = query.lower().strip()
    
    # Get conversation history
    history = get_conversation_history(user_id, limit=3)
    last_intent = get_last_intent(user_id)
    
    # Detect current intent and confidence
    intent, confidence = get_intent_with_confidence(query)
    
    # Extract entities from current query
    entities = {
        "city": extract_city(query),
        "symbol": extract_symbol(query),
        "topic": None  # Will be extracted based on intent
    }
    
    # Extract topic if intent is news
    if intent == "news":
        entities["topic"] = extract_topic(query, intent)
    
    # Check if this is a contextual reference
    is_contextual_reference = any(keyword in query_lower for keyword in REFERENCE_KEYWORDS)
    
    # Handle "unknown" intent with contextual clues
    if intent == "unknown" and last_intent and is_contextual_reference:
        # Try to infer intent from context
        intent = _infer_intent_from_context(query_lower, last_intent, history)
        confidence = 8  # Medium confidence for inferred intent
    
    # Handle follow-up queries (same intent, different entity)
    if intent == last_intent and not entities.get("city") and not entities.get("symbol"):
        # Check if there's a new entity mentioned that we should extract
        if intent == "weather":
            # Try to extract city from ambiguous reference
            entities["city"] = _extract_entity_from_reference(query_lower, "city", user_id)
        elif intent == "market":
            # Try to extract symbol from ambiguous reference
            entities["symbol"] = _extract_entity_from_reference(query_lower, "symbol", user_id)
    
    # Use previous entities if current query doesn't have them
    if not entities.get("city") and intent == "weather":
        entities["city"] = get_entity(user_id, "city")
    
    if not entities.get("symbol") and intent == "market":
        entities["symbol"] = get_entity(user_id, "symbol")
    
    # Determine if this is a follow-up
    is_followup = len(history) > 0
    entity_changed = _check_entity_change(intent, entities, user_id)
    
    return {
        "intent": intent,
        "confidence": confidence,
        "entities": entities,
        "is_followup": is_followup,
        "entity_changed": entity_changed,
        "is_contextual_reference": is_contextual_reference
    }

def _infer_intent_from_context(query: str, last_intent: str, history: list) -> str:
    """
    Infer intent from contextual clues when primary detection fails.
    
    Examples:
        - "what about Mumbai?" after weather query -> infer weather
        - "and that?" after market query -> infer market
    """
    # Check for entity keywords in the query
    if any(word in query for word in ["mumbai", "delhi", "bangalore", "london", "tokyo", "paris"]):
        return "weather"
    
    if any(word in query for word in ["tesla", "apple", "google", "bitcoin", "stock", "price"]):
        return "market"
    
    # If query is very short and contains reference words, use last intent
    if len(query.split()) <= 3:
        return last_intent
    
    # Default to last intent for contextual references
    return last_intent

def _extract_entity_from_reference(query: str, entity_type: str, user_id: str) -> Optional[str]:
    """
    Extract entity from contextual references like "what about Mumbai?" or "there".
    """
    if entity_type == "city":
        # Try standard extraction first
        city = extract_city(query)
        if city:
            return city
        
        # Check for reference to previous city
        if any(word in query for word in ["there", "that place", "same city"]):
            return get_entity(user_id, "city")
    
    elif entity_type == "symbol":
        # Try standard extraction first
        symbol = extract_symbol(query)
        if symbol:
            return symbol
        
        # Check for reference to previous symbol
        if any(word in query for word in ["that", "same stock", "it"]):
            return get_entity(user_id, "symbol")
    
    return None

def _check_entity_change(intent: str, entities: Dict[str, Any], user_id: str) -> bool:
    """Check if the entity has changed from previous query."""
    if intent == "weather" and entities.get("city"):
        last_city = get_entity(user_id, "city")
        return last_city and last_city.lower() != entities["city"].lower()
    
    if intent == "market" and entities.get("symbol"):
        last_symbol = get_entity(user_id, "symbol")
        return last_symbol and last_symbol.upper() != entities["symbol"].upper()
    
    return False

def update_conversation_state(user_id: str, query: str, intent: str, entities: Dict[str, Any]):
    """
    Update conversation state after processing a query.
    
    Args:
        user_id: User identifier
        query: User's query
        intent: Detected intent
        entities: Extracted entities
    """
    # Update last intent
    update_last_intent(user_id, intent)
    
    # Update entities
    if entities.get("city"):
        update_entity(user_id, "city", entities["city"])
    
    if entities.get("symbol"):
        update_entity(user_id, "symbol", entities["symbol"])
    
    # Add to history
    add_to_history(user_id, query, intent, entities)

def resolve_entity_with_preferences(
    intent: str, 
    entities: Dict[str, Any], 
    user_id: str,
    preferences: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Resolve missing entities using user preferences and context.
    
    Args:
        intent: Detected intent
        entities: Current entities
        user_id: User identifier
        preferences: User preferences
    
    Returns:
        Updated entities dict
    """
    if preferences is None:
        preferences = {}
    
    # Resolve city for weather
    if intent == "weather" and not entities.get("city"):
        # Priority: context > preference > default
        entities["city"] = (
            get_entity(user_id, "city") or 
            preferences.get("default_city") or 
            "Delhi"
        )
    
    # Resolve symbol for market
    if intent == "market" and not entities.get("symbol"):
        # Priority: context > preference > default
        entities["symbol"] = (
            get_entity(user_id, "symbol") or 
            preferences.get("default_symbol") or 
            "BTC-USD"
        )
    
    return entities

def is_greeting(query: str) -> bool:
    """Check if query is a greeting."""
    query_lower = query.lower().strip()
    greetings = ["hi", "hello", "hey", "help", "start", "menu", "greetings"]
    
    # Check if query is just a greeting
    return query_lower in greetings or query_lower.startswith(tuple(greetings))

def should_clarify(intent: str, confidence: int, entities: Dict[str, Any]) -> bool:
    """
    Determine if we should ask for clarification.
    
    Args:
        intent: Detected intent
        confidence: Confidence score
        entities: Extracted entities
    
    Returns:
        True if clarification is needed
    """
    # Import here to avoid circular dependency
    from clarifier import needs_clarification
    
    return needs_clarification(intent, confidence, entities)
