import os
import json
from groq import Groq
from src.config import LLM_MODEL_NAME 
from src.schemas.curator_response import CuratorResponse
from src.retrieval.retriever import ArtRetriever
from src.utils.secrets import get_secret
from .guardrails import check_input_safety
from .intent_router import is_art_intent


class ArtCuratorEngine:
    """Core RAG engine for the AI Art Curator interface."""

    def __init__(self, model_name: str = LLM_MODEL_NAME):
        self.model_name = model_name
        self.retriever = ArtRetriever()
        
        # Retrieve the token from environment variables
        api_key = get_secret("GROQ_API_KEY")
        
        # Initialize the Inference Client
        self.client = Groq(api_key=api_key)

    def generate_response(self, user_query: str) -> CuratorResponse:
        """Run the RAG pipeline: check safety -> check intent -> retrieve context -> query LLM."""
        
        # 1. Pre-LLM Injection and Safety Guardrail
        is_safe, refusal_reason = check_input_safety(user_query)
        if not is_safe:
            return CuratorResponse(
                status="off_topic",
                guardrail_message="I can only discuss art and museum exhibits. Your query was flagged as invalid or prohibited.",
                recommendations=[]
            )
    
        # 2. Fast Intent Routing (Check domain relevance before vector search)
        if not is_art_intent(user_query, self.model_name):
            print(f"🛑 INTENT ROUTER: Query '{user_query}' flagged as non-art topic.")
            return CuratorResponse(
                status="off_topic",
                guardrail_message="I am an AI Art Curator. I can only assist with topics related to art, gallery collections, and museum exhibits.",
                recommendations=[]
            )

        # 3. Retrieve Context from Vector DB (Only reached if query is art-related)
        context_artworks = self.retriever.search(query=user_query, top_k=6)

        # 4. Main System Prompt for LLM Curation with Explicit Schema
        system_instructions = f"""
You are an AI Art Curator. Your EXCLUSIVE role is art curation and history.
You MUST respond STRICTLY in a single valid JSON object matching this schema:

{{
  "status": "recommend",
  "clarification_question": null,
  "guardrail_message": null,
  "recommendations": [
    {{
      "artwork_id": "Exact ID string from the artwork context (e.g. 'rijks_200107795')",
      "title": "Title of the artwork",
      "why_this_artwork": "Why this artwork matches the user's query and emotion",
      "curators_note": "Historical background and artistic context",
      "what_to_notice": "Key visual elements for the user to observe"
    }}
  ]
}}

Retrieved Context Artworks:
{context_artworks}

Rules:
1. Map the artwork's id field from the context directly into artwork_id.
2. Do NOT nest raw artwork context objects into recommendations. Use the exact field names specified in the JSON schema above.
3. If the query is vague, set status to "clarify" with a "clarification_question".
4. If recommending artworks, set status to "recommend" and populate "recommendations".
Return ONLY raw valid JSON, without any Markdown formatting or backticks.
"""
        # 5. Cloud LLM Generation Call
        messages = [
            {'role': 'system', 'content': system_instructions},
            {'role': 'user', 'content': user_query}
        ]
        
        try:
            # Requesting completion from Groq
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                response_format={"type": "json_object"},
                max_tokens=1500,
                temperature=0.3,
            )
            
            # Extract the string content from the response
            result_text = response.choices[0].message.content.strip()

            # Strip markdown code blocks if the LLM wraps response in
            if result_text.startswith("```"):
                result_text = result_text.split("```")[1]
                if result_text.startswith("json"):
                    result_text = result_text[4:].strip()
            
            # Pydantic natively parses the JSON string into our schema
            parsed_response = CuratorResponse.model_validate_json(result_text)
            
        except Exception as e:
            print(f"API Error or JSON Parsing failed: {e}")
            # Fallback response if the cloud API fails or returns invalid JSON
            return CuratorResponse(
                status="off_topic",
                guardrail_message="I am having trouble connecting to my knowledge base right now. Please try again in a moment.",
                recommendations=[]
            )

        # 6. Enrich recommendations with image_url from retrieved context metadata
        if parsed_response.recommendations and context_artworks:
            url_map = {}
            for art in context_artworks:
                meta = art.metadata if hasattr(art, "metadata") else (art if isinstance(art, dict) else getattr(art, "dict", {}))
                art_id = meta.get("id") or meta.get("artwork_id")
                img_url = meta.get("image_url")
                if art_id and img_url:
                    url_map[str(art_id)] = str(img_url)

            for item in parsed_response.recommendations:
                if item.artwork_id in url_map:
                    item.image_url = url_map[item.artwork_id]

        return parsed_response