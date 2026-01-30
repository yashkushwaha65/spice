from fastapi import FastAPI
from intents import detect_intent
from services.news_service import get_news
from services.weather_service import get_weather
from services.market_service import get_market
from services.trends_service import get_trends

app = FastAPI(title="Spice – Real-Time Info Bot")

@app.get("/")
def root():
    return {"status": "ok", "message": "Spice backend is running"}

@app.get("/chat")
def chat(q: str):
    intent = detect_intent(q)

    if intent == "news":
        return {"reply": get_news()}

    if intent == "weather":
        city = q.split()[-1]
        return {"reply": get_weather(city)}

    if intent == "market":
        symbol = q.split()[-1].upper()
        return {"reply": get_market(symbol)}

    if intent == "trends":
        return {"reply": get_trends()}

    return {
        "reply": "Ask me about news, weather, markets, or trends."
    }
