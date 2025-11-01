
from typing import List, Annotated, TypedDict, Dict, Any
from langchain_core.messages import BaseMessage
from langgraph.graph import add_messages
from pydantic import BaseModel, Field

class ThreadConfig(BaseModel):
    """Configuration for a conversation thread."""
    thread_id: str = Field(
        ...,
        description="The ID of the conversation thread.",
        min_length=3,
        max_length=64,
        pattern="^[a-zA-Z0-9-_]+$",
    )

class GraphState(TypedDict, total=False):
    """Represents the state of our graph."""
    messages: Annotated[List[BaseMessage], add_messages]
    metadata: Dict[str, Any]
    status: str
    resposta: str
    thread_id: str
    duration_seconds: float
    error: str
