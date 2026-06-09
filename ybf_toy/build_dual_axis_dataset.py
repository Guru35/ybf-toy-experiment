"""
Phase 1C — Dual-axis (GERCEKLIK + SINIR) DPO dataset builder.

Per directive `Dual-Axis Pipeline` (2026-06-09):

  Step 1: Verify existing 5-axis cache has gerceklik + sinir per
          scenario_N_action_{A,B}. Skip re-scoring (zero API cost).
  Step 2: Compute 9-bucket combination distribution of (Δgerceklik, Δsinir).
  Step 3: Build DPO datasets with the VETO rule (any -1 axis → rejected),
          fallback to combined-score tiebreak.

Output files:
  data/dual_axis_scores.jsonl       — flat per-scenario dual scores
  data/dual_axis_distribution.json  — 9-bucket counts + train/test/conflict split
  data/ybf_dual_dpo_train.jsonl     — 80% decisive pairs, TRL-ready
  data/ybf_dual_dpo_test.jsonl      — 20% held-out
  data/ybf_dual_dpo_conflict.jsonl  — only (+1,-1) and (-1,+1) — veto-test subset
"""

import json
import random
from pathlib import Path
from collections import Counter, defaultdict

CACHE_PATH        = "data/scores_cache.json"
SCENARIOS_PATH    = "data/scenarios.json"
SCORES_OUT        = "data/dual_axis_scores.jsonl"
DIST_OUT          = "data/dual_axis_distribution.json"
TRAIN_OUT         = "data/ybf_dual_dpo_train.jsonl"
TEST_OUT          = "data/ybf_dual_dpo_test.jsonl"
CONFLICT_OUT      = "data/ybf_dual_dpo_conflict.jsonl"
SEED              = 42

PROMPT_TEMPLATE = """Situation: {situation}

Intention: {intention}

Among possible responses, the one most aligned with the YBF GERCEKLIK (reality) and SINIR (boundary) axes jointly is:"""


def bucket_key(delta_g, delta_s):
    """Map (Δg, Δs) ∈ {−2,−1,0,1,2}² → 9-bucket triadic key."""
    def sign(x):
        return 1 if x > 0 else (-1 if x < 0 else 0)
    g, s = sign(delta_g), sign(delta_s)
    g_str = f"{g:+d}" if g != 0 else " 0"
    s_str = f"{s:+d}" if s != 0 else " 0"
    return f"({g_str},{s_str})"


def assign_chosen_rejected(moral_g, moral_s, immoral_g, immoral_s):
    """Veto rule first, then combined score. Returns (chosen, rejected) labels
    or None if the pair is undecidable (both vetoed or perfect tie)."""
    moral_vetoed   = (moral_g == -1) or (moral_s == -1)
    immoral_vetoed = (immoral_g == -1) or (immoral_s == -1)

    if moral_vetoed and not immoral_vetoed:
        return "immoral", "moral"     # rare but possible
    if immoral_vetoed and not moral_vetoed:
        return "moral", "immoral"
    if moral_vetoed and immoral_vetoed:
        return None                   # both vetoed → skip

    moral_total   = moral_g + moral_s
    immoral_total = immoral_g + immoral_s
    if moral_total > immoral_total:
        return "moral", "immoral"
    if immoral_total > moral_total:
        return "immoral", "moral"
    return None                       # exact tie → skip


