"""
Download Moral Stories dataset and save raw JSONL.

Adım 1 of SINIR-axis directive. Saves all 12,000 scenarios to
ybf_toy/data/raw/moral_stories_train.jsonl for downstream scoring.

Note: dataset already cached at data/scenarios.json (first 1,200 with our
internal field layout). This script saves the FULL raw dataset with original
field names (moral_action / immoral_action — NOT norm_action / situational_action
as the directive's first draft assumed; see LESSONS C12).
"""

import os, json

DATA_DIR = "data/raw"
OUT_PATH = f"{DATA_DIR}/moral_stories_train.jsonl"


def main():
    os.makedirs(DATA_DIR, exist_ok=True)

    if os.path.exists(OUT_PATH):
        # Already downloaded
        with open(OUT_PATH) as f:
            count = sum(1 for _ in f)
        print(f"✓ Already cached: {OUT_PATH}  ({count} rows)")
        return count

    from datasets import load_dataset
    print("Downloading: demelin/moral_stories (config='full', split='train') ...")
    ds = load_dataset("demelin/moral_stories", "full", split="train")
    print(f"  Columns: {ds.column_names}")
    print(f"  Rows:    {len(ds)}")

    with open(OUT_PATH, "w") as f:
        for item in ds:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")

    print(f"✓ Saved → {OUT_PATH}  ({len(ds)} rows)")
    return len(ds)


if __name__ == "__main__":
    main()
