from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi_utils.tasks import repeat_every
from services.news_service import get_news, search_news
from services.weather_service import get_weather
from services.market_service import get_market
from services.trends_service import get_trends
from services.multi_search_service import get_topic_summary
from cache import set_cache, get_cache

# New intelligent modules
from conversation_manager import (
    detect_contextual_query,
    update_conversation_state,
    resolve_entity_with_preferences,
    is_greeting
)
from response_generator import generate_response
from clarifier import get_clarification_response, needs_clarification
from context import get_session_id, get_preference

app = FastAPI(title="Spice – Smart Context Bot")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- BACKGROUND ENGINE ---
@app.on_event("startup")
@repeat_every(seconds=600)
def refresh_global_cache():
    print("🔄 Background Engine: Refreshing News & Trends...")
    try:
        # These services return Dicts {"text":..., "image":...}
        set_cache("news_global", get_news(), 300)
        set_cache("trends_global", get_trends(), 900)
    except Exception as e:
        print(f"❌ Background Refresh Warning: {e}")

@app.get("/")
def root():
    return {"status": "ok", "message": "Spice Engine Active"}

@app.get("/chat")
def chat(q: str = Query(..., description="User query"), user_id: str = "default_user"):
    """
    Intelligent chat endpoint with conversation memory, clarification, and natural responses.
    
    Returns:
        {
            "reply": str,
            "image": str | None,
            "suggestions": List[str],
            "needs_clarification": bool,
            "confidence": int,
            "session_id": str
        }
    """
    try:
        q_clean = q.strip()
        
        # Get session ID
        session_id = get_session_id(user_id)
        
        # Handle greetings
        if is_greeting(q_clean):
            response = generate_response("hello", None)
            return {
                **response,
                "needs_clarification": False,
                "confidence": 100,
                "session_id": session_id
            }
        
        # Detect intent and entities with contextual understanding
        context_result = detect_contextual_query(q_clean, user_id)
        intent = context_result["intent"]
        confidence = context_result["confidence"]
        entities = context_result["entities"]
        is_followup = context_result["is_followup"]
        entity_changed = context_result["entity_changed"]
        
        # Check if clarification is needed
        if needs_clarification(intent, confidence, entities):
            clarification = get_clarification_response(q_clean, intent, confidence, entities)
            return {
                "reply": clarification["text"],
                "image": None,
                "suggestions": [opt["label"] for opt in clarification.get("options", [])],
                "needs_clarification": True,
                "confidence": confidence,
                "session_id": session_id,
                "clarification_options": clarification.get("options", [])
            }
        
        # Resolve entities with preferences
        user_prefs = {
            "default_city": get_preference(user_id, "default_city"),
            "default_symbol": get_preference(user_id, "default_symbol")
        }
        entities = resolve_entity_with_preferences(intent, entities, user_id, user_prefs)
        
        # Execute service based on intent
        service_data = None
        is_cached = False
        
        if intent == "news":
            topic = entities.get("topic")
            
            if topic:
                # Topic-based multi-source search
                cache_key = f"topic_search:{topic.lower()}"
                cached = get_cache(cache_key)
                if cached:
                    service_data = cached
                    is_cached = True
                else:
                    service_data = get_topic_summary(topic)
                    set_cache(cache_key, service_data, 300)
            else:
                # General news headlines
                cached = get_cache("news_global")
                if cached:
                    service_data = cached
                    is_cached = True
                else:
                    service_data = get_news()
                    set_cache("news_global", service_data, 300)
        
        elif intent == "weather":
            city = entities.get("city", "Delhi")
            cache_key = f"weather_{city.lower()}"
            cached = get_cache(cache_key)
            if cached:
                service_data = cached
                is_cached = True
            else:
                service_data = get_weather(city)
                set_cache(cache_key, service_data, 300)
        
        elif intent == "market":
            symbol = entities.get("symbol", "BTC-USD")
            cache_key = f"market_{symbol.upper()}"
            cached = get_cache(cache_key)
            if cached:
                service_data = cached
                is_cached = True
            else:
                service_data = get_market(symbol)
                set_cache(cache_key, service_data, 180)
        
        elif intent == "trends":
            cached = get_cache("trends_global")
            if cached:
                service_data = cached
                is_cached = True
            else:
                service_data = get_trends()
                set_cache("trends_global", service_data, 900)
        
        else:
            # Unknown intent - shouldn't happen due to clarification
            clarification = get_clarification_response(q_clean, intent, confidence, entities)
            return {
                "reply": clarification["text"],
                "image": None,
                "suggestions": [opt["label"] for opt in clarification.get("options", [])],
                "needs_clarification": True,
                "confidence": confidence,
                "session_id": session_id,
                "clarification_options": clarification.get("options", [])
            }
        
        # Generate natural response
        response = generate_response(
            intent=intent,
            data=service_data,
            is_cached=is_cached,
            is_error=False,
            context=entities
        )
        
        # Update conversation state
        update_conversation_state(user_id, q_clean, intent, entities)
        
        # Return response with metadata
        return {
            **response,
            "needs_clarification": False,
            "confidence": confidence,
            "session_id": session_id
        }
    
    except Exception as e:
        print(f"❌ Server Error: {e}")
        import traceback
        traceback.print_exc()
        
        return {
            "reply": "Something went wrong on my end. 🥶 Mind trying again?",
            "image": None,
            "suggestions": ["Retry", "Latest News", "Help"],
            "needs_clarification": False,
            "confidence": 0,
            "session_id": get_session_id(user_id)
        }
