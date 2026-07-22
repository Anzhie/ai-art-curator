import pytest
from src.retrieval import ArtRetriever


@pytest.fixture(scope="module")
def retriever():
    """
    Initialize the ArtRetriever once for the entire test module.
    Using 'scope="module"' prevents reloading the heavy 2GB embedding model 
    for each individual test function, significantly speeding up test execution.
    """
    print("\nInitializing ArtRetriever for tests...")
    return ArtRetriever()


def test_retriever_initialization(retriever):
    """
    Verify that the retriever correctly initializes both 
    the underlying transformer model and the ChromaDB collection connection.
    """
    assert retriever.model is not None, "Embedding model failed to load"
    assert retriever.collection is not None, "ChromaDB collection failed to load"
    assert retriever.collection.name == "artworks_v1"


def test_search_top_k(retriever):
    """
    Ensure that the 'top_k' parameter is strictly respected 
    and the search returns the exact expected number of results.
    """
    k = 3
    results = retriever.search(query="Deep philosophical meaning", top_k=k)
    
    assert isinstance(results, list), "Search should return a list"
    assert len(results) == k, f"Expected {k} results, got {len(results)}"


def test_search_response_structure(retriever):
    """
    Validate the internal dictionary structure of search hits.
    Checks that all required metadata and distance metrics are present and correctly typed.
    """
    results = retriever.search(query="Classical epic poetry", top_k=1)
    assert len(results) == 1
    
    hit = results[0]
    expected_keys = {"id", "title", "artist", "museum", "year", "description", "distance"}
    
    assert set(hit.keys()) == expected_keys, "Result dictionary is missing required keys"
    assert isinstance(hit["distance"], float), "Distance metric must be a floating-point number"


def test_metadata_filtering(retriever):
    """
    Test hybrid search capabilities by combining a semantic query 
    with a strict structural metadata filter (e.g., filtering by a specific museum).
    """
    target_museum = "Uffizi"
    results = retriever.search(query="Portraits of women", top_k=5, museum_filter=target_museum)
    
    assert len(results) > 0, "Expected to find at least one result in the Uffizi collection"
    for hit in results:
        assert hit["museum"] == target_museum, f"Filter leaked external data: found {hit['museum']} instead of {target_museum}"


def test_empty_query(retriever):
    """
    Check edge-case handling for empty search strings. 
    The embedding model should handle empty input gracefully without throwing exceptions.
    """
    results = retriever.search(query="", top_k=2)
    
    assert len(results) == 2, "System crashed or returned an unexpected number of results on empty query"