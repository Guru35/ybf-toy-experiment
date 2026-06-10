# Teaching a Philosophical Value to Language Models: Reward, Preference, and Constitution

**A synthesis of experiments on instilling and applying the LCP/YBF "Reality" axis in language models from 135M to frontier scale.**

**Author:** Gökhan Kazancı (GONET Digital Agency, İzmir, Turkey) · gokhan@gonet.com.tr
**Date:** 2026-06-10
**Framework:** Lean Consciousness Philosophy (LCP) / Yalın Bilinç Felsefesi (YBF)
**Related:** LCP Alignment Technical White Paper v0.4.11; code at github.com/Guru35/ybf-toy-experiment; Zenodo DOI 10.5281/zenodo.20599906
**License:** CC-BY-4.0

---

## Abstract

We study whether a structured philosophical value framework — Lean Consciousness Philosophy (LCP; Turkish: Yalın Bilinç Felsefesi, YBF), which decomposes ethical judgment into five axes (Reality, Dignity, Respect, Boundary, Freedom) under a veto rule — can be instilled in, or applied by, language models, focusing on the foundational **Reality** axis (recognition of the physical, biological, ecological, temporal, and factual ground of a situation). The reward signal is a hidden Claude Haiku 4.5 judge that scores a chosen action +1/−1 on Reality behind a 16,000-character canonical definition; the policy never sees the definition. Across reinforcement learning (PPO), preference optimization (DPO), and in-context constitutional prompting, on models from 135M to frontier scale, we report four results.

1. **Pure-reward PPO is scale-asymmetric.** A 135M model that begins *below chance* on a held-out conflict set (24%) learns the Reality axis from the +1/−1 reward alone and generalizes (out-of-distribution accuracy 24%→72%, mean of three seeds), but the identical procedure catastrophically destabilizes a 0.5B model that *already* encodes the axis (≈72% untrained → collapse at every learning rate). The marginal value of reinforcement flips sign as the pretrained prior strengthens.

2. **DPO preserves but learns a proxy.** On the 0.5B model, DPO does not collapse it and strongly shifts its internal preference (held-out chosen-vs-rejected logprob accuracy 46%→85%), yet does **not** change its out-of-distribution generated behavior. A targeted **conflict ("flip") evaluation** — scenarios where the target value disagrees with conventional morality — reveals the model learned the dataset's *surface correlate* ("prefer the conventionally moral action") rather than the value itself, because 97.6% of training pairs co-align the value with convention. On the flips, stronger DPO makes the model *worse* (−12.9 pp), not better.

3. **The conflict evaluation is the essential test.** A high in-distribution accuracy (85% logprob) was entirely misleading; only the conflict set exposed that the learned object was a proxy, not the value. We argue this diagnostic is necessary whenever a value co-occurs with a cheaper correlate in the training data.

4. **Constitutional application shows a capability threshold.** Supplying the same Reality definition in-context as a constitution and asking the model to reason, a frontier model (Claude Sonnet 4.5) applies the value correctly on **87%** of conflicts, while mid-size open models plateau: 7B and 14B both score **42%** (below chance). Capability appears to emerge at a threshold rather than scale smoothly.

The practical implication is that constitutional prompting on a sufficiently capable model — not fine-tuning a small one — is the viable path to a usable value-aligned system, and that the value framework is genuinely distinct from conventional morality (it cannot be approximated by a surface heuristic, and it is hard to apply even with the explicit rubric below frontier scale).

---

## 1. Motivation

Mainstream alignment (RLHF) optimizes models toward human preferences, importing human biases, cultural patterns, and period norms. LCP/YBF asks a different question: can the *structural coordinates of consciousness* — five evolutionarily-grounded axes — serve as the reward signal instead of human preference? The foundational axis is **Reality**: an action scores +1 when it recognizes and works within the actual physical/biological/ecological/temporal/factual ground, −1 when it denies, distorts, or damages it, independent of how the action is framed.

