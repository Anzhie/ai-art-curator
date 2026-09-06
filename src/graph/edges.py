from src.graph.state import AgentState
from src.schemas.curator_response import ResponseStatus

def route_decision(state: AgentState) -> str:
    """Conditional edge selector evaluating execution branch after analyzer node."""
    if state["status"] == ResponseStatus.OFF_TOPIC:
        return "off_topic"
    if state["status"] == ResponseStatus.CLARIFY:
        return "clarify"
    return "retrieval"