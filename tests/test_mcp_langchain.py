import sys
from pathlib import Path

# Add project root to sys.path so 'app' is discoverable
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import asyncio
from langchain_google_genai import ChatGoogleGenerativeAI
from app.core.config import settings
from app.core.mcp_client import MCPClientManager

async def test_langchain_mcp():
    # 1. Initialize MCP Client Manager
    mcp_manager = MCPClientManager()
    await mcp_manager.initialize()

    try:
        # 2. Convert MCP tools to LangChain tools
        tools = await mcp_manager.get_langchain_tools()
        print(f"\n Discovered {len(tools)} LangChain Tools:")
        for t in tools:
            print(f"  - {t.name}: {t.description}")

        # 3. Initialize Gemini LLM with bound tools
        llm = ChatGoogleGenerativeAI(
            model=settings.DEFAULT_MODEL,
            google_api_key=settings.GEMINI_API_KEY,
            temperature=0.0
        )
        llm_with_tools = llm.bind_tools(tools)

        # 4. Test 1: Portfolio Question
        print("\n--- Test 1: Portfolio Tool Calling ---")
        prompt1 = "How many AAPL shares do I currently own in my portfolio?"
        print(f"User: {prompt1}")
        response1 = await llm_with_tools.ainvoke(prompt1)
        print(f"LLM Tool Calls Selected: {response1.tool_calls}")

        # 5. Test 2: Market Data Question
        print("\n--- Test 2: Market Data Tool Calling ---")
        prompt2 = "What is the latest market price of NVDA?"
        print(f"User: {prompt2}")
        response2 = await llm_with_tools.ainvoke(prompt2)
        print(f"LLM Tool Calls Selected: {response2.tool_calls}")

    finally:
        await mcp_manager.close()

if __name__ == "__main__":
    asyncio.run(test_langchain_mcp())
