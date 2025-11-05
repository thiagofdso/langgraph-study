"""Shared state definitions for the imagem agent refactor."""

from __future__ import annotations

from typing import Annotated, Any, Dict, List, Optional

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict


class GraphState(TypedDict, total=False):
    """LangGraph shared state for the image analysis workflow."""

    messages: Annotated[List[BaseMessage], add_messages]
    metadata: Dict[str, Any]
    image_path: str
    base64_image: Optional[str]
    llm_response: Optional[str]
    markdown_output: Optional[str]
    status: str
    error: Optional[str]
    duration_seconds: Optional[float]


STATUS_VALIDATED = "validated"
STATUS_PREPARED = "prepared"
STATUS_INVOKED = "invoked"
STATUS_FORMATTED = "formatted"
STATUS_ERROR = "error"
