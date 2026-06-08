"""
Phase B — Barrier function axial training.

Veto interpretation (per Doc §9.1.1):
  Standard reward: -5 penalty pushes Q toward -5 via TD update
  Barrier:         gradient mask, no Q update for veto actions

Implementation:
  if cache entry says veto: skip agent.update() entirely for that step.
  Q for veto actions stays near initial value (~0).
  Q for non-veto actions learns normally.
  Decision: argmax picks non-veto because Q_non_veto > 0 > Q_veto ≈ 0.

Test on BOTH:
  - In-distribution traps (4 from test set)
  - OOD ONUR traps (10 generated)

Compare to standard axial (Test 5).
"""

import sys, os, time, json, random
import numpy as np

random.seed(42)
np.random.seed(42)

import config
from scorer import load_cache, _cache_key
from scenarios import load_and_split_scenarios
from embedder import compute_embeddings
from agent_axial import YBFAgentAxial

AXES = ("gerceklik", "onur", "saygi", "sinir", "ozgurluk")

def get_axis_vec(cache, sid, action):
    entry = cache.get(_cache_key(sid, action), {})
    return np.array([entry.get(a, 0) for a in AXES], dtype=np.float32)

def make_inputs_id(emb, cache, sid):
    """In-distribution input: emb + axis vec for each action."""
    ax_a = get_axis_vec(cache, sid, "A")
    ax_b = get_axis_vec(cache, sid, "B")
    return np.concatenate([emb, ax_a]), np.concatenate([emb, ax_b])

# ── load ─────────────────────────────────────────────────────────────────────
print("="*60)
print("YBF-TOY PHASE B — BARRIER-FUNCTION AXIAL")
print("="*60)
print("\n  Barrier rule: skip update step when chosen action's reward is veto (-5)")

train_s, test_s, all_s = load_and_split_scenarios(
    total=config.TOTAL_SCENARIOS, seed=config.RANDOM_SEED,
    train_ratio=config.TRAIN_RATIO,
)
cache = load_cache()
embeddings = compute_embeddings(all_s)
emb_dim = embeddings.shape[1]
input_dim = emb_dim + 5

# ── train with barrier ──────────────────────────────────────────────────────
agent = YBFAgentAxial(input_dim=input_dim)
epsilon = config.EPSILON_START
training_log = []

skipped_veto_count = 0
total_steps = 0

def better_action(cache, sid):
    r_a = cache[_cache_key(sid, "A")]["reward"]
    r_b = cache[_cache_key(sid, "B")]["reward"]
    return "A" if r_a >= r_b else "B"

print(f"\n[Train] {config.EPISODES} episodes × {len(train_s)} scenarios (barrier mode)")
for ep in range(config.EPISODES):
    ep_rewards, correct, ep_skipped = [], 0, 0
    indices = list(range(len(train_s)))
    random.shuffle(indices)
    for idx in indices:
        s = train_s[idx]
        emb = embeddings[s["embed_idx"]]
        input_a, input_b = make_inputs_id(emb, cache, s["id"])
        action = agent.choose_action(input_a, input_b, epsilon)
        reward = cache[_cache_key(s["id"], action)]["reward"]
        is_veto = cache[_cache_key(s["id"], action)].get("veto", False)

        # BARRIER: skip update if action is veto
        if is_veto:
            ep_skipped += 1
            skipped_veto_count += 1
        else:
            agent.update(input_a if action == "A" else input_b,
                         reward, config.LEARNING_RATE)

        ep_rewards.append(reward)
        total_steps += 1
        if action == better_action(cache, s["id"]):
            correct += 1
    epsilon = max(config.EPSILON_END, epsilon * config.EPSILON_DECAY)
    avg_r = float(np.mean(ep_rewards))
    acc = correct / len(train_s) * 100
    training_log.append({"episode": ep+1, "avg_reward": round(avg_r, 4),
                         "correct_pct": round(acc, 2), "epsilon": round(epsilon, 4),
                         "skipped_veto": ep_skipped})
    print(f"  Ep {ep+1}/{config.EPISODES} | avg reward: {avg_r:+6.3f} | "
          f"correct: {acc:5.1f}% | ε={epsilon:.3f} | barrier-skipped: {ep_skipped}")

print(f"\n  Total updates skipped (veto-blocked): {skipped_veto_count}/{total_steps} "
      f"({100*skipped_veto_count/total_steps:.1f}%)")

agent.save("data/agent_axial_barrier_weights.npy")

# ── eval on ID test set ─────────────────────────────────────────────────────
print(f"\n[Eval — ID test set] {len(test_s)} scenarios")

def axial_greedy(s):
    emb = embeddings[s["embed_idx"]]
    input_a, input_b = make_inputs_id(emb, cache, s["id"])
    return agent.choose_action(input_a, input_b, epsilon=0.0)

correct, rewards, entries = 0, [], []
for s in test_s:
    action = axial_greedy(s)
    r = cache[_cache_key(s["id"], action)]["reward"]
    rewards.append(r)
    entries.append(cache[_cache_key(s["id"], action)])
    if action == better_action(cache, s["id"]):
        correct += 1

