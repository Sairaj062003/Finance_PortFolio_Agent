"""
Main Application Entrypoint for the Finance Portfolio Advisor Agent.
Provides an interactive multi-turn CLI session connected to MCP servers and LangGraph.
"""

import os
import sys
from pathlib import Path

# Ensure project root is in sys.path
ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# Ensure Windows terminal handles UTF-8 characters and emojis
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

import asyncio
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from app.core.mcp_client import MCPClientManager
from app.graph.workflow import build_portfolio_graph

BANNER = r"""
===================================================================
      FINANCIAL PORTFOLIO ADVISOR AGENT (MCP + LangGraph)
===================================================================
 Type your financial questions or use quick slash commands:
   /overview       - Complete portfolio performance & allocation report
   /quote <ticker> - Fetch real-time market quote (e.g. /quote AAPL)
   /clear          - Clear conversation history
   /help           - Display available commands and tips
   /exit or /quit  - Close MCP servers and exit
===================================================================
"""

HELP_TEXT = """
Available Commands:
  /overview       - Generate a full portfolio analysis with PnL, allocations, and top/worst performers.
  /quote <symbol> - Fetch real-time price, daily change, and previous close for a stock.
  /clear          - Reset the current conversation context.
  /help           - Show this help message.
  /exit or /quit  - Terminate the application cleanly.

Example Questions:
  - "How is my portfolio performing today?"
  - "What percentage of my portfolio is invested in Technology?"
  - "What would be the impact if NVDA drops 10%?"
  - "Which position has generated the highest unrealized profit?"
"""

def extract_message_content(msg: AIMessage) -> str:
    """Extract clean string content from an AIMessage, supporting both strings and list parts."""
    content = msg.content
    if isinstance(content, list):
        parts = []
        for part in content:
            if isinstance(part, dict) and "text" in part:
                parts.append(part["text"])
            elif isinstance(part, str):
                parts.append(part)
            else:
                parts.append(str(part))
        return "\n".join(parts)
    return str(content)

async def main():
    print(BANNER)
    print(" Initializing MCP Servers (Portfolio & Market Data)...")
    mcp_manager = MCPClientManager()
    
    try:
        await mcp_manager.initialize()
        tools = await mcp_manager.get_langchain_tools()
        print(f" Connected! Loaded {len(tools)} MCP tools.")

        print(" Building LangGraph agent workflow...")
        agent_app = build_portfolio_graph(tools=tools)
        print(" Agent ready! Ask a question to get started.\n")

        # Multi-turn conversation state
        conversation_messages = []

        while True:
            try:
                user_input = input("You > ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\n\n Exiting application...")
                break

            if not user_input:
                continue

            # Command: Exit
            if user_input.lower() in ("/exit", "/quit", "exit", "quit"):
                print("\n Shutting down Financial Portfolio Agent. Goodbye!")
                break

            # Command: Help
            if user_input.lower() == "/help":
                print(HELP_TEXT)
                continue

            # Command: Clear
            if user_input.lower() == "/clear":
                conversation_messages = []
                print("\n Conversation context cleared.\n")
                continue

            # Command: Overview shortcut
            if user_input.lower() == "/overview":
                user_input = (
                    "Please provide a comprehensive portfolio performance overview including "
                    "total portfolio value, cash balance, overall unrealized P&L, a markdown table "
                    "of all current holdings with allocations, and highlights of top and lagging positions."
                )
                print(" Analyzing portfolio overview...")

            # Command: Quote shortcut
            elif user_input.lower().startswith("/quote"):
                parts = user_input.split()
                if len(parts) > 1:
                    ticker = parts[1].upper()
                    user_input = f"What is the current market price and daily change for {ticker}?"
                    print(f" Fetching quote for {ticker}...")
                else:
                    print("Usage: /quote <symbol> (e.g. /quote AAPL)")
                    continue

            # Append user message to conversation history
            conversation_messages.append(HumanMessage(content=user_input))

            print("\n Analyst thinking & querying tools...")
            try:
                # Stream or invoke workflow
                response_state = await agent_app.ainvoke({"messages": conversation_messages})
                
                # Update conversation messages with the full trail produced by the turn
                conversation_messages = list(response_state["messages"])

                # Find final AIMessage
                last_ai_msg = next(
                    (m for m in reversed(conversation_messages) if isinstance(m, AIMessage) and m.content),
                    None
                )

                if last_ai_msg:
                    formatted_response = extract_message_content(last_ai_msg)
                    print(f"\nAdvisor >\n{formatted_response}\n")
                else:
                    print("\nAdvisor > [Completed with no additional text response]\n")

            except Exception as e:
                print(f"\n Error processing request: {e}\n")

    finally:
        print(" Closing MCP server connections...")
        await mcp_manager.close()
        print(" Cleanup complete. Session terminated.")

if __name__ == "__main__":
    asyncio.run(main())
