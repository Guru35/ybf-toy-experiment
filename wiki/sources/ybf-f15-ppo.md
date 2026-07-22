---
tags: [source, teknik, PPO, DPO]
source: ../ybf_toy/AIEgitim-F15-pure-reward-reality-ppo.md
ingested: 2026-07-22
updated: 2026-07-22
---

# Kaynak: F-15 Saf-Ödül PPO Teknik Raporu (2026-06-10)

**Ne:** [[olcek-asimetrisi]] (F-15) ve [[dpo-kestirmesi]] (F-16) bulgularının teknik ayrıntısı — çöküş→teşhis→fix yolculuğu + Constitutional AI ilk kanıtı.

## Teknik çekirdek (concept'lere yansımayan detay)
- **PPO stabilizasyon reçetesi:** naif config KL→−2000 çöküyor. Fix: `lr 4e-6` + rollout `temperature 0.7` + **collapse-guard** (OOD best'ten ≥20pp düşerse dur) + **best-checkpoint** (round 1-2'de yakala, 20 round koşturma). SmolLM-135M: OOD %24→%72 (+48pp), 3 seed (72/72/68, ort ~%71).
- **Qwen-0.5B çöküşü:** baseline %68 zaten şans-üstü (Reality pretraining'de KODLU) → PPO her lr'de bozdu/çökertti. Hipotez: reward-model misspecification (Haiku kalibrasyonu ≠ Qwen'in mevcut anlayışı).
- **DPO:** 714 temiz ±1 çifti, %97.6 konvansiyon-örtüşük → kestirme. Güçlü DPO ID +38pp / OOD Δ0 / flip −12.9pp.

## Constitutional AI ilk kanıtı (burada doğdu)
7B plain %22.6 → +anayasa %41.9 → Sonnet %87.1. "YBF-spesifik Reality **uygulanabilir** ama küçük-model FT ile DEĞİL, frontier + Constitutional ile." → [[bes-eksen-veto]] · [[synthesis]]
