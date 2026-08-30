import os
from dotenv import load_dotenv
import streamlit as st

load_dotenv()

def get_secret(key: str, default: str = None) -> str:
    """Retrieve a secret from environment variables or Streamlit secrets safely."""
    # 1. Check system environment variables / local .env file (Hugging Face Spaces & local)
    val = os.getenv(key)
    if val:
        return val

    # 2. Fall back to Streamlit Cloud secrets safely
    try:
        return st.secrets.get(key, default)
    except Exception:
        return default