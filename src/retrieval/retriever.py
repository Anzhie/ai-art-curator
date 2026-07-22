import os
from typing import List, Dict, Any, Optional
import chromadb
from sentence_transformers import SentenceTransformer

# Configuration Constants
CHROMA_PATH = "chroma_db"
COLLECTION_NAME = "artworks_v1"
MODEL_NAME = "intfloat/multilingual-e5-large"


class ArtRetriever:
    """
    Handles semantic search queries against the ChromaDB vector index.
    """

    def __init__(self, chroma_path: str = CHROMA_PATH, model_name: str = MODEL_NAME):
        # We load the exact same model used for indexing
        print(f"Loading embedding model: {model_name}...")
        self.model = SentenceTransformer(model_name)
        
        print(f"Connecting to ChromaDB at: {chroma_path}...")
        self.chroma_client = chromadb.PersistentClient(path=chroma_path)
        
        # Connect to the existing collection
        self.collection = self.chroma_client.get_collection(name=COLLECTION_NAME)

    def search(self, query: str, top_k: int = 5, museum_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Executes a semantic vector search.
        
        Args:
            query: The user's natural language search query.
            top_k: Number of results to return.
            museum_filter: Optional strict text filter for a specific museum.
        """
        # E5 model requirement: Prefix user search queries with 'query: '
        prepared_query = f"query: {query}"
        
        # Generate the embedding vector for the search query
        query_embedding = self.model.encode(prepared_query).tolist()
        
        # Build the where clause for metadata filtering (Hybrid Search)
        where_clause = {"museum": museum_filter} if museum_filter else None

        # Perform the nearest neighbor search in ChromaDB
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=where_clause,
            include=["metadatas", "documents", "distances"]
        )
        
        # Parse and format the complex ChromaDB response
        formatted_results = []
        if results and results["ids"] and len(results["ids"][0]) > 0:
            for i in range(len(results["ids"][0])):
                artwork_id = results["ids"][0][i]
                metadata = results["metadatas"][0][i]
                document = results["documents"][0][i]
                
                # Distance represents how "far" the result is from the query.
                # Smaller distance = higher semantic similarity.
                distance = results["distances"][0][i]
                
                formatted_results.append({
                    "id": artwork_id,
                    "title": metadata.get("title", "Unknown"),
                    "artist": metadata.get("artist", "Unknown"),
                    "museum": metadata.get("museum", "Unknown"),
                    "year": metadata.get("year", "Unknown"),
                    "description": document,
                    "distance": round(distance, 4)
                })
                
        return formatted_results


if __name__ == "__main__":
    retriever = ArtRetriever()
    
    print("\n" + "="*60)
    print("🎨 AI Art Curator - Interactive Search Console")
    print("Type 'exit' or 'quit' to stop.")
    print("="*60)
    
    while True:
        try:
            # Wait for user input
            user_query = input("\n🔍 Enter your search query: ").strip()
            
            # Exit condition
            if user_query.lower() in ['exit', 'quit']:
                print("Goodbye! Exiting search console...")
                break
                
            if not user_query:
                print("Query cannot be empty. Please try again.")
                continue
                
            # Execute search
            hits = retriever.search(query=user_query, top_k=3)
            
            # Display results
            print("\n" + "-"*40)
            for rank, hit in enumerate(hits, start=1):
                print(f"[{rank}] {hit['title']} by {hit['artist']} ({hit['year']}) | 🏛️ {hit['museum']}")
                print(f"   Distance: {hit['distance']}")
                # Print the first 100 characters of the description for compactness
                print(f"   Context: {hit['description'][:100]}...")
            print("-" * 40)
            
        except KeyboardInterrupt:
            # Graceful exit on Ctrl+C
            print("\nGoodbye! Exiting search console...")
            break