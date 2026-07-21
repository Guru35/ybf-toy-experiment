"""
Cross-judge validation: re-label the 1200-scenario Moral Stories cache on
the Reality axis using Llama-3.2-3B-Instruct on Modal, with the SAME prompt
as relabel_reality.py (Haiku version).

Purpose:
  Compare three labelings on the same Reality axis:
    OLD     = Haiku, 5-axis short prompt, from scores_cache.json
    HAIKU_NEW = Haiku 4.5, new long EN_v1 prompt
    LLAMA_NEW = Llama-3.2-3B-Instruct, same EN_v1 prompt
  Convergence between HAIKU_NEW and LLAMA_NEW indicates prompt-quality is
  judge-independent; divergence localizes the problem.

Output:
  data/scenarios_reality_relabeled_v1_llama.jsonl

Cost estimate (Modal T4 free tier):
  ~25-35 min wall-clock, ~$0.25-0.35

Usage:
  modal run ybf_toy/relabel_reality_modal.py
"""

import modal
from pathlib import Path

app = modal.App("ybf-reality-relabel-llama")

image = (
    modal.Image.debian_slim(python_version="3.11")
    .apt_install("git")
    .pip_install(
        "torch",
        "transformers",
        "accelerate",
        "huggingface_hub",
    )
)

storage = modal.Volume.from_name("ybf-training-storage", create_if_missing=True)

MODEL_ID = "Qwen/Qwen2.5-3B-Instruct"

# Simpler line-based output format than JSON — more reliable for open
# instruct models. Regex parser tolerates whitespace variations.
USER_TEMPLATE = """Score the Reality axis for both actions below.

Situation: {situation}

Intention: {intention}

Norm: {norm}

Action A (moral_action): {moral_action}

Action B (immoral_action): {immoral_action}

Output your scores in EXACTLY this format (no other text):

ACTION_A_REALITY: <-1, 0, or 1>
ACTION_A_REASON: <one short sentence>
ACTION_B_REALITY: <-1, 0, or 1>
ACTION_B_REASON: <one short sentence>"""


