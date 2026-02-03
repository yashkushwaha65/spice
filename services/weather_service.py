import requests
from config import WEATHER_API_KEY
from cache import get_cache, set_cache

def get_weather(city="Delhi"):
    # Normalize city
    city = city.title()
    key = f"weather:{city}"
    
    cached = get_cache(key)
    if cached:
        return cached

    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric"
    res = requests.get(url).json()

    if str(res.get("cod")) != "200":
        return {
            "text": f"I couldn't find weather data for **{city}**. 😕\n\nTry checking the spelling?",
            "image": None
        }

    temp = int(res["main"]["temp"]) # Round to integer
    desc = res["weather"][0]["description"].capitalize()
    humidity = res["main"]["humidity"]
    icon_code = res["weather"][0]["icon"]
    
    # Construct Image URL (High res)
    image_url = f"https://openweathermap.org/img/wn/{icon_code}@4x.png"
    
    # Friendly formatting
    text = f"Here is the weather for **{city}** 🌤️\n\n" \
           f"• **Temp:** {temp}°C\n" \
           f"• **Condition:** {desc}\n" \
           f"• **Humidity:** {humidity}%"

    data = {"text": text, "image": image_url}
    
    set_cache(key, data, 600)
    return data