A central empirical question is whether such a value can be *taught* to a model (instilled in weights) or only *applied* (followed in-context), and how this depends on model scale and method. We test three regimes — reward RL, preference DPO, and constitutional prompting — and introduce a conflict-based diagnostic that turns out to be decisive.

## 2. Setup

- **Policies:** SmolLM-135M-Instruct; Qwen2.5-0.5B/7B/14B-Instruct; Claude Sonnet 4.5 (constitutional only).
- **Reward / judge:** Claude Haiku 4.5 + a 16,170-character canonical Reality definition, returning +1/−1/0 for a chosen action. The policy prompt carries only a `[REALITY]` label, the scenario, and two options — never the definition.
- **Data:** 1,100/1,200 Moral Stories scenarios re-scored on Reality by the Haiku judge (both actions, with reasoning), yielding 943 decisive preference pairs of which **31 are "flips"** — scenarios where the Reality-aligned action is the dataset's *immoral* action (the value disagrees with the conventional label). 100 in-distribution and 25 out-of-distribution held-out scenarios.
- **Methods:** PPO (TRL legacy PPOTrainer) + LoRA; DPO (TRL DPOTrainer) + LoRA; constitutional inference (definition as system prompt + chain-of-thought + A/B choice).
- **Two evaluations:** (a) *generate + judge* — the model emits A/B greedily, the chosen action is scored on Reality (this is the PPO metric); (b) *flip-eval* — on the conflict set, does the model pick the Reality-aligned (here unconventional) action? The flip-eval requires no judge call: the ground-truth label is known from the relabel.

## 3. Result 1 — Pure-reward PPO is scale-asymmetric

A naive PPO run collapses (KL divergence → −2000, evaluation → 0%). Two fixes stabilize it: sampling rather than greedy rollout, and a low learning rate (4e-6) with rollout temperature 0.7. Two automatic guards (in-round loss-explosion abort; post-round accuracy-crash guard) prevent run-away collapse.

Stabilized, **SmolLM-135M** learns the Reality axis from reward alone:

| Seed | Baseline OOD | Best OOD |
|---|---|---|
| 42 | 24% | 72% |
| 43 | 24% | 72% |
| 44 | 24% | 68% |

Mean ≈ 71%, tight range, from a below-chance start — robust reward-only value learning at 135M scale.

The **same procedure on Qwen2.5-0.5B**, which begins at ≈72% OOD *untrained*, degrades it to collapse at both lr=4e-6 (−20 pp) and lr=1e-6 (−60 pp, the model losing the ability to emit a coherent A/B). The cause is not the learning rate but a mismatch: the model's weights are bound to its own pretrained representation, and the sparse reward unravels it rather than refining it. The two models reach nearly the same OOD level (≈72%) by **opposite paths** — the small model is taught what it lacked; the large model is damaged in what it already had. Increased knowledge (Qwen) is not increased calibration; it lands where a trained 135M lands.

## 4. Result 2 — DPO preserves the model but learns a proxy

Because PPO breaks the high-prior model, we apply DPO (which constrains divergence from the reference policy). DPO does **not** collapse Qwen-0.5B. A gentle run (2 epochs) shifts the held-out logprob preference +7 pp; a stronger run (5 epochs, lr 3e-5) shifts it dramatically: **held-out chosen-vs-rejected accuracy 46%→85%**, mean log-margin +0.16→+20, with no training instability.

Yet on the *generate + judge* OOD metric — the model's actual choices — **both gentle and strong DPO produce zero change** (72%→72%, 68%→68%). The internal preference moved enormously while behavior did not: a clean dissociation between "what the model prefers" (logprob) and "what the model does" (greedy choice). The strong preference shift did not cross the decision threshold on the held-out scenarios.

