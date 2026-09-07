import sys
from pathlib import Path

# Add project root to sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

import asyncio
from langchain_core.messages import HumanMessage, AIMessage
from app.core.mcp_client import MCPClientManager
from app.graph.workflow import build_portfolio_graph
from main import extract_message_content

async def test_multi_turn_smoke():
    print("=== Multi-turn Smoke Test Started ===")
    mcp_manager = MCPClientManager()
    await mcp_manager.initialize()

    try:
        tools = await mcp_manager.get_langchain_tools()
        agent_app = build_portfolio_graph(tools=tools)

        # Turn 1: Initial query
        turn1_query = "What stocks are in my portfolio?"
        print(f"\n[Turn 1] User: {turn1_query}")
        
        state1 = await agent_app.ainvoke({"messages": [HumanMessage(content=turn1_query)]})
        messages = list(state1["messages"])
        
        last_ai_1 = next((m for m in reversed(messages) if isinstance(m, AIMessage) and m.content), None)
        assert last_ai_1 is not None, "Turn 1 should return an AI response"
        resp1_text = extract_message_content(last_ai_1)
        print(f"[Turn 1] Advisor Response:\n{resp1_text[:200]}...")

        # Turn 2: Contextual follow-up referencing turn 1
        turn2_query = "Which one of those has the highest average buy price?"
        print(f"\n[Turn 2] User: {turn2_query}")
        
        messages.append(HumanMessage(content=turn2_query))
        state2 = await agent_app.ainvoke({"messages": messages})
        messages = list(state2["messages"])

        last_ai_2 = next((m for m in reversed(messages) if isinstance(m, AIMessage) and m.content), None)
        assert last_ai_2 is not None, "Turn 2 should return an AI response"
        resp2_text = extract_message_content(last_ai_2)
        print(f"[Turn 2] Advisor Response:\n{resp2_text}\n")

        # In data/portfolio.json: MSFT avg buy price is $405.00, which is the highest.
        assert "MSFT" in resp2_text or "Microsoft" in resp2_text or "405" in resp2_text, (
            "Response should correctly identify MSFT/Microsoft as having the highest buy price ($405.00)"
        )

        print(" Multi-turn smoke test passed successfully!")

    finally:
        await mcp_manager.close()

if __name__ == "__main__":
    asyncio.run(test_multi_turn_smoke())
