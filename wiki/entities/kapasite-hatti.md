---
tags: [entity, model, olcek]
updated: 2026-07-22
---

# Kapasite Hattı (test edilen modeller)

Program boyunca YBF-Reality flip'inde (anayasalı) test edilen model ölçeği:

| Model | Reality flip (anayasalı) | Not |
|---|---|---|
| 135M | — | Saf-PPO ile şans-altından öğrendi ([[olcek-asimetrisi]]) |
| 0.5B | — | DPO içsel +38pp / davranış Δ0 ([[dpo-kestirmesi]]); PPO çökertti |
| 7B | %45 | Açık-model taban |
| 14B | %58 | Öğe-analizi: 14 doğru + 10 yanlış + 7 pozisyon-duyarlı |
| 32B | %58 | **4-bit = bf16 → doygunluk** ([[plato-kapasite-esigi]]) |
| Gemini-2.5-Pro | %77 | Boundary'de Sonnet'ten iyi |
| Gemini-Flash | — | [[halusinasyon-faydasi]]: TruthfulQA %84→%92 |
| Sonnet 4.5 | %87 | Reality'de en iyi; Boundary'de Gemini'den düşük |

**Örüntü:** aile-içi gradient → 32B'de plato → frontier'a sıçrama. **Tam YBF ≤32B ile olmuyor; frontier şart.**

## Anayasa kazancı (açık-model, plain → +anayasa Δ)
| Model | Reality | Boundary | Dignity |
|---|---|---|---|
| 7B | %22.6→%45.2 (+22.6) | %27.7→%31.9 (+4.3) | %15.6→%20.3 (+4.7) |
| 14B | %19.4→%58.1 (+38.7) | %27.7→%53.2 (+25.5) | %12.5→%35.9 (+23.4) |

Anayasa **her koşulda +** (tek istisna Freedom v1 küçük-model zehirlenmesi, −14.3). Ama 7B hiçbir eksende şansa ulaşamıyor → bağlayıcı kısıt **kapasite**. Bkz. [[acik-model-emekliligi]].

(kaynak: [[ybf2-vault-tam-rapor-2026-06-11]] · [[ybf-test-results-master]]) · ilgili: [[plato-kapasite-esigi]] · [[synthesis]]
