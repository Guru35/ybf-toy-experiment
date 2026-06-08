"""
Multi-judge test for §3.8 GERCEKLIK fidelity gap.

Hypothesis: GERCEKLIK scorer-level fidelity gap (Haiku's "comforting=moral"
prior) is NOT a Haiku-specific quirk but a structural language-model prior.
If true: Sonnet 4.5 will produce a similar verdict on the same scenarios.
If false: Sonnet differs → multi-judge ensemble is the mitigation §8 suggests.

Method:
  - 10 GERCEKLIK OOD scenarios (already generated, in data/ood_scenarios_raw.json)
  - Score each with: Haiku 4.5 (already have results) + Sonnet 4.5 (new)
  - Compute axis-level disagreement, especially on GERCEKLIK
  - Compute reward-level disagreement (would each model flag this as trap?)
"""

import json, os, time, subprocess
from anthropic import Anthropic

# API key from keychain
key = subprocess.check_output(
    ['security', 'find-generic-password', '-s', 'ANTHROPIC_API_KEY', '-w']
).decode().strip()
os.environ["ANTHROPIC_API_KEY"] = key
client = Anthropic()

SONNET_MODEL = "claude-sonnet-4-5-20250929"  # Latest available Sonnet 4.5
HAIKU_MODEL = "claude-haiku-4-5-20251001"

# Use the SAME scorer prompt as our existing scorer.py
from scorer import YBF_SYSTEM, YBF_USER, _parse_json, compute_reward

AXES = ["gerceklik", "onur", "saygi", "sinir", "ozgurluk"]


def score_with_model(model_id, situation, intention, action, max_retries=3):
    prompt = YBF_USER.format(situation=situation, intention=intention, action=action)
    for attempt in range(max_retries):
        try:
            resp = client.messages.create(
                model=model_id,
                max_tokens=100,
                system=YBF_SYSTEM,
                messages=[{"role": "user", "content": prompt}]
            )
            text = resp.content[0].text
            parsed = _parse_json(text)
            if parsed and set(parsed.keys()) == set(AXES):
                return parsed
        except Exception as e:
            print(f"  ⚠ {model_id} attempt {attempt+1}: {e}")
            time.sleep(2 ** attempt)
    raise RuntimeError(f"{model_id} failed after {max_retries} retries")


# Load 10 GERCEKLIK scenarios (the ones that all came back A=+5/B=-5 with Haiku)
with open("data/ood_scenarios_raw.json") as f:
    all_scenarios = json.load(f)

gerceklik_scenarios = [s for s in all_scenarios if s["target_axis"] == "gerceklik"]
print(f"Loaded {len(gerceklik_scenarios)} GERCEKLIK OOD scenarios\n")
assert len(gerceklik_scenarios) == 10, "Expected 10 GERCEKLIK scenarios"

# Load existing Haiku scores from the scored file
with open("data/ood_scenarios_scored.json") as f:
    scored = json.load(f)
haiku_by_id = {s["id"]: s for s in scored if s["target_axis"] == "gerceklik"}

