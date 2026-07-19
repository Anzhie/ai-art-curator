from src.ingestion.collectors.louvre_official import fetch_louvre_masterpieces
from src.ingestion.collectors.met_api import fetch_met_masterpieces
from src.ingestion.collectors.rijks_api import get_rijks_masterpieces
from src.ingestion.collectors.uffizi_wikidata import fetch_uffizi_masterpieces
from import_data import build_unified_knowledge_base

def run_pipeline(limit: int = 50):
    """
    Orchestrates the entire ingestion workflow, enforcing a uniform download 
    limit across all museum collectors.
    """
    print(f"=== STARTING INTEGRATED MASTER INGESTION PIPELINE (Target Limit: {limit} per museum) ===")
    
    # 1.1 Louvre Museum
    try:
        print(f"\n[Pipeline] Fetching top {limit} entries from Louvre API...")
        fetch_louvre_masterpieces(limit=limit)
    except Exception as e:
        print(f"[Pipeline] Warning: Louvre collector encountered an error: {e}")
        print("Proceeding with cached Louvre data if available...")

    # 1.2 The Metropolitan Museum of Art
    try:
        print(f"\n[Pipeline] Fetching top {limit} entries from The Met API...")
        fetch_met_masterpieces(limit=limit)
    except Exception as e:
        print(f"[Pipeline] Warning: Met collector encountered an error: {e}")
        print("Proceeding with cached Met data if available...")

    # 1.3 Rijksmuseum
    try:
        print(f"\n[Pipeline] Fetching top {limit} entries from Rijksmuseum Open API...")
        get_rijks_masterpieces(limit=limit)
    except Exception as e:
        print(f"[Pipeline] Warning: Rijksmuseum collector encountered an error: {e}")
        print("Proceeding with cached Rijksmuseum data if available...")

    # 1.4 Uffizi Gallery (via Wikidata)
    try:
        print(f"\n[Pipeline] Fetching top {limit} entries from Uffizi Wikidata API...")
        fetch_uffizi_masterpieces(limit=limit)
    except Exception as e:
        print(f"[Pipeline] Warning: Uffizi collector encountered an error: {e}")
        print("Proceeding with cached Uffizi data if available...")

    # Step 2: Build and enrich the unified knowledge base
    try:
        print("\n[Pipeline] Step 2: Building unified knowledge base with AI tags...")
        build_unified_knowledge_base()
    except Exception as e:
        print(f"\n[Pipeline] Critical Error during knowledge base build: {e}")
        return

    print("\n=== MASTER INGESTION PIPELINE COMPLETED SUCCESSFULLY ===")

if __name__ == "__main__":
    # Change the limit globally right here
    run_pipeline(limit=50)