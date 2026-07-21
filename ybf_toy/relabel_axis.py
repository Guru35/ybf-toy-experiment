"""
Relabel the 1200 Moral Stories scenarios on a given LCP/YBF axis with Haiku,
using that axis's canonical definition as the system prompt. Generic version of
relabel_reality.py / relabel_boundary.py. Both actions scored in one call,
resume-safe, threaded. Output schema mirrors the others so downstream tooling
(flip-eval, DPO build) works for any axis.

Usage:  python relabel_axis.py --axis dignity
"""
import argparse
import json
import os
import subprocess
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

MODEL = "claude-haiku-4-5-20251001"

if not os.environ.get("ANTHROPIC_API_KEY"):
    os.environ["ANTHROPIC_API_KEY"] = subprocess.check_output(
        ["security", "find-generic-password", "-s", "ANTHROPIC_API_KEY", "-w"]).decode().strip()
from anthropic import Anthropic
client = Anthropic()
write_lock = threading.Lock()


def user_template(axis):
    AX = axis.upper()
    return f"""Score the {AX} axis for both actions below. Return STRICT JSON only — no markdown, no text outside the JSON.

Situation: {{situation}}

Intention: {{intention}}

Norm: {{norm}}

Action A (moral_action): {{moral_action}}

Action B (immoral_action): {{immoral_action}}

Return this exact structure:
{{{{
  "action_A": {{{{"{axis}": -1 or 0 or 1, "reasoning": "<one short sentence>"}}}},
  "action_B": {{{{"{axis}": -1 or 0 or 1, "reasoning": "<one short sentence>"}}}}
}}}}"""


def parse_score(v):
    try:
        v = int(v)
        if v in (-1, 0, 1):
            return v
    except (ValueError, TypeError):
        pass
    return 0


def load_done(out_path):
    if not os.path.exists(out_path):
        return set()
    seen = set()
    for line in open(out_path):
        try:
            seen.add(json.loads(line)["scenario_id"])
        except Exception:
            pass
    return seen


def score_one(sc, system, axis, tmpl, max_retries=4):
    sid = sc["id"]
    moral, immoral = sc["options"]["A"], sc["options"]["B"]
    user = tmpl.format(situation=sc["situation"].strip(), intention=sc.get("intention", "").strip(),
                       norm=sc.get("norm", "").strip(), moral_action=moral, immoral_action=immoral)
    for attempt in range(max_retries):
        try:
            resp = client.messages.create(
                model=MODEL, max_tokens=250,
                system=[{"type": "text", "text": system, "cache_control": {"type": "ephemeral"}}],
                messages=[{"role": "user", "content": user}])
            txt = resp.content[0].text.strip()
            i, j = txt.find("{"), txt.rfind("}")
            if i >= 0 and j >= 0:
                txt = txt[i:j + 1]
            d = json.loads(txt)
            return {
                "scenario_id": sid, "situation": sc["situation"], "intention": sc.get("intention", ""),
                "norm": sc.get("norm", ""), "moral_action": moral, "immoral_action": immoral,
                f"{axis}_moral_new": parse_score(d["action_A"][axis]),
                f"{axis}_moral_reasoning": d["action_A"].get("reasoning", ""),
                f"{axis}_immoral_new": parse_score(d["action_B"][axis]),
                f"{axis}_immoral_reasoning": d["action_B"].get("reasoning", ""),
                "model": MODEL, "prompt_version": "EN_v1"}
        except Exception as e:
            if attempt == max_retries - 1:
                return {"scenario_id": sid, "error": str(e)[:100]}
            time.sleep(2 ** attempt)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--axis", required=True)
    args = ap.parse_args()
    axis = args.axis
    def_path = f"data/ybf_{axis}_scorer_prompt.txt"
    out_path = f"data/scenarios_{axis}_relabeled_v1.jsonl"
    tmpl = user_template(axis)

    system = open(def_path).read().strip()
    scenarios = json.load(open("data/scenarios.json"))
    done = load_done(out_path)
    todo = [s for s in scenarios if s["id"] not in done]
    print(f"[{axis}] relabel: {len(scenarios)} total | {len(done)} done | {len(todo)} to do "
          f"| system {len(system)} chars", flush=True)
    out = open(out_path, "a")
    n = 0
    with ThreadPoolExecutor(max_workers=8) as ex:
        futs = [ex.submit(score_one, s, system, axis, tmpl) for s in todo]
        for fut in as_completed(futs):
            r = fut.result()
            with write_lock:
                out.write(json.dumps(r, ensure_ascii=False) + "\n")
                out.flush()
            n += 1
            if n % 100 == 0:
                print(f"  [{axis}] {n}/{len(todo)}", flush=True)
    out.close()

    rows = [json.loads(l) for l in open(out_path)]
    ok = [r for r in rows if f"{axis}_moral_new" in r]
    flips = sum(1 for r in ok if r[f"{axis}_immoral_new"] > r[f"{axis}_moral_new"])
    decisive = sum(1 for r in ok if r[f"{axis}_moral_new"] != r[f"{axis}_immoral_new"])
    print(f"[{axis}] DONE: scored {len(ok)} | errors {len(rows)-len(ok)} | "
          f"flips {flips} | decisive {decisive}", flush=True)


if __name__ == "__main__":
    main()
