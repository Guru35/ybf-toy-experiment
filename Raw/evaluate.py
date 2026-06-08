"""
Evaluation module for YBF-TOY experiment.
C9: Two-phase reporting — Phase 1 (veto avoidance) vs Phase 2 (positive tuning).
"""

import random
import numpy as np
import config
from scorer import _cache_key


# ── helpers ────────────────────────────────────────────────────────────────

def _get_reward(scores_cache, sid, action_key):
    return scores_cache[_cache_key(sid, action_key)]["reward"]


def _better_action(scores_cache, scenario):
    r_a = _get_reward(scores_cache, scenario["id"], "A")
    r_b = _get_reward(scores_cache, scenario["id"], "B")
    return "A" if r_a >= r_b else "B"


def _is_trap(scores_cache, scenario):
    """B actually scores higher than A — counterintuitive."""
    r_a = _get_reward(scores_cache, scenario["id"], "A")
    r_b = _get_reward(scores_cache, scenario["id"], "B")
    return r_b > r_a


def _phase_metrics(chosen_rewards: list[float]) -> dict:
    """
    C9: Split reward list into Phase 1 and Phase 2 metrics.
    Phase 1: veto avoidance  (did we avoid -10?)
    Phase 2: positive tuning (among non-vetoed, mean score)
    """
    veto_r = config.VETO_REWARD
    total  = len(chosen_rewards)
    vetoed = [r for r in chosen_rewards if r == veto_r]
    clean  = [r for r in chosen_rewards if r != veto_r]

    return {
        "phase1_veto_avoided_pct": round((1 - len(vetoed) / total) * 100, 2),
        "phase2_mean_clean":       round(float(np.mean(clean)), 4) if clean else None,
        "phase2_std_clean":        round(float(np.std(clean)),  4) if clean else None,
    }


# ── evaluation conditions ──────────────────────────────────────────────────

def _eval_agent(agent, test_scenarios, embeddings, scores_cache):
    rewards, correct = [], []
    for s in test_scenarios:
        emb    = embeddings[s["embed_idx"]]  # C4
        action = agent.choose_action(emb, epsilon=0.0)
        reward = _get_reward(scores_cache, s["id"], action)
        rewards.append(reward)
        correct.append(action == _better_action(scores_cache, s))

    entries = [scores_cache[_cache_key(s["id"],
               agent.choose_action(embeddings[s["embed_idx"]], epsilon=0.0))]
              for s in test_scenarios]
    return {
        "mean_reward":   round(float(np.mean(rewards)), 4),
        "std_reward":    round(float(np.std(rewards)),  4),
        "correct_pct":   round(sum(correct) / len(correct) * 100, 2),
        "rewards_list":  rewards,
        **_phase_metrics(entries),
    }


def _eval_random(test_scenarios, scores_cache, runs=5):
    """Average over multiple random runs to reduce variance."""
    all_runs = []
    for _ in range(runs):
        rewards = []
        for s in test_scenarios:
            action = random.choice(["A", "B"])
            rewards.append(_get_reward(scores_cache, s["id"], action))
        all_runs.append(rewards)

    # Mean across runs per scenario
    mean_per = [float(np.mean([r[i] for r in all_runs]))
                for i in range(len(test_scenarios))]
    flat = [r for run in all_runs for r in run]

    correct = []
    for s in test_scenarios:
        # "correct" if both choices are equally likely — use 50%
        correct.append(0.5)

    return {
        "mean_reward": round(float(np.mean(mean_per)), 4),
        "std_reward":  round(float(np.std(mean_per)),  4),
        "correct_pct": 50.0,
        "rewards_list": mean_per,
        **_phase_metrics(flat),
    }


def _eval_always_a(test_scenarios, scores_cache):
    rewards = [_get_reward(scores_cache, s["id"], "A") for s in test_scenarios]
    correct = [
        1 if _better_action(scores_cache, s) == "A" else 0
        for s in test_scenarios
    ]
    entries = [scores_cache[_cache_key(s["id"], "A")] for s in test_scenarios]
    return {
        "mean_reward": round(float(np.mean(rewards)), 4),
        "std_reward":  round(float(np.std(rewards)),  4),
        "correct_pct": round(sum(correct) / len(correct) * 100, 2),
        "rewards_list": rewards,
        **_phase_metrics(entries),
    }


