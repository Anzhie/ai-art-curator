import json
import ollama
from src.config import LLM_MODEL_NAME 
from src.schemas.curator_response import CuratorResponse

def test_ollama_json_generation():
    """Test if Ollama correctly generates structured JSON matching the CuratorResponse schema."""
    
    system_instructions = """
    You are an AI Art Curator. Respond strictly in JSON format matching this structure:
    {
      "status": "clarify",
      "clarification_question": "string",
      "guardrail_message": null,
      "recommendations": []
    }
    """
    
    user_query = 'Show me something nice'
    
    response = ollama.chat(
        model=LLM_MODEL_NAME,
        messages=[
            {'role': 'system', 'content': system_instructions},
            {'role': 'user', 'content': user_query}
        ],
        format=CuratorResponse.model_json_schema(),
        options={'keep_alive': 0}  # Release model from memory after execution
    )
    
    raw_output = response['message']['content']
    print("\n--- RAW OUTPUT FROM OLLAMA ---")
    print(raw_output)
    
    # Validate output structure using Pydantic
    parsed = CuratorResponse.model_validate_json(raw_output)
    
    assert parsed.status == "clarify"
    assert parsed.clarification_question is not None
    print("\n--- SUCCESSFULLY PARSED BY PYDANTIC ---")
    print(f"Status: {parsed.status}")
    print(f"Question: {parsed.clarification_question}")