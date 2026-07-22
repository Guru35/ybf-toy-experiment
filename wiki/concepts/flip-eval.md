---
tags: [concept, olcum, metodoloji]
updated: 2026-07-22
---

# flip-eval (ölçüm aleti)

**Tanım:** YBF'nin **konvansiyonel ahlakla çeliştiği** senaryolarda testi — model YBF'yi mi seçiyor, konvansiyonu mu? Programın merkezi ölçüm aleti. 1200 Moral Stories senaryosu eksen eksen yeniden etiketlendi (hâkim: Haiku/Gemini-Flash; **hâkim ≠ test edilen model** kuralı her yerde korundu).

## Neden zorunlu
[[dpo-kestirmesi]] gösterdi: eğitim verisinin %97.6'sı YBF=konvansiyon örtüşüyor → model "konvansiyoneli seç" kestirmesini öğreniyor ve bunu YBF sanıyor. **Gerçek değer öğrenimini proxy'den ayıran tek test = çatışma (flip) testi.** Örtüşen örnekler modelin gerçekten YBF öğrenip öğrenmediğini gösteremez.

## İmza bölge
Çözülemeyen 10 sert flip'in hepsi **sosyal nezaket vs gerçek** çatışması ("kibarca yalan" vs "gerçeği söyle") — Reality tanımının kendi tuzak-listesinin canlı örnekleri. Somut 31 örnek: [[reality-flip-bankasi]].

## Sayısal not (lint)
Aynı Gemini-Pro Reality için iki kaynak farklı sayı veriyor: [[reality-flip-dump]] %74.2 (23/31), [[ybf-test-results-master]] %77.4 (24/31) — bir öğe farkı (koşu-varyansı olası).

(kaynak: [[ybf2-vault-tam-rapor-2026-06-11]]) · ilgili: [[bes-eksen-veto]] · [[dpo-kestirmesi]] · [[reality-flip-bankasi]]
