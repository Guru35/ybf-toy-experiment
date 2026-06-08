"""
A — Reverse-engineer axial agent's learned reward function.

W matrix structure: (389, 1)
  W[:384]   — embedding weights (should be small if model is reward-blind)
  W[384:389] — axis weights (one per: gerceklik, onur, saygi, sinir, ozgurluk)

We compare the agent's learned function to the true reward:
  true: r = sum(axes) if all axes >= 0, else -5
"""

import numpy as np
import json

AXES = ["gerceklik", "onur", "saygi", "sinir", "ozgurluk"]

# ── Load weights ─────────────────────────────────────────────────────────────
data = np.load("data/agent_axial_weights.npy", allow_pickle=True).item()
W = data["W"]  # (389, 1)
b = data["b"]  # (1,)

print("="*68)
print("AXIAL AGENT REVERSE-ENGINEERING")
print("="*68)
print(f"\nW shape: {W.shape}")
print(f"b: {b[0]:+.4f}\n")

# ── Embedding weights ───────────────────────────────────────────────────────
W_emb = W[:384, 0]
print("[Embedding weights — W[:384]]")
print(f"  norm L2:    {np.linalg.norm(W_emb):.3f}")
print(f"  mean:       {W_emb.mean():+.4f}")
print(f"  std:        {W_emb.std():.4f}")
print(f"  max:        {W_emb.max():+.4f}")
print(f"  min:        {W_emb.min():+.4f}")
print(f"  median |w|: {np.median(np.abs(W_emb)):.4f}")

# ── Axis weights ────────────────────────────────────────────────────────────
W_ax = W[384:389, 0]
print("\n[Axis weights — W[384:389]]")
print(f"  {'AXIS':<10}  {'weight':>10}   bar")
print(f"  {'-'*10}  {'-'*10}   {'-'*30}")
for ax, w in zip(AXES, W_ax):
    bar_len = int(abs(w) * 15)
    bar = "█" * min(bar_len, 30)
    sign = "+" if w >= 0 else "-"
    print(f"  {ax.upper():<10}  {w:+10.4f}   {bar} ({sign})")

print(f"\n  Σ(axis weights) = {W_ax.sum():+.4f}")
print(f"  Mean axis weight = {W_ax.mean():+.4f}")
print(f"  If ideal (Σ axes), weights should be ~+1 each. Observed:")
ratios = W_ax / 1.0
print(f"    Ratio to ideal: {[f'{r:+.3f}' for r in ratios]}")

# ── Predicted Q for canonical axis patterns ──────────────────────────────────
print("\n[Predicted Q for canonical axis patterns — embedding=0]")
print(f"  Note: real input has embedding too. Pure-axis Q tests function shape.")

# Make a fake input: emb=0, then axes
def predict_axis_only(axis_values):
    """Predict Q assuming embedding is zero."""
    inp = np.zeros(389, dtype=np.float32)
    inp[384:389] = axis_values
    return float((inp @ W + b).item())

cases = [
    ("All +1 (best)",       [+1, +1, +1, +1, +1], 5.0),
    ("All  0 (neutral)",    [ 0,  0,  0,  0,  0], 0.0),
    ("Single -1: GERCEKLIK", [-1,  0,  0,  0,  0], -5.0),  # veto trigger
    ("Single -1: ONUR",      [ 0, -1,  0,  0,  0], -5.0),
    ("Single -1: SAYGI",     [ 0,  0, -1,  0,  0], -5.0),
    ("Single -1: SINIR",     [ 0,  0,  0, -1,  0], -5.0),
    ("Single -1: OZGURLUK",  [ 0,  0,  0,  0, -1], -5.0),
    ("Mixed +1/0",          [+1, +1, +1,  0,  0], 3.0),
    ("Trap 1 A (vetoed)",   [+1,  0, -1,  0, -1], -5.0),
    ("Trap 1 B (clean)",    [+1, +1, +1, +1, +1], 5.0),
    ("Trap 2 A (vetoed)",   [ 0, +1, +1, -1,  0], -5.0),
    ("Trap 2 B (clean)",    [+1, +1, +1, +1, +1], 5.0),
    ("Trap 3 A (soft)",     [+1, +1, +1,  0, +1], 4.0),
    ("Trap 3 B (soft)",     [+1, +1, +1, +1, +1], 5.0),
    ("All -1 (worst)",       [-1, -1, -1, -1, -1], -5.0),
]

