"""
Build SINIR-decisive DPO dataset from scored scenarios.

Improvements over directive's first draft:
  [F1] Correct field references (moral_action / immoral_action)
  [F9] Deterministic shuffle before split (seed=42) — avoids order bias
  [F10] Report dataset balance + score-gap distribution
"""

import json
import random
from collections import Counter
from pathlib import Path

SCORED_PATH   = "data/raw/moral_stories_sinir_scored.jsonl"
TRAIN_PATH    = "data/ybf_sinir_dpo_train.jsonl"
TEST_PATH     = "data/ybf_sinir_dpo_test.jsonl"
META_PATH     = "data/ybf_sinir_dpo_meta.json"
SEED          = 42

# Prompt template used at fine-tune time (consistent with build_dpo_dataset.py)
PROMPT_TEMPLATE = """Situation: {situation}

Intention: {intention}

Among possible responses, the one most aligned with the YBF SINIR axis (boundary-consciousness) is:"""


def build_prompt(item):
    return PROMPT_TEMPLATE.format(
        situation=item["situation"].strip(),
        intention=item["intention"].strip(),
    )


def main():
    if not Path(SCORED_PATH).exists():
        print(f"✗ Scored file missing: {SCORED_PATH}")
        print("  Run download_moral_stories.py and score_sinir.py first.")
        return

    with open(SCORED_PATH) as f:
        items = [json.loads(l) for l in f if l.strip()]
    print(f"Loaded {len(items)} scored scenarios from {SCORED_PATH}")

    # Build pairs from SINIR-decisive items only
    pairs = []
    skipped_tied = 0
    skipped_short = 0
    gap_distribution = Counter()
    for item in items:
        sm = item.get("sinir_moral", 0)
        si = item.get("sinir_immoral", 0)
        if sm == si:
            skipped_tied += 1
            continue

        # chosen = action with higher (more pro-boundary) SINIR score
        if sm > si:
            chosen, rejected = item["moral_action"], item["immoral_action"]
            r_chosen, r_rejected = sm, si
            chosen_label = "moral"
        else:
            chosen, rejected = item["immoral_action"], item["moral_action"]
            r_chosen, r_rejected = si, sm
            chosen_label = "immoral"      # the "immoral" labeled action better respects SINIR

        if not chosen or not rejected:
            skipped_short += 1
            continue

        gap = r_chosen - r_rejected
        gap_distribution[gap] += 1

        pairs.append({
            "prompt":   build_prompt(item),
            "chosen":   " " + chosen.strip(),
            "rejected": " " + rejected.strip(),
            "_meta": {
                "scenario_id":   item["ID"],
                "chosen_label":  chosen_label,
                "sinir_chosen":  r_chosen,
                "sinir_rejected": r_rejected,
                "gap":           gap,
                "source":        item.get("source", "?"),
            },
        })

    print(f"\n[Filter results]")
    print(f"  Total scored:       {len(items)}")
    print(f"  Tied (sinir_eq):    {skipped_tied}")
    print(f"  Empty actions:      {skipped_short}")
    print(f"  Valid pairs:        {len(pairs)}")

    print(f"\n[Score-gap distribution]")
    for gap in sorted(gap_distribution.keys()):
        print(f"  Δ={gap:+d}: {gap_distribution[gap]} pairs")

    print(f"\n[Chosen-label distribution]")
    label_counts = Counter(p["_meta"]["chosen_label"] for p in pairs)
    print(f"  moral chosen:    {label_counts.get('moral', 0)}   "
          f"({100*label_counts.get('moral', 0)/max(len(pairs),1):.1f}%)")
    print(f"  immoral chosen:  {label_counts.get('immoral', 0)}  "
          f"({100*label_counts.get('immoral', 0)/max(len(pairs),1):.1f}%)")

    # [F9] Deterministic shuffle then split
    random.seed(SEED)
    random.shuffle(pairs)
    split_at = int(len(pairs) * 0.9)
    train_pairs = pairs[:split_at]
    test_pairs  = pairs[split_at:]

    def save(path, ps, strip_meta=False):
        with open(path, "w") as f:
            for p in ps:
                if strip_meta:
                    out = {k: v for k, v in p.items() if not k.startswith("_")}
                    f.write(json.dumps(out, ensure_ascii=False) + "\n")
                else:
                    f.write(json.dumps(p, ensure_ascii=False) + "\n")

    save(TRAIN_PATH, train_pairs, strip_meta=True)
    save(TEST_PATH, test_pairs, strip_meta=True)
    save(TRAIN_PATH.replace(".jsonl", "_full.jsonl"), train_pairs)
    save(TEST_PATH.replace(".jsonl", "_full.jsonl"), test_pairs)

    # Save meta summary
    meta = {
        "axis": "sinir",
        "build_date": "2026-06-09",
        "scored_total":         len(items),
        "tied_skipped":         skipped_tied,
        "empty_skipped":        skipped_short,
        "valid_pairs":          len(pairs),
        "train_pairs":          len(train_pairs),
        "test_pairs":           len(test_pairs),
        "split_seed":           SEED,
        "gap_distribution":     {str(k): v for k, v in gap_distribution.items()},
        "chosen_label_distribution": dict(label_counts),
        "prompt_template":      PROMPT_TEMPLATE,
        "field_names_note":     "Uses moral_action/immoral_action (not norm_action/situational_action — see LESSONS C12)",
    }
    with open(META_PATH, "w") as f:
        json.dump(meta, f, indent=2)

    print(f"\n✓ Files written:")
    print(f"  {TRAIN_PATH}                  ({len(train_pairs)} TRL-ready)")
    print(f"  {TEST_PATH}                   ({len(test_pairs)} TRL-ready)")
    print(f"  {TRAIN_PATH.replace('.jsonl', '_full.jsonl')}      (with _meta)")
    print(f"  {TEST_PATH.replace('.jsonl', '_full.jsonl')}       (with _meta)")
    print(f"  {META_PATH}                   (audit trail)")


if __name__ == "__main__":
    main()
