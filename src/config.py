import os

# Default fallback limit per museum for the entire project
DEFAULT_MUSEUM_LIMIT: int = 2000

# Project-wide limit reading from environment or falling back to default
MUSEUM_ITEM_LIMIT: int = int(os.getenv("MUSEUM_ITEM_LIMIT", DEFAULT_MUSEUM_LIMIT))

# LLM Configuration (Generative)
LLM_MODEL_NAME: str = os.getenv("LLM_MODEL_NAME", "qwen2.5:1.5b")

# Vector Search Configuration (Embeddings)
EMBEDDING_MODEL_NAME: str = os.getenv("EMBEDDING_MODEL_NAME", "intfloat/multilingual-e5-large")