import requests
import csv
import os
import re
import time

def fetch_louvre_masterpieces():
    print("=== STARTING LOUVRE INGESTION PIPELINE ===")
    
    # Base URL for the HTML search page filtered by collection 1 (Paintings / Peintures)
    search_base_url = "https://collections.louvre.fr/en/recherche?collection[]=1&page="
    headers = {
        "User-Agent": "ArtCuratorBot/1.0 (your-email@example.com) Python-requests"
    }
    
    ark_ids = set()
    page = 1
    
    # Step 1: Dynamically collect unique ARK IDs from search result pages until we reach 50
    print("Collecting artwork ARK IDs from the Louvre collection website...")
    while len(ark_ids) < 50 and page <= 5:
        url = f"{search_base_url}{page}"
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                # Extract all ARK IDs matching the patterns found in HTML links
                matches = re.findall(r'ark:/53355/(cl\d+)', response.text)
                for match in matches:
                    ark_ids.add(match)
                    if len(ark_ids) >= 50:
                        break
                print(f"Page {page}: Successfully harvested {len(ark_ids)} unique IDs so far.")
            else:
                print(f"Failed to fetch search page {page}. Status code: {response.status_code}")
                break
        except Exception as e:
            print(f"Error occurred while fetching page {page}: {e}")
            break
        
        page += 1
        time.sleep(0.5) # Polite delay between requests to avoid server blocking
        
    masterpiece_ids = list(ark_ids)[:50]
    print(f"Total unique IDs ready for API processing: {len(masterpiece_ids)}")
    
    # Step 2: Fetch metadata and official free image URLs via individual JSON endpoints
    os.makedirs("data", exist_ok=True)
    csv_file_path = "data/raw/louvre_data.csv"
    artworks_saved = 0
    
    with open(csv_file_path, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        # Standardized schema across our database layer
        writer.writerow(["id", "title", "artist", "year", "museum", "image_url", "description"])
        
        for idx, ark_id in enumerate(masterpiece_ids, start=1):
            json_url = f"https://collections.louvre.fr/ark:/53355/{ark_id}.json"
            print(f"Processing artwork [{idx}/50]: {ark_id}...")
            
            try:
                res = requests.get(json_url, headers=headers, timeout=10)
                if res.status_code != 200:
                    print(f"Skipping {ark_id}: Received HTTP status {res.status_code}")
                    continue
                    
                data = res.json()
                
                # Extract and clean up the title (base data is in French)
                title_fr = data.get("title", "Chef-d'œuvre")
                title = title_fr.split(", dit")[0].split(" ; ")[0].strip()
                
                # Extract and clean up the artist name
                creator_list = data.get("creator", [])
                artist = "Unknown Artist"
                if creator_list:
                    artist = creator_list[0].get("label", "Unknown Artist").split(" (")[0].strip()
                
                # Extract the creation year
                date_list = data.get("dateCreated", [])
                year = ""
                if date_list:
                    year = date_list[0].get("startYear", "")
                
                # Extract the high-resolution public domain image URL
                media_list = data.get("media", [])
                image_url = ""
                if media_list and "high" in media_list[0]:
                    image_url = media_list[0]["high"].get("url", "")
                elif media_list and "thumbnail" in media_list[0]:
                    image_url = media_list[0]["thumbnail"].get("url", "")
                
                # Default fallback image if media is unavailable
                if not image_url:
                    image_url = "https://collections.louvre.fr/assets/images/design/logo-louvre.png"
                
                # Generate a rich description for vector-based semantic mood search
                artwork_id = f"louvre_{idx:03d}"
                description = (
                    f"A masterpiece titled '{title}' by the legendary artist {artist}, painted around {year}. "
                    f"Preserved in the Musee du Louvre, this incredible painting is full of deep historical storytelling, "
                    f"classical European aesthetics, and profound cultural significance, making it perfect for reflective, "
                    f"intellectual, and inspiring moods."
                )
                
                writer.writerow([artwork_id, title, artist, year, "Louvre", image_url, description])
                artworks_saved += 1
                
                time.sleep(0.3) # Polite delay between API hits
                
            except Exception as e:
                print(f"Error processing data for artwork {ark_id}: {e}")
                
    print(f"\nSUCCESS: Louvre pipeline completed. {artworks_saved} masterpieces saved to {csv_file_path}")

if __name__ == "__main__":
    fetch_louvre_masterpieces()