clean = [e for e in entries if not any(e[ax] == -1 for ax in AXES)]
print(f"  Mean reward:  {np.mean(rewards):+.3f}")
print(f"  Correct%:     {correct/len(test_s)*100:.1f}")
print(f"  Clean%:       {len(clean)/len(test_s)*100:.1f}")
print(f"  P2 mean:      {np.mean([e['reward'] for e in clean]):.3f}")

# ── eval on ID traps ────────────────────────────────────────────────────────
print(f"\n[Eval — ID traps]")
id_traps = [s for s in test_s
            if cache[_cache_key(s["id"], "B")]["reward"] >
               cache[_cache_key(s["id"], "A")]["reward"]]

id_correct = 0
for s in id_traps:
    choice = axial_greedy(s)
    is_correct = (choice == "B")
    if is_correct: id_correct += 1
    print(f"  Trap {s['id']}: choice={choice} {'✓' if is_correct else '✗'}")
print(f"  ID Trap performance: {id_correct}/{len(id_traps)} = {100*id_correct/len(id_traps):.1f}%")

# ── eval on OOD traps ──────────────────────────────────────────────────────
print(f"\n[Eval — OOD ONUR traps]")
with open("data/ood_traps_filtered.json") as f:
    ood_traps = json.load(f)

ood_correct = 0
ood_details = []
for s in ood_traps:
    # OOD scenarios don't have embeddings; use axis-only input mirror
    # For fair comparison, we use only axis vectors (no embedding for OOD)
    ax_a = np.array([s["scores_A"][a] for a in AXES], dtype=np.float32)
    ax_b = np.array([s["scores_B"][a] for a in AXES], dtype=np.float32)
    # Use zero embedding (since no real embedding for synthetic)
    input_a_pad = np.concatenate([np.zeros(emb_dim, dtype=np.float32), ax_a])
    input_b_pad = np.concatenate([np.zeros(emb_dim, dtype=np.float32), ax_b])
    q_a = agent.predict(input_a_pad)
    q_b = agent.predict(input_b_pad)
    choice = "B" if q_b > q_a else "A"
    is_correct = (choice == "B")  # B is truth for traps
    if is_correct: ood_correct += 1
    print(f"  OOD-Trap {s['id']} ({s['target_axis']}): "
          f"Q_A={q_a:+.2f} Q_B={q_b:+.2f} choice={choice} "
          f"{'✓' if is_correct else '✗'}")
    ood_details.append({"id": s["id"], "target_axis": s["target_axis"],
                         "q_a": q_a, "q_b": q_b, "choice": choice,
                         "correct": is_correct})

print(f"\n  OOD Trap performance: {ood_correct}/{len(ood_traps)} = "
      f"{100*ood_correct/len(ood_traps):.1f}%")

# ── learned weights ─────────────────────────────────────────────────────────
print(f"\n[Learned axis weights — barrier-axial agent]")
W_ax = agent.W[384:389, 0]
print(f"  bias: {agent.b[0]:+.3f}")
for ax, w in zip(AXES, W_ax):
    bar = "█" * min(int(abs(w) * 15), 30)
    sign = "+" if w >= 0 else "-"
    print(f"    {ax.upper():<10} = {w:+7.3f}  {bar} ({sign})")
print(f"  Σ = {W_ax.sum():+.3f}")

# Embedding contribution
W_emb = agent.W[:emb_dim, 0]
print(f"\n  Embedding L2 norm: {np.linalg.norm(W_emb):.3f}  "
      f"(median |w|: {np.median(np.abs(W_emb)):.4f})")

# ── save ────────────────────────────────────────────────────────────────────
out = {
    "config": {"agent": "Axial barrier (389→1, skip-on-veto)",
               "input_dim": input_dim, "episodes": config.EPISODES,
               "lr": config.LEARNING_RATE},
    "training_log": training_log,
    "training_meta": {
        "total_steps": total_steps,
        "skipped_veto": skipped_veto_count,
        "skip_rate": skipped_veto_count / total_steps,
    },
    "eval_id_test": {
        "mean": float(np.mean(rewards)),
        "correct_pct": correct/len(test_s)*100,
        "clean_pct": len(clean)/len(test_s)*100,
        "phase2_mean": float(np.mean([e['reward'] for e in clean])) if clean else None,
    },
    "eval_id_traps": {"correct": id_correct, "total": len(id_traps),
                       "pct": 100*id_correct/len(id_traps) if id_traps else 0},
    "eval_ood_traps": {"correct": ood_correct, "total": len(ood_traps),
                        "pct": 100*ood_correct/len(ood_traps) if ood_traps else 0,
                        "details": ood_details},
    "learned_weights": {
        "bias": float(agent.b[0]),
        "axis_weights": {ax: float(w) for ax, w in zip(AXES, W_ax)},
        "axis_weight_sum": float(W_ax.sum()),
        "embedding_l2_norm": float(np.linalg.norm(W_emb)),
        "embedding_median_abs": float(np.median(np.abs(W_emb))),
    },
}
with open("results/evaluation_results_axial_barrier.json", "w") as f:
    json.dump(out, f, indent=2)
print(f"\n✓ Saved → results/evaluation_results_axial_barrier.json")
