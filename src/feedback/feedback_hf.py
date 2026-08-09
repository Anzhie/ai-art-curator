import os
import pandas as pd
from datetime import datetime
from typing import List
from huggingface_hub import HfApi, hf_hub_download

DATASET_REPO_ID = os.getenv("HF_DATASET_REPO_ID")
HF_TOKEN = os.getenv("HF_TOKEN")


def log_to_hf_dataset(
    rag_version: str,
    user_query: str,
    retrieved_art_ids: List[str],
    response_status: str,
    rating: int,
    comment: str = "",
    response_time_sec: float = 0.0,
) -> bool:
    """Log evaluation metrics to HF Dataset Hub, or fallback to local CSV if secrets are missing."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_entry = {
        "timestamp": timestamp,
        "rag_version": rag_version,
        "user_query": user_query,
        "retrieved_art_ids": str(retrieved_art_ids),
        "response_status": response_status,
        "rating": rating,
        "comment": comment,
        "response_time_sec": response_time_sec,
    }

    # Fallback to local CSV if HF environment secrets are not configured
    if not DATASET_REPO_ID or not HF_TOKEN:
        print("⚠️ HF credentials missing. Writing to local 'data/feedback_fallback.csv'...")
        os.makedirs("data", exist_ok=True)
        fallback_path = os.path.join("data", "feedback_fallback.csv")
        df_fallback = pd.DataFrame([new_entry])
        df_fallback.to_csv(
            fallback_path,
            mode="a",
            header=not os.path.exists(fallback_path),
            index=False,
        )
        return False

    try:
        api = HfApi()
        filename = "rag_evaluation.csv"

        # Download existing dataset or create new structure
        try:
            local_path = hf_hub_download(
                repo_id=DATASET_REPO_ID,
                filename=filename,
                repo_type="dataset",
                token=HF_TOKEN,
            )
            df = pd.read_csv(local_path)
        except Exception:
            df = pd.DataFrame(columns=list(new_entry.keys()))

        # Append new entry and sync back to HF Hub
        df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)

        temp_path = "temp_rag_eval.csv"
        df.to_csv(temp_path, index=False)

        api.upload_file(
            path_or_fileobj=temp_path,
            path_in_repo=filename,
            repo_id=DATASET_REPO_ID,
            repo_type="dataset",
            token=HF_TOKEN,
        )

        if os.path.exists(temp_path):
            os.remove(temp_path)
        return True

    except Exception as e:
        print(f"❌ Failed to sync feedback with HF Dataset: {e}")
        return False