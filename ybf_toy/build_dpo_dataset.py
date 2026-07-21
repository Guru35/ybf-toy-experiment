"""
Faz 1 — Build DPO preference dataset from YBF-scored cache.

INPUT:
  data/scenarios.json         (1200 Moral Stories scenarios, split 960/240)
  data/scores_cache.json      (2400 YBF-scored actions, 5 axes each)
  data/ood_traps_filtered.json (10 synthetic OOD ONUR traps)

OUTPUT:
  data/ybf_dpo_train.jsonl    (preference pairs for training)
  data/ybf_dpo_test.jsonl     (held-out pairs for evaluation)
  data/ybf_dpo_meta.json      (statistics + audit trail)

PREFERENCE PAIR RULE:
  For each scenario with reward(A) != reward(B):
    chosen   = action text with higher YBF reward
    rejected = action text with lower YBF reward
  Ties (reward(A) == reward(B)) excluded — no preference signal.

UPWEIGHTING:
  ID traps (4) and OOD ONUR traps (10) each duplicated 5×.
  Goal: prevent small model from collapsing to Always-A baseline.

IMPORTANT CAVEAT (propagated from §3.8):
  These pairs are derived from Haiku's YBF scoring. The GERCEKLIK scorer-level
  fidelity gap (§3.8) is INHERITED by the fine-tuned model. Specifically:
  any reality-denial-vs-acceptance scenarios in Moral Stories get Haiku's
  "comforting=moral" prior, not true YBF GERCEKLIK. Fine-tuned model will
  reproduce this gap. This is methodological honesty, not a bug.
"""

import json
from collections import Counter

AXES = ["gerceklik", "onur", "saygi", "sinir", "ozgurluk"]
TRAP_UPWEIGHT = 5  # each trap appears this many times in training

# Prompt template — language model completion style
# Designed to be model-agnostic: works for both base and instruct-tuned LLMs
PROMPT_TEMPLATE = """Situation: {situation}

Intention: {intention}

Among possible responses, the one most aligned with consciousness expansion (YBF) is:"""


def build_prompt(s):
    return PROMPT_TEMPLATE.format(
        situation=s["situation"].strip(),
        intention=s["intention"].strip(),
    )


def make_pair(scenario, scores_cache, source_tag):
    """
    Returns a DPO pair dict, or None if reward(A) == reward(B).
    """
    sid = scenario["id"]
    key_a = f"scenario_{sid}_action_A"
    key_b = f"scenario_{sid}_action_B"
    a_entry = scores_cache.get(key_a)
    b_entry = scores_cache.get(key_b)
    if not a_entry or not b_entry:
        return None
    r_a, r_b = a_entry["reward"], b_entry["reward"]
    if r_a == r_b:
        return None  # no preference signal

    if r_a > r_b:
        chosen_action, chosen_axes, chosen_r = scenario["options"]["A"], a_entry, r_a
        rejected_action, rejected_axes, rejected_r = scenario["options"]["B"], b_entry, r_b
        chosen_letter = "A"
    else:
        chosen_action, chosen_axes, chosen_r = scenario["options"]["B"], b_entry, r_b
        rejected_action, rejected_axes, rejected_r = scenario["options"]["A"], a_entry, r_a
        chosen_letter = "B"

    return {
        "prompt": build_prompt(scenario),
        "chosen": " " + chosen_action.strip(),    # leading space helps tokenizers
        "rejected": " " + rejected_action.strip(),
        "_meta": {
            "scenario_id": sid,
            "source": source_tag,        # id_train / id_test / ood_onur
            "trap": (chosen_letter == "B"),
            "chosen_letter": chosen_letter,
            "reward_chosen": chosen_r,
            "reward_rejected": rejected_r,
            "reward_gap": chosen_r - rejected_r,
            "axes_chosen": {ax: chosen_axes[ax] for ax in AXES},
            "axes_rejected": {ax: rejected_axes[ax] for ax in AXES},
            "veto_rejected": rejected_axes.get("veto", False),
        },
    }


# ── Load ────────────────────────────────────────────────────────────────────

with open("data/scenarios.json") as f:
    scenarios = json.load(f)
with open("data/scores_cache.json") as f:
    scores_cache = json.load(f)
with open("data/ood_traps_filtered.json") as f:
    ood_traps = json.load(f)

n_total = len(scenarios)
split = int(n_total * 0.8)
train_scenarios = scenarios[:split]    # 960
test_scenarios = scenarios[split:]      # 240

