# 🚀 Real-Time Info Bot Backend

### ⚡ FastAPI • News • Weather • Markets • Trends • Ultra-Fast Cache

<p align="center">
  <img src="https://img.shields.io/badge/FastAPI-0.110+-green?style=for-the-badge&logo=fastapi"/>
  <img src="https://img.shields.io/badge/Flutter-Frontend-blue?style=for-the-badge&logo=flutter"/>
  <img src="https://img.shields.io/badge/Render-Deployed-black?style=for-the-badge&logo=render"/>
  <img src="https://img.shields.io/badge/License-MIT-purple?style=for-the-badge"/>
</p>

---

## 🌍 About This Project

**Real-Time Info Bot** is a high-performance backend service that aggregates:

📰 Breaking News  
🌦️ Live Weather  
📈 Stock/Market Prices  
🔥 Social & Internet Trends  

and delivers them instantly through a **chat-style API**.

Built using **FastAPI + smart caching + background refresh**, designed for:

✅ ultra-low latency  
✅ minimal API usage  
✅ free-tier friendly  
✅ scalable cloud deployment  

---

## 🎬 Demo Preview

> Flutter App → Chat → Instant replies

```
User: latest news
Bot : 📰 Top News:
      - Headline 1
      - Headline 2
      - Headline 3

User: weather delhi
Bot : 🌦️ 28°C clear sky

User: trending today
Bot : 🔥 Google + Reddit + YouTube trends
```

---

# ✨ Features

## ⚡ Performance

- 🔥 In-memory cache (1–5 ms response)
- 🔁 Background auto-refresh
- 🚀 Async FastAPI endpoints

## 📡 Live Data Sources

- 📰 GNews / NewsAPI
- 🌦️ OpenWeatherMap
- 📈 Yahoo Finance (yfinance)
- 🔍 Google Trends (pytrends)
- 👥 Reddit popular feed
- ▶️ YouTube Trending (optional)

## 💬 Chat-based API

Single endpoint:

```
/chat?q=your question
```

Examples:

```
/chat?q=latest news
/chat?q=weather mumbai
/chat?q=price bitcoin
/chat?q=what is trending
```

## ☁️ Cloud Ready

- Deploy on Render
- Works from anywhere
- No localhost issues
- HTTPS enabled

---

# 🧠 Architecture

```
Flutter/Web App
      ↓
FastAPI Server
      ↓
Intent Router
      ↓
┌────────────┬────────────┬────────────┬────────────┐
│ News       │ Weather    │ Market     │ Trends     │
└────────────┴────────────┴────────────┴────────────┘
      ↓
⚡ In-Memory Cache
```

---

# 🛠 Tech Stack

| Layer      | Technology                   |
|------------|------------------------------|
| Backend    | FastAPI                      |
| Language   | Python 3.11                  |
| Cache      | In-Memory / Redis ready      |
| APIs       | GNews, OpenWeather, Yahoo Finance |
| Deployment | Render                       |
| Frontend   | Flutter                      |

---

# 🚀 Getting Started (Local)

## 1️⃣ Clone

```bash
git clone https://github.com/yourusername/realtime-info-bot-backend
cd backend
```

## 2️⃣ Install

```bash
pip install -r requirements.txt
```

## 3️⃣ Setup Environment

Create `.env`

```env
NEWS_API_KEY=your_key
WEATHER_API_KEY=your_key
YOUTUBE_API_KEY=your_key
CACHE_TTL=300
```

## 4️⃣ Run

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Open:

```
http://127.0.0.1:8000/chat?q=news
```

---

# ☁️ Deploy on Render

1. Push to GitHub
2. Go → [Render](https://render.com)
3. Create Web Service
4. Add env variables
5. Deploy

Then use:

```
https://yourapp.onrender.com/chat?q=news
```

---

# 📊 Performance

| Type         | Response Time |
|--------------|---------------|
| Cached       | ⚡ 1–5 ms     |
| Fresh fetch  | 500–1500 ms   |

---

# 📂 Project Structure

```
backend/
├── main.py              # FastAPI app entry point
├── routes/
│   ├── chat.py          # Chat endpoint
│   └── health.py        # Health check
├── services/
│   ├── news.py          # News aggregation
│   ├── weather.py       # Weather service
│   ├── market.py        # Stock/crypto prices
│   └── trends.py        # Google/Reddit trends
├── utils/
│   ├── cache.py         # Caching logic
│   └── intent.py        # Intent detection
├── requirements.txt     # Dependencies
├── .env.example         # Environment template
└── README.md            # This file
```

---

# 🔑 API Endpoints

## Chat Endpoint

**GET** `/chat?q={query}`

**Parameters:**
- `q` (string, required): User query

**Response:**

```json
{
  "response": "📰 Top news headlines...",
  "cached": true,
  "timestamp": "2026-01-30T10:30:00Z"
}
```

## Health Check

**GET** `/health`

**Response:**

```json
{
  "status": "healthy",
  "cache_size": 42,
  "uptime": "3h 25m"
}
```

---

# 🧪 Example Queries

| Query                     | Response Type    |
|---------------------------|------------------|
| `latest news`             | Top headlines    |
| `weather new york`        | Current weather  |
| `price tesla`             | Stock price      |
| `bitcoin`                 | Crypto price     |
| `trending`                | Google trends    |
| `what's hot on reddit`    | Reddit popular   |

---

# 🎯 Key Features for Resume

- ⚡ **High Performance**: Sub-5ms cached responses using in-memory storage
- 🔄 **Smart Caching**: Background refresh prevents API rate limits
- 🌐 **Multi-Source Aggregation**: News, weather, finance, and social trends in one API
- 🚀 **Cloud-Native**: Production-ready deployment on Render with zero-config HTTPS
- 🎨 **Intent Detection**: NLP-based query routing for natural language understanding
- 📊 **Scalable Architecture**: Async FastAPI with Redis-ready cache layer

---

# 🔒 Security

- ✅ Environment variables for API keys
- ✅ CORS configured for Flutter app
- ✅ Rate limiting ready
- ✅ HTTPS on production
- ✅ No sensitive data in logs

---

# 🤝 Contributing

Contributions welcome! Please:

1. Fork the repo
2. Create a feature branch (`git checkout -b feature/amazing`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing`)
5. Open a Pull Request

---

# 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

# 👨‍💻 Author

**Your Name**

- GitHub: [@yourusername](https://github.com/kalkidevs)
- LinkedIn: [Your Profile](https://linkedin.com/in/kalkidevs)
- Portfolio: [yourwebsite.com](https://developeryash.vercel.app)

---

# 🙏 Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) - Modern web framework
- [GNews](https://gnews.io/) - News API
- [OpenWeatherMap](https://openweathermap.org/) - Weather data
- [Yahoo Finance](https://github.com/ranaroussi/yfinance) - Market data
- [Render](https://render.com/) - Cloud hosting

---

<p align="center">
  Made with ❤️ for real-time information access
</p>

<p align="center">
  ⭐ Star this repo if you found it helpful!
</p>