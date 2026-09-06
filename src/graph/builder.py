from langgraph.graph import StateGraph, START, END
from src.graph.state import AgentState
from src.graph.nodes import (
    analyzer_node, 
    retrieval_node, 
    curator_node, 
    clarify_node, 
    off_topic_node
)
from src.graph.edges import route_decision

def create_curator_graph():
    """Assembles and compiles the LangGraph state machine workflow."""
    workflow = StateGraph(AgentState)

    # Register workflow nodes
    workflow.add_node("analyzer", analyzer_node)
    workflow.add_node("retrieval", retrieval_node)
    workflow.add_node("curator", curator_node)
    workflow.add_node("clarify", clarify_node)
    workflow.add_node("off_topic", off_topic_node)

    # Configure graph edges and conditional routing
    workflow.add_edge(START, "analyzer")
    workflow.add_conditional_edges("analyzer", route_decision)
    workflow.add_edge("retrieval", "curator")
    
    # Terminal transitions to END
    workflow.add_edge("curator", END)
    workflow.add_edge("clarify", END)
    workflow.add_edge("off_topic", END)

    return workflow.compile()

# Compiled graph instance ready for execution
curator_app = create_curator_graph()