"""
YBF Trap Scenario Analysis
Çalıştır: python analyze_traps.py
Dizin: ~/Documents/AI-Egitmek/ybf_toy/
"""

import json
import os

DATA_DIR = "data"
SCENARIOS_PATH  = os.path.join(DATA_DIR, "scenarios.json")
CACHE_PATH      = os.path.join(DATA_DIR, "scores_cache.json")

def load():
    with open(SCENARIOS_PATH) as f:
        scenarios = json.load(f)
    with open(CACHE_PATH) as f:
        cache = json.load(f)
    return scenarios, cache

def get_entry(cache, sid, action):
    key = f"scenario_{sid}_action_{action}"
    return cache.get(key, {})

def is_trap(cache, s):
    a = get_entry(cache, s["id"], "A").get("reward", -99)
    b = get_entry(cache, s["id"], "B").get("reward", -99)
    return b > a

def fmt_axes(entry):
    axes = ["gerceklik","onur","saygi","sinir","ozgurluk"]
    parts = []
    for ax in axes:
        v = entry.get(ax, "?")
        sign = "+" if v == 1 else (" " if v == 0 else "")
        parts.append(f"{ax[:2].upper()}={sign}{v}")
    return "  ".join(parts)

def main():
    scenarios, cache = load()

    # Test seti: son %20
    split = int(len(scenarios) * 0.8)
    test_scenarios = scenarios[split:]

    traps = [s for s in test_scenarios if is_trap(cache, s)]

    print(f"\n{'='*70}")
    print(f"YBF TRAP SENARYOLARI — B'nin A'dan daha yüksek YBF aldığı durumlar")
    print(f"Test seti: {len(test_scenarios)} senaryo | Trap: {len(traps)} bulundu")
    print(f"{'='*70}\n")

    for i, s in enumerate(traps, 1):
        a_entry = get_entry(cache, s["id"], "A")
        b_entry = get_entry(cache, s["id"], "B")
        a_reward = a_entry.get("reward", "?")
        b_reward = b_entry.get("reward", "?")

        print(f"TRAP {i} — Senaryo ID: {s['id']}")
        print(f"{'─'*70}")
        print(f"Durum:     {s.get('situation','?')}")
        print(f"Niyet:     {s.get('intention','?')}")
        print(f"Norm:      {s.get('norm','?')}")
        print()
        print(f"[A] {s['options']['A']}")
        print(f"    {fmt_axes(a_entry)}")
        print(f"    Reward: {a_reward}")
        print()
        print(f"[B] {s['options']['B']}")
        print(f"    {fmt_axes(b_entry)}")
        print(f"    Reward: {b_reward}")
        print()

        # Hangi eksen fark yarattı
        axes = ["gerceklik","onur","saygi","sinir","ozgurluk"]
        diffs = []
        for ax in axes:
            a_v = a_entry.get(ax, 0)
            b_v = b_entry.get(ax, 0)
            if b_v > a_v:
                diffs.append(f"{ax.upper()} (A={a_v} → B={b_v})")
        if diffs:
            print(f"B neden kazanıyor: {', '.join(diffs)}")
        print(f"{'='*70}\n")

if __name__ == "__main__":
    main()
