import ollama
from src.schemas.curator_response import CuratorResponse
from src.retrieval.retriever import ArtRetriever


class ArtCuratorEngine:
    """Core RAG engine for the AI Art Curator interface."""

    def __init__(self, model_name: str = "qwen2.5:7b"):
        self.model_name = model_name
        self.retriever = ArtRetriever()

    def generate_response(self, user_query: str) -> CuratorResponse:
        """Run the RAG pipeline: retrieve context, construct prompt, and query LLM."""
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

        response = ollama.chat(
            model=self.model_name,
            messages=[
                {'role': 'system', 'content': system_instructions},
                {'role': 'user', 'content': user_query}
            ],
            format='json'
        )
        
        return CuratorResponse.model_validate_json(response['message']['content'])