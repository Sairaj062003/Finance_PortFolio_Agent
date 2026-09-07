import sys
from pathlib import Path

# Add project root to sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

import asyncio
from langchain_core.messages import HumanMessage
from app.core.mcp_client import MCPClientManager
from app.graph.workflow import build_portfolio_graph

async def test_agent_workflow():
    print("Initializing MCP Client Manager...")
    mcp_manager = MCPClientManager()
    await mcp_manager.initialize()

    try:
        # Get MCP tools as LangChain tools
        mcp_tools = await mcp_manager.get_langchain_tools()
        print(f"Loaded {len(mcp_tools)} MCP tools.")

        # Build LangGraph workflow
        print("Compiling LangGraph portfolio advisor agent...")
        agent_app = build_portfolio_graph(tools=mcp_tools)

        # Test query
        user_query = "What stocks do I currently hold, what is my cash balance, and what is the current market price of AAPL?"
        print(f"\nUser Query: {user_query}\n")

        # Execute workflow
        initial_state = {
            "messages": [HumanMessage(content=user_query)]
        }

        print("Executing agent graph...")
        result = await agent_app.ainvoke(initial_state)

        # Print message trail
        print("\n=== Agent Execution Trace ===")
        for idx, msg in enumerate(result["messages"]):
            role = msg.__class__.__name__
            msg_str = str(msg.content)
            content_snippet = (msg_str[:150] + "...") if len(msg_str) > 150 else msg_str
            tool_calls = getattr(msg, "tool_calls", None)
            print(f"[{idx}] {role}: {content_snippet}")
            if tool_calls:
                print(f"     -> Triggered Tool Calls: {[tc['name'] for tc in tool_calls]}")

        last_msg = result["messages"][-1]
        final_answer = last_msg.content
        if isinstance(final_answer, list):
            text_parts = [p.get("text", str(p)) if isinstance(p, dict) else str(p) for p in final_answer]
            final_answer = "\n".join(text_parts)

        print("\n=== Final Agent Response ===")
        print(final_answer)

        # Basic assertions
        assert final_answer, "Final answer should not be empty"
        assert len(result["messages"]) > 1, "Agent should have produced response messages"
        print("\n Agent graph test passed successfully!")

    finally:
        await mcp_manager.close()

if __name__ == "__main__":
    asyncio.run(test_agent_workflow())
