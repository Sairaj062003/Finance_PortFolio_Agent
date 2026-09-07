import json
from pathlib import Path
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

DATA_FILE = Path(__file__).resolve().parent.parent.parent / "data" / "portfolio.json"

class Holding(BaseModel):
    symbol: str = Field(description="Stock ticker symbol (e.g. AAPL)")
    company_name: str = Field(description="Full legal company name")
    quantity: float = Field(description="Number of shares owned")
    average_buy_price: float = Field(description="Average price paid per share in USD")
    sector: str = Field(description="Industry sector")

class PortfolioSummary(BaseModel):
    account_id: str = Field(description="Account ID")
    currency: str = Field(description="Currency code (e.g. USD)")
    cash_balance: float = Field(description="Available cash in USD")
    total_positions: int = Field(description="Total number of unique positions")

def load_data() -> Dict[str, Any]:
    """Helper function to load and parse portfolio.json safely."""
    if not DATA_FILE.exists():
        raise FileNotFoundError(f"Portfolio file not found at: {DATA_FILE}")
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def get_portfolio_holdings(symbol: Optional[str] = None) -> List[Dict[str, Any]]:
    """Get portfolio holdings information, with optional filtering by symbol."""
    data = load_data()
    holdings = data.get("holdings", [])
    if symbol:
        symbol_upper = symbol.strip().upper()
        return [h for h in holdings if h.get("symbol", "").upper() == symbol_upper]
    return holdings

def get_portfolio_summary() -> Dict[str, Any]:
    """Get high level portfolio summary statistics."""
    data = load_data()
    holdings = data.get("holdings", [])
    return {
        "account_id": data.get("account_id", "UNKNOWN"),
        "currency": data.get("currency", "USD"),
        "cash_balance": data.get("cash_balance", 0.0),
        "total_positions": len(holdings)
    }

def get_transactions(symbol: Optional[str] = None) -> List[Dict[str, Any]]:
    """Get transaction history, optionally filtered by symbol."""
    data = load_data()
    transactions = data.get("transactions", [])
    if symbol:
        symbol_upper = symbol.strip().upper()
        return [t for t in transactions if t.get("symbol", "").upper() == symbol_upper]
    return transactions
