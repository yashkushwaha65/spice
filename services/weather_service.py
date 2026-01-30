import requests
from config import WEATHER_API_KEY
from cache import get_cache, set_cache

def get_weather(city="Delhi"):
    key = f"weather:{city}"
    cached = get_cache(key)
    if cached:
        return cached

    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric"
    res = requests.get(url).json()

    if res.get("cod") != 200:
        return "City not found."

    temp = res["main"]["temp"]
    desc = res["weather"][0]["description"]

    data = f"🌦️ Weather in {city}: {temp}°C, {desc}"

    set_cache(key, data, 600)
    return data
