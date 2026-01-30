import yfinance as yf
from cache import get_cache, set_cache

def get_market(symbol="AAPL"):
    key = f"market:{symbol}"
    cached = get_cache(key)
    if cached:
        return cached

    stock = yf.Ticker(symbol)
    price = stock.info.get("regularMarketPrice", None)

    if not price:
        return "Symbol not found."

    data = f"📈 {symbol} current price: {price}"

    set_cache(key, data, 120)
    return data
