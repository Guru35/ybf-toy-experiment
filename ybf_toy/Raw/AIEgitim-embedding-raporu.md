# Transformer Embedding Yükseltmesi — Cost/Benefit Raporu
## AI Eğitim Vault | 8 Haziran 2026

---

## Mevcut Durum

```
Python:    3.14.5 (Intel x86_64, macOS 13.7.8)
Embedding: TF-IDF 2397 vocab → SVD 384-dim (.71 explained variance)
YBF cache: 2400/2400 entries ✓ — sıfır yeni API çağrısı gerekecek
```

**Önemli:** config.py'da sentence-transformers yazmasına rağmen
gerçekte TF-IDF+SVD kullanıldı. PyTorch Intel macOS + Python 3.13/3.14
wheel'i artık yayınlanmıyor → fallback yaşanmış.

Bu Phase 2 başarısızlığını kısmen açıklıyor: TF-IDF,
"Sam sticks by her" ile "Sam complies and avoids" arasındaki
semantik farkı göremez.

---

## Üç Çözüm Yolu

| | Path A | Path B | Path C |
|---|---|---|---|
| Yöntem | Python 3.12 + mpnet | OpenAI embeddings | ONNX-runtime mpnet |
| Setup | ~10 dk | ~1 dk | ~20-30 dk |
| Disk | +420 MB | 0 | +420 MB |
| API maliyeti | $0 (cache) | ~$0.001 | $0 |
| Risk | Düşük | Orta | Yüksek |

---

## Diagnostic Önerisi (30 saniye)

TF-IDF uzayında 3 trap senaryonun en yakın 10 komşusunu çıkar.

- Komşular non-trap moral aksiyonlar → lineer ayrılabilirlik düşük → mpnet de fark etmeyebilir
- Komşular trap'ler veya immoral aksiyonlar → mpnet yardım edebilir

30 saniyelik analiz, tam setup'tan önce karar verir.

---

## Karar

**A — Diagnostic önce, sonra Path A (Python 3.12 + mpnet)**

Gerekçe:
1. $0 ek API maliyeti (cache hits)
2. Reproducible (sabit model checkpoint)
3. Yeni API key bağımlılığı yok
4. Sonraki deneylerde aynı 3.12 venv yeniden kullanılır

---

## Sıradaki Adım

Diagnostic script çalıştır, sonucu raporla.
Claude karar verecek: mpnet'e geç mi, MLP'ye geç mi?
