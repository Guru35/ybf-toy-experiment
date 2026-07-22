---
tags: [concept, bulgu, F-15]
updated: 2026-07-22
---

# Ölçek Asimetrisi — "RL bilmeyene öğretir, bileni bozar" (F-15)

**Bulgu:** Saf-ödül PPO (model tanımı hiç görmez, sadece gizli ±1 ödül):
- **135M** model şans-altından öğrendi: OOD %24 → %72 (3 seed replike).
- Aynı prosedür, değeri zaten kodlamış **0.5B**'yi her öğrenme oranında **çökertti**.

## Çıkarım
**"Bilgi ≠ kalibrasyon."** Küçük/boş model ödül sinyaliyle şekillenir; değeri zaten taşıyan model aynı kaba sinyalle bozulur. Ölçek büyüdükçe fine-tuning'in yönü tersine döner.

**Teknik reçete** (PPO çöküşünü önleme): `lr 4e-6` + rollout `temp 0.7` + collapse-guard + best-checkpoint. Detay: [[ybf-f15-ppo]].

(kaynak: [[ybf2-vault-tam-rapor-2026-06-11]] · [[ybf-f15-ppo]]) · ilgili: [[dpo-kestirmesi]] · [[plato-kapasite-esigi]] · [[kapasite-hatti]]
