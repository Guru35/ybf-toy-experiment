"""
YBF × Edison — Mode 3 Review Batch (6 paralel sorgu)
=====================================================
White Paper v0.4 Editör Mode 3 review'undan çıkan 6 Edison Delegate Query.

Çalıştırma:
    cd ~/Documents/AI-Egitmek/edison_queries
    source venv/bin/activate
    python3 batch_mode3.py 2>&1 | tee batch_mode3_log.txt

Çıktılar:
    edison_mode3_<index>_<label>.json (her sorgu için ayrı)
    batch_mode3_summary.json (toplu özet)

API key kaynağı: macOS keychain (futurehouse-api-key)
Paralelleştirme: ThreadPoolExecutor max_workers=6
Beklenen süre: ~8-12 dk (paralel) vs ~48 dk (sıralı)
"""

import os
import json
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

# ─────────────────────────────────────────────
# API key
# ─────────────────────────────────────────────

API_KEY = os.environ.get("EDISON_API_KEY")
if not API_KEY:
    try:
        API_KEY = subprocess.check_output(
            ["security", "find-generic-password", "-s", "futurehouse-api-key", "-w"],
            stderr=subprocess.DEVNULL,
        ).decode().strip()
        print(f"✓ Keychain'den key alındı (uzunluk: {len(API_KEY)})")
    except subprocess.CalledProcessError:
        print("✗ Edison API key bulunamadı")
        sys.exit(1)

from edison_client import EdisonClient, JobNames

# ─────────────────────────────────────────────
# 6 sorgu (Mode 3 review'undan)
# ─────────────────────────────────────────────

QUERIES = [
    {
        "index": 1,
        "label": "MULTI_JUDGE_SCORING",
        "query": (
            "Has multi-judge ensemble scoring been formalized for LLM evaluation "
            "in 2024-2026 literature? What are the leading approaches for combining "
            "multiple LLM judges with disagreement detection?"
        ),
        "job_name": "LITERATURE",
        "priority": "HIGH",
        "affects": "§References + §3.8 + §8 Future Work #1",
    },
    {
        "index": 2,
        "label": "RLHF_REPLICATION",
        "query": (
            "What are the recent (2024-2026) replication studies of RLHF reliability "
            "and annotator consistency? Are there documented cases of human preference "
            "inconsistency in alignment evaluation?"
        ),
        "job_name": "LITERATURE",
        "priority": "HIGH",
        "affects": "§References + §1 Problem + §5 Comparison",
    },
    {
        "index": 3,
        "label": "BARRIER_METHODS_CRL",
        "query": (
            "What are barrier function methods in constrained reinforcement learning? "
            "Provide a survey of recent (2020-2026) advances. How do barrier functions "
            "differ from reward shaping for handling irreversible constraints?"
        ),
        "job_name": "LITERATURE",
        "priority": "BLOCKER",
        "affects": "§References + §3.7 + §5 Comparison",
    },
    {
        "index": 4,
        "label": "PER_AXIS_REWARD_NOVELTY",
        "query": (
            "Has axis decomposition or per-axis reward feeding been explored in AI "
            "alignment or constrained RL literature? Specifically, providing the agent "
            "with multi-dimensional reward component vectors rather than scalar totals?"
        ),
        "job_name": "PRECEDENT",
        "priority": "HIGH",
        "affects": "§3.6 + §4 Finding 3 + §5 Comparison",
    },
    {
        "index": 5,
        "label": "FIDELITY_GAP_PRIOR_ART",
        "query": (
            "Has the concept of 'fidelity gap' or similar (a model learning a biased "
            "projection of intended reward function rather than the true function) "
            "been documented in alignment literature, related to reward hacking or "
            "Goodhart's law in reinforcement learning?"
        ),
        "job_name": "PRECEDENT",
        "priority": "HIGH",
        "affects": "§3.8 + §4 Finding 7",
    },
    {
        "index": 6,
        "label": "DUAL_LAYER_NOVELTY",
        "query": (
            "Has LLM scorer fidelity been evaluated independently from agent fidelity "
            "in alignment systems? Is dual-layer evaluation methodology (testing scorer "
            "and agent as separate sources of misalignment) established in the literature?"
        ),
        "job_name": "PRECEDENT",
        "priority": "BLOCKER",
        "affects": "§3.8 + §4 Finding 7 + §8 Future Work #1",
    },
]

# ─────────────────────────────────────────────
# Helper: Edison sorgu çalıştırma
# ─────────────────────────────────────────────

