"""
B — Embedding-blind ablation.

Train axial agent with input_dim = 5 (axis vector only, NO embedding).
If trap performance is unchanged from Test 5 (4/4), the embedding was
contributing nothing — pure "information limit, not architecture limit" claim
is strengthened.

Test setup mirrors main_axial.py except for input dimension.
"""

import json, random
import numpy as np

random.seed(42)
np.random.seed(42)

import config
from scorer import load_cache, _cache_key
from scenarios import load_and_split_scenarios
from agent_axial import YBFAgentAxial

AXES = ("gerceklik", "onur", "saygi", "sinir", "ozgurluk")

def get_axis_vec(cache, sid, action):
    entry = cache.get(_cache_key(sid, action), {})
    return np.array([entry.get(a, 0) for a in AXES], dtype=np.float32)

# ── load ─────────────────────────────────────────────────────────────────────
print("="*60)
print("YBF-TOY ABLATION — AXIAL AGENT, EMBEDDING-BLIND")
print("="*60)
print("\n  Input dim: 5 (axis vector only, no embedding)")

train_s, test_s, all_s = load_and_split_scenarios(
    total=config.TOTAL_SCENARIOS, seed=config.RANDOM_SEED,
    train_ratio=config.TRAIN_RATIO,
)
cache = load_cache()
assert len(cache) == 2 * len(all_s), f"Cache incomplete: {len(cache)}/{2*len(all_s)}"

# ── train ────────────────────────────────────────────────────────────────────
agent = YBFAgentAxial(input_dim=5)

print(f"\n[Train] {config.EPISODES} episodes × {len(train_s)} scenarios")
epsilon = config.EPSILON_START
training_log = []

def better_action(cache, sid):
    r_a = cache[_cache_key(sid, "A")]["reward"]
    r_b = cache[_cache_key(sid, "B")]["reward"]
    return "A" if r_a >= r_b else "B"

for ep in range(config.EPISODES):
    ep_rewards, correct = [], 0
    indices = list(range(len(train_s)))
    random.shuffle(indices)
    for idx in indices:
        s = train_s[idx]
        # NO embedding — only axis vector
        input_a = get_axis_vec(cache, s["id"], "A")
        input_b = get_axis_vec(cache, s["id"], "B")
        action = agent.choose_action(input_a, input_b, epsilon)
        reward = cache[_cache_key(s["id"], action)]["reward"]
        agent.update(input_a if action == "A" else input_b, reward, config.LEARNING_RATE)
        ep_rewards.append(reward)
        if action == better_action(cache, s["id"]):
            correct += 1
    epsilon = max(config.EPSILON_END, epsilon * config.EPSILON_DECAY)
    avg_r = float(np.mean(ep_rewards))
    acc = correct / len(train_s) * 100
    training_log.append({"episode": ep+1, "avg_reward": round(avg_r, 4),
                         "correct_pct": round(acc, 2), "epsilon": round(epsilon, 4)})
    print(f"  Ep {ep+1}/{config.EPISODES} | "
          f"avg reward: {avg_r:+6.3f} | correct: {acc:5.1f}% | ε={epsilon:.3f}")

agent.save("data/agent_axial_blind_weights.npy")

# ── eval ─────────────────────────────────────────────────────────────────────
print(f"\n[Eval] {len(test_s)} held-out test scenarios")

def axial_blind_greedy(s):
    input_a = get_axis_vec(cache, s["id"], "A")
    input_b = get_axis_vec(cache, s["id"], "B")
    return agent.choose_action(input_a, input_b, epsilon=0.0)

def random_choice(s): return random.choice(["A", "B"])
def always_a(s):      return "A"

def eval_cond(name, choose_fn):
    rewards, entries, correct = [], [], 0
    for s in test_s:
        action = choose_fn(s)
        reward = cache[_cache_key(s["id"], action)]["reward"]
        rewards.append(reward)
        entries.append(cache[_cache_key(s["id"], action)])
        if action == better_action(cache, s["id"]):
            correct += 1
    return {"name": name, "mean": float(np.mean(rewards)),
            "std": float(np.std(rewards)), "correct_pct": correct/len(test_s)*100,
            "rewards": rewards, "entries": entries}

trained_b = eval_cond("Axial Blind", axial_blind_greedy)
rand_b    = eval_cond("Random", random_choice)
aa_b      = eval_cond("Always-A", always_a)

def phase_metrics(entries):
    clean = [e for e in entries if not any(e[ax] == -1 for ax in AXES)]
    return {"clean_pct": len(clean)/len(entries)*100,
            "phase2_mean": float(np.mean([e["reward"] for e in clean])) if clean else None}

