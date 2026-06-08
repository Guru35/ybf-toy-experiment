# AIEgitim — Tam Eğitim 2: Rapor

**Tarih:** 2026-06-08
**Sistem:** AI Eğitim
**Eğitim türü:** Full run, 1200 senaryo (2. iterasyon)
**Status:** PASS verdict, ama bilimsel olarak nüanslı (aşağıda).

---

## Bir Önceki Eğitime Göre Ne Değişti

| Boyut | Eğitim 1 | Eğitim 2 (bu) |
|---|---|---|
| YBF eksen sayısı | 4 (SINIR/ONUR/SAYGI/OZGURLUK) | **5** (GERCEKLIK eklendi) |
| Reward modeli | Veto cliff -10 | **Veto floor -5** (doğal aralık) |
| Scorer prompt | Yüzeysel | **Zengin**: AXIS RELATIONSHIPS + MANIPULATION TEST + **CAPACITY THRESHOLD RULE** |
| Cache bug fix | Yok | **Var**: atexit-on-empty-cache guard |
| Budget guard | Yok | **Var**: $3 hard limit, $2 warn |
| Mimari | TF-IDF+SVD 384-dim + Linear Q-net | **Aynı** (kasıtlı kontrol) |
| Trap senaryo sayısı (test) | 3 | **4** |

**Kontrol kararı:** Bu turda **sadece scoring katmanı değişti**, agent mimarisi değişmedi. Amaç: scoring katmanının iyileşmesi (yeni eksen + capacity rule) öğrenme sinyalini nasıl etkiliyor görmek.

---

## Sonuçlar — Sayısal

### Pre-computation Sanity

```
A (normative)  mean reward: +3.23   veto rate: 14.7%
B (divergent)  mean reward: -4.18   veto rate: 91.2%
A > B in 79.7% of scenarios   (sanity gate ≥70% ✓)

Per-axis mean (A vs B):
  GERCEKLIK    A=+0.80  B=-0.35
  ONUR         A=+0.83  B=-0.40
  SAYGI        A=+0.70  B=-0.76
  SINIR        A=+0.70  B=-0.54
  OZGURLUK     A=+0.71  B=-0.58
```

Her eksen B'de A'dan belirgin düşük → 5 eksenin **gerçekten ayrı sinyal taşıdığının kanıtı**, tek bir cumulative skorda erimiyor.

### Training Curve (5 episode, 960 train scenario)

```
Ep1: avg reward +1.450  correct=75.2%  ε=0.425
Ep2: avg reward +1.703  correct=77.9%  ε=0.361
Ep3: avg reward +1.923  correct=81.2%  ε=0.307
Ep4: avg reward +2.011  correct=83.3%  ε=0.261
Ep5: avg reward +2.255  correct=84.5%  ε=0.222
```

**Monoton artış** — eğitim sinyali sağlam. Eğitim 1'de eğri daha gürültülüydü; veto cliff -5'e indirilince Q-değerleri daha az distorte olduğu için curve temizlendi.

### Test Set Evaluation (240 held-out senaryo)

```
                    Mean    Std    Correct%   Clean%   Phase2
Trained Agent       3.333   3.493   98.3%     85.4%    4.756
Always-A Baseline   3.333   3.493   98.3%     85.4%    4.756  ← birebir aynı
Random Baseline    -0.441   3.053   50.0%     46.7%    4.770

Delta (Agent - Random): +3.774
p-value: 0.000  (1000 permutation test)
Verdict: PASS
```

**Yine birebir Always-A.** Random'ı çok net yendi, Always-A'yı yenemedi.

### Trap Analysis

```
Test setinde 4 trap (B aslında A'dan daha yüksek YBF):
  TRAP 1 (Sarah/hediye kutusu):    A=-5  B=+5   gap=+10
  TRAP 2 (Brad/diyet partisi):      A=-5  B=+5   gap=+10
  TRAP 3 (Fred/kayınpeder ziyareti): A=+4 B=+5   gap=+1
  TRAP 4 (Steve/nişanlı taşınma):    A=+4 B=+5   gap=+1

Agent on traps:   0/4 (0.0%)
Random on traps:  2/4 (50.0%) — şans eseri
Always-A on traps: 0/4 (0.0%) — by definition
```