def run_single_query(q):
    """Tek sorgu çalıştır, sonuç dict döndür."""
    label = q["label"]
    index = q["index"]
    print(f"[{index}/6 {label}] Başlatıldı (job={q['job_name']})", flush=True)

    start = time.time()
    client = EdisonClient(api_key=API_KEY)  # her thread için ayrı client

    try:
        job = getattr(JobNames, q["job_name"], JobNames.PRECEDENT)
        raw_response = client.run_tasks_until_done({
            "name": job,
            "query": q["query"],
        })
        elapsed = time.time() - start

        # Response handling (test_single.py paterniyle)
        if isinstance(raw_response, list):
            if not raw_response:
                raise ValueError("Boş liste döndü")
            response = raw_response[0]
        else:
            response = raw_response

        answer = getattr(response, "answer", None) or getattr(response, "formatted_answer", None)
        has_successful = getattr(response, "has_successful_answer", None)

        if answer is None:
            available_attrs = [a for a in dir(response) if not a.startswith("_")]
            raise ValueError(f"'answer' attribute yok. Available: {available_attrs}")

        result = {
            "index": index,
            "label": label,
            "query": q["query"],
            "job": q["job_name"],
            "priority": q["priority"],
            "affects": q["affects"],
            "status": "SUCCESS",
            "elapsed_seconds": round(elapsed, 1),
            "has_successful_answer": has_successful,
            "answer_length": len(answer),
            "answer": answer,
        }

        # Tek sorgu JSON çıktısı
        out_path = f"edison_mode3_{index:02d}_{label}.json"
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2, default=str)

        print(f"[{index}/6 {label}] ✓ TAMAM ({elapsed:.1f}s, {len(answer)} char, "
              f"success={has_successful}) → {out_path}", flush=True)
        return result

    except Exception as e:
        elapsed = time.time() - start
        result = {
            "index": index,
            "label": label,
            "query": q["query"],
            "job": q["job_name"],
            "priority": q["priority"],
            "status": "ERROR",
            "elapsed_seconds": round(elapsed, 1),
            "error_type": type(e).__name__,
            "error_message": str(e),
        }
        print(f"[{index}/6 {label}] ✗ HATA ({elapsed:.1f}s): {type(e).__name__}: {e}",
              flush=True)
        return result

# ─────────────────────────────────────────────
# Main — paralel çalıştır
# ─────────────────────────────────────────────

print(f"\n{'='*70}")
print(f"YBF × Edison Mode 3 Batch — 6 paralel sorgu başlatılıyor")
print(f"{'='*70}")
print(f"Sorgular:")
for q in QUERIES:
    print(f"  {q['index']}. {q['label']:30} ({q['job_name']:10}) [{q['priority']}]")
print(f"{'='*70}\n")

batch_start = time.time()
results = []

with ThreadPoolExecutor(max_workers=6) as executor:
    future_to_query = {executor.submit(run_single_query, q): q for q in QUERIES}
    for future in as_completed(future_to_query):
        result = future.result()
        results.append(result)

batch_elapsed = time.time() - batch_start

# Sıralı sonuç (index'e göre)
results.sort(key=lambda r: r["index"])

# Özet JSON
summary = {
    "batch": "Mode 3 Review — White Paper v0.4 Edison Delegate Queries",
    "date": time.strftime("%Y-%m-%d %H:%M:%S"),
    "total_queries": len(QUERIES),
    "successful": sum(1 for r in results if r["status"] == "SUCCESS"),
    "failed": sum(1 for r in results if r["status"] == "ERROR"),
    "total_elapsed_seconds": round(batch_elapsed, 1),
    "queries": results,
}

with open("batch_mode3_summary.json", "w", encoding="utf-8") as f:
    json.dump(summary, f, ensure_ascii=False, indent=2, default=str)

# Console özet
print(f"\n{'='*70}")
print(f"✓ BATCH TAMAMLANDI")
print(f"{'='*70}")
print(f"Toplam süre: {batch_elapsed:.1f}s ({batch_elapsed/60:.1f} dk)")
print(f"Başarılı: {summary['successful']}/{summary['total_queries']}")
print(f"Hatalı:   {summary['failed']}/{summary['total_queries']}")
print(f"\nDetaylı sonuçlar:")
for r in results:
    icon = "✓" if r["status"] == "SUCCESS" else "✗"
    print(f"  {icon} [{r['index']}] {r['label']:30} {r.get('elapsed_seconds', '?'):.1f}s "
          f"{'success=' + str(r.get('has_successful_answer', '?')) if r['status']=='SUCCESS' else r.get('error_type', '?')}")

print(f"\nÇıktılar:")
print(f"  edison_mode3_NN_LABEL.json (6 dosya)")
print(f"  batch_mode3_summary.json (özet)")
print(f"\nSıradaki: bu dosyaları wiki/ciktilar/'a kopyala + sentez yaz")
