import os
import sys
import json
import asyncio
from pathlib import Path
from typing import List, Dict, Any
from contextlib import AsyncExitStack

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from langchain_core.tools import StructuredTool

ROOT_DIR = Path(__file__).resolve().parent.parent.parent

class MCPClientManager:
    """Manages connections to multiple MCP servers and exposes them as LangChain tools."""

    def __init__(self):
        self.server_configs: Dict[str, StdioServerParameters] = {
            "portfolio": StdioServerParameters(
                command=sys.executable,
                args=[str(ROOT_DIR / "mcp_servers" / "portfolio" / "server.py")],
                env=dict(os.environ),
            ),
            "market_data": StdioServerParameters(
                command=sys.executable,
                args=[str(ROOT_DIR / "mcp_servers" / "market_data" / "server.py")],
                env=dict(os.environ),
            ),
        }
        self.exit_stack = AsyncExitStack()
        self.sessions: Dict[str, ClientSession] = {}

    async def initialize(self):
        """Connect to all configured MCP servers and initialize sessions."""
        for server_name, server_params in self.server_configs.items():
            read, write = await self.exit_stack.enter_async_context(
                stdio_client(server_params)
            )
            session = await self.exit_stack.enter_async_context(
                ClientSession(read, write)
            )
            await session.initialize()
            self.sessions[server_name] = session
            print(f" Connected to MCP Server: '{server_name}'")

    async def get_langchain_tools(self) -> List[StructuredTool]:
        """Discover tools from all MCP servers and convert them to LangChain StructuredTools."""
        langchain_tools: List[StructuredTool] = []

        for server_name, session in self.sessions.items():
            tools_result = await session.list_tools()
            for mcp_tool in tools_result.tools:
                tool_name = mcp_tool.name
                tool_description = mcp_tool.description or f"MCP Tool: {tool_name}"
                schema = mcp_tool.inputSchema or {}

                # Factory function to capture server_name and tool_name in closure
                def make_tool_func(s_name: str, t_name: str):
                    async def async_tool_wrapper(**kwargs) -> str:
                        res = await self.sessions[s_name].call_tool(t_name, kwargs)
                        # Extract text from content objects
                        text_outputs = [
                            c.text for c in res.content if hasattr(c, "text")
                        ]
                        return "\n".join(text_outputs) if text_outputs else str(res.content)
                    return async_tool_wrapper

                # Create LangChain StructuredTool
                lc_tool = StructuredTool(
                    name=tool_name,
                    description=f"[{server_name.upper()}] {tool_description}",
                    coroutine=make_tool_func(server_name, tool_name),
                    func=None,  # Async-only execution
                    args_schema=None,  # Schema is validated by MCP server
                )
                langchain_tools.append(lc_tool)

        return langchain_tools

    async def close(self):
        """Cleanly close all MCP connections."""
        await self.exit_stack.aclose()
