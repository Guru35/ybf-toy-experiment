"""Results reporting for YBF-TOY experiment."""

import json
import os
import config


def _bar(value, min_val, max_val, width=20):
    """ASCII progress bar."""
    if max_val == min_val:
        filled = 0
    else:
        filled = int((value - min_val) / (max_val - min_val) * width)
    filled = max(0, min(width, filled))
    return "█" * filled + "░" * (width - filled)


def print_results(results: dict, training_log: list):
    ag   = results["trained_agent"]
    rand = results["random_baseline"]
    aa   = results["always_a_baseline"]
    trap = results["trap_analysis"]
    pa   = results["per_axis"]

    # ── Training curve ──────────────────────────────────────────────────
    print("\nTraining Progress (avg reward per episode):")
    min_r = min(e["avg_reward"] for e in training_log)
    max_r = max(e["avg_reward"] for e in training_log)
    for e in training_log:
        bar = _bar(e["avg_reward"], min_r, max_r)
        print(f"  Ep{e['episode']} [{bar}] {e['avg_reward']:+.3f}  "
              f"correct={e['correct_pct']:5.1f}%  ε={e['epsilon']:.3f}")
    print(f"  Range: [{config.MIN_REWARD:.0f}, +{config.MAX_REWARD:.0f}]")

    # ── Main table ──────────────────────────────────────────────────────
    W = 68
    line = "═" * W
    print(f"\n╔{line}╗")
    print(f"║{'YBF-TOY EXPERIMENT RESULTS':^{W}}║")
    print(f"║{'Moral Stories · ' + str(config.TOTAL_SCENARIOS) + ' scenarios':^{W}}║")
    print(f"╠{line}╣")
    print(f"║{'CONDITION':<20} │ {'Mean Reward':^11} │ {'Std':^6} │ {'Correct%':^9} │ {'Clean%':^10}║")
    print(f"║{'─'*20}─┼─{'─'*11}─┼─{'─'*6}─┼─{'─'*9}─┼─{'─'*10}║")

    def row(label, d):
        vf = d["phase1_clean_pct"]
        return (f"║ {label:<19} │ {d['mean_reward']:^11.3f} │ "
                f"{d['std_reward']:^6.3f} │ {d['correct_pct']:^9.1f} │ {vf:^10.1f}║")

    print(row("Trained Agent",     ag))
    print(row("Random Baseline",   rand))
    print(row("Always-A Baseline", aa))
    print(f"╠{line}╣")
    print(f"║  Delta (Agent - Random): {results['delta']:+.3f}   "
          f"p-value: {results['p_value']:.3f}{'':>22}║")
    print(f"╠{line}╣")

    # C9: Two-phase breakdown
    print(f"║{'TWO-PHASE ANALYSIS (C9)':^{W}}║")
    print(f"║{'─'*W}║")
    print(f"║  Phase 1 — No Contraction (all axes ≥ 0, natural sum):{'':>21}║")
    print(f"║    Trained Agent:    {ag  ['phase1_clean_pct']:5.1f}% contraction-free{'':>32}║")
    print(f"║    Random Baseline:  {rand['phase1_clean_pct']:5.1f}% contraction-free{'':>32}║")
    print(f"║    Always-A:         {aa  ['phase1_clean_pct']:5.1f}% contraction-free{'':>32}║")
    print(f"║{'─'*W}║")
    print(f"║  Phase 2 — Positive Tuning (among veto-free actions):{'':>14}║")
    ag_p2   = ag  ['phase2_mean_clean']
    rand_p2 = rand['phase2_mean_clean']
    aa_p2   = aa  ['phase2_mean_clean']
    fmt = lambda v: f"{v:.3f}" if v is not None else "  N/A"
    print(f"║    Trained Agent:    {fmt(ag_p2):>6} mean (±{fmt(ag['phase2_std_clean'])}){'':>25}║")
    print(f"║    Random Baseline:  {fmt(rand_p2):>6} mean{'':>39}║")
    print(f"║    Always-A:         {fmt(aa_p2):>6} mean{'':>39}║")

    # Interpretation hint
    if ag["phase1_clean_pct"] > rand["phase1_clean_pct"]:
        if ag_p2 is not None and rand_p2 is not None and ag_p2 <= rand_p2 + 0.1:
            hint = "Phase 1 ↑, Phase 2 flat → learned to avoid harm; didn't learn to maximize good"
        else:
            hint = "Phase 1 ↑ and Phase 2 ↑ → full YBF alignment signal learned"
    else:
        hint = "Phase 1 flat → veto avoidance not yet learned"
    print(f"║  Interpretation: {hint[:W-20]:<{W-20}}║")

    print(f"╠{line}╣")
    if trap["count"] > 0:
        print(f"║  TRAP SCENARIOS: {trap['count']} found in test set{'':>30}║")
        print(f"║    Agent on traps:  {trap['agent_pct']:5.1f}% correct{'':>37}║")
        print(f"║    Random on traps: {trap['random_pct']:5.1f}% correct{'':>37}║")
    else:
        print(f"║  TRAP SCENARIOS: 0 found in test set{'':>30}║")
    print(f"╠{line}╣")
    print(f"║  PER-AXIS (trained agent chosen actions):{'':>26}║")
    for ax, v in pa.items():
        bar = _bar(v, -1, 1, 15)
        print(f"║    {ax.upper():<12} [{bar}] {v:+.3f}{'':>16}║")
    print(f"╠{line}╣")
    verdict_str = f"VERDICT: {results['verdict']}"
    if results["verdict"] == "PASS":
        detail = "Agent outperforms random on held-out test set."
    else:
        detail = "Agent does not significantly outperform random."
    print(f"║  {verdict_str}  —  {detail:<{W-len(verdict_str)-5}}║")
    print(f"╚{line}╝")


def save_results(results: dict, training_log: list):
    os.makedirs(config.RESULTS_DIR, exist_ok=True)

    # Remove rewards_list from saved JSON (too large)
    slim = {k: v for k, v in results.items() if k != "rewards_list"}
    for cond in ["trained_agent", "random_baseline", "always_a_baseline"]:
        if cond in slim and "rewards_list" in slim[cond]:
            slim[cond] = {k: v for k, v in slim[cond].items() if k != "rewards_list"}

    out = {
        "config": {
            "model":       config.ANTHROPIC_MODEL,
            "total":       config.TOTAL_SCENARIOS,
            "train_ratio": config.TRAIN_RATIO,
            "episodes":    config.EPISODES,
        },
        "training_log": training_log,
        "evaluation":   slim,
    }

    path_json = os.path.join(config.RESULTS_DIR, "evaluation_results.json")
    with open(path_json, "w") as f:
        json.dump(out, f, indent=2)
    print(f"\n  Results saved → {path_json}")
