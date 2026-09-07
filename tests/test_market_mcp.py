import asyncio
import os
import sys
from pathlib import Path
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

ROOT_DIR = Path(__file__).resolve().parent.parent

async def test_server():
    server_params = StdioServerParameters(
        command=sys.executable,
        args=[str(ROOT_DIR / "mcp_servers" / "market_data" / "server.py")],
        env=dict(os.environ),
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            # 1. List tools
            tools_response = await session.list_tools()
            tool_names = [t.name for t in tools_response.tools]
            print(" Discovered Market MCP Tools:", tool_names)
            
            # 2. Call single quote tool
            quote_result = await session.call_tool("get_stock_price", {"symbol": "AAPL"})
            print(" Tool 'get_stock_price(AAPL)':", quote_result.content)

            # 3. Call batch quote tool
            batch_result = await session.call_tool("get_multiple_stock_prices", {"symbols": ["AAPL", "NVDA"]})
            print(" Tool 'get_multiple_stock_prices':", batch_result.content)

if __name__ == "__main__":
    asyncio.run(test_server())