print(f"Sources:")
print(f"  ID train scenarios: {len(train_scenarios)}")
print(f"  ID test scenarios:  {len(test_scenarios)}")
print(f"  OOD ONUR traps:     {len(ood_traps)}")

# ── Build pairs ─────────────────────────────────────────────────────────────

print(f"\n[Build] ID training pairs...")
train_pairs = []
for s in train_scenarios:
    pair = make_pair(s, scores_cache, source_tag="id_train")
    if pair:
        train_pairs.append(pair)
print(f"  {len(train_pairs)} pairs (skipped {len(train_scenarios) - len(train_pairs)} ties)")

print(f"\n[Build] ID test pairs...")
test_pairs = []
for s in test_scenarios:
    pair = make_pair(s, scores_cache, source_tag="id_test")
    if pair:
        test_pairs.append(pair)
print(f"  {len(test_pairs)} pairs (skipped {len(test_scenarios) - len(test_pairs)} ties)")

# ── OOD ONUR traps: need synthetic scoring (already in ood_traps_filtered) ──
print(f"\n[Build] OOD ONUR trap pairs...")
ood_pairs = []
for s in ood_traps:
    # OOD format differs: scores embedded in s["scores_A"] / s["scores_B"]
    sid = s["id"]
    a_entry = {**s["scores_A"], "veto": s["scores_A"].get("veto", False)}
    b_entry = {**s["scores_B"], "veto": s["scores_B"].get("veto", False)}
    r_a, r_b = a_entry["reward"], b_entry["reward"]
    if r_a == r_b:
        continue
    if r_a > r_b:
        chosen = s["options"]["A"]; chosen_axes = a_entry; chosen_r = r_a
        rejected = s["options"]["B"]; rejected_axes = b_entry; rejected_r = r_b
        chosen_letter = "A"
    else:
        chosen = s["options"]["B"]; chosen_axes = b_entry; chosen_r = r_b
        rejected = s["options"]["A"]; rejected_axes = a_entry; rejected_r = r_a
        chosen_letter = "B"
    ood_pairs.append({
        "prompt": build_prompt(s),
        "chosen": " " + chosen.strip(),
        "rejected": " " + rejected.strip(),
        "_meta": {
            "scenario_id": sid, "source": "ood_onur",
            "trap": (chosen_letter == "B"),
            "chosen_letter": chosen_letter,
            "reward_chosen": chosen_r, "reward_rejected": rejected_r,
            "reward_gap": chosen_r - rejected_r,
            "axes_chosen": {ax: chosen_axes[ax] for ax in AXES},
            "axes_rejected": {ax: rejected_axes[ax] for ax in AXES},
            "veto_rejected": rejected_axes.get("veto", False),
            "target_axis": s.get("target_axis"),
        },
    })
print(f"  {len(ood_pairs)} OOD pairs")

# ── Upweight traps ──────────────────────────────────────────────────────────
print(f"\n[Upweight] Duplicating trap pairs {TRAP_UPWEIGHT}×")
train_traps_id = [p for p in train_pairs if p["_meta"]["trap"]]
print(f"  ID train traps:  {len(train_traps_id)}")
print(f"  OOD train traps: {len(ood_pairs)}")

augmented_train = list(train_pairs)
for trap in train_traps_id:
    for _ in range(TRAP_UPWEIGHT - 1):  # already in train_pairs once
        augmented_train.append(trap)
# NOTE: OOD pairs intentionally NOT added to training set.
# They are held out as a held-out OOD evaluation set so we can measure
# generalization beyond the trained distribution. (Pre-fix had this wrong;
# OOD in training defeats the purpose of OOD evaluation.)

print(f"  Final train pair count: {len(augmented_train)} "
      f"(was {len(train_pairs)} before upweighting)")

# ── Stats ───────────────────────────────────────────────────────────────────
print(f"\n[Stats] Final training set composition:")
sources = Counter(p["_meta"]["source"] for p in augmented_train)
traps = sum(1 for p in augmented_train if p["_meta"]["trap"])
unique_traps = sum(1 for p in augmented_train if p["_meta"]["trap"]) // TRAP_UPWEIGHT
print(f"  By source: {dict(sources)}")
print(f"  Trap pairs:        {traps}/{len(augmented_train)} ({100*traps/len(augmented_train):.1f}%)")
print(f"  Reward gap distribution:")
gaps = Counter(int(p["_meta"]["reward_gap"]) for p in augmented_train)
for g in sorted(gaps.keys()):
    print(f"    Δr={g:+d}: {gaps[g]} pairs")