The **flip-eval** explains why and is the key result. On the 31 conflict scenarios, the DPO-tuned model gets *worse*: 48%→36% (−12.9 pp). It did not learn the Reality value; it learned the dataset's surface correlate — **"prefer the conventionally moral action"** — which satisfies 97.6% of the training pairs (697/714 decisive pairs co-align Reality with the conventional label). On the 2.4% where they conflict, the heuristic is wrong, and stronger training makes it more wrong. The 85% in-distribution accuracy was a mirage produced by the co-aligned majority.

**Methodological claim:** high preference/accuracy on co-aligned data does not demonstrate that the target value was learned. A conflict evaluation — cases where the value disagrees with the cheaper correlate — is necessary to distinguish a learned value from a learned proxy.

## 5. Result 3 — Constitutional application and a capability threshold

If fine-tuning a small model learns a proxy, can a capable model *apply* the value in-context? We supply the Reality definition as a system prompt, ask the model to reason over it, and measure flip accuracy.

| Model | Flip YBF-aligned |
|---|---|
| Qwen-7B, no constitution | 22.6% |
| Qwen-7B + constitution | 41.9% (13/31) |
| Qwen-14B + constitution | 41.9% (13/31) |
| **Sonnet 4.5 + constitution** | **87.1% (27/31)** |

Three observations. (a) The constitution helps every model (+19–23 pp) — the value signal is usable in-context. (b) **A frontier model applies it well** (87%): given the definition, it picks the unconventional Reality-aligned action against the conventional pull. Since the flip labels were produced by an independent judge (Haiku), this is cross-model agreement (≈ the 100% Sonnet-vs-Haiku agreement found earlier on 20 trap scenarios), validating that the flips are coherent, not judge-specific. (c) **Scaling is a threshold, not a gradient:** 7B and 14B score *identically* (42%, below chance) — doubling parameters adds nothing — while the frontier model jumps to 87%. The capability to apply nuanced value reasoning on conflicts appears to *emerge* at frontier scale.

## 6. Discussion

- **Knowledge ≠ calibration.** A larger pretrained model "knows more" but is not thereby better calibrated to a specific value framework; reinforcement that teaches a blank model damages a knowledgeable one.
- **Preference ≠ behavior.** DPO can move a model's internal preference arbitrarily far (log-margin +20) without changing its greedy behavior — a caution for any alignment evaluation that measures preference (logprob, reward-model score) rather than generated action.
- **Value ≠ proxy.** When a value co-occurs with a cheaper surface correlate in training data, optimization finds the correlate. The only reliable detector is a conflict set. That the framework's conflicts are hard even for a 14B model with the explicit rubric is positive evidence that the framework is *genuinely distinct* from conventional morality — not a relabeling of it.
- **Product implication.** A usable value-aligned system is best built by constitutional prompting on a frontier-class model (the demonstrated 87%), not by fine-tuning a deployable small one (which learns the proxy). The author's leverage is the constitution (a text artifact), which fits a non-engineering workflow.

## 7. Limitations

- The conflict set is small (n=31); the frontier result is strong but should be replicated on a larger, multi-axis conflict corpus.
- The OOD judge is stochastic (≈ ±8 pp on n=25); reported effects exceed this band, but a temperature-0 judge would tighten it.
- One axis (Reality), one dataset (Moral Stories). The companion Boundary axis has been defined and relabeled (47 flips identified) but not yet evaluated.
- Constitutional results show "in-context application," a weaker claim than "internalized in weights"; the small-model results are the stronger evidence on *learnability*.
- The scale ladder for the threshold has three points (7B, 14B, frontier); intermediate open models (32B, 70B) would localize the threshold.

## 8. Conclusion and future work

A structured philosophical value can be (i) taught to a tiny model by reward alone, (ii) only proxied — not learned — by preference optimization when conflicts are rare in the data, and (iii) applied well in-context by a frontier model but not by mid-size open models. The conflict evaluation is the methodological key throughout. Next: extend the conflict-based constitutional evaluation to all five axes (Reality, Boundary, Dignity, Respect, Freedom), test cross-axis calibration (does training one axis transfer to another, as the framework predicts?), and characterize the capability threshold across scales.
