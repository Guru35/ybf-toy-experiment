"""
YBF-TOY 3rd run — MLP agent (384→128→2)

Same TF-IDF embedding, same cached YBF scores, same training set.
Only the policy network changes: linear → 2-layer MLP with ReLU hidden.

Usage:  python main_mlp.py
        python main_mlp.py --quick   (120 scenarios, 3 episodes)

No new API calls. Cache must exist (from prior full run).
"""

import sys
import os
import time
import random
import numpy as np

random.seed(42)
np.random.seed(42)

import config

quick_mode = "--quick" in sys.argv
total_n  = 120 if quick_mode else config.TOTAL_SCENARIOS
episodes = 3   if quick_mode else config.EPISODES

print("=" * 60)
print("YBF-TOY 3rd RUN — MLP AGENT (384→128→2)")
print("=" * 60)
if quick_mode:
    print("⚡ QUICK MODE: 120 scenarios, 3 episodes")
print()

os.makedirs(config.DATA_DIR,    exist_ok=True)
os.makedirs(config.RESULTS_DIR, exist_ok=True)

start = time.time()

# 1. Scenarios (cached from prior run)
print("[1/5] Loading scenarios...")
from scenarios import load_and_split_scenarios
train_s, test_s, all_s = load_and_split_scenarios(
    total=total_n, seed=config.RANDOM_SEED, train_ratio=config.TRAIN_RATIO
)

# 2. Verify scores cache exists (no API calls)
print("\n[2/5] Loading YBF scores from cache...")
from scorer import load_cache, _cache_key
scores_cache = load_cache()
expected = len(all_s) * 2
have = sum(1 for s in all_s for ak in ["A", "B"]
           if _cache_key(s["id"], ak) in scores_cache)
print(f"  Cache: {have}/{expected} entries")
if have < expected:
    print(f"✗ Incomplete cache ({have}/{expected}). Run main.py first.")
    sys.exit(1)
print("  ✓ Full cache available — no API calls needed")

# 3. Embeddings (cached)
print("\n[3/5] Loading embeddings...")
from embedder import compute_embeddings
embeddings = compute_embeddings(all_s)
emb_dim = embeddings.shape[1]

# 4. MLP Agent + Training
print(f"\n[4/5] Training MLP agent ({emb_dim} → 128 → 2) for {episodes} episodes...")
from agent_mlp import YBFAgentMLP
from train import train

agent = YBFAgentMLP(embedding_dim=emb_dim, hidden_dim=128)
training_log = train(
    agent=agent,
    train_scenarios=train_s,
    embeddings=embeddings,
    scores_cache=scores_cache,
    episodes=episodes,
    lr=config.LEARNING_RATE,
    epsilon_start=config.EPSILON_START,
    epsilon_end=config.EPSILON_END,
    epsilon_decay=config.EPSILON_DECAY,
)
mlp_path = "data/agent_mlp_weights.npy"
agent.save(mlp_path)

# 5. Evaluate
print(f"\n[5/5] Evaluating on {len(test_s)} held-out test scenarios...")
from evaluate import evaluate_all
from report import print_results, save_results

results = evaluate_all(agent, test_s, embeddings, scores_cache)

print_results(results, training_log)

# Save under a distinct filename so we don't overwrite linear results
import json
mlp_results_path = os.path.join(config.RESULTS_DIR, "evaluation_results_mlp.json")
slim_results = {k: v for k, v in results.items()}
for cond in ["trained_agent", "random_baseline", "always_a_baseline"]:
    if cond in slim_results and "rewards_list" in slim_results[cond]:
        slim_results[cond] = {k: v for k, v in slim_results[cond].items() if k != "rewards_list"}
with open(mlp_results_path, "w") as f:
    json.dump({
        "config": {
            "agent":       "MLP (384→128→2)",
            "model":       config.ANTHROPIC_MODEL,
            "total":       config.TOTAL_SCENARIOS,
            "train_ratio": config.TRAIN_RATIO,
            "episodes":    episodes,
            "lr":          config.LEARNING_RATE,
        },
        "training_log": training_log,
        "evaluation":   slim_results,
    }, f, indent=2)
print(f"\n  MLP results saved → {mlp_results_path}")

elapsed = time.time() - start
print(f"\n✓ Done in {elapsed:.1f} sec")
