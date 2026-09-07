import json
from typing import List, Dict, Any, Union
from langchain_core.tools import tool
from app.tools.calculations import (
    calculate_position_metrics as calc_position,
    calculate_portfolio_performance as calc_portfolio
)

@tool
def calculate_position_metrics(holding: Union[str, Dict[str, Any]], quote: Union[str, Dict[str, Any]]) -> str:
    """
    Calculate deterministic financial metrics (invested value, current value, unrealized PnL, ROI%, daily PnL)
    for a single stock position given the holding details and current market quote.
    Both 'holding' and 'quote' can be passed as dicts or JSON strings.
    """
    if isinstance(holding, str):
        try:
            holding = json.loads(holding)
        except Exception:
            return json.dumps({"error": "Invalid JSON format for holding"})
            
    if isinstance(quote, str):
        try:
            quote = json.loads(quote)
        except Exception:
            return json.dumps({"error": "Invalid JSON format for quote"})

    result = calc_position(holding, quote)
    return json.dumps(result, indent=2)

@tool
def calculate_portfolio_performance(
    holdings: Union[str, List[Dict[str, Any]]],
    quotes: Union[str, Dict[str, Dict[str, Any]]],
    cash_balance: float = 0.0
) -> str:
    """
    Calculate aggregate portfolio performance metrics across all holdings and quotes.
    Computes total invested value, current market value, total portfolio value (including cash),
    overall unrealized PnL, total ROI%, asset allocation percentages per stock, and identifies
    top and worst performing assets.
    Inputs can be passed as structured lists/dicts or valid JSON strings.
    """
    if isinstance(holdings, str):
        try:
            holdings = json.loads(holdings)
        except Exception:
            return json.dumps({"error": "Invalid JSON format for holdings"})
            
    if isinstance(quotes, str):
        try:
            quotes = json.loads(quotes)
        except Exception:
            return json.dumps({"error": "Invalid JSON format for quotes"})

    result = calc_portfolio(holdings, quotes, float(cash_balance))
    return json.dumps(result, indent=2)

LOCAL_CALCULATION_TOOLS = [
    calculate_position_metrics,
    calculate_portfolio_performance
]
