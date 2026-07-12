from pydantic import BaseModel, HttpUrl, Field

class Artwork(BaseModel):
    id: str  # Unique prefixed ID, e.g., "met_123" or "louvre_456"
    title: str
    artist: str
    year: int | None = None
    museum: str  # Name of the source museum
    image_url: HttpUrl  # Strict URL validation for images
    description: str  # Main text content for semantic retrieval
    
    # Custom metadata for AI curator (defaulted to empty lists in v0.2.0)
    themes: list[str] = Field(default_factory=list)
    emotions: list[str] = Field(default_factory=list)
    effects: list[str] = Field(default_factory=list)
    keywords: list[str] = Field(default_factory=list)