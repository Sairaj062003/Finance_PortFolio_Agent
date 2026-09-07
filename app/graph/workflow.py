from typing import List, Optional
from langchain_core.tools import BaseTool
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode, tools_condition

from app.graph.state import AgentState
from app.graph.nodes import create_agent_node
from app.tools.portfolio_tools import LOCAL_CALCULATION_TOOLS

def build_portfolio_graph(
    tools: List[BaseTool],
    model_name: Optional[str] = None,
    temperature: float = 0.0
):
    """
    Build and compile the LangGraph workflow with agent reasoning and tool execution cycles.
    """
    # Combine passed tools (e.g. MCP tools) with local deterministic calculation tools
    all_tools = list(tools) + list(LOCAL_CALCULATION_TOOLS)

    # Initialize graph
    workflow = StateGraph(AgentState)

    # Add agent node and prebuilt ToolNode
    agent_node = create_agent_node(all_tools, model_name=model_name, temperature=temperature)
    tool_node = ToolNode(all_tools)

    workflow.add_node("agent", agent_node)
    workflow.add_node("tools", tool_node)

    # Define edges: START -> agent
    workflow.add_edge(START, "agent")

    # Conditional edge: if agent calls tools, go to tools; otherwise finish at END
    workflow.add_conditional_edges(
        "agent",
        tools_condition,
    )

    # Loop back from tools to agent to formulate final answer or execute next tool calls
    workflow.add_edge("tools", "agent")

    # Compile the graph
    app = workflow.compile()
    return app
