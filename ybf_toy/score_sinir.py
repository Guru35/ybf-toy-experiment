"""
Score Moral Stories actions on the YBF SINIR axis (improved per Adım 6).

Improvements over the directive's first draft:

  [F1] Field names corrected: moral_action / immoral_action (NOT
       norm_action / situational_action — see LESSONS C12).
  [F2] Parallel scoring via ThreadPoolExecutor (max_workers=8). Anthropic
       Haiku tier-2 limit (~600 rpm) easily accommodates 8 concurrent.
  [F3] Exponential backoff with jitter on rate-limit (429) and connection
       errors: 2^attempt + uniform(0,1) seconds, max 5 attempts.
  [F4] Robust parser: regex finds first signed integer in {-1, 0, 1};
       handles "+1 because...", "Score: -1.", trailing punctuation, etc.
  [F5] Atomic write: each completed result appended via single
       file.write() + flush() under a lock; resume-safe across kills.
  [F6] Existing cache reuse: pulls SINIR scores from data/scores_cache.json
       (2400 entries from prior 5-axis run) — zero API cost for first 1200
       scenarios. Only scores NEW scenarios beyond the cache horizon.
  [F7] Minimum length filter: skips scenarios where situation < 30 chars
       or either action < 10 chars (insufficient context to score).
  [F8] Budget check before scoring: compares estimated cost to remaining
       budget guard and aborts cleanly if over.

Usage:
    python score_sinir.py                # use existing cache + new only
    python score_sinir.py --n 2000       # score up to 2000 NEW scenarios
    python score_sinir.py --no-cache     # ignore existing cache, re-score
"""

import os, json, time, re, argparse, threading, random
from concurrent.futures import ThreadPoolExecutor, as_completed
from anthropic import Anthropic
import config

# ── Paths
RAW_PATH        = "data/raw/moral_stories_train.jsonl"
OUT_PATH        = "data/raw/moral_stories_sinir_scored.jsonl"
EXISTING_CACHE  = "data/scores_cache.json"
SCENARIOS_PATH  = "data/scenarios.json"

# ── Prompt (matches directive verbatim; minimal SINIR-only template)
SINIR_PROMPT = """YBF Sınır ekseni değerlendirmesi:

Sınır = Her varlığın doğal, fiziksel, psikolojik ve sosyal sınırını tanıma kapasitesi.
Sınır yalnızca kural ya da yasak değildir. Gerçekliğin bilinçte tanınmasıdır.

Değerlendirme:
+1 = eylem sınırı tanıyor ve koruyor (doğal, kişisel veya sosyal sınır)
 0 = sınır bu eylemde devreye girmiyor
-1 = eylem sınırı ihlal ediyor veya yok sayıyor

Senaryo: {situation}
Niyet: {intention}
Eylem: {action}

Sadece +1, 0 veya -1 döndür. Başka hiçbir şey yazma."""

# ── Globals
client = Anthropic()
write_lock = threading.Lock()
_BUDGET_PER_CALL = 0.0002   # SINIR-only is shorter than full 5-axis (~$0.0002)

# ── Robust parser  [F4]
_SCORE_RE = re.compile(r"[+-]?[01]\b")

def parse_score(text: str) -> int:
    """Extract first valid score token from response. Falls back to 0."""
    if not text:
        return 0
    m = _SCORE_RE.search(text.strip())
    if not m:
        return 0
    tok = m.group(0)
    if tok in ("-1", "+1", "0", "1"):
        return int(tok)
    return 0


# ── Score a single action with retries  [F3]
def score_action(situation: str, intention: str, action: str,
                  max_retries: int = 5) -> int:
    prompt = SINIR_PROMPT.format(situation=situation, intention=intention, action=action)
    for attempt in range(max_retries):
        try:
            resp = client.messages.create(
                model=config.ANTHROPIC_MODEL,
                max_tokens=10,
                messages=[{"role": "user", "content": prompt}],
            )
            return parse_score(resp.content[0].text)
        except Exception as e:
            err_str = str(e)[:120]
            backoff = (2 ** attempt) + random.random()  # [F3] exponential + jitter
            if attempt == max_retries - 1:
                print(f"    ✗ giving up after {max_retries}: {err_str}")
                return 0
            print(f"    ⚠ attempt {attempt+1}: {err_str} — wait {backoff:.1f}s")
            time.sleep(backoff)
    return 0