@app.function(
    image=image,
    gpu="T4",
    volumes={"/storage": storage},
    timeout=3600,
)
def relabel_batch(system_prompt: str, scenarios_batch: list, old_scores_map: dict):
    """Process a batch of scenarios on a single T4 container."""
    import re, json, time
    import torch
    from transformers import AutoTokenizer, AutoModelForCausalLM

    print(f"[modal] Loading {MODEL_ID}...")
    t0 = time.time()
    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_ID,
        torch_dtype=torch.bfloat16,
        device_map="cuda",
    )
    model.eval()
    print(f"[modal] Loaded in {time.time()-t0:.1f}s")

    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    # Regex for tolerant parsing of the line-based format
    re_a_score  = re.compile(r"ACTION[_ ]?A[_ ]?REALITY\s*:\s*([+\-]?\d)", re.IGNORECASE)
    re_a_reason = re.compile(r"ACTION[_ ]?A[_ ]?REASON\s*:\s*(.+?)(?=\nACTION|\Z)", re.IGNORECASE | re.DOTALL)
    re_b_score  = re.compile(r"ACTION[_ ]?B[_ ]?REALITY\s*:\s*([+\-]?\d)", re.IGNORECASE)
    re_b_reason = re.compile(r"ACTION[_ ]?B[_ ]?REASON\s*:\s*(.+?)(?=\n|\Z)", re.IGNORECASE | re.DOTALL)

    def coerce(s):
        try:
            v = int(s)
            if v in (-1, 0, 1):
                return v
        except (ValueError, TypeError):
            pass
        return 0

    results = []
    for i, sc in enumerate(scenarios_batch):
        user_msg = USER_TEMPLATE.format(
            situation=sc["situation"].strip(),
            intention=sc["intention"].strip(),
            norm=sc.get("norm", "").strip(),
            moral_action=sc["options"]["A"].strip(),
            immoral_action=sc["options"]["B"].strip(),
        )
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_msg},
        ]
        # Two-step pattern: render template to string, then tokenize.
        # apply_chat_template(return_tensors="pt") behaviour varies across
        # transformers versions (Tensor vs BatchEncoding); the string-then-
        # tokenize path is stable.
        prompt_str = tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )
        inputs = tokenizer(prompt_str, return_tensors="pt").to("cuda")
        input_len = inputs["input_ids"].shape[1]
        with torch.no_grad():
            out = model.generate(
                **inputs,
                max_new_tokens=200,
                do_sample=False,
                temperature=0.0,
                pad_token_id=tokenizer.eos_token_id,
            )
        text = tokenizer.decode(out[0][input_len:], skip_special_tokens=True)

        a_match = re_a_score.search(text)
        b_match = re_b_score.search(text)
        ar_match = re_a_reason.search(text)
        br_match = re_b_reason.search(text)

        a_score = coerce(a_match.group(1)) if a_match else 0
        b_score = coerce(b_match.group(1)) if b_match else 0
        a_reason = (ar_match.group(1).strip() if ar_match else "")[:300]
        b_reason = (br_match.group(1).strip() if br_match else "")[:300]

        sid = sc["id"]
        old_moral, old_immoral = old_scores_map.get(str(sid), [0, 0])
        results.append({
            "scenario_id":               sid,
            "situation":                 sc["situation"],
            "intention":                 sc["intention"],
            "norm":                      sc.get("norm", ""),
            "moral_action":              sc["options"]["A"],
            "immoral_action":            sc["options"]["B"],
            "reality_moral_new":         a_score,
            "reality_moral_reasoning":   a_reason,
            "reality_immoral_new":       b_score,
            "reality_immoral_reasoning": b_reason,
            "reality_moral_old":         old_moral,
            "reality_immoral_old":       old_immoral,
            "model":                     MODEL_ID,
            "prompt_version":            "EN_v1",
            "raw_output":                text[:600],
        })

        if (i + 1) % 50 == 0:
            print(f"[modal] {i+1}/{len(scenarios_batch)}")

    print(f"[modal] Batch done in {time.time()-t0:.1f}s")
    return results


@app.local_entrypoint()
def main():
    import json
    from pathlib import Path

    prompt_path = Path("ybf_toy/Raw/YBF_Reality_Definition_EN_v1.txt")
    scenarios_path = Path("ybf_toy/data/scenarios.json")
    cache_path = Path("ybf_toy/data/scores_cache.json")
    out_path = Path("ybf_toy/data/scenarios_reality_relabeled_v1_llama.jsonl")

    prompt_text = prompt_path.read_text().strip()
    scenarios = json.loads(scenarios_path.read_text())
    raw_cache = json.loads(cache_path.read_text())

    # Build old_scores_map: scenario_id (as str) → (moral, immoral) gerceklik
    old_scores_map = {}
    for k, v in raw_cache.items():
        parts = k.split("_")
        if len(parts) < 4:
            continue
        try:
            sid = int(parts[1])
        except ValueError:
            continue
        action = parts[3]
        d = old_scores_map.setdefault(str(sid), [0, 0])
        if action == "A":
            d[0] = v.get("gerceklik", 0)
        elif action == "B":
            d[1] = v.get("gerceklik", 0)

    # Resume: skip already-scored scenarios
    done = set()
    if out_path.exists():
        with open(out_path) as f:
            for line in f:
                try:
                    done.add(json.loads(line)["scenario_id"])
                except Exception:
                    pass

    todo = [s for s in scenarios if s["id"] not in done]
    print(f"Prompt: {len(prompt_text)} chars")
    print(f"Scenarios total: {len(scenarios)}")
    print(f"Already scored:  {len(done)}")
    print(f"To score:        {len(todo)}")
    if not todo:
        print("Nothing to do.")
        return

    print(f"\nDispatching {len(todo)} scenarios to Modal T4 in one batch...")
    results = relabel_batch.remote(prompt_text, todo, old_scores_map)

    with open(out_path, "a") as f:
        for r in results:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"\n✓ {len(results)} scored → {out_path}")
