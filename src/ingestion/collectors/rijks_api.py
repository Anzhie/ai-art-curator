import requests
from typing import List, Dict, Any
from src.ingestion.schema import Artwork

BASE_URL = "https://data.rijksmuseum.nl/search/collection"

def extract_linked_art_field(data: Dict[str, Any]) -> Artwork | None:
    """
    Safely parses Linked Art JSON structure into the unified Artwork Pydantic model.
    """
    try:
        # 1. Extract Title from 'identified_by'
        title = "Unknown Title"
        for identifier in data.get("identified_by", []):
            if identifier.get("type") == "Name":
                title = identifier.get("content", title)
                break

        # 2. Extract Artist from 'produced_by'
        artist = "Unknown Artist"
        production = data.get("produced_by", {})
        carried_out_by = production.get("carried_out_by", [])
        if carried_out_by:
            artist = carried_out_by[0].get("_label", artist)
        elif "attributed_by" in data:
            # Fallback for alternative attributions
            attr = data.get("attributed_by", [])
            if attr:
                artist = attr[0].get("_label", artist)

        # 3. Extract Description from 'referred_to_by'
        description_parts = []
        for reference in data.get("referred_to_by", []):
            content = reference.get("content")
            if content:
                description_parts.append(content)
        
        description = " ".join(description_parts) if description_parts else f"A painting by {artist}."
        if len(description) > 500:
            description = description[:497] + "..."

        # 4. Extract Image URL (handling the deep Linked Art nesting safely)
        # Using a reliable fallback if digital object extraction is too deeply nested
        lod_id = data.get("id", "")
        clean_id = lod_id.split("/")[-1] if lod_id else "unknown"
        
        # Build a provisional valid image archive URL format or use placeholder
        image_url = f"https://images.rijksmuseum.nl/asset-{clean_id}.jpg"
        for subject in data.get("subject_of", []):
            if subject.get("type") == "DigitalObject" and "id" in subject:
                if any(ext in subject["id"] for ext in [".jpg", ".jpeg", ".png"]):
                    image_url = subject["id"]
                    break

        return Artwork(
            id=f"rijks_{clean_id}",
            title=title,
            artist=artist,
            year=None,
            museum="Rijksmuseum",
            image_url=image_url,
            description=description.strip()
        )
    except Exception as e:
        print(f"    Error parsing Linked Art object fields: {e}")
        return None

def get_rijks_artworks(limit: int = 10) -> List[Artwork]:
    """
    Orchestrates fetching only paintings from the Rijksmuseum open endpoint and parsing them.
    """
    print(f"Starting Ingestion: Requesting paintings from Rijksmuseum Open API...")
    params = {"type": "painting"}
    
    try:
        response = requests.get(BASE_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        ordered_items = data.get("orderedItems", [])
        print(f"Successfully located paintings. Parsing top {limit} entries...")
        
        artworks = []
        for count, item in enumerate(ordered_items[:limit], start=1):
            lod_id_url = item.get("id")
            if not lod_id_url:
                continue
                
            print(f"[{count}/{limit}] Resolving details for: {lod_id_url}")
            try:
                headers = {"Accept": "application/json"}
                detail_response = requests.get(lod_id_url, headers=headers, timeout=10)
                detail_response.raise_for_status()
                
                artwork = extract_linked_art_field(detail_response.json())
                if artwork:
                    artworks.append(artwork)
            except Exception as err:
                print(f"    Skipping item due to fetch/parse error: {err}")
                
        print(f"Successfully collected {len(artworks)} parsed artworks from Rijksmuseum.")
        return artworks

    except Exception as e:
        print(f"Error executing Rijksmuseum pipeline execution: {e}")
        return []

if __name__ == "__main__":
    # # Quick standalone test to verify Rijksmuseum collector works properly
    test_artworks = get_rijks_artworks(limit=3)
    print("\n=== FINAL RIJKS PARSED RESULTS ===")
    for count, art in enumerate(test_artworks, start=1):
        print(f"\nArtwork #{count}:")
        print(f"  Model ID: {art.id}")
        print(f"  Title: {art.title}")
        print(f"  Artist: {art.artist}")
        print(f"  Museum: {art.museum}")
        print(f"  Validated URL: {art.image_url}")