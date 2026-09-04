import os
import pytest
from dotenv import load_dotenv
from groq import Groq

from src.config import LLM_MODEL_NAME
from src.rag.analyzer import QueryAnalyzer

# Load environment variables from .env file
load_dotenv()


@pytest.fixture
def analyzer():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        pytest.fail(
            "GROQ_API_KEY environment variable is not set. Please check your .env file."
        )

    client = Groq(api_key=api_key)
    return QueryAnalyzer(client=client, model_name=LLM_MODEL_NAME)


def test_analyzer_detects_off_topic(analyzer):
    """Test: The model should recognize non-art queries and set is_off_topic to True."""
    query = "How do I write a binary search algorithm in Python?"
    decision = analyzer.evaluate(query)

    print(f"\n[Off-topic Query] Reasoning: {decision.reasoning}")

    assert decision.is_off_topic is True
    assert decision.search_intent is None


def test_analyzer_detects_ambiguity(analyzer):
    """Test: The model should recognize an abstract art query and ask a clarifying question."""
    query = "Show me something interesting"
    decision = analyzer.evaluate(query)

    print(f"\n[Ambiguous Query] Reasoning: {decision.reasoning}")
    print(f"[Ambiguous Query] Question: {decision.clarifying_question}")

    assert decision.is_off_topic is False
    assert decision.is_ambiguous is True
    assert decision.clarifying_question is not None


def test_analyzer_detects_clear_intent(analyzer):
    """Test: The model should accept a specific art query and form a search intent."""
    query = "Light floral still lifes"
    decision = analyzer.evaluate(query)

    print(f"\n[Specific Query] Reasoning: {decision.reasoning}")
    print(f"[Specific Query] Intent: {decision.search_intent}")

    assert decision.is_off_topic is False
    assert decision.is_ambiguous is False
    assert decision.search_intent is not None


def test_analyzer_resolves_context_with_history(analyzer):
    """Test: The model should combine short queries with chat history to build search intent."""
    query = "green ones"
    history_context = "User asked for peaceful landscape paintings."
    decision = analyzer.evaluate(query, history_context=history_context)

    print(f"\n[Context Query] Reasoning: {decision.reasoning}")
    print(f"[Context Query] Intent: {decision.search_intent}")

    assert decision.is_off_topic is False
    assert decision.is_ambiguous is False
    assert decision.search_intent is not None