# Score each with Sonnet
print(f"Scoring with Sonnet 4.5 ({SONNET_MODEL})...\n")
results = []
for i, s in enumerate(gerceklik_scenarios, 1):
    print(f"[{i}/10] sid={s['id']}: {s['situation'][:60]}...")
    haiku = haiku_by_id[s["id"]]
    haiku_A = haiku["scores_A"]
    haiku_B = haiku["scores_B"]

    sonnet_A = score_with_model(SONNET_MODEL, s["situation"], s["intention"], s["options"]["A"])
    time.sleep(0.5)
    sonnet_B = score_with_model(SONNET_MODEL, s["situation"], s["intention"], s["options"]["B"])
    time.sleep(0.5)

    sonnet_A_reward = compute_reward(sonnet_A)
    sonnet_B_reward = compute_reward(sonnet_B)
    sonnet_is_trap = sonnet_B_reward > sonnet_A_reward

    haiku_is_trap = haiku_B["reward"] > haiku_A["reward"]

    print(f"   Haiku:  A_axes={[haiku_A[a] for a in AXES]} r={haiku_A['reward']}  "
          f"B_axes={[haiku_B[a] for a in AXES]} r={haiku_B['reward']}  trap={haiku_is_trap}")
    print(f"   Sonnet: A_axes={[sonnet_A[a] for a in AXES]} r={sonnet_A_reward}  "
          f"B_axes={[sonnet_B[a] for a in AXES]} r={sonnet_B_reward}  trap={sonnet_is_trap}")

    results.append({
        "id": s["id"], "situation": s["situation"], "intention": s["intention"],
        "options": s["options"],
        "haiku":  {"A_axes": haiku_A, "B_axes": haiku_B,
                    "A_reward": haiku_A["reward"], "B_reward": haiku_B["reward"],
                    "is_trap": haiku_is_trap},
        "sonnet": {"A_axes": {**sonnet_A, "reward": sonnet_A_reward},
                    "B_axes": {**sonnet_B, "reward": sonnet_B_reward},
                    "A_reward": sonnet_A_reward, "B_reward": sonnet_B_reward,
                    "is_trap": sonnet_is_trap},
        "agreement": {
            "trap_match": haiku_is_trap == sonnet_is_trap,
            "axis_agreement": {
                ax: {
                    "A_match": haiku_A[ax] == sonnet_A[ax],
                    "B_match": haiku_B[ax] == sonnet_B[ax],
                } for ax in AXES
            },
        },
    })
    print()

# Aggregate analysis
print("="*70)
print("AGGREGATE — Multi-judge GERCEKLIK fidelity test")
print("="*70)

trap_match_count = sum(1 for r in results if r["agreement"]["trap_match"])
print(f"\nTrap verdict agreement: {trap_match_count}/10")

sonnet_trap_count = sum(1 for r in results if r["sonnet"]["is_trap"])
haiku_trap_count = sum(1 for r in results if r["haiku"]["is_trap"])
print(f"  Haiku  identifies as trap: {haiku_trap_count}/10")
print(f"  Sonnet identifies as trap: {sonnet_trap_count}/10")

print(f"\nPer-axis agreement on action A (n=10):")
for ax in AXES:
    a_match = sum(1 for r in results if r["agreement"]["axis_agreement"][ax]["A_match"])
    print(f"  {ax.upper():<10} A axis match: {a_match}/10")

print(f"\nPer-axis agreement on action B (n=10):")
for ax in AXES:
    b_match = sum(1 for r in results if r["agreement"]["axis_agreement"][ax]["B_match"])
    print(f"  {ax.upper():<10} B axis match: {b_match}/10")

# GERCEKLIK-specific analysis (the supposed fidelity gap axis)
print(f"\n🎯 GERCEKLIK axis specifically (the gap §3.8 identified):")
print(f"  {'sid':<8} {'A action':<50} {'Haiku G_A':>10} {'Sonnet G_A':>10} {'agreement':>10}")
for r in results:
    a_match = "✓" if r["agreement"]["axis_agreement"]["gerceklik"]["A_match"] else "✗"
    print(f"  {r['id']:<8} {r['options']['A'][:48]:<50} "
          f"{r['haiku']['A_axes']['gerceklik']:>+10} "
          f"{r['sonnet']['A_axes']['gerceklik']:>+10}  {a_match:>9}")

# Save
out = {
    "config": {"sonnet_model": SONNET_MODEL, "haiku_model": HAIKU_MODEL, "n_scenarios": 10},
    "results": results,
    "summary": {
        "trap_agreement": f"{trap_match_count}/10",
        "haiku_traps": f"{haiku_trap_count}/10",
        "sonnet_traps": f"{sonnet_trap_count}/10",
        "axis_agreement_A": {ax: sum(1 for r in results if r["agreement"]["axis_agreement"][ax]["A_match"]) for ax in AXES},
        "axis_agreement_B": {ax: sum(1 for r in results if r["agreement"]["axis_agreement"][ax]["B_match"]) for ax in AXES},
    },
}
with open("results/multijudge_gerceklik_results.json", "w") as f:
    json.dump(out, f, indent=2, ensure_ascii=False)
print(f"\n✓ Saved → results/multijudge_gerceklik_results.json")
