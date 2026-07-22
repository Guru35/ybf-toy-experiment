---
tags: [concept, bulgu, F-16]
updated: 2026-07-22
---

# DPO Kestirmesi — "düşünce ≠ eylem" (F-16)

**Bulgu:** DPO, 0.5B'nin **içsel tercihini +38pp** oynattı ama **davranış Δ0**. Neden: eğitim verisinin %97.6'sı YBF=konvansiyon örtüşüyor → model "konvansiyoneli seç" **kestirmesini** öğrendi. Çatışmalarda (flip) eğitim güçlendikçe **kötüleşti (−12.9pp)**.

## Çıkarım
Küçük-model fine-tuning yolu **kapalı**. İçsel metrik iyileşmesi davranışı garanti etmez; ölçüm çatışmadan yapılmalı → [[flip-eval]]'in zorunluluğu. Bu bulgu [[olcek-asimetrisi]] ile birlikte "fine-tuning değil, anayasa" kararını verdirdi.

(kaynak: [[ybf2-vault-tam-rapor-2026-06-11]] · [[ybf-f15-ppo]] · [[ybf-test-results-master]]) · ilgili: [[flip-eval]] · [[olcek-asimetrisi]] · [[synthesis]]
