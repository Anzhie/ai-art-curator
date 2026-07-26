import pytest
from src.retrieval.retriever import ArtRetriever, COLLECTION_NAME


@pytest.fixture(scope="module")
def retriever():
    """Initialize ArtRetriever once per module to save memory and execution time."""
    return ArtRetriever()


def test_retriever_initialization(retriever):
    """Verify that model and ChromaDB collection initialize correctly."""
    assert retriever.model is not None, "Embedding model failed to load"
    assert retriever.collection is not None, "ChromaDB collection failed to load"
    
    # Check equality via constant
    assert retriever.collection.name == COLLECTION_NAME


def test_search_top_k(retriever):
    """Ensure top_k parameter strictly controls result count."""
    k = 3
    results = retriever.search(query="Deep philosophical meaning", top_k=k)
    
    assert isinstance(results, list), "Search should return a list"
    assert len(results) == k, f"Expected {k} results, got {len(results)}"


def test_search_response_structure(retriever):
    """Validate keys and data types of returned search items."""
    results = retriever.search(query="Classical epic poetry", top_k=1)
    assert len(results) == 1
    
    hit = results[0]
    expected_keys = {"id", "title", "artist", "museum", "year", "description", "distance"}
    
    assert set(hit.keys()) == expected_keys, "Result dictionary missing required keys"
    assert isinstance(hit["distance"], float), "Distance metric must be float"


def test_metadata_filtering(retriever):
    """Verify metadata filtering logic in hybrid search."""
    target_museum = "Uffizi"
    results = retriever.search(query="Portraits of women", top_k=5, museum_filter=target_museum)
    
    assert len(results) > 0, "Expected to find at least one result in Uffizi collection"
    for hit in results:
        assert hit["museum"] == target_museum, f"Filter leaked external data: {hit['museum']}"


def test_empty_query(retriever):
    """Ensure empty string queries are handled without crashing."""
    results = retriever.search(query="", top_k=2)
    assert len(results) == 2