def main():
    # ── Step 1: load cache + scenarios, extract dual scores
    cache = json.load(open(CACHE_PATH))
    scenarios = json.load(open(SCENARIOS_PATH))
    print(f"╔{'═'*64}╗")
    print(f"║ Phase 1C — Dual-axis (GERCEKLIK + SINIR) dataset builder")
    print(f"╠{'═'*64}╣")
    print(f"║ Cache entries:   {len(cache)}")
    print(f"║ Scenarios:       {len(scenarios)}")

    flat = []
    missing = 0
    for s in scenarios:
        sid = s["id"]
        key_a = f"scenario_{sid}_action_A"
        key_b = f"scenario_{sid}_action_B"
        a, b = cache.get(key_a), cache.get(key_b)
        if not (a and b):
            missing += 1
            continue
        flat.append({
            "scenario_id":       sid,
            "situation":         s["situation"],
            "intention":         s["intention"],
            "moral_action":      s["options"]["A"],
            "immoral_action":    s["options"]["B"],
            "moral_gerceklik":   a["gerceklik"],
            "moral_sinir":       a["sinir"],
            "immoral_gerceklik": b["gerceklik"],
            "immoral_sinir":     b["sinir"],
        })
    print(f"║ Dual-scored:     {len(flat)}  (missing: {missing})")

    with open(SCORES_OUT, "w") as f:
        for rec in flat:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    print(f"║ ✓ {SCORES_OUT}")

    # ── Step 2: 9-bucket distribution by (sign(Δg), sign(Δs))
    buckets = defaultdict(list)
    for rec in flat:
        dg = rec["moral_gerceklik"]   - rec["immoral_gerceklik"]
        ds = rec["moral_sinir"]       - rec["immoral_sinir"]
        buckets[bucket_key(dg, ds)].append(rec["scenario_id"])

    expected_keys = [
        "(+1,+1)", "(+1, 0)", "(+1,-1)",
        "( 0,+1)", "( 0, 0)", "( 0,-1)",
        "(-1,+1)", "(-1, 0)", "(-1,-1)",
    ]
    print(f"╠{'═'*64}╣")
    print(f"║ Distribution by (sign(Δgerceklik), sign(Δsinir)):")
    print(f"║   sign(Δg)\\sign(Δs):    -1       0      +1")
    rows = {"+1": [], " 0": [], "-1": []}
    for g in ("+1", " 0", "-1"):
        for s in (" -1", "  0", " +1"):
            # Adjusted to match keys above: bucket_key produces "(+1,+1)" etc.
            pass
    for k in expected_keys:
        n = len(buckets.get(k, []))
        print(f"║     {k}: {n:>4d}")

    under_threshold = [k for k in expected_keys
                       if k not in {"( 0, 0)"} and len(buckets.get(k, [])) < 30]
    if under_threshold:
        print(f"║ ⚠  Below 30-pair threshold: {under_threshold}")
        print(f"║    (decisive-pair buckets; '( 0, 0)' excluded — it's intentionally skipped)")

    # ── Step 3: assign chosen/rejected, build DPO pairs
    decisive = []
    skipped_both_veto = 0
    skipped_tied      = 0
    veto_pairs        = []
    chosen_label_counts = Counter()
    for rec in flat:
        result = assign_chosen_rejected(
            rec["moral_gerceklik"], rec["moral_sinir"],
            rec["immoral_gerceklik"], rec["immoral_sinir"],
        )
        if result is None:
            if (rec["moral_gerceklik"] == -1 or rec["moral_sinir"] == -1) and \
               (rec["immoral_gerceklik"] == -1 or rec["immoral_sinir"] == -1):
                skipped_both_veto += 1
            else:
                skipped_tied += 1
            continue

        chosen_label, rejected_label = result
        chosen_label_counts[chosen_label] += 1

        chosen_text   = rec[f"{chosen_label}_action"]
        rejected_text = rec[f"{rejected_label}_action"]
        chosen_g      = rec[f"{chosen_label}_gerceklik"]
        chosen_s      = rec[f"{chosen_label}_sinir"]
        rejected_g    = rec[f"{rejected_label}_gerceklik"]
        rejected_s    = rec[f"{rejected_label}_sinir"]
        dg = rec["moral_gerceklik"]   - rec["immoral_gerceklik"]
        ds = rec["moral_sinir"]       - rec["immoral_sinir"]

        pair = {
            "prompt":   PROMPT_TEMPLATE.format(
                situation=rec["situation"].strip(),
                intention=rec["intention"].strip(),
            ),
            "chosen":   " " + chosen_text.strip(),
            "rejected": " " + rejected_text.strip(),
            "_meta": {
                "scenario_id":      rec["scenario_id"],
                "chosen_label":     chosen_label,
                "bucket":           bucket_key(dg, ds),
                "chosen_g":         chosen_g,
                "chosen_s":         chosen_s,
                "rejected_g":       rejected_g,
                "rejected_s":       rejected_s,
                "veto_triggered":   (rejected_g == -1 or rejected_s == -1),
            },
        }
        decisive.append(pair)
        if pair["_meta"]["bucket"] in ("(+1,-1)", "(-1,+1)"):
            veto_pairs.append(pair)

    print(f"╠{'═'*64}╣")
    print(f"║ Decisive pairs:           {len(decisive)}")
    print(f"║   moral chosen:           {chosen_label_counts['moral']}")
    print(f"║   immoral chosen:         {chosen_label_counts['immoral']}   (veto-driven)")
    print(f"║ Skipped — both vetoed:    {skipped_both_veto}")
    print(f"║ Skipped — exact tie:      {skipped_tied}")
    print(f"║ Conflict pairs (±1/∓1):   {len(veto_pairs)}")

    # ── Step 4: deterministic shuffle + 80/20 split
    random.seed(SEED)
    random.shuffle(decisive)
    cut = int(len(decisive) * 0.8)
    train_pairs = decisive[:cut]
    test_pairs  = decisive[cut:]

    def save(path, pairs, strip_meta=True):
        with open(path, "w") as f:
            for p in pairs:
                out = {k: v for k, v in p.items() if not (strip_meta and k.startswith("_"))}
                f.write(json.dumps(out, ensure_ascii=False) + "\n")

    save(TRAIN_OUT, train_pairs)
    save(TEST_OUT,  test_pairs)
    save(CONFLICT_OUT, veto_pairs, strip_meta=False)  # keep _meta for analysis
    save(TRAIN_OUT.replace(".jsonl", "_full.jsonl"), train_pairs, strip_meta=False)
    save(TEST_OUT.replace(".jsonl", "_full.jsonl"),  test_pairs,  strip_meta=False)

    distribution = {
        "axis_pair":            "gerceklik × sinir",
        "build_date":           "2026-06-09",
        "total_scenarios":      len(flat),
        "bucket_counts":        {k: len(buckets.get(k, [])) for k in expected_keys},
        "decisive_pairs":       len(decisive),
        "moral_chosen":         chosen_label_counts["moral"],
        "immoral_chosen_veto":  chosen_label_counts["immoral"],
        "skipped_both_veto":    skipped_both_veto,
        "skipped_tied":         skipped_tied,
        "conflict_pairs":       len(veto_pairs),
        "train_n":              len(train_pairs),
        "test_n":               len(test_pairs),
        "split_seed":           SEED,
        "veto_rule":            "any axis = -1 → action is rejected (overrides total-score tiebreak)",
        "prompt_template":      PROMPT_TEMPLATE,
    }
    with open(DIST_OUT, "w") as f:
        json.dump(distribution, f, indent=2)

    print(f"╠{'═'*64}╣")
    print(f"║ Train: {len(train_pairs)}  Test: {len(test_pairs)}  Conflict (held-aside): {len(veto_pairs)}")
    print(f"║ ✓ {TRAIN_OUT}")
    print(f"║ ✓ {TEST_OUT}")
    print(f"║ ✓ {CONFLICT_OUT}")
    print(f"║ ✓ {DIST_OUT}")
    print(f"╚{'═'*64}╝")


if __name__ == "__main__":
    main()
