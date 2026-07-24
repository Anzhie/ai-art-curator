import requests
import csv
import os
import time
import re
from src.config import MUSEUM_ITEM_LIMIT

# Starting point - Open LOD API (no API key required)
BASE_URL = "https://data.rijksmuseum.nl/search/collection?type=painting&material=oil%20paint"

def get_rijks_masterpieces(limit: int = MUSEUM_ITEM_LIMIT):
    print(f"=== STARTING RIJKSMUSEUM KEYLESS (MICRIO) INGESTION ===")
    print(f"Target limit set to: {limit} artworks.")
    
    headers = {
        "Accept": "application/ld+json",
        "User-Agent": "ArtCuratorBot/1.0"
    }
    
    os.makedirs("data/raw", exist_ok=True)
    csv_file_path = "data/raw/rijks_data.csv"
    
    saved_count = 0
    items_checked = 0
    current_url = BASE_URL
    
    with open(csv_file_path, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["id", "title", "artist", "year", "museum", "image_url", "description"])
        
        # Continue looping as long as there is a next page AND the limit is not reached
        while current_url and saved_count < limit:
            print(f"\nFetching LOD API page... Current saved count: {saved_count}/{limit}")
            try:
                response = requests.get(current_url, headers=headers, timeout=15)
                response.raise_for_status()
                data = response.json()
            except Exception as e:
                print(f"Failed to fetch API page: {e}")
                break
                
            ordered_items = data.get("orderedItems", [])
            if not ordered_items:
                print("No more items found in the API response.")
                break
                
            for item in ordered_items:
                # Hard stop as soon as we collect the required number of successful records
                if saved_count >= limit:
                    break
                    
                lod_url = item.get("id")
                if not lod_url:
                    continue
                    
                raw_id = lod_url.split("/")[-1]
                items_checked += 1
                print(f"[{items_checked}] Extracting data for ID: {raw_id}")
                
                try:
                    # Request HTML from the LOD URL. The server redirects to the artwork's webpage
                    html_resp = requests.get(
                        lod_url, 
                        headers={"Accept": "text/html", "User-Agent": "Mozilla/5.0"}, 
                        timeout=15
                    )
                    html_content = html_resp.text

                    # Search for the Micrio ID in the page source (e.g., "micrioId":"ApPZn")
                    micrio_code = None

                    # Attempt A: Look for a direct IIIF link
                    m1 = re.search(r'iiif\.micr\.io/([A-Za-z0-9]+)', html_content)
                    if m1:
                        micrio_code = m1.group(1)
                    else:
                        # Attempt B: Look for attributes like micrio-id="ApPZn" or "micrioId":"ApPZn"
                        m2 = re.search(r'micrio[-a-zA-Z]*["\']?\s*[:=]\s*["\']([A-Za-z0-9]{5,6})["\']', html_content, re.IGNORECASE)
                        if m2:
                            micrio_code = m2.group(1)

                    # Extract Title and Artist from SEO tags (og:title)
                    title = "Untitled Masterpiece"
                    artist = "Unknown Artist"
                    title_match = re.search(r'<meta property="og:title" content="([^"]+)"', html_content)
                    if title_match:
                        # Split strings like "The Night Watch, Rembrandt van Rijn, 1642"
                        full_title = title_match.group(1)
                        parts = [p.strip() for p in full_title.split(",")]
                        title = parts[0]
                        if len(parts) > 1:
                            artist = parts[1]

                    # Construct the final image URL
                    if micrio_code:
                        img_url = f"https://iiif.micr.io/{micrio_code}/full/max/0/default.jpg"
                        print(f"    -> Success: Found Micrio Code [{micrio_code}]")
                    else:
                        # Fallback: If no Micrio code, use the standard og:image
                        img_match = re.search(r'<meta property="og:image" content="([^"]+)"', html_content)
                        img_url = img_match.group(1) if img_match else ""
                        print("    -> Micrio code not found. Using standard image fallback.")
                        
                    if not img_url:
                        print("    -> Skipping: No image found.")
                        continue
                        
                    description = f"Masterpiece '{title}' by {artist}. Preserved at the Rijksmuseum, Amsterdam."

                    # Year is sometimes the 3rd part of the title; leave blank for schema stability
                    writer.writerow([
                        f"rijks_{raw_id}",
                        title,
                        artist,
                        "", 
                        "Rijksmuseum",
                        img_url,
                        description
                    ])
                    saved_count += 1

                    # Polite delay since we are downloading full HTML pages
                    time.sleep(0.5)
                    
                except Exception as err:
                    print(f"    -> Skipping item due to error: {err}")
            
            # If the limit is reached inside the for loop, break the outer while loop too
            if saved_count >= limit:
                break
                
            # Look for the next page link (Pagination)
            next_page = data.get("next")
            
            # Different LOD APIs might return 'next' as a string (URL) or as an object {"id": "URL"}
            if isinstance(next_page, str):
                current_url = next_page
            elif isinstance(next_page, dict):
                current_url = next_page.get("id")
            elif "view" in data and "next" in data["view"]:
                # Fallback for certain JSON-LD standards
                current_url = data["view"]["next"] if isinstance(data["view"]["next"], str) else data["view"]["next"].get("id")
            else:
                print("No next page token found. Pagination complete.")
                current_url = None

    print(f"\nSUCCESS: Pipeline completed! {saved_count} masterpieces saved to {csv_file_path}")

if __name__ == "__main__":
    get_rijks_masterpieces()