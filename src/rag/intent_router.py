import json
import ollama


def is_art_intent(user_query: str, model_name: str) -> bool:
    """Classifies whether the user query is strictly related to art, museum curation, or artwork recommendations."""
    system_prompt = """
You are an Intent Classifier for an AI Art Curator. 
Your job is to determine if the user's input is valid for retrieving artwork.

Handling Short Inputs & Ambiguity:
If the user's input consists of 1-2 words that represent a broad concept (e.g., "Nature", "Love", "Sad") or is grammatically incomplete (e.g., prepositions like "About", "In"), DO NOT classify it as "off_topic". Instead, return status: "clarify".
Exception: If the 1-2 words are specific art entities (e.g., artist names like "Van Gogh" or famous styles like "Cubism"), return status: "search".

VALID inputs include:
1. Direct requests for art (e.g., "Show me impressionist paintings").
2. Descriptions of moods, emotions, or atmospheres (e.g., "I feel sad", "I want to see vast quiet landscapes", "nostalgic atmosphere").
3. Abstract concepts and single nouns that could represent a visual theme (e.g., "Nature", "Solitude", "Love").

INVALID (off-topic) inputs include:
1. Coding questions, math, recipes, or general knowledge (e.g., "How to bake bread", "Write a python script").
2. Harmful or inappropriate content.

If the input is VALID, return status: "search".
If the input is INVALID, return status: "off_topic".
If the input is complete gibberish (e.g., "asdfgh"), return status: "clarify".
"""

    try:
        response = ollama.chat(
            model=model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"User query: '{user_query}'"},
            ],
            format={
                "type": "object",
                "properties": {"is_art_related": {"type": "boolean"}},
                "required": ["is_art_related"],
            },
        )
        data = json.loads(response["message"]["content"])
        return data.get("is_art_related", False)
    except Exception as e:
        print(f"⚠️ Intent classification error: {e}")
        # Fallback to True on error so valid queries are not blocked
        return True