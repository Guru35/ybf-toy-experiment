"""
YBF × Edison — Single Query Test
================================
Sadece VETO_KURALI (PRECEDENT) sorgusu — kurulum + key doğrulama amaçlı.

Çalıştırma:
    cd ~/Documents/AI-Egitmek/edison_queries
    source venv/bin/activate
    python3 test_single.py

API key kaynağı (sırasıyla):
1. EDISON_API_KEY env var
2. macOS keychain (service: futurehouse-api-key)
"""

import os
import json
import subprocess
import sys
import time

# ─────────────────────────────────────────────
# API key resolution: env var → keychain fallback
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
        print("✗ EDISON_API_KEY env var YOK, keychain'de futurehouse-api-key YOK")
        print("  Manuel set için:")
        print("    export EDISON_API_KEY=$(security find-generic-password -s futurehouse-api-key -w)")
        sys.exit(1)
else:
    print(f"✓ Env var'dan key alındı (uzunluk: {len(API_KEY)})")

from edison_client import EdisonClient, JobNames

client = EdisonClient(api_key=API_KEY)

# ─────────────────────────────────────────────
# Tek sorgu — en kritik (IP açısından)
# ─────────────────────────────────────────────

QUERY = (
    "Has anyone formalized irreversibility as a distinct category "
    "in ethical decision-making or AI value alignment frameworks?"
)
LABEL = "VETO_KURALI"

print(f"\n{'='*60}")
print(f"[{LABEL}] Edison'a soruluyor (PRECEDENT)...")
print(f"Sorgu: {QUERY}")
print(f"{'='*60}\n")

start = time.time()

try:
    raw_response = client.run_tasks_until_done({
        "name": JobNames.PRECEDENT,
        "query": QUERY,
    })

    elapsed = time.time() - start
    print(f"✓ Edison çağrısı tamamlandı ({elapsed:.1f}s)")
    print(f"Response type: {type(raw_response).__name__}")

    # Adaptive response handling — v0.11.1 'list' döndürüyor
    if isinstance(raw_response, list):
        print(f"Response liste, uzunluk: {len(raw_response)}")
        if not raw_response:
            raise ValueError("Edison boş liste döndürdü")
        response = raw_response[0]
        print(f"İlk öge tipi: {type(response).__name__}")
    else:
        response = raw_response

    # Mevcut attribute'leri keşfet
    available_attrs = [a for a in dir(response) if not a.startswith('_')]
    print(f"Response attributes: {available_attrs[:15]}{'...' if len(available_attrs) > 15 else ''}")

    answer = getattr(response, 'answer', None) or getattr(response, 'formatted_answer', None)
    if answer is None:
        # Belki dict-like
        if hasattr(response, '__dict__'):
            print(f"__dict__ keys: {list(response.__dict__.keys())[:15]}")
        raise ValueError(f"'answer' attribute bulunamadı. Available: {available_attrs}")

    has_successful = getattr(response, 'has_successful_answer', None)

    result = {
        "label": LABEL,
        "query": QUERY,
        "job": "PRECEDENT",
        "answer": answer,
        "has_successful_answer": has_successful,
        "elapsed_seconds": round(elapsed, 1),
        "response_type": type(response).__name__,
        "all_attributes": available_attrs,
    }

    print(f"\n✓ YANIT (ilk 2000 karakter):")
    print(f"{'─'*60}")
    print(answer[:2000])
    if len(answer) > 2000:
        print(f"\n... [+{len(answer)-2000} karakter daha, JSON'da tam metin]")

    with open("test_single_result.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2, default=str)
    print(f"\n{'='*60}")
    print(f"✓ Tam yanıt JSON: test_single_result.json")
    print(f"✓ Süre: {elapsed:.1f} saniye")
    print(f"✓ has_successful_answer: {has_successful}")

except Exception as e:
    elapsed = time.time() - start
    print(f"\n✗ HATA ({elapsed:.1f}s sonra): {type(e).__name__}: {e}")
    sys.exit(1)
