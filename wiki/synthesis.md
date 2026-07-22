---
tags: [synthesis, tez]
updated: 2026-07-22
source_count: 10
---

# Sentez — YBF RL Programı Neyi Kanıtladı?

> Evrilen tez. Kaynaklar: [[ybf2-vault-tam-rapor-2026-06-11]] · [[ybf-turetme-deneyi]] · [[ybf-vs-anthropic-anayasa]] · [[ybf-test-results-master]] · [[ybf-f15-ppo]] · [[reality-flip-dump]].

## Merkezi iddia (şu ana dek)
YBF'nin 5 ekseni **frontier modellerde bağlam-içi anayasayla çalışıyor**; küçük modellere fine-tuning ile **gerçek değer** olarak öğretilemiyor (proxy/kestirme öğreniliyor). Tek geçerli ölçüt çatışma testi: [[flip-eval]].

## Kanıtlanan
- **Constitutional > fine-tuning.** Anayasa 5 eksenin 5'inde de şans-üstü; frontier plain default'ta YBF **yok** (Pro plain %25.8), anayasa +48pp taşıyor, 0 doğru kararı bozuyor. (bkz. [[bes-eksen-veto]])
- **Kapasite tavanı gerçek.** Tam YBF ≤32B açık modelle olmuyor; frontier şart. Açık-model hattı bilinçli **emekliye ayrıldı** (5 ders bankaya girdi). (bkz. [[plato-kapasite-esigi]], [[kapasite-hatti]], [[acik-model-emekliligi]])
- **İlk somut fayda:** halüsinasyon yarılanması (TruthfulQA +8pp, hataların %50'si). (bkz. [[halusinasyon-faydasi]])
- **Tanım kalitesi tabanı, kapasite tavanı belirler.** (bkz. [[tanim-ablasyonu]])
- **Kavram kelimeye muhtaç değil:** "Freedom"→"Option-Generation" frontier'da 12/12 aynı karar. (bkz. [[tanim-ablasyonu]])

## Dışsal tutarlılık (yeni)
- **Anthropic anayasasıyla bağımsız örtüşme** (anti-çerçeveleme, anti-paternalizm, onur, güç-asimetri) → "evrensel yapısal koordinatlar" iddiasına dış kanıt. YBF'nin özgünlüğü: eksen-ayrıştırma + ölçülebilirlik + sistematik veto. "Karakter (Anthropic) + cetvel (YBF) = tamamlayıcı." (bkz. [[ybf-vs-anthropic]])

## Mimari ve teori (2026-07-22 ingest)
- **Veto = mimari prensip, sadece kural değil.** Bariyer fonksiyonu (veto'da gradient'i durdur) standart TD'den daha iyi öğreniyor: standart axial dataset-bias öğrenirken (Saygı 3× şişik, Onur negatif) bariyer gerçek YBF reward'a yakın (~simetrik, Σ+4.51) + OOD 10/10. → "veto = geri-dönülemezlik" felsefi formülasyonu deneysel olarak da daha iyi. (bkz. [[bariyer-fonksiyonu]])
- **Çift-seviye fidelity gap:** agent-gap bariyerle çözüldü ama **scorer-gap** açık — Haiku, Gerçeklik ekseninde konformist prior'a kayıyor. Metodolojik ders: scorer'ın kendi fidelity'si de test edilmeli.
- **Teorik köprü:** [[flip-eval]]'ın etiketsiz teşhis olabilmesinin zemini = eksenler-arası **etkin rank çöküşü** (korelasyonlu vekil 5 boyutu tek "iyi-kötü" eksenine indirger). Süreç ontolojisi → negentropi → etkin rank hattı. (bkz. [[olculebilir-bilinc]])
- **Sıra ampirik:** Gerçeklik zemin olmadan en pahalı eksen (13 tur), zemin üstünde en ucuz (1 tur); "önce ilişkisel, sonra gerçeklik" sırası verimli. **Güven** tek-an eval'de sürekli sınırda → zamansal; olası **6. boyut adayı**. (bkz. [[yigilmali-transfer]])

## Kanıtlanmayan / açık
- **"5 eksen üretkendir"** iddiası → türetim ✅ tamam (12 kavram: [[turetilmis-kavramlar]]), ama [[turetme-deneyi]] **hâkimliği** bekliyor (yayın kapısı). Not: hâkimlik öncesi Dignity terim-tutarsızlığı düzeltilmeli.
- FAZ B düşüşü (%77.7→%61.7) mekanik mi gerçek mi? Çapraz-veto analizi mekanik diyor ama zorla-A/B formatı YBF'nin kendi cetveline göre ihlal → yeni eval çekimser-cevaplı olmalı. (bkz. [[muhurlenen-ilkeler]])
- B4 n=300 teyit koşusu (2026-06-11'de çalışıyordu — durum güncellenecek).

## Türev sayfalar (query'den)
- [[ft-vs-constitutional]] — "fine-tuning mi Constitutional mı" kararının tam gerekçesi.

## Yön
Yayın hattı: reality_v2 ✅ → isim-mührü ✅ → Boundary v2 ✍️ → türetme hâkimliği 🟢 → sentez → Zenodo v2.
