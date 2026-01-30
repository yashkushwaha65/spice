# config.py

import os
from dotenv import load_dotenv

# load .env file
load_dotenv()

# ==============================
# API KEYS
# ==============================

NEWS_API_KEY = os.getenv("NEWS_API_KEY")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

# ==============================
# CACHE
# ==============================

CACHE_TTL = int(os.getenv("CACHE_TTL", 300))

# ==============================
# SERVER
# ==============================

HOST = os.getenv("HOST", "127.0.0.1")
PORT = int(os.getenv("PORT", 8000))

# ==============================
# ENV
# ==============================

ENV = os.getenv("ENV", "development")
DEBUG = os.getenv("DEBUG", "true").lower() == "true"
