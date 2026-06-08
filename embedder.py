"""
TF-IDF + TruncatedSVD scenario embeddings (no torch required).

Pivot from sentence-transformers (C10): torch has no wheels for
Intel macOS + Python 3.13+. TF-IDF + SVD is fully reproducible,
needs no model download, and gives the linear Q-net enough signal
to discriminate scenarios for this toy experiment.

Output dim is adaptive: min(384, n_samples-1, n_features). The agent
reads embeddings.shape[1] and sizes itself accordingly.
"""

import os
import numpy as np
import config

TARGET_DIM = 384


def compute_embeddings(all_scenarios: list) -> np.ndarray:
    """
    Args:   all_scenarios — list of dicts with 'situation', 'intention'
    Returns: np.ndarray shape (n, k), L2-normalized, float32,
             where k = min(TARGET_DIM, n-1, vocab_size)
    Saves to config.EMBEDDINGS_PATH; loads if shape matches.
    """
    n = len(all_scenarios)

    if os.path.exists(config.EMBEDDINGS_PATH):
        embs = np.load(config.EMBEDDINGS_PATH)
        if embs.shape[0] == n:
            print(f"  ✓ Embeddings loaded from cache: shape {embs.shape}")
            return embs
        print(f"  Cache shape mismatch ({embs.shape[0]} vs {n}) — recomputing")

    print(f"  Computing TF-IDF + SVD embeddings for {n} scenarios...")
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.decomposition import TruncatedSVD

    texts = [
        f"{s['situation']} {s['intention']}"
        for s in all_scenarios
    ]

    vec = TfidfVectorizer(
        lowercase=True,
        stop_words="english",
        ngram_range=(1, 2),
        min_df=2,
        max_df=0.95,
    )
    tfidf = vec.fit_transform(texts)  # (n, vocab)
    vocab_size = tfidf.shape[1]
    print(f"    TF-IDF vocab: {vocab_size} features")

    k = min(TARGET_DIM, n - 1, vocab_size)
    svd = TruncatedSVD(n_components=k, random_state=42)
    reduced = svd.fit_transform(tfidf)  # (n, k) dense
    print(f"    SVD reduced to {k} dims "
          f"(explained variance: {svd.explained_variance_ratio_.sum():.3f})")

    norms = np.linalg.norm(reduced, axis=1, keepdims=True)
    norms = np.where(norms == 0, 1.0, norms)
    embs = (reduced / norms).astype(np.float32)

    os.makedirs(config.DATA_DIR, exist_ok=True)
    np.save(config.EMBEDDINGS_PATH, embs)
    print(f"  ✓ Embeddings saved: shape {embs.shape}")
    return embs
