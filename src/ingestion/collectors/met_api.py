import requests
from typing import List, Dict, Any
from src.ingestion.schema import Artwork

BASE_URL = "https://collectionapi.metmuseum.org/public/collection/v1"
EUROPEAN_PAINTINGS_DEPT = 11

def fetch_met_artwork_ids(limit: int = 10) -> List[int]:
    """
    Fetches a list of artwork IDs from the European Paintings department that have images.
    """
    search_url = f"{BASE_URL}/search"
    params = {
        "departmentId": EUROPEAN_PAINTINGS_DEPT,
        "hasImages": "true",
        "q": "painting"  # General query to get a broad selection of paintings
    }
    
    try:
        response = requests.get(search_url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        object_ids = data.get("objectIDs", [])
        return object_ids[:limit]
    except requests.RequestException as e:
        print(f"Error fetching IDs from The Met: {e}")
        return []

def fetch_met_artwork_details(object_id: int) -> Artwork | None:
    """
    Fetches detailed information for a specific object ID and maps it to the Artwork schema.
    """
    object_url = f"{BASE_URL}/objects/{object_id}"
    
    try:
        response = requests.get(object_url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # Verify required fields and public domain image availability
        if not data.get("primaryImageSmall") or not data.get("title"):
            return None
            
        # Construct description from available metadata fields
        medium = data.get("medium", "Unknown medium")
        culture = data.get("culture", "Unknown culture")
        credit = data.get("creditLine", "")
        description = f"A {medium} painting. {culture}. {credit}"
        
        return Artwork(
            id=f"met_{object_id}",
            title=data.get("title"),
            artist=data.get("artistDisplayName") or "Unknown Artist",
            year=data.get("objectBeginDate"),
            museum="The Metropolitan Museum of Art",
            image_url=data.get("primaryImageSmall"),
            description=description.strip()
        )
    except requests.RequestException as e:
        print(f"Error fetching object {object_id} details from The Met: {e}")
        return None
    except Exception as e:
        print(f"Error parsing object {object_id}: {e}")
        return None

def get_met_artworks(limit: int = 10) -> List[Artwork]:
    """
    Orchestrates fetching and parsing of The Met artworks.
    """
    print(f"Starting Ingestion: Fetching top {limit} artwork IDs from The Met...")
    ids = fetch_met_artwork_ids(limit=limit)
    
    artworks = []
    for count, obj_id in enumerate(ids, start=1):
        print(f"[{count}/{len(ids)}] Processing Met object ID: {obj_id}")
        artwork = fetch_met_artwork_details(obj_id)
        if artwork:
            artworks.append(artwork)
            
    print(f"Successfully collected {len(artworks)} artworks from The Met.")
    return artworks


if __name__ == "__main__":
    # Quick standalone test to verify The Met collector works properly
    try:
        # Fetch a small batch of 3 artworks for testing
        test_artworks = get_met_artworks(limit=3)
        
        print("\n=== TEST RESULTS ===")
        for count, art in enumerate(test_artworks, start=1):
            print(f"\nArtwork #{count}:")
            print(f"  ID: {art.id}")
            print(f"  Title: {art.title}")
            print(f"  Artist: {art.artist}")
            print(f"  Museum: {art.museum}")
            print(f"  Image URL: {art.image_url}")
            print(f"  Description Snippet: {art.description[:60]}...")
            
    except Exception as e:
        print(f"\n[ERROR] Test execution failed: {e}")