---
tags: [concept, bulgu, olcek]
updated: 2026-07-22
---

# Plato / Kapasite Eşiği

**Bulgu (Reality flip, anayasalı):** 7B %45 → 14B %58 → **32B %58** → Gemini %77 → Sonnet %87.
- **Nüans (master'da 2× revize):** 7B↔14B **gradient** (kademeli artış); 14B↔32B **plato** (doygunluk); frontier'a **sıçrama**. Yani "plato" 14B-32B arasında, 7B-14B'de değil.
- 32B'de **4-bit ve tam-kalite bf16 birebir aynı** → doygunluk kanıtlandı (nicemleme değil, **kapasite sınıfı** sınırı).
- Öğe-düzeyi (14B vs 32B): ortak kararlı çekirdek **11 öğe (%75)** — aynı seviye ama birebir aynı sorular değil. **Aile-dirençli 7 flip** hiçbir koşulda çözülmedi (bkz. [[acik-model-emekliligi]]).
- ⚠️ Repro: greedy açık-model eval'i ortamlar arası ±~10pp oynuyor.

## Ürün sonucu
**Tam YBF ≤32B açık modelle olmuyor; frontier şart.** (Açık-model hattı burada kapandı.)

(kaynak: [[ybf2-vault-tam-rapor-2026-06-11]] · [[ybf-test-results-master]]) · ilgili: [[kapasite-hatti]] · [[olcek-asimetrisi]] · [[acik-model-emekliligi]] · [[synthesis]]