print(f"\n  {'case':<26}  {'true r':>7}  {'pred Q':>8}  {'error':>8}")
print(f"  {'-'*26}  {'-'*7}  {'-'*8}  {'-'*8}")
errors_clean = []
errors_veto = []
for label, axes, true_r in cases:
    pred = predict_axis_only(axes)
    err = pred - true_r
    if true_r == -5.0:
        errors_veto.append(err)
    else:
        errors_clean.append(err)
    flag = " ⚠" if abs(err) > 1.0 else ""
    print(f"  {label:<26}  {true_r:+7.2f}  {pred:+8.3f}  {err:+8.3f}{flag}")

print(f"\n[Error analysis]")
print(f"  Clean cases (n={len(errors_clean)}):  mean error = {np.mean(errors_clean):+.3f}, "
      f"max |error| = {np.max(np.abs(errors_clean)):.3f}")
print(f"  Veto cases  (n={len(errors_veto)}):  mean error = {np.mean(errors_veto):+.3f}, "
      f"max |error| = {np.max(np.abs(errors_veto)):.3f}")

# ── Veto detection capability ────────────────────────────────────────────────
print("\n[Veto detection per axis]")
print("  How much Q drops when ONE axis flips from 0 → -1 (other axes 0)")
print(f"  Ideal drop: -5.0 (full veto penalty). Observed:")
for i, ax in enumerate(AXES):
    base = predict_axis_only([0]*5)
    veto_ax = [0]*5
    veto_ax[i] = -1
    pred = predict_axis_only(veto_ax)
    drop = pred - base
    pct = drop / -5.0 * 100
    print(f"    {ax.upper():<10}  drop = {drop:+.3f}   ({pct:.0f}% of ideal -5)")

# ── Save figure data for white paper ─────────────────────────────────────────
fig_data = {
    "embedding_weights": {
        "norm": float(np.linalg.norm(W_emb)),
        "mean": float(W_emb.mean()),
        "std": float(W_emb.std()),
        "max_abs": float(np.abs(W_emb).max()),
        "median_abs": float(np.median(np.abs(W_emb))),
    },
    "axis_weights": {ax: float(w) for ax, w in zip(AXES, W_ax)},
    "axis_weight_sum": float(W_ax.sum()),
    "bias": float(b[0]),
    "predictions": [
        {"case": label, "axes": list(axes), "true_reward": tr,
         "predicted_q": predict_axis_only(axes)}
        for label, axes, tr in cases
    ],
    "clean_case_max_error": float(np.max(np.abs(errors_clean))),
    "veto_case_max_error": float(np.max(np.abs(errors_veto))),
    "veto_detection_drops": {
        ax: float(predict_axis_only([(0 if j!=i else -1) for j in range(5)]) - predict_axis_only([0]*5))
        for i, ax in enumerate(AXES)
    },
}

with open("results/axial_weight_analysis.json", "w") as f:
    json.dump(fig_data, f, indent=2)
print(f"\n✓ Saved analysis data → results/axial_weight_analysis.json")

# ── Conclusion ───────────────────────────────────────────────────────────────
print("\n" + "="*68)
print("INTERPRETATION")
print("="*68)

axis_avg = W_ax.mean()
emb_norm = np.linalg.norm(W_emb)
emb_to_axis_ratio = (emb_norm / np.sqrt(384)) / abs(axis_avg)

print(f"""
Learned approximate function:
  Q(emb, axes) ≈ Σ_i ({W_ax[0]:+.2f}·G + {W_ax[1]:+.2f}·O + {W_ax[2]:+.2f}·Sa
                      + {W_ax[3]:+.2f}·Si + {W_ax[4]:+.2f}·Öz) + (small emb contribution)

Compared to the true reward function:
  r = Σ(axes) - 5·is_veto(axes)
    = Σ(axes)         if all axes ≥ 0
    = -5              if any axis = -1

Axis weight ratios to ideal +1: {[f'{w:.2f}' for w in W_ax]}
Average axis weight: {axis_avg:+.3f} (ideal +1.0)

Embedding contribution per unit input:
  Per-feature mean weight: {abs(W_emb).mean():.4f}
  Total embedding L2 norm: {emb_norm:.3f}
  Relative to axis weights (per dim): {(abs(W_emb).mean() / abs(axis_avg) * 100):.1f}%

The agent learned the axis-sum part well but cannot model the veto cliff
(piecewise -5 jump) with a purely linear function. It approximates the veto
by driving Q strongly negative through the -1 axis weights instead — the
'drop per axis' analysis above shows the per-axis linear penalty it learned.
""")
