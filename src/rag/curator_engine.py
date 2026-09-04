import json
from groq import Groq
from src.config import LLM_MODEL_NAME
from src.schemas.curator_response import CuratorResponse, ResponseStatus
from src.retrieval.retriever import ArtRetriever
from src.utils.secrets import get_secret
from .guardrails import check_input_safety
from .analyzer import QueryAnalyzer


class ArtCuratorEngine:
    """Core RAG engine for the AI Art Curator interface."""

    def __init__(self, client: Groq = None, model_name: str = LLM_MODEL_NAME):
        self.model_name = model_name
        self.retriever = ArtRetriever()

        # Initialize native Groq client if not provided via DI
        self.client = client or Groq(api_key=get_secret("GROQ_API_KEY"))

        # Initialize QueryAnalyzer
        self.analyzer = QueryAnalyzer(
            client=self.client,
            model_name=self.model_name
        )

    def generate_response(self, user_query: str, history_context: str = "") -> CuratorResponse:
        """Run the RAG pipeline: Guardrails -> Analyzer -> Retrieval -> LLM Generation."""

        # 1. Pre-LLM Injection and Safety Guardrail
        is_safe, refusal_reason = check_input_safety(user_query)
        if not is_safe:
            return CuratorResponse(
                status=ResponseStatus.OFF_TOPIC,
                guardrail_message="I can only discuss art and museum exhibits. Your query was flagged as invalid or prohibited.",
                recommendations=[]
            )

        # 2. Query Analysis
        try:
            decision = self.analyzer.evaluate(user_query, history_context=history_context)
        except Exception as e:
            print(f"⚠️ Query Analyzer error: {e}")
            decision = None
        
        # 3. Branch A: Off-topic query -> Guardrail response
        if decision and decision.is_off_topic:
            print(f"🛑 ANALYZER: Query '{user_query}' flagged as non-art topic.")
            return CuratorResponse(
                status=ResponseStatus.OFF_TOPIC,
                guardrail_message="I am an AI Art Curator. I can only assist with topics related to art, gallery collections, and museum exhibits.",
                recommendations=[]
            )
        
        # 4. Branch B: Ambiguous query -> Clarification
        if decision and decision.is_ambiguous:
            return CuratorResponse(
                status=ResponseStatus.CLARIFY,
                clarification_question=decision.clarifying_question,
                recommendations=[]
            )

        # 5. Branch C: Specific query -> Retrieve context using resolved search intent
        search_query = decision.search_intent if (decision and decision.search_intent) else user_query
        context_artworks = self.retriever.search(query=search_query, top_k=6)

        # 6. Main System Prompt for Curation
        system_instructions = f"""
You are an AI Art Curator. Your EXCLUSIVE role is art curation and history.
You MUST respond STRICTLY in a single valid JSON object matching this JSON Schema:

{json.dumps(CuratorResponse.model_json_schema(), indent=2)}

Retrieved Context Artworks:
{json.dumps(context_artworks, indent=2)}

CRITICAL FIELD RULES:
1. "status": Must be one of ["recommend", "clarify", "off_topic"].
2. "artwork_id": Must EXACTLY match the "id" string from the context artwork (e.g. "rijks_200107795").
3. Do NOT wrap output in Markdown code blocks (no `json). Output raw valid JSON only.
"""

        user_prompt = f"User query: '{user_query}'"
        if decision and decision.search_intent:
            user_prompt += f" (Resolved search intent: '{decision.search_intent}')"

        messages = [
            {'role': 'system', 'content': system_instructions},
            {'role': 'user', 'content': user_prompt}
        ]
        # 7. LLM Response Generation
        try:
            # Requesting completion from Groq
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                response_format={"type": "json_object"},
                max_tokens=1500,
                temperature=0.3,
            )

            result_text = response.choices[0].message.content.strip()
            # Pydantic natively parses the JSON string into our schema
            parsed_response = CuratorResponse.model_validate_json(result_text)

        except Exception as e:
            print(f"API Error or JSON Parsing failed: {e}")
            return CuratorResponse(
                status=ResponseStatus.OFF_TOPIC,
                guardrail_message="I am having trouble connecting to my knowledge base right now. Please try again in a moment.",
                recommendations=[]
            )

        # 8. Enrich recommendations with image_url metadata
        if parsed_response.recommendations and context_artworks:
            url_map = {
                str(art["id"]): str(art.get("image_url", ""))
                for art in context_artworks
                if isinstance(art, dict) and "id" in art
            }

            for item in parsed_response.recommendations:
                if item.artwork_id in url_map:
                    item.image_url = url_map[item.artwork_id]

        return parsed_response