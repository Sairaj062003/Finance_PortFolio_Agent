from typing import List, Any
from langchain_core.messages import SystemMessage, BaseMessage
from langchain_core.tools import BaseTool
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import ToolNode, tools_condition

from app.core.config import settings
from app.prompts.system_prompt import FINANCIAL_ADVISOR_SYSTEM_PROMPT
from app.graph.state import AgentState

def create_agent_node(tools: List[BaseTool], model_name: str = None, temperature: float = 0.0):
    """
    Creates the agent node function that calls Gemini with tools bound.
    """
    selected_model = model_name or settings.DEFAULT_MODEL
    llm = ChatGoogleGenerativeAI(
        model=selected_model,
        google_api_key=settings.GEMINI_API_KEY,
        temperature=temperature,
        max_retries=3,
    )
    llm_with_tools = llm.bind_tools(tools)

    async def agent_node(state: AgentState) -> dict:
        messages = list(state["messages"])
        
        # Inject system prompt if not present
        if not messages or not isinstance(messages[0], SystemMessage):
            messages = [SystemMessage(content=FINANCIAL_ADVISOR_SYSTEM_PROMPT)] + messages
            
        response = await llm_with_tools.ainvoke(messages)
        return {"messages": [response]}

    return agent_node
