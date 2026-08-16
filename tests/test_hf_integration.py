import os
from dotenv import load_dotenv
from huggingface_hub import InferenceClient
from src.config import LLM_MODEL_NAME
from src.schemas.curator_response import CuratorResponse

load_dotenv()


def test_hf_inference_api_json_generation():
    """Test if Hugging Face Inference API is reachable and generates valid JSON."""
    hf_token = os.environ.get("HF_TOKEN")
    client = InferenceClient(model=LLM_MODEL_NAME, token=hf_token)

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

    response = client.chat_completion(
        messages=messages,
        max_tokens=200,
        temperature=0.1
    )

    result_text = response.choices[0].message.content.strip()
    
    # Strip markdown if wrapped
    if result_text.startswith("```"):
        result_text = result_text.split("```")[1]
        if result_text.startswith("json"):
            result_text = result_text[4:].strip()

    parsed = CuratorResponse.model_validate_json(result_text)
    assert parsed.status in ["clarify", "recommend", "off_topic"]