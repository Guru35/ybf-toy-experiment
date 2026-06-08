"""
YBF-TOY 5th run — Axial agent with per-axis input feeding.

Input: emb (384) + axis_vec_of_chosen_action (5) = 389-dim.
Q-net is a SINGLE scalar output; called twice per scenario (once per action's
input vector) and argmax selects.

No new API calls — cache from prior full run is reused.

Specific reporting: for each of the 4 traps, print Q_A vs Q_B with axis
vectors so we can see whether the agent's Q properly orders B above A when
B's axes are clearly better.
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

# ── input helper ─────────────────────────────────────────────────────────────
def get_axis_vec(cache, scenario_id, action):
    entry = cache.get(_cache_key(scenario_id, action), {})
    return np.array([entry.get(a, 0) for a in AXES], dtype=np.float32)

def make_inputs(emb, cache, sid):
    """Returns (input_a, input_b), both 389-dim."""
    ax_a = get_axis_vec(cache, sid, "A")
    ax_b = get_axis_vec(cache, sid, "B")
    return np.concatenate([emb, ax_a]), np.concatenate([emb, ax_b])

# ── load ─────────────────────────────────────────────────────────────────────
print("="*60)
print("YBF-TOY 5th RUN — AXIAL AGENT (389-dim per-axis input)")
print("="*60)

train_s, test_s, all_s = load_and_split_scenarios(
    total=config.TOTAL_SCENARIOS, seed=config.RANDOM_SEED,
    train_ratio=config.TRAIN_RATIO,
)
cache = load_cache()
embeddings = compute_embeddings(all_s)
emb_dim = embeddings.shape[1]
input_dim = emb_dim + 5
print(f"\n  Embedding dim: {emb_dim} | + 5 axis = input dim: {input_dim}")

assert len(cache) == 2 * len(all_s), \
    f"Cache incomplete: {len(cache)}/{2*len(all_s)}"

# ── train ────────────────────────────────────────────────────────────────────
agent = YBFAgentAxial(input_dim=input_dim)

print(f"\n[Train] {config.EPISODES} episodes × {len(train_s)} scenarios")
epsilon = config.EPSILON_START
training_log = []

def better_action_by_reward(cache, sid):
    r_a = cache[_cache_key(sid, "A")]["reward"]
    r_b = cache[_cache_key(sid, "B")]["reward"]
    return "A" if r_a >= r_b else "B"

for ep in range(config.EPISODES):
    ep_rewards, correct = [], 0
    indices = list(range(len(train_s)))
    random.shuffle(indices)
    for idx in indices:
        s = train_s[idx]
        emb = embeddings[s["embed_idx"]]
        input_a, input_b = make_inputs(emb, cache, s["id"])
        action = agent.choose_action(input_a, input_b, epsilon)
        reward = cache[_cache_key(s["id"], action)]["reward"]
        agent.update(input_a if action == "A" else input_b, reward, config.LEARNING_RATE)
        ep_rewards.append(reward)
        if action == better_action_by_reward(cache, s["id"]):
            correct += 1
    epsilon = max(config.EPSILON_END, epsilon * config.EPSILON_DECAY)
    avg_r = float(np.mean(ep_rewards))
    acc = correct / len(train_s) * 100
    training_log.append({"episode": ep+1, "avg_reward": round(avg_r, 4),
                          "correct_pct": round(acc, 2), "epsilon": round(epsilon, 4)})
    print(f"  Ep {ep+1}/{config.EPISODES} | "
          f"avg reward: {avg_r:+6.3f} | correct: {acc:5.1f}% | ε={epsilon:.3f}")

agent.save("data/agent_axial_weights.npy")

# ── eval on test set ────────────────────────────────────────────────────────
print(f"\n[Eval] {len(test_s)} held-out test scenarios")

def eval_condition(name, choose_fn):
    rewards, entries, correct = [], [], 0
    for s in test_s:
        action = choose_fn(s)
        reward = cache[_cache_key(s["id"], action)]["reward"]
        entry  = cache[_cache_key(s["id"], action)]
        rewards.append(reward)
        entries.append(entry)
        if action == better_action_by_reward(cache, s["id"]):
            correct += 1
    return {
        "name": name, "mean": float(np.mean(rewards)),
        "std": float(np.std(rewards)), "correct_pct": correct/len(test_s)*100,
        "rewards": rewards, "entries": entries,
    }

def axial_greedy(s):
    emb = embeddings[s["embed_idx"]]
    input_a, input_b = make_inputs(emb, cache, s["id"])
    return agent.choose_action(input_a, input_b, epsilon=0.0)

def random_choice(s): return random.choice(["A", "B"])
def always_a(s):      return "A"

results = {
    "trained":  eval_condition("Trained Agent (Axial)", axial_greedy),
    "random":   eval_condition("Random Baseline", random_choice),
    "always_a": eval_condition("Always-A Baseline", always_a),
}

def phase_metrics(entries):
    clean = [e for e in entries if not any(e[ax] == -1 for ax in AXES)]
    return {
        "clean_pct": len(clean)/len(entries)*100,
        "phase2_mean": float(np.mean([e["reward"] for e in clean])) if clean else None,
    }

for k, r in results.items():
    p = phase_metrics(r["entries"])
    print(f"  {r['name']:25s} mean={r['mean']:+.3f}  std={r['std']:.3f}  "
          f"correct={r['correct_pct']:5.1f}%  clean={p['clean_pct']:.1f}%  "
          f"P2={(p['phase2_mean'] if p['phase2_mean'] is not None else 0):.3f}")

# ── permutation test ────────────────────────────────────────────────────────
def permutation_p(a, b, n=1000):
    a, b = np.asarray(a), np.asarray(b)
    diff = a.mean() - b.mean()
    combined = np.concatenate([a, b])
    rng = np.random.default_rng(42)
    count = 0
    for _ in range(n):
        perm = rng.permutation(combined)
        if perm[:len(a)].mean() - perm[len(a):].mean() >= diff:
            count += 1
    return diff, count / n

delta, pval = permutation_p(results["trained"]["rewards"], results["random"]["rewards"])
print(f"\n  Delta (trained - random): {delta:+.3f}  p-value: {pval:.3f}")

delta_aa, pval_aa = permutation_p(results["trained"]["rewards"], results["always_a"]["rewards"])
print(f"  Delta (trained - Always-A): {delta_aa:+.3f}  p-value: {pval_aa:.3f}")

# ── TRAP analysis (the headline) ────────────────────────────────────────────
print(f"\n[Traps] Test set, where reward(B) > reward(A)")
traps = [s for s in test_s
         if cache[_cache_key(s["id"], "B")]["reward"] >
            cache[_cache_key(s["id"], "A")]["reward"]]
print(f"  Found {len(traps)} traps in test set\n")

agent_trap_correct = 0
for i, s in enumerate(traps, 1):
    emb = embeddings[s["embed_idx"]]
    input_a, input_b = make_inputs(emb, cache, s["id"])
    q_a = agent.predict(input_a)
    q_b = agent.predict(input_b)
    choice = agent.choose_action(input_a, input_b, epsilon=0.0)
    correct = (choice == "B")
    if correct: agent_trap_correct += 1
    ax_a = get_axis_vec(cache, s["id"], "A")
    ax_b = get_axis_vec(cache, s["id"], "B")
    r_a = cache[_cache_key(s["id"], "A")]["reward"]
    r_b = cache[_cache_key(s["id"], "B")]["reward"]
    print(f"  TRAP {i} — scenario {s['id']}  (B better: r_A={r_a:+.0f} vs r_B={r_b:+.0f})")
    print(f"    A axes: G={int(ax_a[0]):+d} O={int(ax_a[1]):+d} Sa={int(ax_a[2]):+d} "
          f"Si={int(ax_a[3]):+d} Öz={int(ax_a[4]):+d}  → Q_A={q_a:+.3f}")
    print(f"    B axes: G={int(ax_b[0]):+d} O={int(ax_b[1]):+d} Sa={int(ax_b[2]):+d} "
          f"Si={int(ax_b[3]):+d} Öz={int(ax_b[4]):+d}  → Q_B={q_b:+.3f}")
    print(f"    Choice: {choice}  gap(Q_B - Q_A)={q_b - q_a:+.3f}  "
          f"{'✓ CORRECT' if correct else '✗ WRONG'}\n")

print(f"  Trap performance: {agent_trap_correct}/{len(traps)} = "
      f"{agent_trap_correct/len(traps)*100:.1f}%")

# ── per-axis profile ────────────────────────────────────────────────────────
print(f"\n[Per-axis profile — trained agent's test choices]")
per_axis = {ax: [] for ax in AXES}
for s in test_s:
    emb = embeddings[s["embed_idx"]]
    input_a, input_b = make_inputs(emb, cache, s["id"])
    action = agent.choose_action(input_a, input_b, epsilon=0.0)
    entry = cache[_cache_key(s["id"], action)]
    for ax in AXES:
        per_axis[ax].append(entry[ax])
for ax in AXES:
    print(f"  {ax.upper():<10}  mean = {np.mean(per_axis[ax]):+.3f}")

# ── save ────────────────────────────────────────────────────────────────────
out = {
    "config": {"agent": "Axial linear (389→1)", "episodes": config.EPISODES,
               "lr": config.LEARNING_RATE, "input_dim": input_dim},
    "training_log": training_log,
    "eval": {k: {kk: vv for kk, vv in r.items() if kk not in ("rewards","entries")}
             for k, r in results.items()},
    "trap_performance": {"correct": agent_trap_correct, "total": len(traps),
                          "pct": agent_trap_correct/len(traps)*100 if traps else 0},
    "per_axis_mean": {ax: float(np.mean(per_axis[ax])) for ax in AXES},
    "stats": {"delta_vs_random": float(delta), "p_value_vs_random": float(pval),
              "delta_vs_always_a": float(delta_aa), "p_value_vs_always_a": float(pval_aa)},
}
path = os.path.join(config.RESULTS_DIR, "evaluation_results_axial.json")
with open(path, "w") as f:
    json.dump(out, f, indent=2)
print(f"\n✓ Saved → {path}")
