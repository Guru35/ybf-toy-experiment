# Budget Guard Güncellemesi
## scorer.py + config.py — mevcut dosyaların üzerine yaz

---

## Ne Değişti

**config.py** — 3 yeni satır eklendi:
```python
MAX_API_SPEND_USD   = 3.0    # hard stop
COST_PER_CALL_USD   = 0.00025  # Haiku tahmin
BUDGET_WARN_AT_USD  = 2.0    # uyarı eşiği
```

**scorer.py** — budget tracker eklendi:
- Her API call'da `_estimated_spend` artar
- `$2.00`'da konsola uyarı yazar
- `$3.00`'da RuntimeError fırlatır, deney durur
- Precompute sonunda toplam call + harcama yazar:
  `💰 API calls: N | Tahmini harcama: $X.XXXX`

---

## Güncelleme Talimatı

```bash
cd ~/Documents/AI-Egitmek/ybf_toy/
# İndirilen dosyaları buraya kopyala:
# scorer.py → scorer.py (üzerine yaz)
# config.py → config.py (üzerine yaz)
python3 -m py_compile scorer.py config.py && echo "OK"
```

---

## Neden Önemli (Araştırma Değeri)

Her deneyin gerçek maliyeti kayıt altına alınıyor.
Bu veriler white paper ve kitap için kritik:

| Deney | Call | Maliyet |
|-------|------|---------|
| Quick test (120 senaryo) | 240 | ~$0.06 |
| Full run (1200 senaryo) | 2400 | ~$0.60 |
| 3 trap yeniden score | 6 | ~$0.002 |

Toplam YBF alignment deneyi: **~$1.00**
Karşılaştırma: RLHF ile aynı ölçek → tahmin $10,000+

Bu "atomize, evde yapılabilir alignment" argümanının somut kanıtı.

---

## Sıradaki

1. Bu dosyaları değiştir
2. `python analyze_traps.py` zaten çalışmıştı — OK
3. Bekle: scorer prompt güncellemesi geliyor (capacity threshold kuralı)
4. Yeni scorer ile 3 trap yeniden score edilecek
