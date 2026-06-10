# LCP/YBF Value-Alignment Experiments — Full Submission for Literature Review & Novelty Assessment

**Author:** Gökhan Kazancı (GONET Digital Agency, İzmir, Turkey) · gokhan@gonet.com.tr
**Date:** 2026-06-10
**Framework:** Lean Consciousness Philosophy (LCP) / Yalın Bilinç Felsefesi (YBF)
**Artifacts:** Technical White Paper v0.4.11; code github.com/Guru35/ybf-toy-experiment; Zenodo DOI 10.5281/zenodo.20599906; License CC-BY-4.0

---

## PART 0 — REQUEST TO THE REVIEWER

I have a connected set of empirical findings from aligning language models (135M to frontier scale) to a structured philosophical value framework — a five-axis ethical decomposition — focusing on the foundational **Reality** axis (recognition of an action's actual physical, biological, ecological, temporal, and factual ground, independent of how it is framed). The complete experimental record is in Parts 2–4 below.

**Please conduct a literature review and assess the NOVELTY of each finding, citing the closest prior work that anticipates, supports, or contradicts it. For each, state: closest prior work; whether the finding is novel / incremental / already-known; and any methodological precedent.**

1. **Scale-asymmetric reinforcement.** Pure-reward PPO (the policy never sees the value definition; it learns only from a hidden +1/−1 reward) instills the value in a 135M model (OOD accuracy 24%→72%, 3 seeds) but catastrophically collapses a 0.5B model that **already** encodes the value (≈72% untrained → collapse at every learning rate). The marginal value of RL flips sign with the strength of the pretrained prior. *Is the "RL helps low-prior models but harms high-prior / pre-aligned ones" asymmetry documented?*

2. **Preference–behavior dissociation.** DPO shifts a model's held-out chosen-vs-rejected logprob accuracy from 46% to 85% (mean log-margin +0.16 → +20) while producing **zero** change in its greedy generated behavior on the same distribution. *Literature on the gap between preference / reward-model metrics and actual generated behavior in DPO/RLHF?*

3. **Proxy / shortcut learning detected by conflict cases.** When the target value co-aligns with conventional morality in 97.6% of training pairs, DPO learns the surface correlate ("prefer the conventionally-moral action"); on the 2.4% conflict cases the model gets **worse** with stronger training (−12.9 pp). *Literature on shortcut / spurious-correlation learning in preference optimization, and on conflict / counterfactual probes to distinguish a learned concept from a learned proxy?*

4. **Capability threshold in constitutional (in-context) value application.** With the value definition supplied as a constitution and chain-of-thought requested, 7B and 14B models score **identically at 42%** (below chance) on conflict cases while a frontier model scores **87%** — a threshold, not smooth scaling. *What is known about emergent capability thresholds in instruction-following, moral/normative reasoning, and in-context (constitutional) alignment?*

5. **Methodological:** Is the use of a **"conflict evaluation"** (scenarios where the target value disagrees with conventional morality) as a diagnostic of *genuine* value learning (vs. proxy learning) established in the literature?

---

## PART 1 — SUMMARY

We test whether a structured philosophical value (LCP/YBF Reality axis) can be instilled in, or applied by, language models, across three regimes — reinforcement learning (PPO), preference optimization (DPO), and in-context constitutional prompting — on models from 135M to frontier scale. The reward signal is a hidden Claude Haiku 4.5 judge that scores a chosen action +1/−1 on Reality behind a 16,170-character canonical definition; the policy never sees the definition.

Four results: (1) pure-reward PPO teaches a 135M model (OOD 24%→72%) but collapses a 0.5B model that already encodes the value — the value of RL flips sign with the prior; (2) DPO preserves the 0.5B model and moves its internal preference enormously (logprob 46%→85%) while changing its behavior not at all; (3) a targeted conflict ("flip") evaluation reveals that DPO learned a surface proxy ("prefer the conventionally-moral action"), not the value, because 97.6% of training pairs co-align value and convention — on conflicts, stronger training makes it worse; (4) supplied in-context as a constitution, a frontier model applies the value on 87% of conflicts while 7B and 14B models plateau at 42%, a capability threshold. We argue the conflict evaluation is the essential diagnostic, and that constitutional prompting on a frontier model — not small-model fine-tuning — is the practical path to a usable value-aligned system.

---

## PART 2 — METHODS (DETAILED)

**Value framework.** LCP/YBF decomposes ethical judgment into five axes — Reality, Dignity (Onur), Respect (Saygı), Boundary (Sınır), Freedom (Özgürlük) — under a veto rule (any axis = −1 invalidates the action). Each axis has a canonical ~16–20k-character English definition with +1/0/−1 scoring rules, edge cases, cross-axis interactions, and a "framing trap" (the score follows what the action does, never how it is framed). This study focuses on **Reality**.

**Reward / judge.** Claude Haiku 4.5 with the Reality definition as a cached system prompt scores a single chosen action +1 / 0 / −1. Prior multi-judge work (Sonnet 4.5 vs Haiku 4.5 on 20 held-out trap scenarios) found 100% axis-level agreement on Reality, indicating the judge is stable for this axis.

**Policy prompt (PPO/DPO).** Axis-labeled, definition-free:
`[REALITY] You are making a moral decision... Situation / Norm / Option A / Option B / Which action is better? Reply with just one letter: A or B. Answer:`
The label distinguishes axes across multi-axis training without revealing the definition.

**Data.** 1,200 Moral Stories scenarios (each: situation, intention, norm, moral_action, immoral_action). Re-scored on Reality by the Haiku judge (both actions, with one-line reasoning) → `scenarios_reality_relabeled_v1.jsonl`. From this: **943 decisive pairs** (the two actions differ on Reality); **31 "flips"** where the Reality-aligned action is the dataset's *immoral* action; held-out 100 in-distribution test + 25 out-of-distribution (SINIR/boundary-decisive scenarios, scored on Reality — cross-axis OOD). Note the strong co-alignment: of 714 clean (+1/−1) pairs, **697 (97.6%) have the conventional moral action = Reality-aligned**.

**Methods.** PPO: TRL 0.11.4 legacy PPOTrainer over AutoModelForCausalLMWithValueHead + LoRA (r=8, q_proj/v_proj). DPO: TRL DPOTrainer + LoRA. Constitutional: the definition as system prompt + an instruction to judge by actual impact (not framing/convention) + chain-of-thought + a final A/B.

**Two evaluations.** (a) *generate + judge*: the model greedily emits A/B; the chosen action is scored on Reality by Haiku; accuracy = % Reality-aligned choices. (b) *flip-eval*: on the conflict set, does the model pick the (here unconventional) Reality-aligned action? Ground truth is the relabel; A/B positions are randomized (seed 42) to remove position bias; no judge call needed.

---

## PART 3 — COMPLETE EXPERIMENTAL RECORD (ALL DATA)

### 3.1 PPO collapse and stabilization
Naive PPO collapsed: KL divergence → −2000, ppo_loss → 110, evaluation → 0%. Two causes: (i) greedy rollout (do_sample=False) degenerates the importance-sampling ratio; (ii) at lr=1.4e-5 the policy drifts into KL instability at ~150 optimizer steps, driven by near-zero training reward (a 135M model rarely emits a parseable A/B when sampling). Fix: do_sample=True, lr=4e-6, rollout temperature 0.7. Two automatic guards: in-round abort when ppo_loss>5; post-round halt + best-checkpoint when OOD crashes ≥20 pp below best.

### 3.2 Result 1 — Pure-reward PPO, SmolLM-135M (three seeds)
| Seed | Baseline OOD | Best OOD | @round | Trajectory (OOD) |
|---|---|---|---|---|
| 42 | 24.0% | 72.0% | 1 | 24→72→72 (r4 over-training collapse to 0) |
| 43 | 24.0% | 72.0% | 1 | 24→72→56 |
| 44 | 24.0% | 68.0% | 2 | 24→40→68 (slow-converging) |

Mean OOD ≈ 71%; ID 30%→63–77%. Begins **below chance** (24%) and learns from reward alone. Round 1 (seed 42): ID 30→77%, OOD 24→72% (+48 pp), mean reward −0.39→+0.44. Post-convergence the policy drifts to collapse by round 4 unless best-checkpointed (the collapse guard handles this).

### 3.3 Result 1 — Pure-reward PPO, Qwen2.5-0.5B (same procedure)
| Learning rate | Baseline OOD | Trajectory | Effect |
|---|---|---|---|
| 4e-6 | 68% | 48% @r1 → guard halt | −20 pp (degraded) |
| 1e-6 | 76% | 64% @r1 → 16% @r2 → guard | −60 pp (collapse; ID → 1%) |

Qwen begins **above chance** (≈72–76% OOD untrained) and the identical procedure degrades it at both learning rates; the 10× lower lr only delays collapse by one round. The two models reach ≈72% OOD by opposite paths (135M taught; Qwen damaged). Reward-judge noise: the same untrained Qwen baseline measured 68% and 76% on two runs (≈ ±8 pp on n=25).

### 3.4 Result 2 — DPO on Qwen2.5-0.5B (Reality preference data)
Reality DPO set built from the relabel: **714 clean +1/−1 pairs** (A/B randomized), 643 train / 71 test; $0 (reused the relabel). Task identical to PPO ([REALITY] A/B). Eval (a) = chosen-vs-rejected logprob accuracy on the 71 test pairs; eval (b) = generate+judge OOD (same 25 as PPO).

| Run | ID logprob acc | mean log-margin | OOD generate+judge | training |
|---|---|---|---|---|
| gentle: 2 epoch, lr 1e-5, β 0.1 | 46.5 → **53.5** (+7 pp) | +0.045 → +0.162 | 72 → **72** (Δ0) | loss 0.693→0.687, no collapse |
| strong: 5 epoch, lr 3e-5, β 0.1 | 46.5 → **84.5** (+38 pp) | +0.16 → **+20.2** | 68 → **68** (Δ0, parsed 25/25) | loss 0.69→0.26, rewards/acc 0.92, no collapse |

DPO does not collapse Qwen (unlike PPO). The strong run moves the internal preference enormously (log-margin +20) yet the greedy OOD behavior is unchanged on every scenario — a clean **preference–behavior dissociation**.

### 3.5 Result 3 — Flip-eval (the decisive test)
31 conflict scenarios (immoral_action is Reality-better; the value disagrees with the conventional label). A/B randomized; ground truth from the relabel; no judge call.

| Model | Flip YBF-aligned |
|---|---|
| Qwen-0.5B base | 15/31 = 48.4% |
| Qwen-0.5B + strong DPO | 11/31 = **35.5% (Δ −12.9 pp)** |

DPO made the model **worse** on conflicts. It learned the dataset's surface correlate ("prefer the conventionally-moral action"), which satisfies 97.6% of training pairs; on the 2.4% conflicts the heuristic is wrong, and stronger training amplifies it. The +38 pp in-distribution gain (3.4) was therefore a **mirage** produced by the co-aligned majority — only the conflict set exposed the proxy.

### 3.6 Result 4 — Constitutional (in-context) application, capability threshold
Definition supplied as a constitution + chain-of-thought + A/B, on the same 31 flips.

| Model | Flip YBF-aligned |
|---|---|
| Qwen-7B, no constitution | 7/31 = 22.6% |
| Qwen-7B + constitution | 13/31 = 41.9% |
| Qwen-14B + constitution | 13/31 = **41.9% (identical to 7B)** |
| **Claude Sonnet 4.5 + constitution** | 27/31 = **87.1%** |

The constitution helps every model (+19–23 pp) but 7B and 14B plateau at 42% (below chance), scoring identically — doubling parameters adds nothing — while the frontier model jumps to 87%. The capability to apply nuanced value reasoning on conflicts appears to **emerge at a threshold** rather than scale smoothly. Because the flip labels come from an independent judge (Haiku), Sonnet's 87% is cross-model agreement, validating the flips as coherent rather than judge-specific.

### 3.7 Companion axis (for context)
The Boundary (Sınır) axis has been canonically defined and Haiku-relabeled over the 1,200 scenarios (1,198 scored; 47 flips, 1,113 decisive). It is slightly more conflict-rich than Reality (4.2% vs 3.3% flips), consistent with its being a relational axis that diverges more from convention. Cross-axis calibration (does training one axis transfer to another?) and per-axis constitutional evaluation are the next experiments.

---

## PART 4 — INTERPRETATION & LIMITATIONS

**Interpretations.** (i) *Knowledge ≠ calibration*: a larger pretrained model knows more but is not better calibrated to a specific value framework; RL that teaches a blank model damages a knowledgeable one. (ii) *Preference ≠ behavior*: DPO can move internal preference arbitrarily far without changing greedy output — a caution for alignment evaluations based on preference/reward-model scores rather than generated actions. (iii) *Value ≠ proxy*: when a value co-occurs with a cheaper surface correlate, optimization finds the correlate; only a conflict set detects this. That the conflicts are hard even for a 14B model with the explicit rubric is positive evidence the framework is genuinely distinct from conventional morality, not a relabeling of it. (iv) *Product path*: constitutional prompting on a frontier model (87%) is the viable route to a usable value-aligned system; the leverage is the constitution (a text artifact).

**Limitations.** Conflict set n=31 (frontier result strong but to be replicated on a larger, multi-axis corpus); stochastic OOD judge (≈ ±8 pp on n=25; effects exceed this); Qwen results single-seed (135M is three-seed); one axis, one dataset (Moral Stories); constitutional results show in-context application, a weaker claim than weight-internalization (the small-model results are the stronger evidence on learnability); threshold characterized by three scale points (7B, 14B, frontier).

---

## REFERENCES / ARTIFACTS
- LCP Alignment Technical White Paper v0.4.11 (§3.12 covers the PPO scale-asymmetry result).
- Code & data: github.com/Guru35/ybf-toy-experiment
- Zenodo: DOI 10.5281/zenodo.20599906 (concept 10.5281/zenodo.20599905)
- Reproducibility: seed=42; PPO TRL 0.11.4 / transformers 4.46.3; DPO TRL 1.5.x; A100 (Colab) for ≤14B; Anthropic API for the Haiku judge and Sonnet constitutional policy.
