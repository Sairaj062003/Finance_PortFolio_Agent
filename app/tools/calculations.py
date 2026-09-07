from typing import List, Dict, Any

def calculate_position_metrics(holding: Dict[str, Any], quote: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calculate deterministic financial metrics for a single stock holding.
    """
    quantity = float(holding.get("quantity", 0.0))
    avg_buy_price = float(holding.get("average_buy_price", 0.0))
    current_price = float(quote.get("price", 0.0))
    daily_change = float(quote.get("change", 0.0))
    daily_change_pct = float(quote.get("change_percent", 0.0))

    invested_value = quantity * avg_buy_price
    current_value = quantity * current_price
    unrealized_pnl = current_value - invested_value
    roi_percent = (unrealized_pnl / invested_value * 100) if invested_value > 0 else 0.0
    daily_pnl = quantity * daily_change

    return {
        "symbol": holding.get("symbol", "").upper(),
        "company_name": holding.get("company_name", ""),
        "quantity": quantity,
        "average_buy_price": round(avg_buy_price, 2),
        "current_price": round(current_price, 2),
        "invested_value": round(invested_value, 2),
        "current_value": round(current_value, 2),
        "unrealized_pnl": round(unrealized_pnl, 2),
        "roi_percent": round(roi_percent, 2),
        "daily_pnl": round(daily_pnl, 2),
        "daily_change_percent": round(daily_change_pct, 2),
        "sector": holding.get("sector", "Other")
    }

def calculate_portfolio_performance(
    holdings: List[Dict[str, Any]],
    quotes: Dict[str, Dict[str, Any]],
    cash_balance: float = 0.0
) -> Dict[str, Any]:
    """
    Calculate comprehensive portfolio metrics across all positions including asset weights.
    """
    positions = []
    total_invested = 0.0
    total_market_value = 0.0
    total_daily_pnl = 0.0

    for h in holdings:
        sym = h.get("symbol", "").upper()
        quote = quotes.get(sym, {})
        if "error" in quote or not quote:
            pos = {
                "symbol": sym,
                "error": quote.get("error", f"Missing quote for {sym}"),
                "quantity": h.get("quantity", 0.0),
                "invested_value": h.get("quantity", 0.0) * h.get("average_buy_price", 0.0),
            }
            positions.append(pos)
            total_invested += pos["invested_value"]
            continue

        pos_metrics = calculate_position_metrics(h, quote)
        positions.append(pos_metrics)
        total_invested += pos_metrics["invested_value"]
        total_market_value += pos_metrics["current_value"]
        total_daily_pnl += pos_metrics["daily_pnl"]

    # Calculate asset allocation percentages
    for pos in positions:
        if "current_value" in pos and total_market_value > 0:
            pos["allocation_percent"] = round((pos["current_value"] / total_market_value) * 100, 2)
        else:
            pos["allocation_percent"] = 0.0

    total_unrealized_pnl = total_market_value - total_invested
    total_roi_percent = (total_unrealized_pnl / total_invested * 100) if total_invested > 0 else 0.0
    total_portfolio_value = total_market_value + cash_balance

    # Identify top & bottom performers
    valid_positions = [p for p in positions if "roi_percent" in p]
    best_performer = max(valid_positions, key=lambda x: x["roi_percent"]) if valid_positions else None
    worst_performer = min(valid_positions, key=lambda x: x["roi_percent"]) if valid_positions else None

    return {
        "cash_balance": round(cash_balance, 2),
        "total_invested": round(total_invested, 2),
        "total_market_value": round(total_market_value, 2),
        "total_portfolio_value": round(total_portfolio_value, 2),
        "total_unrealized_pnl": round(total_unrealized_pnl, 2),
        "total_roi_percent": round(total_roi_percent, 2),
        "total_daily_pnl": round(total_daily_pnl, 2),
        "positions_count": len(positions),
        "best_performer": best_performer["symbol"] if best_performer else None,
        "worst_performer": worst_performer["symbol"] if worst_performer else None,
        "positions": positions,
    }
