import os
from groq import Groq
from src.config import LLM_MODEL_NAME
from src.utils.secrets import get_secret

def test_groq_api_json_generation():
    """Test if Groq API is reachable and generates valid JSON."""
    api_key = get_secret("GROQ_API_KEY")
    client = Groq(api_key=api_key)

    system_instructions = """
    You are an AI Art Curator. Respond strictly in valid JSON matching this schema:
    {
      "status": "clarify",
      "clarification_question": "What kind of art are you looking for?",
      "guardrail_message": null,
      "recommendations": []
    }
    """

    messages = [
        {'role': 'system', 'content': system_instructions},
        {'role': 'user', 'content': 'Show me something nice'}
    ]

    response = client.chat.completions.create(
        model=LLM_MODEL_NAME,
        messages=messages,
        response_format={"type": "json_object"},
        max_tokens=200,
        temperature=0.1
    )

    assert response.choices[0].message.content is not None