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

    def generate_response(self, user_query: str) -> CuratorResponse:
        """Run the RAG pipeline: retrieve context, construct prompt, and query LLM."""
        
        # Immediate Pre-LLM Guardrail check
        is_safe, refusal_reason = check_input_safety(user_query)
        if not is_safe:
            return CuratorResponse(
                status="off_topic",
                guardrail_message="I can only discuss art and museum exhibits. Your query was flagged as invalid or prohibited.",
                recommendations=[]
            )
    
        context_artworks = self.retriever.search(query=user_query, top_k=3)
        
        system_instructions = f"""
You are an advanced AI Art Curator. Your task is to help users explore artworks based on context.
You must respond strictly in valid JSON format matching the CuratorResponse schema.

Available Context Artworks:
{context_artworks}

Rules:
1. If the user query matches or relates to the context or art appreciation, choose status "recommend" and select up to 3 artworks from the provided context.
2. If the user query is too vague, ambiguous, or lacks direction (e.g., "show me something nice"), choose status "clarify" and provide a helpful "clarification_question".
3. If the user query is completely off-topic (not related to art), choose status "off_topic" and provide a polite "guardrail_message".
"""

        # Build arguments for the Ollama call dynamically
        chat_kwargs = {
            "model": self.model_name,
            "messages": [
                {'role': 'system', 'content': system_instructions},
                {'role': 'user', 'content': user_query}
            ],
            "format":  CuratorResponse.model_json_schema()
        }
        
        # Pass keep_alive only if it is explicitly set (e.g., to 0 in testing environments)
        if self.keep_alive is not None:
            chat_kwargs["options"] = {'keep_alive': self.keep_alive}

        response = ollama.chat(**chat_kwargs)
        
        return CuratorResponse.model_validate_json(response['message']['content'])