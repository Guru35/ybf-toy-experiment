"""
YBF-TOY Experiment — Main Entry Point

Usage:
  python main.py           # full experiment (1200 scenarios)
  python main.py --quick   # quick test    (120 scenarios, 3 episodes)
"""

import sys
import os
import time
import random
import numpy as np

# ── RNG seeds first (C3) ───────────────────────────────────────────────────
random.seed(42)
np.random.seed(42)

# ── API key check ──────────────────────────────────────────────────────────
if not os.environ.get("ANTHROPIC_API_KEY"):
    print("✗ ANTHROPIC_API_KEY is not set.")
    print("  Run: export ANTHROPIC_API_KEY='sk-ant-...'")
    sys.exit(1)

import config

quick_mode = "--quick" in sys.argv
total_n    = 120 if quick_mode else config.TOTAL_SCENARIOS
episodes   = 3   if quick_mode else config.EPISODES

print("=" * 60)
print("YBF-TOY REINFORCEMENT LEARNING EXPERIMENT")
print("Yalın Bilinç Felsefesi as Reward Signal")
print("=" * 60)
if quick_mode:
    print("⚡ QUICK MODE: 120 scenarios, 3 episodes")
print()

os.makedirs(config.DATA_DIR,    exist_ok=True)
os.makedirs(config.RESULTS_DIR, exist_ok=True)

start = time.time()

# ── 1. Scenarios ───────────────────────────────────────────────────────────
print("[1/6] Loading scenarios...")
from scenarios import load_and_split_scenarios
train_s, test_s, all_s = load_and_split_scenarios(
    total=total_n,
    seed=config.RANDOM_SEED,
    train_ratio=config.TRAIN_RATIO
)

# ── 2. YBF scores (pre-compute, cached) ───────────────────────────────────
print("\n[2/6] Pre-computing YBF scores...")
from scorer import precompute_all_scores, load_cache
precompute_all_scores(all_s)
scores_cache = load_cache()

# ── 3. Embeddings ──────────────────────────────────────────────────────────
print("\n[3/6] Computing embeddings...")
from embedder import compute_embeddings
embeddings = compute_embeddings(all_s)

# ── 4. Agent ───────────────────────────────────────────────────────────────
print("\n[4/6] Initializing agent...")
from agent import YBFAgent
emb_dim = embeddings.shape[1]
agent = YBFAgent(embedding_dim=emb_dim)
print(f"  ✓ Linear Q-network ready ({emb_dim} → 2)")

# ── 5. Train ───────────────────────────────────────────────────────────────
print(f"\n[5/6] Training ({episodes} episodes)...")
from train import train
training_log = train(
    agent       = agent,
    train_scenarios = train_s,
    embeddings  = embeddings,
    scores_cache = scores_cache,
    episodes    = episodes,
    lr          = config.LEARNING_RATE,
    epsilon_start = config.EPSILON_START,
    epsilon_end   = config.EPSILON_END,
    epsilon_decay = config.EPSILON_DECAY,
)
agent.save(config.MODEL_PATH)

# ── 6. Evaluate ────────────────────────────────────────────────────────────
print(f"\n[6/6] Evaluating on {len(test_s)} held-out test scenarios...")
from evaluate import evaluate_all
from report import print_results, save_results

results = evaluate_all(agent, test_s, embeddings, scores_cache)

print_results(results, training_log)
save_results(results, training_log)

elapsed = time.time() - start
print(f"\n✓ Done in {elapsed/60:.1f} min")
if quick_mode:
    print("  ➜ If A>B ≥ 70% and PASS: run full experiment with  python main.py")
