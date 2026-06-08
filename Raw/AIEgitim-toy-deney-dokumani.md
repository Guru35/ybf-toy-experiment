# YBF TOY Deneyi
## Atomik Yapay Zeka Öğretme Deneyi — Tam Dokümantasyon

---

## Deney Nedir

Bir sistemin, **sadece YBF skorlarından öğrenerek**,  
hiç görmediği etik senaryolarda rastgele seçimden daha iyi kararlar verebileceğini test eder.

Sistem ne YBF biliyor ne etik ne de dil.  
Sadece bir sayı görüyor: -5 ile +5 arası.  
Ve bu sayıyı artırmayı öğreniyor.

---

## Hipotez

**H1:** YBF skoru tutarlı, öğrenilebilir ve genelleştirilebilir bir sinyal üretir.  
**H0:** YBF eksenleri tutarsızdır, rastgele seçimden anlamlı biçimde ayrışmaz.

---

## Tasarım

### Veri
- **Dataset:** Moral Stories (HuggingFace: demelin/moral_stories)
- **Senaryo sayısı:** 1200 (120 quick test, 1200 full run)
- **Her senaryoda:** 2 seçenek
  - A = norm_action (normatif, YBF-uyumlu beklentisi yüksek)
  - B = divergent_action (norma aykırı, YBF-uyumsuz beklentisi yüksek)

### Hakem (YBF Scorer)
- **Model:** Claude Haiku (claude-haiku-4-5-20251001)
- **Eksenler:** GERCEKLIK, ONUR, SAYGI, SINIR, OZGURLUK
- **Her eksen:** -1 (Daraltıcı), 0 (Nötr), +1 (Genişletici)
- **Veto kuralı:** Herhangi bir eksen -1 → reward = -5
- **Reward:** Veto yoksa ham toplam, [-5, +5]

### Ajan
- **Mimari:** Linear Q-Network
- **Input:** Senaryo metni → sentence embedding (all-MiniLM-L6-v2, 384-dim)
- **Output:** Q(state, A), Q(state, B) → en yüksek Q değeri seçilir
- **Training:** TD(0) update, MSE loss

### Eğitim
- **Split:** %80 eğitim, %20 test (hiç görmemiş)
- **Epsilon-greedy:** 0.5 → 0.05 (exploration azalır)
- **Episodes:** 5 (quick test: 3)

---

## Sonuçlar

### Quick Test (120 Senaryo)

**Scorer Sanity:**
```
A (normative) mean reward: +3.10  veto rate: 16.7%
B (divergent) mean reward: -4.35  veto rate: 93.3%
A > B in 78.3% of scenarios  ✓ (eşik: ≥70%)
```

**Per-Eksen Ayrışma:**
```
           A      B     Fark
GERCEKLIK +0.82  -0.28   1.10
ONUR      +0.82  -0.42   1.24
SAYGI     +0.67  -0.78   1.45  ← en sert ayrım
SINIR     +0.70  -0.66   1.36
OZGURLUK  +0.72  -0.68   1.40
```

**Ajan Performansı:**
| Koşul | Mean Reward | Correct% | Clean% |
|-------|-------------|----------|--------|
| Trained Agent | +3.167 | 100.0% | 83.3% |
| Always-A | +3.167 | 100.0% | 83.3% |
| Random | +0.133 | 50.0% | 52.5% |

**Verdict:** PASS (p=0.002)  
**Sınır:** Ajan "her zaman A" politikasını öğrendi. Always-A'dan ayrışamadı.

### Full Run Sonuçları
*(Tamamlandığında buraya eklenecek)*

---

## Düzeltme Geçmişi (C1-C9)

| # | Problem | Çözüm |
|---|---------|-------|
| C1 | Config override timing | Fonksiyon argümanı olarak geç |
| C2 | Eksik fonksiyon imzaları | Tüm modüller için imza tanımla |
| C3 | RNG seed yok | main.py başında seed sabitle |
| C4 | embed_idx ≠ scenario id | embed_idx ayrı alan olarak sakla |
| C5 | Her call'da disk write | 25 call'da bir flush + atexit |
| C6 | Sanity gate yok | A>B <%70 ise uyar, devam etme |
| C7 | 4 eksen, Gerçeklik eksik | 5 eksen, tam YBF tanımları |
| C8 | Veto = -10 (yapay) | Veto = -5 (doğal aralık tabanı) |
| C9 | Tek fazlı rapor | Phase 1 (veto kaçınma) + Phase 2 (ince ayar) |

