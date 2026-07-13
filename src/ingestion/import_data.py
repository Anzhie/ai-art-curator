import csv
import json
import os
from src.ingestion.schema import Artwork

def parse_tags(text: str, keyword_list: list) -> list:
    """Helper to extract tags from description text based on keywords."""
    return [word for word in keyword_list if word in text.lower()]

def build_unified_knowledge_base():
    print("=== STARTING UNIFIED KNOWLEDGE BASE IMPORT ===")
    
    # Vocabulary lists for rule-based tag generation
    available_emotions = ["serenity", "joy", "peace", "calm", "furious", "dark", "shocking", "triumphant", "intense", "powerful", "romantic"]
    available_themes = ["mythology", "classical", "renaissance", "biblical", "baroque", "history", "portrait", "nature"]
    available_effects = ["calming", "inspiring", "reflective", "energetic", "disturbing", "warm"]

    unified_artworks = []
    
    # Ingestion registry containing source files for all 4 museums
    sources = [
        {"file": "louvre_data.csv", "museum": "Louvre"},
        {"file": "uffizi_data.csv", "museum": "Uffizi"},
        {"file": "met_data.csv", "museum": "The Met"},
        {"file": "rijks_data.csv", "museum": "Rijksmuseum"}
    ]
    
    for source in sources:
        file_path = os.path.join("data/raw", source["file"])
        if not os.path.exists(file_path):
            print(f"Warning: Source file {file_path} not found. Skipping...")
            continue
            
        print(f"Importing and structuring data from {source['file']}...")
        with open(file_path, mode="r", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                # Use safe dictionary lookups in case schema layout slightly fluctuates
                desc = row.get("description", "").lower()
                
                # Extract customized semantic tags based on description context
                emotions = parse_tags(desc, available_emotions)
                themes = parse_tags(desc, available_themes)
                effects = parse_tags(desc, available_effects)
                
                # Extract normalized tokens from metadata names to act as internal keywords
                keywords = list(set(row["title"].lower().split() + row["artist"].lower().split()))
                keywords = [k.strip(",.()\"'") for k in keywords if len(k) > 3]

                try:
                    # Map row entries into a strictly validated Pydantic model instance
                    artwork = Artwork(
                        id=row["id"],
                        title=row["title"],
                        artist=row["artist"],
                        year=int(row["year"]) if row.get("year") and row["year"].isdigit() else None,
                        museum=row["museum"],
                        image_url=row["image_url"],
                        description=row.get("description", ""),
                        themes=themes if themes else ["classical"],
                        emotions=emotions if emotions else ["reflective"],
                        effects=effects if effects else ["inspiring"],
                        keywords=keywords
                    )
                    # Enforce json mode to safely convert advanced HttpUrl fields into serializable text
                    unified_artworks.append(artwork.model_dump(mode="json"))
                except Exception as e:
                    print(f"Validation error for artwork {row.get('id')}: {e}")

    # Write the formatted payload directly into the target database file
    output_path = "data/processed/artworks.json"
    with open(output_path, "w", encoding="utf-8") as out_file:
        json.dump(unified_artworks, out_file, indent=2, ensure_ascii=False)
        
    print(f"\nSUCCESS: Created unified knowledge base at {output_path}")
    print(f"Total structured artworks imported: {len(unified_artworks)}")

if __name__ == "__main__":
    build_unified_knowledge_base()