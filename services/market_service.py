import yfinance as yf
from cache import get_cache, set_cache
import logging

logger = logging.getLogger("yfinance")
logger.setLevel(logging.CRITICAL)

def get_market(symbol="AAPL"):
    # Common mappings
    mappings = {
        "BITCOIN": "BTC-USD", "BTC": "BTC-USD",
        "ETHEREUM": "ETH-USD", "ETH": "ETH-USD",
        "TESLA": "TSLA",
        "APPLE": "AAPL",
        "GOOGLE": "GOOGL",
        "NIFTY": "^NSEI",
        "SENSEX": "^BSESN",
        "GOLD": "GC=F",
    }
    
    query_symbol = mappings.get(symbol, symbol)
    key = f"market:{query_symbol}"
    
    cached = get_cache(key)
    if cached:
        return cached

    try:
        ticker = yf.Ticker(query_symbol)
        hist = ticker.history(period="1d")
        
        if hist.empty:
            return {"text": f"I couldn't find market data for **{symbol}**. 📉", "image": None}
            
        price = hist['Close'].iloc[-1]
        open_price = hist['Open'].iloc[-1]
        change = ((price - open_price) / open_price) * 100
        
        icon = "📈" if change >= 0 else "📉"
        color_hex = "00FF00" if change >= 0 else "FF0000"
        
        fmt_price = f"{price:,.2f}"
        fmt_change = f"{change:+.2f}%"

        text = f"{icon} **{symbol}** Update:\n\n" \
               f"• **Price:** {fmt_price}\n" \
               f"• **Today:** {fmt_change}"

        # OPTIONAL: Generate a mini chart URL (QuickChart.io is great for this)cl
        # For now, we return None for image, or you could add a stock logo API here
        data = {"text": text, "image": None}

        set_cache(key, data, 120) 
        return data

    except Exception:
         return {"text": f"I couldn't find a price for **{symbol}**. 📉", "image": None}