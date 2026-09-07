from typing import Annotated, Sequence, TypedDict
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

class AgentState(TypedDict):
    """
    State schema for the Financial Portfolio Advisor LangGraph workflow.
    """
    messages: Annotated[Sequence[BaseMessage], add_messages]
