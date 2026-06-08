"""Load and split Moral Stories scenarios."""

import json
import os
import random


def load_and_split_scenarios(total=None, seed=None, train_ratio=None):
    """
    Returns: (train_scenarios, test_scenarios, all_scenarios)
    Each scenario dict has: id, embed_idx, situation, intention,
    options {A, B}, norm
    
    C4: embed_idx is position in all_scenarios list — never scenario id.
    """
    import config
    total       = total       or config.TOTAL_SCENARIOS
    seed        = seed        or config.RANDOM_SEED
    train_ratio = train_ratio or config.TRAIN_RATIO

    if os.path.exists(config.SCENARIOS_PATH):
        print(f"  Loading scenarios from cache: {config.SCENARIOS_PATH}")
        with open(config.SCENARIOS_PATH) as f:
            all_scenarios = json.load(f)
        # Respect requested total
        all_scenarios = all_scenarios[:total]
    else:
        print(f"  Downloading {total} scenarios from {config.DATASET_NAME}...")
        from datasets import load_dataset
        ds = load_dataset(config.DATASET_NAME, config.DATASET_SPLIT, split="train")
        
        # Shuffle deterministically
        indices = list(range(len(ds)))
        rng = random.Random(seed)
        rng.shuffle(indices)
        
        all_scenarios = []
        embed_idx = 0
        for hf_idx in indices:
            if embed_idx >= total:
                break
            story = ds[hf_idx]
            norm_action      = (story.get("moral_action")   or "").strip()
            divergent_action = (story.get("immoral_action") or "").strip()
            if not norm_action or not divergent_action:
                continue
            all_scenarios.append({
                "id":        hf_idx,        # original HuggingFace index
                "embed_idx": embed_idx,     # C4: position in this list
                "situation": (story.get("situation") or "").strip(),
                "intention": (story.get("intention") or "").strip(),
                "norm":      (story.get("norm")      or "").strip(),
                "options": {
                    "A": norm_action,
                    "B": divergent_action,
                }
            })
            embed_idx += 1
        
        os.makedirs(config.DATA_DIR, exist_ok=True)
        with open(config.SCENARIOS_PATH, "w") as f:
            json.dump(all_scenarios, f, indent=2, ensure_ascii=False)
        print(f"  Saved to {config.SCENARIOS_PATH}")

    split_at = int(len(all_scenarios) * train_ratio)
    train_scenarios = all_scenarios[:split_at]
    test_scenarios  = all_scenarios[split_at:]

    print(f"  ✓ {len(all_scenarios)} scenarios  "
          f"(train={len(train_scenarios)}, test={len(test_scenarios)})")
    return train_scenarios, test_scenarios, all_scenarios
