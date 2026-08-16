import os
import torch
import pytest
from src.rag.curator_engine import ArtCuratorEngine
from src.retrieval.retriever import ArtRetriever

# Enforce single-threaded execution before ML libraries load to prevent thread contention and Windows memory issues
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["VECLIB_MAXIMUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"
os.environ["TOKENIZERS_PARALLELISM"] = "false"

# Disable asynchronous weight loading in Hugging Face Transformers to prevent Windows Access Violation crashes
os.environ["HF_DEACTIVATE_ASYNC_LOAD"] = "1"

# Restrict thread count within PyTorch
torch.set_num_threads(1)


@pytest.fixture(scope="session")
def engine():
    """Initialize ArtCuratorEngine once for all tests to save memory and execution time."""
    return ArtCuratorEngine()


@pytest.fixture(scope="session")
def retriever():
    """Initialize ArtRetriever once for all tests to save memory and execution time."""
    return ArtRetriever()