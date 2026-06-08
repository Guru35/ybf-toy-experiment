"""
Score OOD scenarios with the same YBF scorer used for in-distribution data,
then filter to actual traps.
"""

import os, json, subprocess
key = subprocess.check_output(
    ['security', 'find-generic-password', '-s', 'ANTHROPIC_API_KEY', '-w']
).decode().strip()
os.environ["ANTHROPIC_API_KEY"] = key

from scorer import _call_api, compute_reward, has_veto
AXES = ["gerceklik", "onur", "saygi", "sinir", "ozgurluk"]

with open("data/ood_scenarios_raw.json") as f:
    scenarios = json.load(f)

print(f"Scoring {len(scenarios)} OOD scenarios × 2 actions = {len(scenarios)*2} API calls\n")

scored = []
for i, s in enumerate(scenarios):
    print(f"  [{i+1}/{len(scenarios)}] {s['target_axis']}: {s['situation'][:50]}...")
    a_axes = _call_api(s["situation"], s["intention"], s["options"]["A"])
    b_axes = _call_api(s["situation"], s["intention"], s["options"]["B"])
    a_reward = compute_reward(a_axes)
    b_reward = compute_reward(b_axes)
    a_veto = has_veto(a_axes)
    b_veto = has_veto(b_axes)
    scored.append({
        **s,
        "scores_A": {**a_axes, "reward": a_reward, "veto": a_veto},
        "scores_B": {**b_axes, "reward": b_reward, "veto": b_veto},
        "is_trap": b_reward > a_reward,
        "target_axis_differential": b_axes[s["target_axis"]] - a_axes[s["target_axis"]],
    })
    print(f"      A reward={a_reward:+.0f} | B reward={b_reward:+.0f} | trap={scored[-1]['is_trap']}")

with open("data/ood_scenarios_scored.json", "w") as f:
    json.dump(scored, f, indent=2, ensure_ascii=False)

# Filter to actual traps where target axis is decisive
true_traps = []
for s in scored:
    if not s["is_trap"]:
        continue
    # Decisive = target axis differential is the largest single contributor
    diffs = {ax: s["scores_B"][ax] - s["scores_A"][ax] for ax in AXES}
    top_axis = max(diffs, key=lambda k: diffs[k])
    s["decisive_axis"] = top_axis
    s["axis_differentials"] = diffs
    if diffs[s["target_axis"]] > 0:
        true_traps.append(s)

print(f"\n{'='*65}")
print(f"SCORING SUMMARY")
print(f"{'='*65}")
print(f"  Total generated:           {len(scenarios)}")
print(f"  Actual traps (r_B > r_A):  {sum(1 for s in scored if s['is_trap'])}")
print(f"  Target-axis traps:         {len(true_traps)}")
print(f"    GERCEKLIK-decisive:      {sum(1 for s in true_traps if s['target_axis']=='gerceklik')}")
print(f"    ONUR-decisive:           {sum(1 for s in true_traps if s['target_axis']=='onur')}")

# Show top traps per axis
for axis_name in ["gerceklik", "onur"]:
    axis_traps = [s for s in true_traps if s["target_axis"] == axis_name]
    print(f"\n  {axis_name.upper()} traps ({len(axis_traps)}):")
    for s in axis_traps[:5]:
        print(f"    [{s['id']}] {s['situation'][:60]}...")
        print(f"      A axes: {[s['scores_A'][a] for a in AXES]} r={s['scores_A']['reward']:+.0f}")
        print(f"      B axes: {[s['scores_B'][a] for a in AXES]} r={s['scores_B']['reward']:+.0f}")

with open("data/ood_traps_filtered.json", "w") as f:
    json.dump(true_traps, f, indent=2, ensure_ascii=False)
print(f"\n✓ Filtered traps saved → data/ood_traps_filtered.json")
