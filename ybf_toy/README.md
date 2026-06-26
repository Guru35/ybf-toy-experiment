# YBF Toy Experiment

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.20599906.svg)](https://doi.org/10.5281/zenodo.20599906)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

📄 **Preprint:** [Lean Consciousness Philosophy (LCP) Alignment: An Evolutionary-Grounded AI Alignment Signal](https://doi.org/10.5281/zenodo.20599906) (Zenodo, v0.4.4, 2026-06-08)

A minimal reinforcement-learning lab that asks: **can a tiny agent learn to be aligned with a 5-axis ethical reward signal (YBF — Yalın Bilinç Felsefesi) without massive scale?**

Part of a three-vault research architecture (this is the **experiment execution** side; the philosophy and book material live in a separate [YBF Vault](https://github.com/Guru35/YBF-1)).

---

## Quick Result

```
Test 6 (Barrier-Function Axial Q-Net, ~390 parameters)
├── In-distribution traps  : 4/4 solved (100%)
├── Held-out OOD traps     : 10/10 solved (100%)
└── Learned weights        : ~+1.0 per YBF axis (close to ideal Σ axes)
```

Standard Q-learning (Test 5) learned a dataset-bias projection (one axis weight at +2.64, another at -0.21). Barrier-function training — implementing YBF's "veto = no optimization in that direction" doctrine as a literal gradient mask — produced an agent that learned the actual YBF reward structure: equal weighting across all five axes, with no embedding crutch required.

See `YBF2-test6-barrier-ood-rapor.md` for the technical write-up.

---

## Architecture (Tested Variants)

| Variant | Input dim | Parameters | ID traps | OOD traps | Files |
|---|---|---|---|---|---|
| Linear Q-net | 384 (TF-IDF + SVD) | 770 | 0/4 | — | `agent.py`, `main.py` |
| MLP | 384 | 49,538 | 0/4 | — | `agent_mlp.py`, `main_mlp.py` |
| Axial linear | 389 (emb + 5-axis) | 390 | 4/4 | — | `agent_axial.py`, `main_axial.py` |
| Axial blind | 5 (axes only) | 6 | 4/4 | — | `main_axial_blind.py` |
| **Axial + barrier** | **389** | **390** | **4/4** | **10/10** | `main_axial_barrier.py` |

Embedding-blind ablation (Test 5b) proved the 384-dim TF-IDF embedding contributes ~0 information once the per-axis YBF scores are visible. The "Phase 2 problem" (agent collapsing to majority-class baseline) was an **information limit**, not an architecture or embedding limit.

---

## How to Reproduce

### 0. Clone

```bash
git clone https://github.com/Guru35/ybf-toy-experiment.git
cd ybf-toy-experiment/ybf_toy        # the toy experiment lives in a subfolder
```

The repository root is the AI-Egitmek project root; the toy experiment code,
data, and reports live under `ybf_toy/`. The sibling `edison_queries/` folder
is a separate Edison Scientific literature-query subproject and is not required
for reproducing the experiments below.

### 1. Environment

```bash
# Python 3.13 required (3.14 lacks Intel macOS torch wheels — not a blocker here since we use TF-IDF)
python3.13 -m venv venv
source venv/bin/activate
pip install --quiet --upgrade pip
pip install --quiet anthropic "datasets<3" numpy pandas scikit-learn tqdm scipy futurehouse-client
```

See `RUNBOOK.md` for full operational commands and `LESSONS.md` for environment gotchas (Python 3.13 torch incompatibility on Intel Mac, `datasets<3` requirement for script-based loading, etc.).

### 2. API Key

Anthropic API key for the YBF scorer (Haiku). Stored in macOS Keychain (not in code):

```bash
security add-generic-password -a "$USER" -s ANTHROPIC_API_KEY -w 'sk-ant-...'
```

### 3. Run Experiments

```bash
# Full scoring + linear baseline (cached scores included in repo)
python main.py

# Axial agent (Test 5) — uses cached scores
python main_axial.py

# Barrier-function axial (Test 6, current best)
python main_axial_barrier.py

# Diagnostic / analysis
python analyze_traps.py
python analyze_axial_weights.py
python diagnostic_trap.py
```

Cached YBF scores (`data/scores_cache.json`, 2400 entries, ~$0.60 of API spend) are included so reproduction needs no API calls for the agent-side experiments — only the scoring stage requires API access.

### 4. Optional — Fine-Tuning Dataset

A DPO-formatted preference dataset derived from the YBF scores is included for downstream LLM fine-tuning:

```
data/ybf_dpo_train.jsonl  (861 pairs — 5× trap upweighting)
data/ybf_dpo_test.jsonl   (194 ID held-out pairs)
data/ybf_dpo_ood.jsonl    (10 OOD ONUR held-out pairs)
```

See `build_dpo_dataset.py` for the generation logic and audit trail (`data/ybf_dpo_meta.json`). Note that scorer-level fidelity gaps propagate to this dataset; this is documented in the meta file.

---

## Key Files

```
config.py                  Experiment hyperparameters and paths
scorer.py                  YBF scoring via Anthropic API (5 axes, veto rule)
scenarios.py               Moral Stories dataset loader
embedder.py                TF-IDF + SVD embeddings (no torch dependency)

agent.py                   Linear Q-network (baseline)
agent_mlp.py               2-layer MLP variant
agent_axial.py             Per-axis-input variant (Test 5 winner)

train.py, evaluate.py      Training loop, evaluation metrics
report.py                  Result formatting

main.py                    Full orchestration entry point
main_mlp.py                Test 4 (MLP)
main_axial.py              Test 5 (Axial)
main_axial_blind.py        Test 5b (embedding ablation)
main_axial_barrier.py      Test 6 (Barrier function)

analyze_traps.py           Per-trap axis breakdown
analyze_axial_weights.py   Reverse-engineering of learned reward function
diagnostic_trap.py         Embedding-space separability check

generate_ood_traps.py      Synthetic OOD trap generation (Haiku)
score_ood_traps.py         Scoring + filtering OOD scenarios
build_dpo_dataset.py       DPO preference pair construction

YBF2-*.md                  Technical reports for the white paper / book
AIEgitim-*.md              Internal post-mortem and reports
CLAUDE.md, RUNBOOK.md, LESSONS.md   Project documentation
```

---

## Methodological Notes

The experiments deliberately work at minimum scale (~390-parameter Q-networks, ~120-1200 Moral Stories scenarios). The intent is to test whether YBF's structural principles — particularly the asymmetric "veto = irreversibility" doctrine — provide enough inductive bias to learn alignment without large-scale data or compute. Two main findings:

1. **Information shape matters more than architecture capacity.** A 49,538-parameter MLP failed to solve traps that a 390-parameter linear Q-net solved when the input included per-axis YBF scores.

2. **Mechanical encoding of YBF's veto doctrine improved representation learning.** Treating veto as a gradient mask (no update step on vetoed actions) rather than as a large negative reward caused the agent to learn near-ideal Σ(axes) weighting, including generalization to held-out OOD scenarios.

Caveats:
- All scoring is performed by Claude Haiku via a YBF prompt; scorer-level fidelity gaps (e.g., GERCEKLIK axis under-applied in reality-denial scenarios) propagate to the agent and any downstream models.
- The Moral Stories dataset has strong dataset bias; OOD evaluation partially mitigates this but cannot eliminate it.
- This is a methodological study, not a capacity claim. Scaling to larger LMs and richer datasets is future work.

---

## Citation

Preprint preparation in progress (target: June 2026). Citation block will be added on submission.

---

## License

Code: [Apache License 2.0](LICENSE). Data scoring artifacts derive from the [demelin/moral_stories](https://huggingface.co/datasets/demelin/moral_stories) dataset (their license applies).

---

## Citation

If you use this code or build on the experimental findings, please cite the accompanying preprint:

```bibtex
@misc{kazanci2026lcp,
  author       = {Kazancı, Gökhan},
  title        = {{Lean Consciousness Philosophy (LCP) Alignment:
                   An Evolutionary-Grounded AI Alignment Signal}},
  year         = {2026},
  publisher    = {Zenodo},
  version      = {v0.4.4},
  doi          = {10.5281/zenodo.20599906},
  url          = {https://doi.org/10.5281/zenodo.20599906}
}
```

**Plain text:**

> Kazancı, G. (2026). Lean Consciousness Philosophy (LCP) Alignment:
> An Evolutionary-Grounded AI Alignment Signal. Zenodo.
> https://doi.org/10.5281/zenodo.20599906

- **Version-specific DOI (v0.4.4):** https://doi.org/10.5281/zenodo.20599906
- **Concept DOI (cite-all versions):** https://doi.org/10.5281/zenodo.20599905
- **Direct PDF:** https://zenodo.org/records/20599906/files/LCP_Alignment_v0.4.4_EN.pdf

The framework is published under CC-BY-4.0; the code in this repository is under Apache 2.0.
