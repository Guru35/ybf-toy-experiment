---
tags: [concept, sentez, karar, query-turevi]
updated: 2026-07-22
origin: query
---

# Fine-tuning mi Constitutional mı? — Yöntem Kararı

> Bu sayfa bir **query'den** doğdu (2026-07-22): "YBF neden fine-tuning'i bırakıp Constitutional'a geçti?" Wiki'deki 5 sayfanın sentezi, geri-dosyalandı.

## Kısa cevap
**Fine-tuning yolu (küçük model) kapandı; Constitutional + frontier açık kaldı.** Sebep tek cümlede: *değer öğretmek değil, kapasiteli modelde var-olanı aktive etmek* — "bilgi ≠ kalibrasyon".

## Fine-tuning neden kapandı (iki bağımsız kanıt)
| Yol | Bulgu | Sonuç |
|---|---|---|
| **PPO** ([[olcek-asimetrisi]], F-15) | Bilmeyene öğretir (135M %24→%72) ama **bileni bozar** (0.5B çöker) — ölçek asimetrisi | Yüksek-prior modelde marjinal değer negatif |
| **DPO** ([[dpo-kestirmesi]], F-16) | Büyüğü korur ama **kestirme** öğrenir (%97.6 veri örtüşük → "konvansiyoneli seç"); flip'te −12.9pp | İçsel +38pp serap; davranış Δ0 |

→ Ortak ders: küçük-model fine-tuning YBF için **kapalı yol**. Ölçüt: yalnız [[flip-eval]] gerçeği gösterir.

## Constitutional neden açık kaldı
- Frontier + tek-eksen anayasa **5 eksende de** çalışıyor (Reality Sonnet %87.1). ([[bes-eksen-veto]])
- Yetenek kapasiteyle **gradient** halinde ölçekleniyor — ama ≤32B'de **plato** ([[plato-kapasite-esigi]]); tam YBF için **frontier şart**.
- Bu yüzden açık-model hattı bilinçli **emekliye ayrıldı** ([[acik-model-emekliligi]]).

## Mekanizma (neden böyle?)
Frontier model Reality'yi pretraining'de zaten taşıyor (0.5B bile %68 zero-shot). YBF "dışarıdan yüklenecek bilgi" değil — **var olanı koruma/keskinleştirme** problemi. Fine-tuning kaba ödülle bu yapıyı bozarken, in-context anayasa onu **aktive** ediyor. Küçük modelde ise aktive edilecek yeterli yapı yok → tavan kapasitede.

(kaynaklar: [[olcek-asimetrisi]] · [[dpo-kestirmesi]] · [[plato-kapasite-esigi]] · [[bes-eksen-veto]] · [[acik-model-emekliligi]]) · üst-tez: [[synthesis]]
