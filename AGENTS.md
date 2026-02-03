# AGENTS.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

Spice is a real-time information aggregation backend built with FastAPI. It provides a chat-style API that returns news, weather, stock prices, and social trends with ultra-low latency via in-memory caching.

## Commands

### Setup
```bash
pip install -r requirements.txt
```

### Run Development Server
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Production (Render)
Uses `Procfile`: `uvicorn main:app --host 0.0.0.0 --port 10000`

### Test Endpoints
```bash
curl "http://127.0.0.1:8000/chat?q=news"
curl "http://127.0.0.1:8000/chat?q=weather%20mumbai"
curl "http://127.0.0.1:8000/chat?q=price%20AAPL"
curl "http://127.0.0.1:8000/chat?q=trending"
```

## Architecture

### Request Flow
```
/chat?q=... → main.py → intents.py (detect_intent) → services/*_service.py → cache.py
```

### Key Components

**main.py** - FastAPI application entry point
- Single `/chat` endpoint that routes queries based on detected intent
- Background task (`@repeat_every(seconds=600)`) pre-warms cache for news and trends
- Intent-based routing: news, weather, market, trends

**intents.py** - Keyword-based intent detection
- Returns one of: `news`, `weather`, `market`, `trends`, `unknown`
- No ML/LLM - pure keyword matching for low latency

**cache.py** - In-memory TTL cache
- `CACHE` dict stores `(data, timestamp, ttl)` tuples
- Functions: `get_cache(key)`, `set_cache(key, data, ttl)`

**services/** - External API integrations
- `news_service.py` - GNews API (TTL: 300s)
- `weather_service.py` - OpenWeatherMap API (TTL: 600s)
- `market_service.py` - Yahoo Finance via yfinance (TTL: 120s)
- `trends_service.py` - Google Trends (pytrends) + Reddit popular (TTL: 900s)

### Caching Strategy
- Global cache pre-warmed every 10 minutes for news/trends
- Per-request cache for weather (keyed by city) and market (keyed by symbol)
- Cached responses return in ~1-5ms; fresh fetches take 500-1500ms

## Environment Variables

Required in `.env`:
- `NEWS_API_KEY` - GNews API key
- `WEATHER_API_KEY` - OpenWeatherMap API key
- `YOUTUBE_API_KEY` - YouTube API key (optional, not currently used)
- `CACHE_TTL` - Default cache TTL (default: 300)

## Adding New Intents

1. Add keywords to `intents.py` `detect_intent()` function
2. Create new service in `services/` following existing pattern (cache check → API call → format → cache set)
3. Add handler case in `main.py` `/chat` endpoint
