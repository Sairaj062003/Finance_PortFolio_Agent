from typing import List, Dict, Any, Optional
import yfinance as yf
from pydantic import BaseModel, Field

class StockQuote(BaseModel):
    symbol: str = Field(description="Stock ticker symbol")
    price: float = Field(description="Current / latest market price")
    currency: str = Field(default="USD", description="Price currency")
    previous_close: float = Field(description="Previous trading day closing price")
    change: float = Field(description="Absolute price change today")
    change_percent: float = Field(description="Percentage price change today")

class HistoricalBar(BaseModel):
    date: str = Field(description="Date in YYYY-MM-DD format")
    open: float
    high: float
    low: float
    close: float
    volume: int

def get_current_price(symbol: str) -> Dict[str, Any]:
    """Fetch live price and daily change for a single stock ticker."""
    symbol_upper = symbol.strip().upper()
    try:
        stock = yf.Ticker(symbol_upper)
        
        info = stock.fast_info
        
        # Access attributes safely
        price = getattr(info, "last_price", None)
        previous_close = getattr(info, "previous_close", None)
        currency = getattr(info, "currency", "USD")

        # Fallback to history if fast_info attributes are None
        if price is None or previous_close is None:
            hist = stock.history(period="2d")
            if hist.empty:
                return {"error": f"No market data found for ticker '{symbol_upper}'"}
            price = float(hist["Close"].iloc[-1])
            previous_close = float(hist["Close"].iloc[-2]) if len(hist) > 1 else price

        change = price - previous_close
        change_percent = (change / previous_close * 100) if previous_close else 0.0

        return {
            "symbol": symbol_upper,
            "price": round(float(price), 2),
            "currency": currency,
            "previous_close": round(float(previous_close), 2),
            "change": round(float(change), 2),
            "change_percent": round(float(change_percent), 2)
        }
    except Exception as e:
        return {"error": f"Failed to fetch market quote for '{symbol_upper}': {str(e)}"}

def get_batch_prices(symbols: List[str]) -> Dict[str, Any]:
    """Fetch current prices for a list of stock tickers."""
    results = {}
    for sym in symbols:
        clean_sym = sym.strip().upper()
        results[clean_sym] = get_current_price(clean_sym)
    return results

def get_historical_prices(symbol: str, period: str = "1mo") -> List[Dict[str, Any]]:
    """
    Fetch historical daily OHLCV prices for a stock.
    Valid periods: 5d, 1mo, 3mo, 6mo, 1y, ytd
    """
    symbol_upper = symbol.strip().upper()
    try:
        stock = yf.Ticker(symbol_upper)
        history = stock.history(period=period)
        
        if history.empty:
            return [{"error": f"No historical data found for '{symbol_upper}'"}]

        result = []
        for date, row in history.iterrows():
            result.append({
                "date": date.strftime("%Y-%m-%d"),
                "open": round(float(row["Open"]), 2),
                "high": round(float(row["High"]), 2),
                "low": round(float(row["Low"]), 2),
                "close": round(float(row["Close"]), 2),
                "volume": int(row["Volume"])
            })
        return result
    except Exception as e:
        return [{"error": f"Failed to fetch history for '{symbol_upper}': {str(e)}"}]
