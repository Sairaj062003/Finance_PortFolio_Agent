import sys
from pathlib import Path
from typing import List, Dict, Any, Optional

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from mcp.server.fastmcp import FastMCP
from mcp_servers.market_data.tools import (
    get_current_price,
    get_batch_prices,
    get_historical_prices,
)

mcp = FastMCP("MarketDataServer")

@mcp.tool()
def get_stock_price(symbol: str) -> Dict[str, Any]:
    """
    Retrieve current real-time or latest market price and daily change for a single stock ticker.
    
    Args:
        symbol: Stock ticker symbol (e.g. 'AAPL', 'MSFT', 'GOOGL', 'NVDA').
    
    Returns:
        Dictionary containing symbol, price, currency, previous_close, change, and change_percent.
    """
    return get_current_price(symbol)

@mcp.tool()
def get_multiple_stock_prices(symbols: List[str]) -> Dict[str, Any]:
    """
    Retrieve current market prices for a list of stock tickers in batch.
    
    Args:
        symbols: List of stock ticker symbols (e.g. ['AAPL', 'MSFT', 'NVDA']).
    
    Returns:
        Dictionary mapping each ticker symbol to its quote dictionary.
    """
    return get_batch_prices(symbols)

@mcp.tool()
def get_stock_history(symbol: str, period: str = "1mo") -> List[Dict[str, Any]]:
    """
    Retrieve historical daily OHLCV price bars for a stock ticker over a given timeframe.
    
    Args:
        symbol: Stock ticker symbol (e.g. 'AAPL').
        period: Time period. Options: '5d', '1mo', '3mo', '6mo', '1y', 'ytd'. Default is '1mo'.
    
    Returns:
        List of daily price bars containing date, open, high, low, close, volume.
    """
    return get_historical_prices(symbol=symbol, period=period)

if __name__ == "__main__":
    mcp.run(transport="stdio")

