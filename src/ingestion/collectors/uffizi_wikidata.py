import requests
import csv
import os
from src.config import MUSEUM_ITEM_LIMIT

def fetch_uffizi_masterpieces(limit: int = MUSEUM_ITEM_LIMIT):
    print("=== STARTING UFFIZI INGESTION PIPELINE ===")
    print("Connecting to the Wikidata SPARQL API...")
    url = "https://query.wikidata.org/sparql"
    
    # Broadened SPARQL query: 
    # Removed the "painting" restriction entirely. 
    # Now fetching ANY item located in or part of the Uffizi collection that has an image.
    query = f"""
    SELECT DISTINCT ?item ?title ?artistLabel ?year ?imageUrl WHERE {{
      ?item (wdt:P276|wdt:P195)/wdt:P361* wd:Q51252 ;      # Location or Collection (including sub-units)
            wdt:P18 ?imageUrl .                            # Must have a public Wikimedia image
      
      # Fetch the English title of the artwork
      OPTIONAL {{ ?item rdfs:label ?title . FILTER(LANG(?title) = "en") }}
      
      # Fetch the English name of the creator/artist
      OPTIONAL {{ 
        ?item wdt:P170 ?artist . 
        ?artist rdfs:label ?artistLabel . FILTER(LANG(?artistLabel) = "en") 
      }}
      
      # Fetch the creation or inception year
      OPTIONAL {{ 
        ?item wdt:P571 ?inception . 
        BIND(YEAR(?inception) AS ?year)
      }}
    }}
    LIMIT {limit}
    """

    # Provide a polite user agent identification for the Wikimedia API foundation
    headers = {
        "User-Agent": "ArtCuratorBot/1.0 (anzhie.k@gmail.com) Python-requests"
    }
    
    try:
        response = requests.get(url, params={'format': 'json', 'query': query}, headers=headers, timeout=30)
        response.raise_for_status()
        data = response.json()

        # Enforce slicing via the limit parameter just in case
        results = data['results']['bindings'][:limit]
        print(f"Successfully retrieved {len(results)} real artworks from Uffizi via Wikidata!")

        # Ensure the destination data directory exists properly
        os.makedirs("data/raw", exist_ok=True)
        csv_file_path = "data/raw/uffizi_data.csv"
        artworks_saved = 0
        
        with open(csv_file_path, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            # Apply the standardized schema used across our data layer
            writer.writerow(["id", "title", "artist", "year", "museum", "image_url", "description"])
            
            for idx, row in enumerate(results, start=1):
                # Extract properties with safe fallback defaults
                title = row.get('title', {}).get('value', 'Untitled Masterpiece').strip()
                artist = row.get('artistLabel', {}).get('value', 'Unknown Artist').strip()
                year = row.get('year', {}).get('value', '').strip()
                img_url = row.get('imageUrl', {}).get('value', '').strip()
                
                artwork_id = f"uffizi_{idx:03d}"

                # Generate a semantically rich English description for vector-based mood searching
                description = (
                    f"A magnificent classical artwork titled '{title}' created by {artist} around the year {year}. "
                    f"Located in the Uffizi Gallery, this piece represents unparalleled historical depth, cultural significance, "
                    f"and unique emotional resonance suitable for reflective, artistic, and historical moods."
                )
                
                writer.writerow([artwork_id, title, artist, year, "Uffizi", img_url, description])
                artworks_saved += 1
                
        print(f"SUCCESS: Uffizi pipeline completed. {artworks_saved} masterpieces saved to {csv_file_path}")
        
    except Exception as e:
        print(f"Error occurred while fetching from Wikidata API: {e}")

if __name__ == "__main__":
    fetch_uffizi_masterpieces()