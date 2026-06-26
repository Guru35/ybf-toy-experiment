"""
YBF Diagnostic — Trap Separability Check
30 saniye, mevcut env'de çalışır, yeni bağımlılık yok.

Çalıştır: python diagnostic_trap.py
Dizin:    ~/Documents/AI-Egitmek/ybf_toy/
"""

import json
import numpy as np
import os

DATA_DIR = "data"

def load():
    with open(os.path.join(DATA_DIR, "scenarios.json")) as f:
        scenarios = json.load(f)
    with open(os.path.join(DATA_DIR, "scores_cache.json")) as f:
        cache = json.load(f)
    emb_path = os.path.join(DATA_DIR, "embeddings.npy")
    if os.path.exists(emb_path):
        embeddings = np.load(emb_path)
        print(f"Embeddings loaded: shape {embeddings.shape}")
    else:
        embeddings = None
        print("No embeddings.npy found — will try TF-IDF rebuild")
    return scenarios, cache, embeddings

def get_reward(cache, sid, action):
    key = f"scenario_{sid}_action_{action}"
    return cache.get(key, {}).get("reward", -99)

def build_tfidf(scenarios):
    """Rebuild TF-IDF embeddings if .npy not available."""
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.decomposition import TruncatedSVD

    texts = [f"{s['situation']} {s['intention']}" for s in scenarios]
    vec = TfidfVectorizer(max_features=2397)
    X = vec.fit_transform(texts)
    svd = TruncatedSVD(n_components=384, random_state=42)
    embs = svd.fit_transform(X).astype(np.float32)
    norms = np.linalg.norm(embs, axis=1, keepdims=True)
    norms = np.where(norms == 0, 1.0, norms)
    return embs / norms

def cosine_sim(a, b):
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-8))

def main():
    scenarios, cache, embeddings = load()

    split = int(len(scenarios) * 0.8)
    test_s = scenarios[split:]

    # Find traps
    traps = [s for s in test_s
             if get_reward(cache, s["id"], "B") > get_reward(cache, s["id"], "A")]

    print(f"\nTest set: {len(test_s)} | Traps: {len(traps)}\n")

    if embeddings is None:
        print("Rebuilding TF-IDF embeddings...")
        embeddings = build_tfidf(scenarios)

    # All non-trap test scenarios
    non_traps = [s for s in test_s if s not in traps]

    print("=" * 65)
    print("TRAP SEPARABILITY DIAGNOSTIC")
    print("=" * 65)

    for i, trap in enumerate(traps, 1):
        trap_emb = embeddings[trap["embed_idx"]]
        r_a = get_reward(cache, trap["id"], "A")
        r_b = get_reward(cache, trap["id"], "B")

        # Cosine similarity to all other test scenarios
        sims = []
        for s in non_traps:
            sim = cosine_sim(trap_emb, embeddings[s["embed_idx"]])
            s_r_a = get_reward(cache, s["id"], "A")
            s_r_b = get_reward(cache, s["id"], "B")
            is_moral_a = s_r_a > s_r_b  # A is clearly better
            sims.append((sim, s, is_moral_a))

        sims.sort(key=lambda x: x[0], reverse=True)
        top10 = sims[:10]

        moral_a_count = sum(1 for _, _, is_a in top10 if is_a)
        trap_like_count = sum(1 for _, _, is_a in top10 if not is_a)

        print(f"\nTRAP {i} — Senaryo {trap['id']}")
        print(f"  A reward: {r_a}  B reward: {r_b}  (B wins)")
        print(f"  Situation: {trap['situation'][:70]}...")
        print(f"\n  Top-10 nearest neighbors in embedding space:")
        print(f"  {'moral=A (non-trap)':>22}: {moral_a_count}/10")
        print(f"  {'trap-like or B>A':>22}: {trap_like_count}/10")

        print(f"\n  Nearest 5:")
        for j, (sim, s, is_a) in enumerate(top10[:5], 1):
            label = "moral=A" if is_a else "TRAP-like"
            print(f"  {j}. sim={sim:.3f} [{label}] {s['situation'][:55]}...")

        print(f"\n  VERDICT: ", end="")
        if moral_a_count >= 8:
            print("🔴 LOW SEPARABILITY — mostly surrounded by moral=A neighbors")
            print("     mpnet yardım etmeyebilir. MLP/nonlinear agent daha etkili.")
        elif moral_a_count <= 4:
            print("🟢 HIGH SEPARABILITY — trap-like neighbors dominant")
            print("     mpnet yardım edebilir. Path A mantıklı.")
        else:
            print("🟡 MIXED — belirsiz sinyal")
            print("     mpnet denemeye değer ama garanti yok.")

    print("\n" + "=" * 65)
    print("Bu sonucu Claude'a yapıştır → Path A mı MLP mi kararı verilecek.")

if __name__ == "__main__":
    main()
