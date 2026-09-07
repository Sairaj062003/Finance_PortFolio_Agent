import sys
from pathlib import Path
from typing import Optional, List, Dict, Any


ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


from mcp.server.fastmcp import FastMCP

from mcp_servers.portfolio.tools import (
    get_portfolio_holdings,
    get_portfolio_summary,
    get_transactions
)
mcp = FastMCP("PortfolioServer")

@mcp.tool()
def get_holdings(symbol: Optional[str] = None) -> List[Dict[str, Any]]:
    return get_portfolio_holdings(symbol)

@mcp.tool()
def get_summary() -> Dict[str, Any]:
    return get_portfolio_summary()

@mcp.tool()
def  get_transaction_history(symbol: Optional[str] = None) -> List[Dict[str, Any]]:
    return get_transactions(symbol)

if __name__ == "__main__":
    mcp.run(transport="stdio")
