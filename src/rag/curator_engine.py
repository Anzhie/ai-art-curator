import ollama
from src.config import LLM_MODEL_NAME 
from src.schemas.curator_response import CuratorResponse
from src.retrieval.retriever import ArtRetriever
from .guardrails import check_input_safety


class ArtCuratorEngine:
    """Core RAG engine for the AI Art Curator interface."""

    # Add keep_alive parameter, defaulting to None (uses Ollama's default behavior)
    def __init__(self, model_name: str = LLM_MODEL_NAME, keep_alive: int | None = None):
        self.model_name = model_name
        self.retriever = ArtRetriever()
        self.keep_alive = keep_alive

    import ollama
from src.config import LLM_MODEL_NAME 
from src.schemas.curator_response import CuratorResponse
from src.retrieval.retriever import ArtRetriever
from .guardrails import check_input_safety
from .intent_router import is_art_intent  # <-- IMPORT INTENT ROUTER


class ArtCuratorEngine:
    """Core RAG engine for the AI Art Curator interface."""

    def __init__(self, model_name: str = LLM_MODEL_NAME, keep_alive: int | None = None):
        self.model_name = model_name
        self.retriever = ArtRetriever()
        self.keep_alive = keep_alive

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
        context_artworks = self.retriever.search(query=user_query, top_k=3)

        # 4. Main System Prompt for LLM Curation
        system_instructions = f"""
You are an AI Art Curator. Your EXCLUSIVE role is art curation and history.
You MUST respond strictly in valid JSON matching CuratorResponse schema.

Retrieved Context Artworks:
{context_artworks}

Rules:
1. If the user query is vague about art, set status to "clarify" with a "clarification_question".
2. If the user query matches art context, set status to "recommend" with matching recommendations.
"""

        chat_kwargs = {
            "model": self.model_name,
            "messages": [
                {'role': 'system', 'content': system_instructions},
                {'role': 'user', 'content': user_query}
            ],
            "format": CuratorResponse.model_json_schema()
        }
        
        if self.keep_alive is not None:
            chat_kwargs["options"] = {'keep_alive': self.keep_alive}

        response = ollama.chat(**chat_kwargs)
        
        parsed_response = CuratorResponse.model_validate_json(response['message']['content'])

        # Enrich recommendations with image_url from retrieved context metadata
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