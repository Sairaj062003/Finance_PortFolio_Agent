import pytest
from app.tools.calculations import calculate_position_metrics, calculate_portfolio_performance

def test_calculate_position_metrics_profit():
    holding = {"symbol": "AAPL", "company_name": "Apple", "quantity": 10.0, "average_buy_price": 150.0}
    quote = {"price": 200.0, "change": 5.0, "change_percent": 2.56}
    
    metrics = calculate_position_metrics(holding, quote)
    
    assert metrics["invested_value"] == 1500.0
    assert metrics["current_value"] == 2000.0
    assert metrics["unrealized_pnl"] == 500.0
    assert metrics["roi_percent"] == 33.33
    assert metrics["daily_pnl"] == 50.0

def test_calculate_position_metrics_loss():
    holding = {"symbol": "MSFT", "company_name": "Microsoft", "quantity": 5.0, "average_buy_price": 400.0}
    quote = {"price": 350.0, "change": -10.0, "change_percent": -2.78}
    
    metrics = calculate_position_metrics(holding, quote)
    
    assert metrics["invested_value"] == 2000.0
    assert metrics["current_value"] == 1750.0
    assert metrics["unrealized_pnl"] == -250.0
    assert metrics["roi_percent"] == -12.50
    assert metrics["daily_pnl"] == -50.0

def test_calculate_portfolio_performance():
    holdings = [
        {"symbol": "AAPL", "quantity": 10.0, "average_buy_price": 150.0},
        {"symbol": "MSFT", "quantity": 5.0, "average_buy_price": 400.0},
    ]
    quotes = {
        "AAPL": {"price": 200.0, "change": 5.0, "change_percent": 2.56},
        "MSFT": {"price": 400.0, "change": 0.0, "change_percent": 0.0},
    }
    
    summary = calculate_portfolio_performance(holdings, quotes, cash_balance=500.0)
    
    assert summary["total_invested"] == 3500.0  # 1500 + 2000
    assert summary["total_market_value"] == 4000.0  # 2000 + 2000
    assert summary["total_portfolio_value"] == 4500.0  # 4000 + 500 cash
    assert summary["total_unrealized_pnl"] == 500.0
    assert summary["total_roi_percent"] == 14.29
    assert summary["best_performer"] == "AAPL"
    assert summary["positions"][0]["allocation_percent"] == 50.0
    assert summary["positions"][1]["allocation_percent"] == 50.0