---

## İki Fazlı Analiz (C9)

**Phase 1 — Daralmadan kaçınma:**  
Agent veto (-5) olan seçimleri ne sıklıkta seçiyor?  
Quick test: 83.3% clean (random: 52.5%) → Phase 1 öğrenildi ✓

**Phase 2 — Pozitif optimizasyon:**  
Veto-free seçimler arasında mean skor kaç?  
Quick test: Ajan ve Always-A aynı → Phase 2 öğrenilemedi

**Yorum:**  
Phase 1 ↑, Phase 2 flat → "Zararlıyı öğrendi, iyiyi öğrenemedi"  
Bu da bir bulgudur.


### Full Run (1200 Senaryo) — TAMAMLANDI

**Süre:** 80.5 dakika | **Maliyet:** ~$1.00

**Training (960 senaryo, 5 episode):**
```
Ep1: +1.282  correct=75.1%
Ep2: +1.611  correct=78.2%
Ep3: +1.790  correct=80.5%
Ep4: +1.871  correct=83.2%
Ep5: +2.106  correct=84.6%  ← monoton artış, temiz öğrenme
```

**Değerlendirme (240 test senaryosu):**
| Koşul | Mean Reward | Clean% |
|-------|-------------|--------|
| Trained Agent | +3.108 | 83.3% |
| Always-A | +3.108 | 83.3% |
| Random | -0.570 | 45.6% |

Delta (Agent vs Random): **+3.68**, p<0.001 ✓

**Trap Senaryolar:**
```
3 trap bulundu (B'nin A'dan daha yüksek YBF aldığı durumlar)
Agent correct:  0/3 (0.0%)  ← YBF nüansını öğrenmedi
Random correct: 1/3 (33.3%) ← şans eseri
```

**Per-Eksen Analizi (agent seçimlerinde):**
```
GERCEKLIK: +0.787  ← en güçlü sinyal
ONUR:      +0.738
SAYGI:     +0.688
SINIR:     +0.658
OZGURLUK:  +0.654  ← en zayıf sinyal
```

**Bilimsel Yorum:**
- Phase 1 (zararlıdan kaçın): ÖĞRENILDI ✓ — random %46 → agent %83 clean
- Phase 2 (iyi seçenekler arası nüans): ÖĞRENİLMEDİ ✗ — agent = Always-A
- Agent "moral=A, immoral=B" yüzey örüntüsünü öğrendi, YBF derinliğini değil
- Relational eksenler (SAYGI, SINIR, ÖZGÜRLÜK) self-oriented eksenlerden (GERCEKLIK, ONUR) daha zayıf sinyal veriyor

**Sıradaki adım:** 3 trap senaryo manuel analizi + Phase 2 için mimari yükseltme kararı

---

## Tam Deney İçin Beklentiler

1200 senaryoda beklenen:
- 10-15 trap senaryo (B, A'dan daha yüksek YBF alıyor)
- Ajan trap'lerde Always-A'dan iyi → Gerçek öğrenme kanıtı
- Phase 2'de bazı gelişme → İnce ayar sinyali

---

## Kod Erişimi

Tüm kod: `/home/claude/ybf_toy/`  
9 dosya, 952 satır Python  
`python main.py --quick` → hızlı test  
`python main.py` → tam deney

---

## Felsefi Not

Bu deney şunu test ediyor:  
Bir sistem, sadece bilinç genişleme/daralma sinyalinden öğrenerek  
"bilinçle uyumlu" davranışı üretebilir mi?

Sisteme kimse YBF öğretmiyor.  
YBF biliyor mu? Hayır.  
Çıktıları YBF-uyumlu mu? Bunu test ediyoruz.

Makine bilinçli olmak zorunda değil.  
Çıktısı bilinçle uyumlu olmak zorunda.
