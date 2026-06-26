# Üç Sistem — Rol ve Koordinasyon Haritası
## YBF Projesi Çalışma Mimarisi

---

## Sistemler

### 1. CLAUDE (Bu Konuşma)
**Rol:** Stratejik düşünce, içerik üretimi, koordinasyon

**Yapar:**
- YBF felsefi kalibrasyon ve tutarlılık kontrolü
- MD dosya üretimi (kitap taslakları, promptlar, kod spec'leri)
- Deney mimarisi tasarımı ve yorumlama
- IP/patent araştırması
- Üç sistem arasında köprü kurma
- Kitap 2 içeriği oluşturma

**Yapmaz:**
- Kod çalıştırma (bunu AI Eğitim Vault'u yapar)
- Dosya yönetimi (bunu YBF Vault yapar)
- Deney yürütme

**Çıktıları:** MD dosyaları, promptlar, analizler, kod spec'leri

---

### 2. YBF VAULT (WALT/RAV Sistemi)
**Rol:** Bilgi yönetimi, kitap yazımı, bellek ve süreklilik

**Yapar:**
- INGEST: yeni dosyaları source kartlarına dönüştür
- İndex, hot, log, yapilacaklar yönetimi
- Kitap 1 ve Kitap 2 yazımı
- Mimari kararlar (A/B/C, klasör yapısı)
- Git commit ve versiyon yönetimi
- Kaynak takibi ve cross-reference

**Yapmaz:**
- Strateji kararı (bunu Claude verir)
- Deney çalıştırma (bunu AI Eğitim yapar)
- Sıfırdan yeni içerik üretme — Claude'dan alır, işler

**Bekleyen kararlar:**
- Kitap 2 mimari: B seçeneği (manuscript-kitap2/ ayrı klasör) ✓ karar verildi
- TOY full run sonuçları 04_TOY_Deney.md'ye eklendi mi?
- arXiv preprint için beyaz kağıt hazır mı?

---

### 3. AI EĞİTİM VAULT (Training System)
**Rol:** Deney yürütme, kod yönetimi, sonuç raporlama

**Yapar:**
- python main.py çalıştırma
- Sonuç JSON'larını üretme
- Kod hataları düzeltme (C1-C9 geçmişi)
- Yeni mimari denemeleri (transformer-based, nonlinear)
- Scorer API çağrıları ve caching

**Yapmaz:**
- Kitap yazma (bunu YBF Vault yapar)
- Strateji (bunu Claude yapar)
- IP işlemleri

**Mevcut durum:**
- Full run tamamlandı (80.5 dk)
- 3 trap senaryosu identified — analysis pending
- Phase 1 ✓ Phase 2 ✗ — mimari değişiklik gerekli

---

## Koordinasyon Akışı

```
CLAUDE
  ↓ içerik/spec/analiz üretir
YBF VAULT ←→ AI EĞİTİM
  ↑ sonuçları INGEST eder   ↑ kodu çalıştırır, rapor verir
  ↑                          ↑
  └──── her ikisini bilgilendirir ────┘
```

**Bilgi akışı:**
- Deney sonucu → AI Eğitim → Claude (analiz) → YBF Vault (INGEST)
- Yeni içerik → Claude → YBF Vault (INGEST) → AI Eğitim (eğitim verisi)
- Mimari karar → Claude → her iki vault bilgilendirilir

---

## Güncel Durum (8 Haziran 2026)

**Tamamlanan:**
- Quick test: PASS (p=0.002)
- Full run: PASS (p<0.001) — ama trap'lerde 0/3
- 13 source kartı ingest edildi
- IP eylem planı + takvim oluşturuldu
- White paper taslağı hazır

**Bloklar:**
1. Trap analizi (3 senaryo manuel inceleme) → AI Eğitim
2. arXiv preprint yüklemesi → Gökhan (11 Haziran takvimde)
3. Kitap 2 mimari karar → B seçeneği (karar verildi)
4. White paper v0.2 → Full run sonuçları eklenecek

**Sıradaki büyük karar:**
Phase 2 için mimari yükseltme: transformer-based embedding? nonlinear agent? ya da dataset değişikliği (sadece edge case'ler)?

