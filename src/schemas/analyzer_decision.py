from typing import Optional
from pydantic import BaseModel, Field


class AnalyzerDecision(BaseModel):
    is_off_topic: bool = Field(
        description="True ONLY if query is completely unrelated to visual arts, paintings, or sculptures."
    )
    is_ambiguous: bool = Field(
        description="True ONLY if query is too vague to perform a vector search (e.g. 'show me art'). False if query has any specific title, artist, subject, or style."
    )
    reasoning: str = Field(description="Brief explanation of the decision.")
    clarifying_question: Optional[str] = Field(
        default=None, description="Question for the user if is_ambiguous is True."
    )
    search_intent: Optional[str] = Field(
        default=None, description="Optimized vector search query if is_ambiguous is False."
    )