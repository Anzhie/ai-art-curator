from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field

class ResponseStatus(str, Enum):
    RECOMMEND = "recommend"
    CLARIFY = "clarify"
    OFF_TOPIC = "off_topic"

class ArtworkRecommendation(BaseModel):
    artwork_id: str = Field(..., description="Unique artwork ID from context")
    title: str = Field(..., description="Title of the artwork")
    why_this_artwork: str = Field(..., description="Emotional connection to user query")
    curators_note: str = Field(..., description="Art history context and story")
    what_to_notice: str = Field(..., description="Specific visual elements to observe")

class CuratorResponse(BaseModel):
    status: ResponseStatus = Field(..., description="Decision status: recommend, clarify, or off_topic")
    clarification_question: Optional[str] = Field(None, description="Question if query is ambiguous")
    guardrail_message: Optional[str] = Field(None, description="Polite response if off-topic")
    recommendations: Optional[List[ArtworkRecommendation]] = Field(default=[], description="Artwork recommendations")