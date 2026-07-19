import requests
import csv
import os
import re
import time

def fetch_louvre_masterpieces():
    print("=== STARTING LOUVRE INGESTION PIPELINE ===")
    
    # EXACT URL encoded parameter: limit 100, collection 8 (artworks)
    search_base_url = "https://collections.louvre.fr/en/recherche?limit=100&collection%5B0%5D=8&page="
    headers = {
        "User-Agent": "ArtCuratorBot/1.0 (your-email@example.com) Python-requests"
    }
    
    ark_ids = set()
    # Starting from page 63
    page = 63 
    
    print("Collecting artwork ARK IDs from the Louvre collection website...")
    
    # Collect a large buffer of IDs (e.g., 200)
    while len(ark_ids) < 200 and page <= 65:
        url = f"{search_base_url}{page}"
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                # The regex strictly matches the pattern ark:/53355/cl...
                matches = re.findall(r'ark:/53355/(cl\d+)', response.text)
                for match in matches:
                    ark_ids.add(match)
                print(f"Page {page}: Successfully harvested {len(ark_ids)} unique IDs so far.")
            else:
                print(f"Failed to fetch search page {page}. Status code: {response.status_code}")
                break
        except Exception as e:
            print(f"Error occurred while fetching page {page}: {e}")
            break
        
        page += 1
        time.sleep(0.5)
        
    masterpiece_ids = list(ark_ids)
    print(f"Total unique IDs ready for API processing: {len(masterpiece_ids)}")
    
    os.makedirs("data/raw", exist_ok=True)
    csv_file_path = "data/raw/louvre_data.csv"
    artworks_saved = 0
    
    with open(csv_file_path, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["id", "title", "artist", "year", "museum", "image_url", "description"])
        
        # Iterate through the large pool of IDs
        for ark_id in masterpiece_ids:
            # Stop exactly when we successfully SAVE 50 valid artworks
            if artworks_saved >= 50:
                break
                
            json_url = f"https://collections.louvre.fr/ark:/53355/{ark_id}.json"
            
            try:
                res = requests.get(json_url, headers=headers, timeout=10)
                if res.status_code != 200:
                    continue
                    
                data = res.json()
                
                # EXTRACT IMAGE: Using the correct key "urlImage" from the JSON structure
                image_list = data.get("image", [])
                image_url = ""
                
                if isinstance(image_list, list) and len(image_list) > 0:
                    # Get high-res 'urlImage', fallback to 'urlThumbnail' if missing
                    image_url = image_list[0].get("urlImage") or image_list[0].get("urlThumbnail", "")
                
                # Skip if no valid image is found
                if not image_url:
                    print(f"Skipping {ark_id}: No image found.")
                    continue
                
                title_fr = data.get("title", "Chef-d'œuvre")
                title = title_fr.split(", dit")[0].split(" ; ")[0].strip()
                
                creator_list = data.get("creator", [])
                artist = "Unknown Artist"
                if creator_list:
                    artist = creator_list[0].get("label", "Unknown Artist").split(" (")[0].strip()
                
                date_list = data.get("dateCreated", [])
                year = ""
                if date_list:
                    year = date_list[0].get("startYear", "")
                
                # Assign ID based on the saved count, not the loop index
                artwork_id = f"louvre_{artworks_saved + 1:03d}"
                description = (
                    f"A masterpiece titled '{title}' by the legendary artist {artist}, painted around {year}. "
                    f"Preserved in the Musee du Louvre, this incredible painting is full of deep historical storytelling, "
                    f"classical European aesthetics, and profound cultural significance, making it perfect for reflective, "
                    f"intellectual, and inspiring moods."
                )
                
                writer.writerow([artwork_id, title, artist, year, "Louvre", image_url, description])
                artworks_saved += 1
                
                print(f"[{artworks_saved}/50] Successfully saved: {title}")
                time.sleep(0.3)
                
            except Exception as e:
                print(f"Error processing data for artwork {ark_id}: {e}")
                
    print(f"\nSUCCESS: Louvre pipeline completed. {artworks_saved} masterpieces saved to {csv_file_path}")

if __name__ == "__main__":
    fetch_louvre_masterpieces()