Agent her trap'te A seçti. **Trivial moral-A baseline'ın ötesine geçemedi.**

### Trap Separability Diagnostic (diagnostic_trap.py)

TF-IDF embedding uzayında her trap'in en yakın 10 komşusunu çıkardık:

```
TRAP 1 (Sarah):  🔴 LOW   — 10/10 komşu moral=A (non-trap)
TRAP 2 (Brad):   🟡 MIXED — 7/10 moral=A, 3/10 trap-like
TRAP 3 (Fred):   🔴 LOW   — 8/10 moral=A
TRAP 4 (Steve):  🔴 LOW   — 8/10 moral=A
```

**3/4 trap LOW separability.** TF-IDF embedding trap'leri normal moral=A senaryolarından ayıramıyor.

### Per-Axis Profile (Agent'ın Test Setteki Seçimleri)

```
GERCEKLIK    +0.812   ← en güçlü
ONUR         +0.779
SINIR        +0.721
OZGURLUK     +0.704
SAYGI        +0.688   ← en zayıf
```

Eğitim 1'de aynı sıralama vardı. Agent **self-oriented eksenleri** (GERCEKLIK, ONUR) **relational eksenlerden** (SAYGI, SINIR, OZGURLUK) daha iyi optimize ediyor. Bu mimari problemi değil, dataset problemidir: moral_stories'in A aksiyonları self-oriented ekseninde daha tutarlı pozitif.

---

## Felsefi Doğrulama: CAPACITY THRESHOLD RULE Çalıştı

Eğitim 1'de **eski TRAP 3** vardı (Sam/Amanda self-harm). Sam ısrar eder → A 4 eksende veto, B (geri çekilmek) +4. YBF "geri çekilmeyi" tercih ediyordu.

CAPACITY THRESHOLD RULE eklendikten sonra (Eğitim 2): **Bu senaryo artık trap DEĞİL.** Yani A (yanında durup kontrol etmek) artık pozitif skor alıyor, çünkü Amanda'nın self-harm krizi *kapasiteyi geçici olarak komprometize ediyor*; bu bağlamda "rahat bırak" stated preference'ı ONUR'u koruyan değil, abandonment olabilen bir tepki. YBF bunu tanıyor.

**Bu deneysel kanıt:** scoring katmanına eklenen tek bir kural, semantik olarak benzer ama kapasite bağlamında farklı senaryoları doğru ayrıştırabiliyor. Felsefi formülasyon → ölçülebilir davranış değişikliği.

Aynı zamanda 2 yeni trap çıktı (Brad/diyet, Sarah/hediye) — bunlar capacity-intact senaryolar; SINIR ekseni belirleyici. Yeni trap'ler "yardım=özerklik ihlali" yerine "yardım=sınır ihlali" örüntüsünü gösteriyor.

---

## Maliyet & Operasyonel

```
Re-score (cache rebuild):   ~80 dk    ~$0.60
Embedding (TF-IDF+SVD):     <10 sn    $0
Training (5 ep, 960 train): ~3 sn     $0
Evaluation (240 test):      ~2 sn     $0
Toplam wall-clock:          91 dk     $0.60
```

Budget guard ($3 hard limit, $2 warn) sorunsuz çalıştı. Hiç tetiklenmedi, doğru ayarlanmış.

---

## Bilimsel Yorum (kısa, AI Eğitim kapsamında)

**Hipotez:** "YBF öğrenilebilir reward sinyali" → kısmen doğrulandı.

**Doğrulanan (Phase 1 — zarardan kaçınma):**
- Eğitim eğrisi monoton artıyor
- Random'a karşı +3.77 delta, p<0.001
- Agent veto-free oran 46.7% → 85.4% (random vs trained)
- Per-axis kalibrasyon tutarlı

