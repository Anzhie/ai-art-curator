import os
import json
from huggingface_hub import InferenceClient

def is_art_intent(user_query: str, model_name: str) -> bool:
    """Classifies whether the user query is strictly related to art, museum curation, or artwork recommendations."""
    
    system_prompt = """
You are an Intent Classifier for an AI Art Curator. 
Your job is to determine if the user's input is valid for retrieving artwork.

Handling Short Inputs & Ambiguity:
If the user's input consists of 1-2 words that represent a broad concept (e.g., "Nature", "Love", "Sad") or is grammatically incomplete (e.g., prepositions like "About", "In"), DO NOT classify it as invalid. Instead, consider it VALID.
Exception: If the 1-2 words are specific art entities (e.g., artist names like "Van Gogh" or famous styles like "Cubism"), consider it VALID.

VALID inputs include:
1. Direct requests for art (e.g., "Show me impressionist paintings").
2. Descriptions of moods, emotions, or atmospheres (e.g., "I feel sad", "I want to see vast quiet landscapes", "nostalgic atmosphere").
3. Abstract concepts and single nouns that could represent a visual theme (e.g., "Nature", "Solitude", "Love").

INVALID (off-topic) inputs include:
1. Coding questions, math, recipes, or general knowledge (e.g., "How to bake bread", "Write a python script").
2. Harmful or inappropriate content.
3. Complete gibberish (e.g., "asdfgh").

You MUST respond STRICTLY in JSON format with a single key "is_art_related" mapping to a boolean value.
If the input is VALID, return exactly: {"is_art_related": true}
If the input is INVALID, return exactly: {"is_art_related": false}
"""

    # Retrieve the token from environment variables
    hf_token = os.environ.get("HF_TOKEN")
    
    # Initialize the Inference Client
    client = InferenceClient(
        model=model_name, 
        token=hf_token
    )

    try:
        # Requesting completion from Hugging Face Inference API
        response = client.chat_completion(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"User query: '{user_query}'"},
            ],
            max_tokens=50,      # We only need a tiny JSON response
            temperature=0.1     # Low temperature for classification stability
        )
        
        # Extract the string content
        result_text = response.choices[0].message.content
        
        # Parse the JSON
        data = json.loads(result_text)
        return data.get("is_art_related", False)
        
    except Exception as e:
        print(f"⚠️ Intent classification error: {e}")
        # Fallback to True on error so valid queries are not blocked
        return True