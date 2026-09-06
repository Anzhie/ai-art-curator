from unittest.mock import patch, MagicMock
import pytest
from src.graph.builder import curator_app
from src.schemas.analyzer_decision import AnalyzerDecision
from src.schemas.curator_response import CuratorResponse, ResponseStatus


def test_graph_recommendation_flow():
    """Test graph routing to recommendation branch using mocked components."""
    mock_decision = AnalyzerDecision(
        is_off_topic=False,
        is_ambiguous=False,
        reasoning="Valid art query",
        search_intent="impressionist paintings with water lilies"
    )
    
    mock_curator_response = CuratorResponse(
        status=ResponseStatus.RECOMMEND,
        recommendations=[
            {
                "artwork_id": "monet_water_lilies",
                "title": "Water Lilies",
                "why_this_artwork": "Iconic impressionist masterpiece.",
                "curators_note": "Masterpiece of light and atmosphere.",
                "what_to_notice": "Notice the brushwork."
            }
        ]
    )

    with patch("src.graph.nodes.analyzer.evaluate", return_value=mock_decision), \
         patch("src.graph.nodes.retriever.search", return_value=[{"id": "monet_water_lilies", "title": "Water Lilies"}]), \
         patch("src.graph.nodes.groq_client.chat.completions.create") as mock_groq:
        
        mock_groq.return_value.choices = [
            MagicMock(message=MagicMock(content=mock_curator_response.model_dump_json()))
        ]

        inputs = {
            "user_query": "Show me impressionist paintings with water lilies",
            "history_context": "",
            "retrieved_artworks": []
        }
        result = curator_app.invoke(inputs)
        response = result["final_response"]

        assert response is not None
        assert response.status == ResponseStatus.RECOMMEND
        assert len(response.recommendations) > 0


def test_graph_clarify_flow():
    """Test graph routing to clarify branch using mocked LLM decision."""
    mock_decision = AnalyzerDecision(
        is_off_topic=False,
        is_ambiguous=True,
        reasoning="Query is too broad",
        clarifying_question="Which era or artist do you prefer?"
    )

    with patch("src.graph.nodes.analyzer.evaluate", return_value=mock_decision):
        inputs = {
            "user_query": "show me art",
            "history_context": "",
            "retrieved_artworks": []
        }
        result = curator_app.invoke(inputs)
        response = result["final_response"]

        assert response.status == ResponseStatus.CLARIFY
        assert response.clarification_question == "Which era or artist do you prefer?"


def test_graph_off_topic_flow():
    """Test graph routing to off-topic branch via mocked LLM decision."""
    mock_decision = AnalyzerDecision(
        is_off_topic=True,
        is_ambiguous=False,
        reasoning="Technical question outside art domain"
    )

    with patch("src.graph.nodes.analyzer.evaluate", return_value=mock_decision):
        inputs = {
            "user_query": "How to write a Python script for sales forecasting?",
            "history_context": "",
            "retrieved_artworks": []
        }
        result = curator_app.invoke(inputs)
        response = result["final_response"]

        assert response.status == ResponseStatus.OFF_TOPIC
        assert response.guardrail_message is not None