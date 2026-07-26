import pytest
from src.rag.curator_engine import ArtCuratorEngine
from src.schemas import CuratorResponse


def test_curator_engine_recommendation():
    """Verify that the RAG engine processes the query and outputs a valid CuratorResponse structure."""
    engine = ArtCuratorEngine()

    # Pass exact artwork titles as stored in ChromaDB
    user_query = "Show me Pietà or Nativité et Adoration des bergers"
    response = engine.generate_response(user_query)

    # Validate Pydantic response schema
    assert isinstance(response, CuratorResponse), "Response must be an instance of CuratorResponse"
    assert response.status in ["recommend", "clarify", "off_topic"], f"Unexpected status: {response.status}"

    # Verify recommendations structure for positive status
    if response.status == "recommend":
        assert isinstance(response.recommendations, list), "Recommendations field must be a list"