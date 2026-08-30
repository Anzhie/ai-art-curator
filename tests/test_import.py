import json
import os
import requests
import pytest
from src.config import MUSEUM_ITEM_LIMIT

DATA_FILE = "data/processed/artworks.json"

@pytest.fixture
def loaded_artworks():
    """Fixture to load JSON data before tests."""
    assert os.path.exists(DATA_FILE), f"File {DATA_FILE} not found. Please run import_data.py"
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        # If the JSON is invalid, the test will fail here (json.decoder.JSONDecodeError)
        data = json.load(f) 
    return data

def test_json_is_valid_and_count_is_correct(loaded_artworks):
    """Verify successful import and dynamic artwork count."""
    assert isinstance(loaded_artworks, list), "JSON must contain a list of objects"
    
    # Calculate expected count dynamically based on the central config limit (Rijksmuseum max 1500, Uffizi - 1000)
    expected_count = int((2 * MUSEUM_ITEM_LIMIT + 1500 + 1000) * 0.6)
    
    assert len(loaded_artworks) >= expected_count, f"Expected at least {expected_count} artworks, but got {len(loaded_artworks)}"

def test_custom_fields_exist(loaded_artworks):
    """Verify the presence of custom generated fields in all objects."""
    required_fields = ["id", "themes", "emotions", "effects", "keywords", "image_url"]
    
    for item in loaded_artworks:
        for field in required_fields:
            assert field in item, f"Object {item.get('id')} is missing field '{field}'"

def test_images_are_accessible(loaded_artworks):
    """
    Verify image accessibility.
    Perform a lightweight HEAD request (without downloading the file) to keep the test fast.
    """
    # Check the first 5 artworks to avoid sending 200 requests and potentially getting banned
    sample_artworks = loaded_artworks[:5] 
    
    headers = {"User-Agent": "AIArtCuratorBot/1.0 (https://github.com/ai-art-curator)"}
    
    for item in sample_artworks:
        img_url = item["image_url"]
        try:
            # HEAD request fetches only headers, saving bandwidth
            response = requests.get(img_url, headers=headers, timeout=10, stream=True, allow_redirects=True)
            
            # Verify status code 200 (OK)
            assert response.status_code in [200, 301, 302], f"Image unreachable: {img_url} (Status: {response.status_code})"
        except requests.RequestException as e:
            pytest.fail(f"Network error checking URL {img_url}: {e}")