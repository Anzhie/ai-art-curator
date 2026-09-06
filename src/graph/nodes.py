import json
from groq import Groq
from src.config import LLM_MODEL_NAME
from src.utils.secrets import get_secret
from src.schemas.curator_response import CuratorResponse, ResponseStatus
from src.graph.state import AgentState
from src.rag.analyzer import QueryAnalyzer
from src.rag.guardrails import check_input_safety
from src.retrieval.retriever import ArtRetriever

# Initialize core services globally for nodes
groq_client = Groq(api_key=get_secret("GROQ_API_KEY"))
analyzer = QueryAnalyzer(client=groq_client)
retriever = ArtRetriever()


def analyzer_node(state: AgentState) -> dict:
    """Evaluates user intent and checks safety."""
    
    # 1. Pre-LLM Injection and Safety Guardrail
    is_safe, refusal_reason = check_input_safety(state["user_query"])
    if not is_safe:
        return {
            "status": ResponseStatus.OFF_TOPIC,
            "guardrail_message": refusal_reason or "Input flagged as invalid or prohibited."
        }

    # 2. Query Analysis via LLM
    decision = analyzer.evaluate(state["user_query"], history_context=state.get("history_context", ""))
    
    if decision.is_off_topic:
        return {
            "status": ResponseStatus.OFF_TOPIC, 
            "guardrail_message": "I am an AI Art Curator. I can only assist with topics related to art, gallery collections, and museum exhibits."
        }
    if decision.is_ambiguous:
        return {
            "status": ResponseStatus.CLARIFY, 
            "clarifying_question": decision.clarifying_question
        }
    
    return {
        "status": ResponseStatus.RECOMMEND, 
        "search_intent": decision.search_intent or state["user_query"]
    }


def retrieval_node(state: AgentState) -> dict:
    """Retrieves relevant artworks from vector database based on search intent."""
    search_query = state.get("search_intent") or state["user_query"]
    artworks = retriever.search(search_query, top_k=3)
    return {"retrieved_artworks": artworks}


def curator_node(state: AgentState) -> dict:
    """Generates structured response via LLM using retrieved artwork context."""
    user_query = state["user_query"]
    search_intent = state.get("search_intent")
    context_artworks = state.get("retrieved_artworks", [])

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
    if search_intent:
        user_prompt += f" (Resolved search intent: '{search_intent}')"

    messages = [
        {'role': 'system', 'content': system_instructions},
        {'role': 'user', 'content': user_prompt}
    ]
    
    try:
        response = groq_client.chat.completions.create(
            model=LLM_MODEL_NAME,
            messages=messages,
            response_format={"type": "json_object"},
            max_tokens=1500,
            temperature=0.3,
        )

        result_text = response.choices[0].message.content.strip()
        parsed_response = CuratorResponse.model_validate_json(result_text)

    except Exception as e:
        print(f"API Error or JSON Parsing failed: {e}")
        return {
            "final_response": CuratorResponse(
                status=ResponseStatus.OFF_TOPIC,
                guardrail_message="I am having trouble connecting to my knowledge base right now. Please try again in a moment.",
                recommendations=[]
            )
        }
    # Enrich recommendations with image_url metadata
    if parsed_response.recommendations and context_artworks:
        url_map = {
            str(art["id"]): str(art.get("image_url", ""))
            for art in context_artworks
            if isinstance(art, dict) and "id" in art
        }

        for item in parsed_response.recommendations:
            if item.artwork_id in url_map:
                item.image_url = url_map[item.artwork_id]

    return {"final_response": parsed_response}


def clarify_node(state: AgentState) -> dict:
    """Handles ambiguous queries by asking a clarifying question."""
    return {
        "final_response": CuratorResponse(
            status=ResponseStatus.CLARIFY,
            clarification_question=state.get("clarifying_question", "Could you please clarify your request?"),
            recommendations=[]
        )
    }


def off_topic_node(state: AgentState) -> dict:
    """Handles off-topic or safety-flagged queries."""
    return {
        "final_response": CuratorResponse(
            status=ResponseStatus.OFF_TOPIC,
            guardrail_message=state.get("guardrail_message", "I am an AI Art Curator and can only discuss art and gallery collections."),
            recommendations=[]
        )
    }