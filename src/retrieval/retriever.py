import os
from functools import lru_cache
from typing import List, Dict, Any, Optional

import chromadb
from sentence_transformers import SentenceTransformer
from src.config import EMBEDDING_MODEL_NAME

# Configuration Constants
CHROMA_PATH = "chroma_db"
COLLECTION_NAME = "artworks_v1"


@lru_cache(maxsize=1)
def get_embedding_model() -> SentenceTransformer:
    """
    Load the embedding model only once per Python process.
    All ArtRetriever instances reuse the same model.
    """
    print(f"Loading embedding model: {EMBEDDING_MODEL_NAME}...")

    return SentenceTransformer(EMBEDDING_MODEL_NAME)


class ArtRetriever:
    """
    Performs semantic search over the ChromaDB vector index.
    """

    def __init__(
        self,
        chroma_path: str = CHROMA_PATH,
    ):
        # Reuse cached model
        self.model = get_embedding_model()

        print(f"Connecting to ChromaDB at: {chroma_path}...")

        self.chroma_client = chromadb.PersistentClient(path=chroma_path)

        self.collection = self.chroma_client.get_collection(
            name=COLLECTION_NAME
        )

    def search(
        self,
        query: str,
        top_k: int = 5,
        museum_filter: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Execute semantic search.

        Args:
            query: User search query.
            top_k: Number of results.
            museum_filter: Optional metadata filter.

        Returns:
            List of formatted search results.
        """

        prepared_query = f"query: {query}"

        query_embedding = self.model.encode(
            prepared_query
        ).tolist()

        where_clause = (
            {"museum": museum_filter}
            if museum_filter
            else None
        )

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=where_clause,
            include=[
                "metadatas",
                "documents",
                "distances",
            ],
        )

        formatted_results = []

        if results and results["ids"] and results["ids"][0]:
            for i in range(len(results["ids"][0])):

                metadata = results["metadatas"][0][i]

                formatted_results.append(
                    {
                        "id": results["ids"][0][i],
                        "title": metadata.get("title", "Unknown"),
                        "artist": metadata.get("artist", "Unknown"),
                        "museum": metadata.get("museum", "Unknown"),
                        "year": metadata.get("year", "Unknown"),
                        "description": results["documents"][0][i],
                        "distance": round(
                            results["distances"][0][i], 4
                        ),
                    }
                )

        return formatted_results


if __name__ == "__main__":
    retriever = ArtRetriever()

    print("\n" + "=" * 60)
    print("🎨 AI Art Curator - Interactive Search Console")
    print("Type 'exit' or 'quit' to stop.")
    print("=" * 60)

    while True:
        try:
            user_query = input("\n🔍 Enter your search query: ").strip()

            if user_query.lower() in {"exit", "quit"}:
                print("Goodbye!")
                break

            if not user_query:
                print("Query cannot be empty.")
                continue

            hits = retriever.search(query=user_query, top_k=3)

            print("\n" + "-" * 40)

            for rank, hit in enumerate(hits, start=1):
                print(
                    f"[{rank}] {hit['title']} "
                    f"by {hit['artist']} "
                    f"({hit['year']}) | "
                    f"🏛️ {hit['museum']}"
                )
                print(f"   Distance: {hit['distance']}")
                print(f"   Context: {hit['description'][:100]}...")

            print("-" * 40)
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break