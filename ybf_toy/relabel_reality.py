"""
Re-label the 1200-scenario Moral Stories cache on the Reality axis only,
using the new expanded prompt (YBF_Reality_Definition_EN_v1.txt).

Goals:
  1. Use the 2400-word canonical Reality prompt (from Raw/) as the SYSTEM
     message — prompt caching halves input cost.
  2. For each scenario, score BOTH actions in a single Haiku call (returns
     JSON with two scores + brief reasoning each) — halves call count.
  3. Preserve the OLD cache (data/scores_cache.json). Output goes to a NEW
     file (data/scenarios_reality_relabeled_v1.jsonl) for side-by-side
     comparison.
  4. Resume-safe: skip scenarios already in the output file.
  5. Parallel via ThreadPoolExecutor (workers=8).

Output schema per line:
  {
    "scenario_id": int,
    "situation": str,
    "intention": str,
    "norm": str,
    "moral_action": str,
    "immoral_action": str,
    "reality_moral_new": -1 | 0 | +1,
    "reality_moral_reasoning": str,
    "reality_immoral_new": -1 | 0 | +1,
    "reality_immoral_reasoning": str,
    "reality_moral_old": -1 | 0 | +1,   (from scores_cache.json)
    "reality_immoral_old": -1 | 0 | +1,
    "model": "claude-haiku-4-5-20251001",
    "prompt_version": "EN_v1"
  }

Cost estimate (with prompt caching, system block ~3200 tokens):
  - Cached read: ~$0.08/1M tokens × 3200 × 1200 = ~$0.31
  - Uncached write (first call only): ~$0.80/1M × 3200 = ~$0.003
  - User msg + output per call: ~600 tokens × 1200 = ~$0.30 total
  - Total: ~$0.65 for full 1200-scenario relabel
"""

import os, json, time, threading, argparse, random
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from anthropic import Anthropic

PROMPT_PATH    = "Raw/YBF_Reality_Definition_EN_v1.txt"
SCENARIOS_PATH = "data/scenarios.json"
CACHE_PATH     = "data/scores_cache.json"
OUT_PATH       = "data/scenarios_reality_relabeled_v1.jsonl"
MODEL          = "claude-haiku-4-5-20251001"

client = Anthropic()
write_lock = threading.Lock()

USER_TEMPLATE = """Score the Reality axis for both actions below. Return STRICT JSON only — no markdown, no explanation outside the JSON.

Situation: {situation}

Intention: {intention}

Norm: {norm}

Action A (moral_action): {moral_action}

Action B (immoral_action): {immoral_action}

Return this exact structure:
{{
  "action_A": {{"reality": -1 or 0 or 1, "reasoning": "<one short sentence>"}},
  "action_B": {{"reality": -1 or 0 or 1, "reasoning": "<one short sentence>"}}
}}"""


def load_prompt():
    with open(PROMPT_PATH) as f:
        return f.read().strip()


def load_scenarios():
    with open(SCENARIOS_PATH) as f:
        return json.load(f)


def load_old_cache():
    """Map scenario_id → (reality_moral_old, reality_immoral_old) from
    5-axis cache. A = moral, B = immoral."""
    with open(CACHE_PATH) as f:
        cache = json.load(f)
    out = {}
    for k, v in cache.items():
        # keys look like 'scenario_3785_action_A' or '_B'
        parts = k.split("_")
        if len(parts) < 4:
            continue
        try:
            sid = int(parts[1])
        except ValueError:
            continue
        action = parts[3]
        out.setdefault(sid, {})[action] = v.get("gerceklik", 0)
    return {sid: (d.get("A", 0), d.get("B", 0)) for sid, d in out.items()}


def load_already_scored():
    if not os.path.exists(OUT_PATH):
        return set()
    seen = set()
    with open(OUT_PATH) as f:
        for line in f:
            try:
                seen.add(json.loads(line)["scenario_id"])
            except Exception:
                pass
    return seen


def parse_reality(val):
    """Coerce any numeric-ish to {-1, 0, 1}; default 0."""
    try:
        v = int(val)
        if v in (-1, 0, 1):
            return v
    except (ValueError, TypeError):
        pass
    return 0


