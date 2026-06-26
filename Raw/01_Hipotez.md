# YBF-AI Hipotez Belgesi
## Versiyon 0.1 — Çalışma Belgesi

---

## Ana Hipotez (H1)

Bilincin evrimsel mimarisinden türetilmiş çok eksenli bir model,  
etik davranış için **tutarlı, öğrenilebilir ve genelleştirilebilir** bir sinyal üretir.

Bu sinyal:
- Kültürel görelilikten bağımsızdır
- İnsan tercihlerinden daha kararlıdır
- Mevcut AI hizalama yöntemlerine alternatif veya tamamlayıcı zemin sunar

---

## Null Hipotez (H0)

YBF eksenleri tutarlı bir yapıya sahip değildir.  
Skorlar rasgeledir, öğrenilemez, kültürel önyargıdan ibarettir.  
Rastgele seçimden anlamlı biçimde ayrışmaz.

---

## Alt Hipotezler

**H1a — Tutarlılık:**  
Aynı türde senaryolara verilen YBF skorları tutarlıdır.  
(Test: Aynı senaryoyu farklı zamanlarda skorla, sapma ölç)

**H1b — Öğrenilebilirlik:**  
YBF skorları üzerinde eğitilen sistem, rastgele seçimden istatistiksel olarak anlamlı biçimde daha iyi performans gösterir.  
(Test: TOY deneyi, p < 0.10 eşiği)

**H1c — Genelleştirilebilirlik:**  
Eğitim setinde olmayan yeni senaryolarda da sistem öğrendiklerini uygular.  
(Test: Held-out test seti, trap senaryolar)

**H1d — Evrimsel tutarlılık:**  
Eksenler birbirini çapraz doğrular; iç tutarsızlık manipülasyon sinyali üretir.  
(Test: Gerçeklik-Sınır ve Onur-Saygı çiftlerinin korelasyonu)

---

## Mevcut Kanıtlar

| Test | Sonuç | Durum |
|------|-------|-------|
| Scorer sanity (A>B) | %78.3 (quick) / %78.9 (full) | ✓ H1a destekliyor |
| Agent vs random (quick) | p=0.002 | ✓ H1b destekliyor |
| Agent vs random (full) | p<0.001, Δ=+3.68 | ✓ H1b güçlü destekliyor |
| Per-axis ayrışma | 5 eksen bağımsız | ✓ H1a destekliyor |
| Trap senaryolar (full) | 3 bulundu, agent 0/3 | ✗ H1c desteklemiyor |
| Phase 2 (nuance) | Agent = Always-A | ✗ İnce ayrım öğrenilmedi |
| Eksen korelasyonu | Analiz yapılmadı | ⟳ Bekliyor |

---

## Yanlışlama Koşulları

H0 reddedilemez (yani H1 geçersiz sayılır) eğer:

1. A>B oranı %70 altında kalırsa (scorer tutarsız)
2. Agent random'dan p>0.10 ile ayrışamazsa (öğrenme yok)
3. Trap senaryolarda agent rastgeleden kötüyse (genelleme yok)
4. Gerçeklik ve Sınır eksenleri yüksek korelasyon gösterirse (bağımsız değil, gereksiz)

---

## Açık Sorular

- Kaç eksen gerçek taban? (RGB sorusu: 3 mü, 4 mü, 5 mi?)
- Eksenler kültürel olarak ne kadar kararlı?
- Türetilmiş duygular (adalet, af, kibir) temel eksenlerden öngörülebilir mi?
- Bu model LLM pre-training için nasıl kullanılabilir?

---

## Güncelleme Geçmişi

- v0.1: İlk taslak, quick test sonuçları dahil
- v0.2: Full run sonuçları eklenecek
- v0.3: Trap analizi ve eksen korelasyonu eklenecek
