"""
Sentence embeddings for scenario state representation.
C4: embed_idx is position in all_scenarios — guaranteed correct.
"""

import os
import numpy as np
import config


def compute_embeddings(all_scenarios: list) -> np.ndarray:
    """
    Args:   all_scenarios — list of scenario dicts with 'embed_idx'
    Returns: np.ndarray shape (len(all_scenarios), 384), L2-normalized, float32
    Saves to config.EMBEDDINGS_PATH; loads from file if exists and size matches.
    """
    n = len(all_scenarios)

    if os.path.exists(config.EMBEDDINGS_PATH):
        embs = np.load(config.EMBEDDINGS_PATH)
        if embs.shape[0] == n:
            print(f"  ✓ Embeddings loaded from cache: shape {embs.shape}")
            return embs
        print(f"  Cache shape mismatch ({embs.shape[0]} vs {n}) — recomputing")

    print(f"  Computing embeddings for {n} scenarios...")
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer(config.EMBED_MODEL)

    # State text: situation + [SEP] + intention
    texts = [
        f"{s['situation']} [SEP] {s['intention']}"
        for s in all_scenarios
    ]

    raw = model.encode(texts, batch_size=64, show_progress_bar=True,
                       convert_to_numpy=True)  # (n, 384) float32

    # L2 normalize each row
    norms = np.linalg.norm(raw, axis=1, keepdims=True)
    norms = np.where(norms == 0, 1.0, norms)
    embs = (raw / norms).astype(np.float32)

    os.makedirs(config.DATA_DIR, exist_ok=True)
    np.save(config.EMBEDDINGS_PATH, embs)
    print(f"  ✓ Embeddings saved: shape {embs.shape}")
    return embs