print(f"\n[Stats] Test set ({len(test_pairs)} pairs):")
test_traps = sum(1 for p in test_pairs if p["_meta"]["trap"])
print(f"  Trap pairs: {test_traps}/{len(test_pairs)} ({100*test_traps/len(test_pairs):.1f}%)")

# ── Save ────────────────────────────────────────────────────────────────────

def save_jsonl(path, pairs, strip_meta=False):
    with open(path, "w") as f:
        for p in pairs:
            if strip_meta:
                clean = {k: v for k, v in p.items() if not k.startswith("_")}
                f.write(json.dumps(clean, ensure_ascii=False) + "\n")
            else:
                f.write(json.dumps(p, ensure_ascii=False) + "\n")

# Full dataset with metadata (for our analysis)
save_jsonl("data/ybf_dpo_train_full.jsonl", augmented_train)
save_jsonl("data/ybf_dpo_test_full.jsonl", test_pairs)
save_jsonl("data/ybf_dpo_ood_full.jsonl", ood_pairs)

# TRL-ready dataset (strip _meta — TRL DPOTrainer only needs prompt/chosen/rejected)
save_jsonl("data/ybf_dpo_train.jsonl", augmented_train, strip_meta=True)
save_jsonl("data/ybf_dpo_test.jsonl", test_pairs, strip_meta=True)
save_jsonl("data/ybf_dpo_ood.jsonl", ood_pairs, strip_meta=True)

# Sample inspection file
samples = {
    "id_train_example": next(p for p in augmented_train if p["_meta"]["source"] == "id_train" and not p["_meta"]["trap"]),
    "id_trap_example": next((p for p in augmented_train if p["_meta"]["source"] == "id_train" and p["_meta"]["trap"]), None),
    "ood_trap_example": next((p for p in augmented_train if p["_meta"]["source"] == "ood_onur"), None),
}

with open("data/ybf_dpo_samples.json", "w") as f:
    json.dump(samples, f, indent=2, ensure_ascii=False)

# Audit trail
meta = {
    "build_date": "2026-06-08",
    "source_caches": {
        "scenarios": "data/scenarios.json",
        "ybf_scores": "data/scores_cache.json (2400 entries)",
        "ood_traps": "data/ood_traps_filtered.json (10 ONUR pairs)",
    },
    "split": {
        "train_scenarios": len(train_scenarios),
        "test_scenarios": len(test_scenarios),
        "train_pairs_unique": len(train_pairs),
        "test_pairs": len(test_pairs),
        "ood_pairs_unique": len(ood_pairs),
    },
    "upweighting": {
        "factor": TRAP_UPWEIGHT,
        "train_id_traps": len(train_traps_id),
        "train_pairs_after_upweight": len(augmented_train),
    },
    "trap_density": {
        "train_set": f"{traps}/{len(augmented_train)} = {100*traps/len(augmented_train):.1f}%",
        "test_set": f"{test_traps}/{len(test_pairs)} = {100*test_traps/len(test_pairs):.1f}%",
        "natural_rate": f"~1.7% (4/240 in original Moral Stories test slice)",
    },
    "prompt_template": PROMPT_TEMPLATE,
    "fidelity_gap_warning": (
        "Pairs derived from Haiku scorer. GERCEKLIK scorer-fidelity gap (§3.8) "
        "propagates: any reality-denial-vs-acceptance scenarios in Moral Stories "
        "carry Haiku's 'comforting=moral' prior, not true YBF GERCEKLIK semantics. "
        "Fine-tuned model is expected to reproduce this. Methodological honesty, "
        "not a bug."
    ),
}
with open("data/ybf_dpo_meta.json", "w") as f:
    json.dump(meta, f, indent=2)

print(f"\n✓ Files written:")
print(f"  data/ybf_dpo_train.jsonl       ({len(augmented_train)} TRL-ready pairs)")
print(f"  data/ybf_dpo_test.jsonl        ({len(test_pairs)} TRL-ready pairs)")
print(f"  data/ybf_dpo_ood.jsonl         ({len(ood_pairs)} held-out OOD pairs)")
print(f"  data/ybf_dpo_train_full.jsonl  (with _meta, for analysis)")
print(f"  data/ybf_dpo_test_full.jsonl   (with _meta, for analysis)")
print(f"  data/ybf_dpo_ood_full.jsonl    (with _meta, for analysis)")
print(f"  data/ybf_dpo_samples.json      (inspection samples)")
print(f"  data/ybf_dpo_meta.json         (audit trail + caveats)")
