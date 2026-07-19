import pytest
from pydantic import ValidationError
from src.ingestion.schema import Artwork

def test_artwork_structure_valid():
    """Verify successful object creation with valid data."""
    art = Artwork(
        id="test_001",
        title="Mona Lisa",
        artist="Leonardo da Vinci",
        year="1503",
        museum="Louvre",
        image_url="https://example.com/mona.jpg",
        description="A beautiful masterpiece."
    )
    
    assert art.id == "test_001"
    assert art.title == "Mona Lisa"
    # If tags (themes, emotions) are generated directly in Pydantic via @model_validator,
    # verify that they are initialized:
    assert hasattr(art, "themes")
    assert hasattr(art, "emotions")

def test_artwork_missing_required_fields():
    """Verify that the schema raises a validation error when required fields are missing."""
    with pytest.raises(ValidationError):
        # Missing the required 'title' field
        Artwork(
            id="test_002",
            artist="Leonardo da Vinci",
            museum="Louvre",
            image_url="https://example.com/mona.jpg",
            description="Missing title."
        )