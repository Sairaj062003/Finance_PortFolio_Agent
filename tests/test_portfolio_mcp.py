import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

async def test_server():
    server_params = StdioServerParameters(
        command=sys.executable,
        args=[str(ROOT_DIR / "mcp_servers" / "portfolio" / "server.py")],
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            # List available tools
            tools_response = await session.list_tools()
            tool_names = [t.name for t in tools_response.tools]
            print(" Discovered MCP Tools:", tool_names)
            
            # Call get_summary tool
            summary_result = await session.call_tool("get_summary", {})
            print(" Tool 'get_summary' result:", summary_result.content)
            
            # Call get_holdings tool
            holdings_result = await session.call_tool("get_holdings", {"symbol": "AAPL"})
            print(" Tool 'get_holdings(AAPL)' result:", holdings_result.content)

if __name__ == "__main__":
    asyncio.run(test_server())