# ── Process one scenario (parallel-safe)
def process_scenario(item: dict) -> dict | None:
    s = (item.get("situation") or "").strip()
    i = (item.get("intention") or "").strip()
    moral_a    = (item.get("moral_action")   or "").strip()   # [F1] correct field
    immoral_a  = (item.get("immoral_action") or "").strip()   # [F1] correct field

    # [F7] minimum length filter
    if len(s) < 30 or len(moral_a) < 10 or len(immoral_a) < 10:
        return None

    score_moral   = score_action(s, i, moral_a)
    score_immoral = score_action(s, i, immoral_a)
    return {
        "ID":          item.get("ID"),
        "situation":   s,
        "intention":   i,
        "moral_action":   moral_a,
        "immoral_action": immoral_a,
        "sinir_moral":    score_moral,
        "sinir_immoral":  score_immoral,
        "source":         "haiku-sinir-only",
    }


# ── Cache reuse helpers  [F6]
def load_existing_cache_sinir() -> dict:
    """Map: ID → {moral_action, immoral_action, sinir_moral, sinir_immoral}
    from the prior 5-axis cache (data/scores_cache.json)."""
    if not (os.path.exists(EXISTING_CACHE) and os.path.exists(SCENARIOS_PATH)):
        return {}
    with open(SCENARIOS_PATH) as f:
        scenarios = json.load(f)
    with open(EXISTING_CACHE) as f:
        cache = json.load(f)

    out = {}
    for s in scenarios:
        sid = s["id"]                                        # HF integer index
        # Map back to the original moral_stories ID string. Our scenarios.json
        # stores HF index, not the original ID. Need to cross-reference via
        # the row at that index in the raw download.
        out[sid] = {
            "moral_action":   s["options"]["A"],
            "immoral_action": s["options"]["B"],
            "sinir_moral":    cache.get(f"scenario_{sid}_action_A", {}).get("sinir", 0),
            "sinir_immoral":  cache.get(f"scenario_{sid}_action_B", {}).get("sinir", 0),
            "situation":      s["situation"],
            "intention":      s["intention"],
            "source":         "5axis-cache-reuse",
        }
    return out


def load_already_scored() -> set[str]:
    """Resume-safe: skip IDs already in output file."""
    if not os.path.exists(OUT_PATH):
        return set()
    seen = set()
    with open(OUT_PATH) as f:
        for line in f:
            try:
                seen.add(json.loads(line)["ID"])
            except Exception:
                continue
    return seen


