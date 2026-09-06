from typing import TypedDict, List, Dict, Any, Optional
from src.schemas.curator_response import CuratorResponse, ResponseStatus

class AgentState(TypedDict):
    """Shared state dictionary passed between LangGraph nodes."""
    user_query: str
    history_context: str
    search_intent: Optional[str]
    status: Optional[ResponseStatus]
    clarifying_question: Optional[str]
    guardrail_message: Optional[str]
    retrieved_artworks: List[Dict[str, Any]]
    final_response: Optional[CuratorResponse]