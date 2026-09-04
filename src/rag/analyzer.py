import json
from groq import Groq
from src.config import LLM_MODEL_NAME
from src.schemas.analyzer_decision import AnalyzerDecision


class QueryAnalyzer:
    def __init__(self, client: Groq, model_name: str = LLM_MODEL_NAME):
        self.client = client
        self.model_name = model_name

    def evaluate(self, query: str, history_context: str = "") -> AnalyzerDecision:
        """Evaluates user query and dialogue history for domain relevance and searchability."""

        schema_json = json.dumps(AnalyzerDecision.model_json_schema(), indent=2)

        system_prompt = f"""You are the Query Analyzer for an AI Art Curator RAG pipeline.
Your task is to classify whether the user query can be used to search an art database.

CRITERIA:
- is_off_topic: Set to true ONLY if the request is completely unrelated to visual arts, art history, museums, artists, or aesthetics.
- is_ambiguous: Set to false if the query or context contains ANY searchable detail (specific artist, artwork title, style, movement, color, or descriptive subject). Set to true ONLY for generic prompts that lack any art direction (e.g., "show me art", "something nice").

Output ONLY a JSON object strictly following this JSON schema:
{schema_json}"""

        # Format user content without injecting empty context noise
        if history_context and history_context.strip():
            user_content = f"Chat History Context: {history_context.strip()}\nCurrent User Query: {query}"
        else:
            user_content = f"Current User Query: {query}"

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content}
        ]

        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            response_format={"type": "json_object"},
            max_tokens=300,
            temperature=0.0
        )

        result_text = response.choices[0].message.content.strip()

        if result_text.startswith("```"):
            lines = result_text.splitlines()
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].startswith("`"):
                lines = lines[:-1]
            result_text = "\n".join(lines).strip()

        return AnalyzerDecision.model_validate_json(result_text)