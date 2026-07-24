import requests
import csv
import os
import time
from src.config import MUSEUM_ITEM_LIMIT

def fetch_met_masterpieces(limit: int = MUSEUM_ITEM_LIMIT):
    print("=== STARTING THE MET INGESTION PIPELINE ===")
    search_url = "https://collectionapi.metmuseum.org/public/collection/v1/search"
    
    # Query parameters to target only entries containing paintings with public images
    params = {"q": "painting", "hasImages": "true"}
    headers = {
        "User-Agent": "ArtCuratorBot/1.0 (anzhie.k@gmail.com) Python-requests"
    }
    
    try:
        print("Querying The Met search endpoint for matching artwork catalog IDs...")
        response = requests.get(search_url, params=params, headers=headers, timeout=15)
        response.raise_for_status()
        object_ids = response.json().get("objectIDs", [])
        
        # Slicing the catalog arrays dynamically using the limit parameter
        masterpiece_ids = object_ids[:limit]
        print(f"Successfully harvested IDs. Hydrating data for the top {len(masterpiece_ids)} items...")
        
        # Create output environment properly
        os.makedirs("data/raw", exist_ok=True)
        csv_file_path = "data/raw/met_data.csv"
        artworks_saved = 0
        
        with open(csv_file_path, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            # Match our uniform schema definitions
            writer.writerow(["id", "title", "artist", "year", "museum", "image_url", "description"])
            
            for idx, obj_id in enumerate(masterpiece_ids, start=1):
                object_url = f"https://collectionapi.metmuseum.org/public/collection/v1/objects/{obj_id}"
                print(f"Fetching object metadata [{idx}/{len(masterpiece_ids)}]: Met ID {obj_id}...")
                
                try:
                    # Implement retry mechanism specifically for 403 errors
                    max_retries = 3
                    request_successful = False
                    
                    for attempt in range(max_retries):
                        res = requests.get(object_url, headers=headers, timeout=10)
                        
                        # Handle specific 403 Rate Limit error with a long pause
                        if res.status_code == 403:
                            print(f"HTTP 403 on ID {obj_id}. Pausing 10s (Attempt {attempt + 1}/{max_retries})...")
                            time.sleep(10)
                            continue
                        
                        # Handle other HTTP errors (e.g., 404 Not Found)
                        if res.status_code != 200:
                            print(f"Skipping ID {obj_id}: HTTP status {res.status_code}")
                            break
                            
                        # Break the retry loop if request is successful (HTTP 200)
                        request_successful = True
                        break
                        
                    # Move to the next artwork if all retries failed or it's a hard error
                    if not request_successful or res.status_code != 200:
                        continue
                        
                    obj_data = res.json()
                    
                    # Ensure a primary high-res resource image is completely valid
                    img_url = obj_data.get("primaryImage")
                    if not img_url:
                        print(f"Skipping ID {obj_id}: Missing primary web asset resource.")
                        continue
                        
                    title = obj_data.get("title", "Untitled Masterpiece").strip()
                    artist = obj_data.get("artistDisplayName", "Unknown Artist").strip()
                    year = str(obj_data.get("objectBeginDate", ""))
                    medium = obj_data.get("medium", "Oil on canvas")
                    credit = obj_data.get("creditLine", "")
                    
                    artwork_id = f"met_{obj_id}"
                    
                    # Construct rich textual descriptions engineered for vector search embeddings
                    description = (
                        f"A beautiful masterpiece titled '{title}' created by {artist} around the year {year}. "
                        f"This artwork is a {medium} execution. Preserved in The Metropolitan Museum of Art, "
                        f"it carries immense historical weight ({credit}), presenting a profound visual narrative "
                        f"perfect for reflective, cultural, and emotionally intense moods."
                    )
                    
                    writer.writerow([artwork_id, title, artist, year, "The Met", img_url, description])
                    artworks_saved += 1
                    
                    # Stop as soon as the target limit of saved artworks is reached
                    if artworks_saved >= MUSEUM_ITEM_LIMIT:
                        break
                    
                except Exception as item_error:
                    print(f"Error compiling record for Met asset {obj_id}: {item_error}")
                
                finally:
                    # RATE LIMITING: Always executed to protect against HTTP 403 bans
                    time.sleep(0.2)
                    
        print(f"\nSUCCESS: The Met pipeline completed. {artworks_saved} masterpieces saved to {csv_file_path}")
        
    except Exception as e:
        print(f"Critical operational error inside The Met ingestion pipeline: {e}")

if __name__ == "__main__":
    fetch_met_masterpieces()