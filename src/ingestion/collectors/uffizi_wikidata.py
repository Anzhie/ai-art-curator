import requests
import csv
import os

def fetch_uffizi_masterpieces():
    print("=== STARTING UFFIZI INGESTION PIPELINE ===")
    print("Connecting to the Wikidata SPARQL API...")
    url = "https://query.wikidata.org/sparql"
    
    # SPARQL query: Find items that are paintings (Q3305213) located in the Uffizi Gallery (Q51252)
    query = """
    SELECT ?item ?title ?artistLabel ?year ?imageUrl WHERE {
      ?item wdt:P31 wd:Q3305213 ;          # Instance of: painting
            wdt:P276 wd:Q51252 ;         # Location: Uffizi Gallery
            wdt:P18 ?imageUrl .          # Must have a public domain image from Wikimedia Commons
      
      # Fetch the English title of the artwork
      OPTIONAL { ?item rdfs:label ?title . FILTER(LANG(?title) = "en") }
      
      # Fetch the English name of the creator/artist
      OPTIONAL { 
        ?item wdt:P170 ?artist . 
        ?artist rdfs:label ?artistLabel . FILTER(LANG(?artistLabel) = "en") 
      }
      
      # Fetch the creation or inception year
      OPTIONAL { 
        ?item wdt:P571 ?inception . 
        BIND(YEAR(?inception) AS ?year)
      }
    }
    LIMIT 50
    """
    
    # Provide a polite user agent identification for the Wikimedia API foundation
    headers = {
        "User-Agent": "ArtCuratorBot/1.0 (your-email@example.com) Python-requests"
    }
    
    try:
        response = requests.get(url, params={'format': 'json', 'query': query}, headers=headers, timeout=15)
        response.raise_for_status()
        data = response.json()
        
        results = data['results']['bindings']
        print(f"Successfully retrieved {len(results)} real artworks from Uffizi via Wikidata!")
        
        # Ensure the destination data directory exists
        os.makedirs("data", exist_ok=True)
        csv_file_path = "data/raw/uffizi_data.csv"
        
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
                    f"A magnificent classical painting titled '{title}' created by the master {artist} around the year {year}. "
                    f"Located in the Uffizi Gallery, this artwork represents unparalleled historical depth, cultural significance, "
                    f"and unique emotional resonance suitable for reflective, artistic, and historical moods."
                )
                
                writer.writerow([artwork_id, title, artist, year, "Uffizi", img_url, description])
                
        print(f"SUCCESS: Uffizi pipeline completed. Clean data saved to {csv_file_path}")
        
    except Exception as e:
        print(f"Error occurred while fetching from Wikidata API: {e}")

if __name__ == "__main__":
    fetch_uffizi_masterpieces()