from sentence_transformers import SentenceTransformer
import numpy as np

MODEL_NAME = "all-MiniLM-L6-v2"

_model = None


def get_model():
    global _model
    if _model is None:
        print("Loading embedding model...")
        _model = SentenceTransformer(MODEL_NAME)
    return _model


def create_embedding(text: str):
    if not text:
        return None
    model = get_model()
    vector = model.encode(text)
    return vector.astype(np.float32)