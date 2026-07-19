import requests
import csv
import os
import time

# Open Access catalog hub for Linked Open Data (LOD)
BASE_URL = "https://data.rijksmuseum.nl/search/collection"

def extract_linked_art_field(json_data: dict) -> dict:
    """
    Parses open Linked-Art JSON payload graphs and constructs robust metadata items.
    """
    try:
        # Extract the core identification string (e.g., from an HTTP URI or standard ID field)
        raw_uri = json_data.get("id", json_data.get("@id", ""))
        if not raw_uri:
            return None
            
        raw_id = raw_uri.split("/")[-1]
        title = json_data.get("label", "Untitled Masterpiece").strip()
        
        # Default fallbacks for open cultural heritage datasets
        artist = "Unknown Artist"
        year = ""
        
        # Construct a reliable, high-resolution direct image asset link using the museum's IIIF server open pattern
        img_url = f"https://api.rijksmuseum.nl/iiif/v2/{raw_id}/full/max/0/default.jpg"
        
        description = (
            f"A classical masterpiece titled '{title}' by {artist}. "
            f"Part of the open data collection preserved at the Rijksmuseum, Amsterdam. "
            f"This object represents pure open cultural heritage, presenting exquisite composition "
            f"and color depth ideal for serene, historical, or academic semantic searches."
        )
        
        return {
            "id": f"rijks_{raw_id}",
            "title": title,
            "artist": artist,
            "year": year,
            "museum": "Rijksmuseum",
            "image_url": img_url,
            "description": description
        }
    except Exception:
        return None

def get_rijks_masterpieces(limit: int = 50):
    """
    Orchestrates fetching only paintings from the Rijksmuseum open endpoint,
    parsing them, and writing results directly into a structured database CSV file.
    """
    print(f"Starting Ingestion: Requesting paintings from Rijksmuseum Open API...")
    params = {"type": "painting"}
    headers = {"Accept": "application/json"}
    
    try:
        response = requests.get(BASE_URL, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        ordered_items = data.get("orderedItems", [])
        print(f"Successfully located paintings. Parsing top {limit} entries...")
        
        # Enforce destination folder environment presence
        os.makedirs("data", exist_ok=True)
        csv_file_path = "data/raw/rijks_data.csv"
        artworks_saved = 0
        
        with open(csv_file_path, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            # Write standardized headers matching our data pipeline requirements
            writer.writerow(["id", "title", "artist", "year", "museum", "image_url", "description"])
            
            for count, item in enumerate(ordered_items[:limit], start=1):
                lod_id_url = item.get("id")
                if not lod_id_url:
                    continue
                    
                print(f"[{count}/{limit}] Resolving details for: {lod_id_url}")
                try:
                    detail_response = requests.get(lod_id_url, headers=headers, timeout=10)
                    detail_response.raise_for_status()
                    
                    artwork_data = extract_linked_art_field(detail_response.json())
                    
                    if artwork_data:
                        writer.writerow([
                            artwork_data["id"],
                            artwork_data["title"],
                            artwork_data["artist"],
                            artwork_data["year"],
                            artwork_data["museum"],
                            artwork_data["image_url"],
                            artwork_data["description"]
                        ])
                        artworks_saved += 1
                        
                    time.sleep(0.1)  # Smooth rate limiting buffer
                    
                except Exception as err:
                    print(f"    Skipping item due to fetch/parse error: {err}")
                    
        print(f"\nSUCCESS: Rijksmuseum open pipeline completed. {artworks_saved} masterpieces saved to {csv_file_path}")

    except Exception as e:
        print(f"Critical error executing Rijksmuseum pipeline execution: {e}")

if __name__ == "__main__":
    # Execute production data harvest for the top 50 masterpieces
    get_rijks_masterpieces(limit=50)