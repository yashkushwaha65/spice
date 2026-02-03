# Enhanced conversation context with memory and session tracking
import time
from typing import Optional, Dict, List, Any
from datetime import datetime

# Structure: { 
#   "user_id": { 
#     "session_id": str,
#     "created_at": timestamp,
#     "last_active": timestamp,
#     "conversation_history": [{"query": str, "intent": str, "entities": dict, "timestamp": float}],
#     "preferences": {"default_city": str, "default_currency": str, ...},
#     "last_entities": {"city": str, "symbol": str, "topic": str},
#     "last_intent": str,
#     "context_data": {"key": "value"}
#   }
# }
_context_store = {}

# Session timeout (30 minutes)
SESSION_TIMEOUT = 1800
MAX_HISTORY_SIZE = 20

def _init_user_context(user_id: str) -> Dict[str, Any]:
    """Initialize context structure for a new user."""
    return {
        "session_id": f"{user_id}_{int(time.time())}",
        "created_at": time.time(),
        "last_active": time.time(),
        "conversation_history": [],
        "preferences": {},
        "last_entities": {},
        "last_intent": None,
        "context_data": {}
    }

def _check_session_timeout(user_id: str) -> bool:
    """Check if session has timed out and reset if needed."""
    if user_id in _context_store:
        last_active = _context_store[user_id].get("last_active", 0)
        if time.time() - last_active > SESSION_TIMEOUT:
            # Reset session but keep preferences
            prefs = _context_store[user_id].get("preferences", {})
            _context_store[user_id] = _init_user_context(user_id)
            _context_store[user_id]["preferences"] = prefs
            return True
    return False

def get_or_create_context(user_id: str) -> Dict[str, Any]:
    """Get existing context or create new one."""
    if user_id not in _context_store:
        _context_store[user_id] = _init_user_context(user_id)
    else:
        _check_session_timeout(user_id)
        _context_store[user_id]["last_active"] = time.time()
    return _context_store[user_id]

def add_to_history(user_id: str, query: str, intent: str, entities: Dict[str, Any]):
    """Add a query to conversation history."""
    context = get_or_create_context(user_id)
    
    history_entry = {
        "query": query,
        "intent": intent,
        "entities": entities,
        "timestamp": time.time()
    }
    
    context["conversation_history"].append(history_entry)
    
    # Keep only recent history
    if len(context["conversation_history"]) > MAX_HISTORY_SIZE:
        context["conversation_history"] = context["conversation_history"][-MAX_HISTORY_SIZE:]

def get_conversation_history(user_id: str, limit: int = 5) -> List[Dict[str, Any]]:
    """Get recent conversation history."""
    context = get_or_create_context(user_id)
    history = context["conversation_history"]
    return history[-limit:] if history else []

def update_last_intent(user_id: str, intent: str):
    """Update the last detected intent."""
    context = get_or_create_context(user_id)
    context["last_intent"] = intent

def get_last_intent(user_id: str) -> Optional[str]:
    """Get the last detected intent."""
    context = get_or_create_context(user_id)
    return context.get("last_intent")

def update_entity(user_id: str, entity_type: str, entity_value: str):
    """Update a specific entity (city, symbol, topic, etc.)."""
    context = get_or_create_context(user_id)
    context["last_entities"][entity_type] = entity_value

def get_entity(user_id: str, entity_type: str) -> Optional[str]:
    """Get a specific entity from context."""
    context = get_or_create_context(user_id)
    return context["last_entities"].get(entity_type)

def update_preference(user_id: str, pref_key: str, pref_value: Any):
    """Update user preferences."""
    context = get_or_create_context(user_id)
    context["preferences"][pref_key] = pref_value

def get_preference(user_id: str, pref_key: str, default: Any = None) -> Any:
    """Get user preference with optional default."""
    context = get_or_create_context(user_id)
    return context["preferences"].get(pref_key, default)

def get_session_id(user_id: str) -> str:
    """Get current session ID."""
    context = get_or_create_context(user_id)
    return context["session_id"]

# Legacy compatibility functions
def update_context(user_id: str, key: str, value: str):
    """Legacy function - stores in context_data."""
    context = get_or_create_context(user_id)
    context["context_data"][key] = value

def get_context(user_id: str, key: str) -> Optional[str]:
    """Legacy function - retrieves from context_data."""
    context = get_or_create_context(user_id)
    return context["context_data"].get(key)