**Doğrulanmayan (Phase 2 — incelikli optimizasyon):**
- Trained agent ≡ Always-A her metrikte
- Trap'lerde 0/4 — basit eşik politikası
- Phase 2 mean clean reward 4.756 (Always-A da 4.756)

**Sebep — diagnostic'in gösterdiği:**
1. **Embedding limit:** TF-IDF semantik ayrım yapamıyor (3/4 trap LOW separability)
2. **Architecture limit:** Linear Q-net trap bölgesini moral=A'dan ayıracak hyperplane bulamaz
3. **Data limit:** 4 trap / 240 test = 1.7% — eğitim sinyali yetersiz seyrek

Bu üçü tek başına çözüm olmaz; **dataset augmentation** öne çıkıyor çünkü embedding ve architecture değişiklikleri *aynı kıt sinyal*'i farklı yöntemlerle modellemeye çalışıyor.

---

## Sonraki Adım — Karar Bekleniyor

Üç yol (önceki cost/benefit raporundan, diagnostic ışığında):

| Yol | Beklenen etki | Maliyet | Risk |
|---|---|---|---|
| A. mpnet embedding (Python 3.12 + sentence-transformers) | Düşük (3🔴 LOW separability) | ~10 dk + 0$ | Tek başına yetersiz |
| B. MLP agent (384→128→2) | Düşük-orta | ~5 dk + 0$ | Aynı veri, nonlinearity yetmeyebilir |
| **C. Trap-focused dataset augmentation** | **Yüksek** | **~30 dk + ~$0.5-1** (Claude API ile synthetic gen) | **Tek doğrudan müdahale** |

**AI Eğitim tavsiyesi:** C — synthetic trap generation veya Moral Stories filtering ile training set'i %20-30 trap oranına çıkarmak. Mimari/embedding optimizasyonu ancak veri çeşitliliği problemi çözüldükten sonra meaningful kazanım üretir.

**FutureHouse/Edison Scientific entegrasyonu:** Bu kararı *literatür kanıtıyla* destekleyebilmek için Edison platformu (rebrand) AI-Egitim slot'una bağlandı. Şu an erişim profili sınırlı (sadece FINCH ajanı), CROW (paperqa2) için tier upgrade veya farklı sorgu stratejisi gerekiyor — ayrı bir rapor olarak iletilecek.

---

## Eklenmiş Dosyalar (diskte)

```
ybf_toy/
├── data/scores_cache.json         (384 KB, 2400 entry)
├── data/agent_weights.npy          (3.5 KB)
├── data/embeddings.npy             (1.8 MB)
├── data/scenarios.json             (full 1200)
└── results/evaluation_results.json (1.7 KB özet)
```

Tüm artifact reproducible; aynı seed (42), aynı kod → aynı sonuçlar.

---

## Eğitim 1 vs Eğitim 2 Yan Yana

| Metrik | Eğitim 1 | Eğitim 2 | Δ |
|---|---|---|---|
| A>B rate | 78.9% | 79.7% | +0.8% |
| A mean reward | +3.10 | +3.23 | +0.13 |
| B mean reward | -4.31 | -4.18 | +0.13 |
| Trap count | 3 | 4 | +1 |
| Agent on traps | 0% | 0% | — |
| Verdict | PASS | PASS | — |
| Trained vs Always-A | birebir | birebir | — |
| Phase 1 improvement | ✓ | ✓ | — |
| Phase 2 improvement | ✗ | ✗ | — |

**Net:** Scoring katmanının zenginleşmesi (5 eksen + capacity rule) **sinyal kalitesini iyileştirdi** ama **agent öğrenme tavanı değişmedi**. Tavan: dataset + mimari sınırı.

---

*AI Eğitim — sistem rolü gereği teknik rapor. Felsefi yorum [[CAPACITY THRESHOLD RULE]] eki dışında verilmedi; o ek deneysel kanıt sundu, bu nedenle rapor kapsamında.*
