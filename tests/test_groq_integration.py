import os
from dotenv import load_dotenv
from groq import Groq
from src.config import LLM_MODEL_NAME
from src.schemas.curator_response import CuratorResponse

load_dotenv()


def test_groq_integration_json_generation():
    """Test if Groq API is reachable and generates valid JSON conforming to CuratorResponse."""
    api_key = os.environ.get("GROQ_API_KEY")
    client = Groq(api_key=api_key)

    system_instructions = """
    You are a JSON generator. Respond strictly in valid JSON matching this schema:
    {"status": "recommend" | "clarify" | "off_topic", "guardrail_message": str|null, "clarification_question": str|null, "recommendations": []}
    """

    response = client.chat.completions.create(
        model=LLM_MODEL_NAME,
        messages=[
            {"role": "system", "content": system_instructions},
            {"role": "user", "content": "I want something artistic"}
        ],
        response_format={"type": "json_object"},
        temperature=0.1
    )

    result_text = response.choices[0].message.content.strip()

    # Strip markdown wrapper if present
    if result_text.startswith("```"):
        result_text = result_text.split("```")[1]
        if result_text.startswith("json"):
            result_text = result_text[4:].strip()

    parsed = CuratorResponse.model_validate_json(result_text)
    assert parsed.status in ["clarify", "recommend", "off_topic"]