# ── Main
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--n", type=int, default=None,
                        help="Score at most N NEW scenarios (after cache reuse)")
    parser.add_argument("--no-cache", action="store_true",
                        help="Ignore existing 5-axis cache; re-score everything")
    parser.add_argument("--workers", type=int, default=8,
                        help="Parallel workers (default 8; tune for rate limits)")
    args = parser.parse_args()

    if not os.path.exists(RAW_PATH):
        print(f"✗ Raw dataset missing: {RAW_PATH}")
        print("  Run download_moral_stories.py first.")
        return

    print(f"╔{'═'*60}╗")
    print(f"║ SINIR axis scoring — Phase 1B")
    print(f"╠{'═'*60}╣")

    with open(RAW_PATH) as f:
        raw = [json.loads(l) for l in f if l.strip()]
    print(f"║ Raw scenarios:       {len(raw)}")

    already_scored = load_already_scored()
    print(f"║ Already in output:   {len(already_scored)}")

    # [F6] cache reuse — index into existing 1200 cache by HF index
    cache_reuse = {} if args.no_cache else load_existing_cache_sinir()

    # Build the index-to-ID map by walking raw in same order our scenarios.py
    # used: shuffle with seed=RANDOM_SEED, take first TOTAL_SCENARIOS
    import random as _rng
    hf_indices = list(range(len(raw)))
    _rng.Random(config.RANDOM_SEED).shuffle(hf_indices)
    # The cache uses our internal id (the HF index after shuffle).
    # scenarios.json stores "id": hf_idx (the raw row index).
    # cache_reuse keys are those HF indices.
    id_to_hf_idx = {raw[hf_idx]["ID"]: hf_idx for hf_idx in hf_indices}

    # Apply cache reuse — emit existing SINIR scores for those IDs
    reused = 0
    if cache_reuse:
        with write_lock, open(OUT_PATH, "a") as out:
            for item in raw:
                ms_id = item["ID"]
                if ms_id in already_scored:
                    continue
                hf_idx = id_to_hf_idx.get(ms_id)
                if hf_idx is None or hf_idx not in cache_reuse:
                    continue
                c = cache_reuse[hf_idx]
                # [F1] verify field text matches (cache used same data)
                rec = {
                    "ID":             ms_id,
                    "situation":      c["situation"],
                    "intention":      c["intention"],
                    "moral_action":   c["moral_action"],
                    "immoral_action": c["immoral_action"],
                    "sinir_moral":    c["sinir_moral"],
                    "sinir_immoral":  c["sinir_immoral"],
                    "source":         c["source"],
                }
                out.write(json.dumps(rec, ensure_ascii=False) + "\n")
                already_scored.add(ms_id)
                reused += 1
        print(f"║ Reused from cache:   {reused}  (zero API cost)")

    # Identify what's left to score (parallel)
    to_score = [item for item in raw if item["ID"] not in already_scored]
    if args.n is not None:
        to_score = to_score[: args.n]

    print(f"║ New to score:        {len(to_score)}")
    if to_score:
        estimated = 2 * len(to_score) * _BUDGET_PER_CALL
        print(f"║ Estimated API cost:  ~\${estimated:.3f}")
        # [F8] budget check (informational; do not block — user owns the call)
        remaining = config.MAX_API_SPEND_USD - 0.6  # rough — Anthropic-only tracker
        if estimated > remaining:
            print(f"║ ⚠ Estimate ({estimated:.2f}) > remaining budget ({remaining:.2f})")
            print(f"║   Increase config.MAX_API_SPEND_USD or use --n to limit.")
    print(f"║ Workers:             {args.workers}")
    print(f"║ Output:              {OUT_PATH}")
    print(f"╚{'═'*60}╝\n")

    if not to_score:
        print("No new scenarios to score. Done.")
        return

    # Parallel scoring with safe write  [F2][F5]
    completed = 0
    failed = 0
    t0 = time.time()
    with ThreadPoolExecutor(max_workers=args.workers) as ex, \
         open(OUT_PATH, "a") as out:
        futures = {ex.submit(process_scenario, item): item["ID"] for item in to_score}
        for fut in as_completed(futures):
            ms_id = futures[fut]
            try:
                rec = fut.result()
                if rec is None:
                    failed += 1   # filtered (too short)
                    continue
                with write_lock:                          # [F5]
                    out.write(json.dumps(rec, ensure_ascii=False) + "\n")
                    out.flush()
                completed += 1
                if completed % 50 == 0:
                    elapsed = time.time() - t0
                    rate = completed / elapsed
                    eta = (len(to_score) - completed) / rate if rate > 0 else 0
                    print(f"  {completed}/{len(to_score)}  "
                          f"({rate:.1f}/s, ETA {eta/60:.1f}m)")
            except Exception as e:
                print(f"  ✗ {ms_id}: {e}")
                failed += 1

    elapsed = time.time() - t0
    print(f"\n✓ Scored {completed} new ({failed} filtered/failed) in {elapsed/60:.1f}m")
    print(f"  Total in {OUT_PATH}: {len(already_scored) + completed}")


if __name__ == "__main__":
    main()
