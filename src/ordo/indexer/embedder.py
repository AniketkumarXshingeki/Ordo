from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List

MODEL_NAME = "all-MiniLM-L6-v2"

_model = None


def _get_device():
    try:
        import torch
        return "cuda" if torch.cuda.is_available() else "cpu"
    except Exception:
        return "cpu"


def get_model():
    global _model
    if _model is None:
        device = _get_device()
        print(f"Loading embedding model on {device}...")
        _model = SentenceTransformer(MODEL_NAME, device=device)
    return _model


def create_embedding(text: str):
    if not text:
        return None
    model = get_model()
    vector = model.encode(text)
    return np.asarray(vector, dtype=np.float32)


def create_embeddings(texts: List[str]):
    if not texts:
        return []
    model = get_model()
    vectors = model.encode(texts, show_progress_bar=False, convert_to_numpy=True)
    return np.asarray(vectors, dtype=np.float32)
