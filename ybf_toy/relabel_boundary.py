"""
Relabel the 1200 Moral Stories scenarios on the BOUNDARY (SINIR) axis with
Haiku, using the canonical Boundary definition (EN_v1) as the system prompt.
Parallel to relabel_reality.py: both actions scored in one call, resume-safe,
threaded. Output schema mirrors the Reality relabel so the same downstream
tooling (DPO build, flip-eval) works.

~1200 Haiku calls (prompt-cached system). Run locally on the Mac.
"""
import json
import os
import subprocess
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

DEF_PATH = "data/ybf_boundary_scorer_prompt.txt"
SCENARIOS_PATH = "data/scenarios.json"
OUT_PATH = "data/scenarios_boundary_relabeled_v1.jsonl"
MODEL = "claude-haiku-4-5-20251001"

os.environ["ANTHROPIC_API_KEY"] = subprocess.check_output(
    ["security", "find-generic-password", "-s", "ANTHROPIC_API_KEY", "-w"]).decode().strip()
from anthropic import Anthropic
client = Anthropic()
write_lock = threading.Lock()

USER_TEMPLATE = """Score the BOUNDARY axis for both actions below. Return STRICT JSON only — no markdown, no text outside the JSON.

Situation: {situation}

Intention: {intention}

Norm: {norm}

Action A (moral_action): {moral_action}

Action B (immoral_action): {immoral_action}

Return this exact structure:
{{
  "action_A": {{"boundary": -1 or 0 or 1, "reasoning": "<one short sentence>"}},
  "action_B": {{"boundary": -1 or 0 or 1, "reasoning": "<one short sentence>"}}
}}"""


def parse_score(v):
    try:
        v = int(v)
        if v in (-1, 0, 1):
            return v
    except (ValueError, TypeError):
        pass
    return 0


def load_done():
    if not os.path.exists(OUT_PATH):
        return set()
    seen = set()
    for line in open(OUT_PATH):
        try:
            seen.add(json.loads(line)["scenario_id"])
        except Exception:
            pass
    return seen


def score_one(sc, system, max_retries=4):
    sid = sc["id"]
    moral, immoral = sc["options"]["A"], sc["options"]["B"]
    user = USER_TEMPLATE.format(
        situation=sc["situation"].strip(), intention=sc.get("intention", "").strip(),
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
                "boundary_moral_new": parse_score(d["action_A"]["boundary"]),
                "boundary_moral_reasoning": d["action_A"].get("reasoning", ""),
                "boundary_immoral_new": parse_score(d["action_B"]["boundary"]),
                "boundary_immoral_reasoning": d["action_B"].get("reasoning", ""),
                "model": MODEL, "prompt_version": "EN_v1"}
        except Exception as e:
            if attempt == max_retries - 1:
                return {"scenario_id": sid, "error": str(e)[:100]}
            time.sleep(2 ** attempt)


def main():
    system = open(DEF_PATH).read().strip()
    scenarios = json.load(open(SCENARIOS_PATH))
    done = load_done()
    todo = [s for s in scenarios if s["id"] not in done]
    print(f"Boundary relabel: {len(scenarios)} total | {len(done)} done | {len(todo)} to do "
          f"| system {len(system)} chars", flush=True)
    out = open(OUT_PATH, "a")
    n = 0
    with ThreadPoolExecutor(max_workers=8) as ex:
        futs = [ex.submit(score_one, s, system) for s in todo]
        for fut in as_completed(futs):
            r = fut.result()
            with write_lock:
                out.write(json.dumps(r, ensure_ascii=False) + "\n")
                out.flush()
            n += 1
            if n % 50 == 0:
                print(f"  {n}/{len(todo)}", flush=True)
    out.close()

    import collections
    rows = [json.loads(l) for l in open(OUT_PATH)]
    ok = [r for r in rows if "boundary_moral_new" in r]
    errs = len(rows) - len(ok)
    dist = collections.Counter((r["boundary_moral_new"], r["boundary_immoral_new"]) for r in ok)
    flips = sum(1 for r in ok if r["boundary_immoral_new"] > r["boundary_moral_new"])
    print(f"\n==== BOUNDARY RELABEL DONE ====", flush=True)
    print(f"  scored {len(ok)} | errors {errs}")
    print(f"  Boundary flips (immoral better): {flips}")
    print(f"  decisive (scores differ): {sum(1 for r in ok if r['boundary_moral_new'] != r['boundary_immoral_new'])}")
    for k in sorted(dist, key=lambda x: -dist[x]):
        print(f"    moral={k[0]:+d} immoral={k[1]:+d}: {dist[k]}")


if __name__ == "__main__":
    main()
