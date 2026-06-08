"""
Edison novelty probe — has anyone classified ethical principles by their
degree of encoding in pretrained LM priors?

Specific question: the v0.4.7 finding that LCP's 5 axes partition into
encoded (GERCEKLIK, OZGURLUK) vs not-encoded (ONUR, SAYGI, SINIR) in
pretrained priors of Anthropic Claude models, with implications for per-axis
alignment cost — is this novel, or has prior work made similar empirical
claims about per-principle pretrained encoding?
"""

import os, json, subprocess, time, sys
from futurehouse_client import FutureHouseClient, JobNames

key = subprocess.check_output(
    ['security', 'find-generic-password', '-s', 'futurehouse-api-key-aiegitim', '-w']
).decode().strip()

client = FutureHouseClient(
    api_key=key,
    service_uri="https://api.platform.edisonscientific.com",
    verbose_logging=False,
)

QUERY = """In AI alignment research, has any prior empirical work classified
or measured the differential encoding of distinct ethical principles or axes
within pretrained language model priors? Specifically: has anyone shown that
some ethical dimensions (e.g., reality-acceptance, dignity, respect-for-other,
boundary-consciousness, autonomy, freedom-within-limits) are already absorbed
into pretrained LM priors during the pretraining stage, while others are not?

Related angles to search:
- Constitutional AI principles — per-principle pretrained encoding analysis
- HHH (helpfulness/harmlessness/honesty) — per-axis pretraining alignment
- Reward-model decomposition — per-dimension priors vs learned signal
- Multi-judge eval / "judge-as-audit" of LM priors per ethical axis
- "Free" vs "costly" alignment axes — per-principle alignment cost
- Generative adversarial probing of LM ethical priors per category
- Differential alignment training requirements per ethics dimension

If prior art exists, summarize it with citations. If novel, state so.
The question is specifically about empirical measurement of per-axis
encoding asymmetry in pretrained model priors, not about classifying
ethical theories themselves."""

print(f"[Edison probe] Submitting FINCH task (~5-15 min wall)...")
print(f"Query length: {len(QUERY)} chars\n")

t0 = time.time()
try:
    results = client.run_tasks_until_done(
        task_data={"name": JobNames.FINCH, "query": QUERY},
        timeout=1800, verbose=False, progress_bar=False,
    )
except Exception as e:
    print(f"✗ FINCH task failed: {type(e).__name__}: {e}")
    client.close()
    sys.exit(1)

elapsed = time.time() - t0
print(f"\n✓ Completed in {elapsed:.1f}s")

r = results[0]
for attr in ('answer', 'formatted_answer', 'response', 'output'):
    if hasattr(r, attr):
        v = getattr(r, attr)
        if v:
            answer = str(v)
            break
else:
    answer = "(no answer field found)"

print(f"\n=== ANSWER ({len(answer)} char) ===\n")
print(answer)

# Save
out = {
    "query": QUERY,
    "elapsed_seconds": elapsed,
    "answer_length": len(answer),
    "answer": answer,
    "model_used": "FINCH (job-futurehouse-data-analysis-crow-high)",
}
os.makedirs("../edison_queries", exist_ok=True)
with open("audit_novelty_probe_result.json", "w") as f:
    json.dump(out, f, indent=2, ensure_ascii=False)
print(f"\n✓ Saved → audit_novelty_probe_result.json")

client.close()