# ── trap analysis ──────────────────────────────────────────────────────────

def _trap_analysis(agent, test_scenarios, embeddings, scores_cache):
    traps = [s for s in test_scenarios if _is_trap(scores_cache, s)]
    if not traps:
        return {"count": 0}

    agent_correct, random_correct = 0, 0
    for s in traps:
        best = _better_action(scores_cache, s)  # == "B" for traps
        emb  = embeddings[s["embed_idx"]]
        if agent.choose_action(emb, epsilon=0.0) == best:
            agent_correct += 1
        if random.choice(["A", "B"]) == best:
            random_correct += 1

    return {
        "count":         len(traps),
        "agent_pct":     round(agent_correct  / len(traps) * 100, 2),
        "random_pct":    round(random_correct / len(traps) * 100, 2),
    }


# ── per-axis analysis ──────────────────────────────────────────────────────

def _per_axis(agent, test_scenarios, embeddings, scores_cache):
    axes = ["gerceklik", "onur", "saygi", "sinir", "ozgurluk"]
    sums = {ax: [] for ax in axes}
    for s in test_scenarios:
        emb    = embeddings[s["embed_idx"]]
        action = agent.choose_action(emb, epsilon=0.0)
        entry  = scores_cache[_cache_key(s["id"], action)]
        for ax in axes:
            sums[ax].append(entry[ax])
    return {ax: round(float(np.mean(v)), 4) for ax, v in sums.items()}


# ── statistical test ───────────────────────────────────────────────────────

def _p_value(agent_rewards, random_rewards):
    """Simple permutation test (1000 shuffles)."""
    diff_obs = np.mean(agent_rewards) - np.mean(random_rewards)
    combined = np.array(agent_rewards + random_rewards)
    n = len(agent_rewards)
    count = 0
    rng = np.random.default_rng(42)
    for _ in range(1000):
        perm  = rng.permutation(combined)
        diff  = np.mean(perm[:n]) - np.mean(perm[n:])
        if diff >= diff_obs:
            count += 1
    return round(count / 1000, 4)


# ── public API ─────────────────────────────────────────────────────────────

def evaluate_all(agent, test_scenarios, embeddings, scores_cache) -> dict:
    """
    Returns dict with keys:
      trained_agent, random_baseline, always_a_baseline
        → {mean_reward, std_reward, correct_pct, rewards_list,
           phase1_veto_avoided_pct, phase2_mean_clean, phase2_std_clean}
      trap_analysis  → {count, agent_pct, random_pct}
      per_axis       → {gerceklik, onur, saygi, sinir, ozgurluk}
      p_value, verdict, delta, agent_vs_random
    """
    print("  Evaluating: trained agent...")
    ag = _eval_agent(agent, test_scenarios, embeddings, scores_cache)

    print("  Evaluating: random baseline (5 runs)...")
    rand = _eval_random(test_scenarios, scores_cache, runs=5)

    print("  Evaluating: always-A baseline...")
    aa = _eval_always_a(test_scenarios, scores_cache)

    print("  Computing trap analysis & per-axis stats...")
    traps    = _trap_analysis(agent, test_scenarios, embeddings, scores_cache)
    per_axis = _per_axis(agent, test_scenarios, embeddings, scores_cache)

    delta   = round(ag["mean_reward"] - rand["mean_reward"], 4)
    p_val   = _p_value(ag["rewards_list"], rand["rewards_list"])
    verdict = "PASS" if (ag["mean_reward"] > rand["mean_reward"] and p_val < 0.10) else "FAIL"

    return {
        "trained_agent":      ag,
        "random_baseline":    rand,
        "always_a_baseline":  aa,
        "trap_analysis":      traps,
        "per_axis":           per_axis,
        "delta":              delta,
        "p_value":            p_val,
        "verdict":            verdict,
        "agent_vs_random":    delta,
    }
