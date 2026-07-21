"""
FutureHouse auth + CROW probe.
Single query, measure latency, dump response shape + answer.
"""
import os
import sys
import time
import subprocess
from futurehouse_client import FutureHouseClient, JobNames

# Retrieve key from keychain (AI-Egitim's dedicated slot)
try:
    KEY = subprocess.check_output(
        ['security', 'find-generic-password', '-s', 'futurehouse-api-key-aiegitim', '-w'],
        stderr=subprocess.DEVNULL
    ).decode().strip()
except Exception as e:
    print(f"✗ Keychain retrieval failed: {e}")
    sys.exit(1)

print(f"✓ Key loaded from keychain (length={len(KEY)}, prefix={KEY[:6]})")

EDISON_URL = "https://api.platform.edisonscientific.com"  # FutureHouse → Edison rebrand
client = FutureHouseClient(
    api_key=KEY,
    service_uri=EDISON_URL,
    verbose_logging=False,
)

QUERY = (
    "In reinforcement learning with sparse/rare positive examples "
    "(<2% of the dataset), what empirically validated techniques mitigate "
    "policy collapse to a majority-class baseline? Focus on small-data "
    "(n<1000) ethical or moral decision settings if available."
)

print(f"\n📝 Query ({len(QUERY)} chars):")
print(f"   {QUERY}\n")

print("⏳ Submitting CROW task...")
t0 = time.time()

try:
    results = client.run_tasks_until_done(
        task_data={"name": JobNames.CROW, "query": QUERY},
        verbose=False,
        progress_bar=False,
        timeout=600,  # 10 min cap for probe
    )
except Exception as e:
    print(f"✗ Task failed: {type(e).__name__}: {e}")
    client.close()
    sys.exit(2)

elapsed = time.time() - t0
print(f"\n✓ Completed in {elapsed:.1f}s")
print(f"  Results: {len(results)} response(s)")

for i, r in enumerate(results):
    print(f"\n=== Response {i+1} ===")
    print(f"  type: {type(r).__name__}")
    print(f"  fields: {[f for f in dir(r) if not f.startswith('_')][:30]}")
    # try to print answer
    for attr in ('answer', 'formatted_answer', 'response', 'output', 'result', 'text'):
        if hasattr(r, attr):
            v = getattr(r, attr)
            if v:
                print(f"\n  --- {attr} ---")
                s = str(v)
                print(s[:3000])
                if len(s) > 3000:
                    print(f"\n  ... [{len(s)-3000} more chars truncated]")
                break

client.close()
print("\n✓ Probe done.")