def score_scenario(scenario, system_prompt, old_scores, max_retries=4):
    sid = scenario["id"]
    moral = scenario["options"]["A"]
    immoral = scenario["options"]["B"]
    user_msg = USER_TEMPLATE.format(
        situation=scenario["situation"].strip(),
        intention=scenario["intention"].strip(),
        norm=scenario.get("norm", "").strip(),
        moral_action=moral.strip(),
        immoral_action=immoral.strip(),
    )

    for attempt in range(max_retries):
        try:
            resp = client.messages.create(
                model=MODEL,
                max_tokens=400,
                system=[
                    {
                        "type": "text",
                        "text": system_prompt,
                        "cache_control": {"type": "ephemeral"},
                    }
                ],
                messages=[{"role": "user", "content": user_msg}],
            )
            text = resp.content[0].text.strip()
            # Strip code fences if any
            if text.startswith("```"):
                text = text.split("```", 2)[1]
                if text.startswith("json"):
                    text = text[4:]
                text = text.strip()
            data = json.loads(text)
            a = data.get("action_A", {})
            b = data.get("action_B", {})
            old_moral, old_immoral = old_scores.get(sid, (0, 0))
            return {
                "scenario_id":             sid,
                "situation":               scenario["situation"],
                "intention":               scenario["intention"],
                "norm":                    scenario.get("norm", ""),
                "moral_action":            moral,
                "immoral_action":          immoral,
                "reality_moral_new":       parse_reality(a.get("reality")),
                "reality_moral_reasoning": str(a.get("reasoning", ""))[:300],
                "reality_immoral_new":     parse_reality(b.get("reality")),
                "reality_immoral_reasoning": str(b.get("reasoning", ""))[:300],
                "reality_moral_old":       old_moral,
                "reality_immoral_old":     old_immoral,
                "model":                   MODEL,
                "prompt_version":          "EN_v1",
            }
        except Exception as e:
            backoff = (2 ** attempt) + random.random()
            if attempt == max_retries - 1:
                print(f"  ✗ sid={sid} giving up: {str(e)[:80]}")
                return None
            time.sleep(backoff)
    return None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--n", type=int, default=None, help="Limit to N scenarios")
    parser.add_argument("--workers", type=int, default=8)
    args = parser.parse_args()

    system_prompt = load_prompt()
    scenarios = load_scenarios()
    old_scores = load_old_cache()
    already = load_already_scored()

    print(f"╔{'═'*60}╗")
    print(f"║ Reality re-labeling — Haiku, EN_v1 prompt (~3200 tok cached)")
    print(f"╠{'═'*60}╣")
    print(f"║ Prompt file:     {PROMPT_PATH}  ({len(system_prompt)} chars)")
    print(f"║ Scenarios:       {len(scenarios)}")
    print(f"║ Old cache:       {len(old_scores)} scenarios with G scores")
    print(f"║ Already scored:  {len(already)}")
    print(f"║ Output:          {OUT_PATH}")
    print(f"║ Model:           {MODEL}")
    print(f"║ Workers:         {args.workers}")
    print(f"╚{'═'*60}╝\n")

    todo = [s for s in scenarios if s["id"] not in already]
    if args.n is not None:
        todo = todo[: args.n]
    print(f"To score: {len(todo)}\n")

    t0 = time.time()
    completed = 0
    failed = 0

    with ThreadPoolExecutor(max_workers=args.workers) as ex, open(OUT_PATH, "a") as out:
        futures = {ex.submit(score_scenario, s, system_prompt, old_scores): s["id"]
                   for s in todo}
        for fut in as_completed(futures):
            sid = futures[fut]
            try:
                rec = fut.result()
                if rec is None:
                    failed += 1
                    continue
                with write_lock:
                    out.write(json.dumps(rec, ensure_ascii=False) + "\n")
                    out.flush()
                completed += 1
                if completed % 50 == 0:
                    elapsed = time.time() - t0
                    rate = completed / elapsed if elapsed > 0 else 0
                    eta = (len(todo) - completed) / rate if rate > 0 else 0
                    print(f"  {completed}/{len(todo)}  "
                          f"({rate:.1f}/s, ETA {eta/60:.1f}m)")
            except Exception as e:
                print(f"  ✗ sid={sid} exception: {e}")
                failed += 1

    elapsed = time.time() - t0
    print(f"\n✓ Done. {completed} scored, {failed} failed in {elapsed/60:.1f}m")
    print(f"  Output: {OUT_PATH}")


if __name__ == "__main__":
    main()