for r in [trained_b, rand_b, aa_b]:
    p = phase_metrics(r["entries"])
    print(f"  {r['name']:18s}  mean={r['mean']:+.3f}  correct={r['correct_pct']:5.1f}%  "
          f"clean={p['clean_pct']:.1f}%  P2={(p['phase2_mean'] or 0):.3f}")

# ── traps ───────────────────────────────────────────────────────────────────
print(f"\n[Traps]")
traps = [s for s in test_s
         if cache[_cache_key(s["id"], "B")]["reward"] >
            cache[_cache_key(s["id"], "A")]["reward"]]
print(f"  {len(traps)} traps in test set\n")

correct_traps = 0
trap_details = []
for i, s in enumerate(traps, 1):
    ax_a = get_axis_vec(cache, s["id"], "A")
    ax_b = get_axis_vec(cache, s["id"], "B")
    q_a = agent.predict(ax_a)
    q_b = agent.predict(ax_b)
    choice = agent.choose_action(ax_a, ax_b, epsilon=0.0)
    is_correct = (choice == "B")
    if is_correct: correct_traps += 1
    r_a = cache[_cache_key(s["id"], "A")]["reward"]
    r_b = cache[_cache_key(s["id"], "B")]["reward"]
    print(f"  TRAP {i} — scenario {s['id']}  (r_A={r_a:+.0f} vs r_B={r_b:+.0f})")
    print(f"    A axes: {[int(v) for v in ax_a]}  → Q_A={q_a:+.3f}")
    print(f"    B axes: {[int(v) for v in ax_b]}  → Q_B={q_b:+.3f}")
    print(f"    Choice: {choice}  gap={q_b-q_a:+.3f}  "
          f"{'✓ CORRECT' if is_correct else '✗ WRONG'}\n")
    trap_details.append({"id": s["id"], "axes_a": [int(v) for v in ax_a],
                          "axes_b": [int(v) for v in ax_b],
                          "q_a": q_a, "q_b": q_b, "choice": choice,
                          "correct": is_correct})

trap_pct = correct_traps / len(traps) * 100 if traps else 0
print(f"  Trap performance: {correct_traps}/{len(traps)} = {trap_pct:.1f}%")

# ── compare to Test 5 (with embedding) ──────────────────────────────────────
print("\n" + "="*60)
print("COMPARISON vs Test 5 (with embedding)")
print("="*60)

# Load Test 5 results for direct compare
try:
    test5 = json.load(open("results/evaluation_results_axial.json"))
    t5_mean = test5["eval"]["trained"]["mean"]
    t5_correct = test5["eval"]["trained"]["correct_pct"]
    t5_trap_pct = test5["trap_performance"]["pct"]
    print(f"  Test 5 (389-dim):  mean={t5_mean:+.3f}  correct={t5_correct:.1f}%  trap={t5_trap_pct:.1f}%")
    print(f"  Ablation (5-dim):  mean={trained_b['mean']:+.3f}  correct={trained_b['correct_pct']:.1f}%  trap={trap_pct:.1f}%")
    print(f"  Delta:             mean={trained_b['mean']-t5_mean:+.3f}  correct={trained_b['correct_pct']-t5_correct:+.1f}%  trap={trap_pct-t5_trap_pct:+.1f}%")
except Exception as e:
    print(f"  (couldn't load Test 5 results: {e})")

# ── learned weights ────────────────────────────────────────────────────────
print(f"\n[Learned axis weights — embedding-blind agent]")
W_ax = agent.W[:, 0]
print(f"  bias: {agent.b[0]:+.3f}")
for ax, w in zip(AXES, W_ax):
    bar_len = int(abs(w) * 15)
    bar = "█" * min(bar_len, 30)
    sign = "+" if w >= 0 else "-"
    print(f"    {ax.upper():<10} = {w:+7.3f}  {bar} ({sign})")
print(f"  Σ = {W_ax.sum():+.3f}")

# ── save ────────────────────────────────────────────────────────────────────
out = {
    "config": {"agent": "Axial blind (5→1)", "input_dim": 5,
               "episodes": config.EPISODES, "lr": config.LEARNING_RATE},
    "training_log": training_log,
    "eval": {k: {kk: vv for kk, vv in r.items() if kk not in ("rewards","entries")}
             for k, r in [("trained", trained_b), ("random", rand_b), ("always_a", aa_b)]},
    "trap_performance": {"correct": correct_traps, "total": len(traps),
                          "pct": trap_pct, "details": trap_details},
    "learned_weights": {
        "bias": float(agent.b[0]),
        "axis_weights": {ax: float(w) for ax, w in zip(AXES, W_ax)},
        "axis_weight_sum": float(W_ax.sum()),
    },
}
with open("results/evaluation_results_axial_blind.json", "w") as f:
    json.dump(out, f, indent=2)
print(f"\n✓ Saved → results/evaluation_results_axial_blind.json")
