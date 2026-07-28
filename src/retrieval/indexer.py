import json
import os
from typing import List, Dict, Any
import chromadb
from sentence_transformers import SentenceTransformer
from src.config import EMBEDDING_MODEL_NAME

# Configuration Constants
DATA_PATH = "data/processed/artworks.json"
CHROMA_PATH = "chroma_db"
COLLECTION_NAME = "artworks_v1"


class ArtworkIndexer:
    """
    Handles the vectorization of artwork descriptions and builds a searchable 
    vector index inside ChromaDB using sentence-transformers embeddings.
    """

    def __init__(self, chroma_path: str = CHROMA_PATH, model_name: str = EMBEDDING_MODEL_NAME):
        print(f"Loading embedding model: {model_name}...")
        self.model = SentenceTransformer(model_name)
        
        print(f"Initializing ChromaDB client at: {chroma_path}...")
        self.chroma_client = chromadb.PersistentClient(path=chroma_path)
        
        # Get existing collection or create a new one configured for cosine similarity
        self.collection = self.chroma_client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"}
        )

    def load_artworks(self, file_path: str = DATA_PATH) -> List[Dict[str, Any]]:
        """
        Loads preprocessed artwork records from the target JSON artifact.
        
        Raises:
            FileNotFoundError: If the input file is missing.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Artifact {file_path} not found. Run ingestion pipeline first!")
        
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def build_index(self) -> None:
        """
        Extracts artwork descriptions, formats them for the E5 model, 
        generates dense vector embeddings, and upserts everything into ChromaDB.
        """
        artworks = self.load_artworks()
        print(f"Loaded {len(artworks)} artworks for indexing.")

        ids = []
        documents = []
        metadatas = []
        texts_to_embed = []

        for item in artworks:
            artwork_id = item["id"]
            # Fallback to basic details if description key is missing
            description = item.get("description", f"{item.get('title')} by {item.get('artist')}")
            
            # E5 model requirement: Prefix indexed documents/passages with 'passage: '
            prepared_text = f"passage: {description}"
            
            ids.append(artwork_id)
            documents.append(description)  # Keep clean text for presentation
            texts_to_embed.append(prepared_text)
            
            # Attach structural metadata for metadata filtering during search
            metadatas.append({
                "title": item.get("title", "Untitled"),
                "artist": item.get("artist", "Unknown"),
                "museum": item.get("museum", "Unknown"),
                "year": str(item.get("year", "")),
                "image_url": item.get("image_url", "")
            })

        print("Generating embeddings (this might take a few moments)...")
        # Generate vector embeddings in batch mode for efficiency
        embeddings = self.model.encode(texts_to_embed, show_progress_bar=True).tolist()

        print("Upserting vectors into ChromaDB...")
        self.collection.upsert(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas
        )

        print(f"SUCCESS: Successfully indexed {self.collection.count()} items into '{COLLECTION_NAME}'!")


if __name__ == "__main__":
    # Execute indexing when run directly
    indexer = ArtworkIndexer()
    indexer.build_index()