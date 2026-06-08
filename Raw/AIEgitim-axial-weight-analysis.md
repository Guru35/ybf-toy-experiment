# Axial Agent Ağırlık Analizi
## Test A — Reward Function Reverse-Engineering

---

## Bulgular

Axial agent'ın W matrisinden son 5 ağırlık (eksen girdilerine karşılık gelen):

```
Eksen        İdeal   Öğrenilen   Oran
GERCEKLIK    +1.00   +0.093     0.09×   → neredeyse sıfır
ONUR         +1.00   -0.208    -0.21×   → NEGATİF
SAYGI        +1.00   +2.638     2.64×   → 3× büyütülmüş
SINIR        +1.00   +1.137     1.14×   → ideale yakın
OZGURLUK     +1.00   +1.778     1.78×   → 2× büyütülmüş
Σ = +5.44  (ideal +5.0)
bias = -0.76
```

Embedding ağırlıkları (W[:384]): L2 norm=1.66, median |w|=0.05 → %6 katkı.

---

## Yorum

Ajan Σ(axes) öğrenmedi. **Dataset varyansına göre ağırlıklı projeksiyon** öğrendi:

- GERCEKLIK ve ONUR Moral Stories'de neredeyse her zaman +1 → düşük varyans → ağırlık ~0
- SAYGI en yüksek varyansa sahip → en yüksek ağırlık
- 4 trap'i çözmesi şanslı hizalama: trap'lerin tamamı SAYGI/SINIR/OZGURLUK eksenlerinde

**ONUR'un negatif çıkması:** Veri setinde normatif davranışlar zaman zaman Onur'u hafif feda ederek Saygı'yı maksimize ediyor. Bu Sam/Amanda trap'indeki bias'ın aynısı.

**Fidelity gap:** Q ≈ +0.09·G - 0.21·O + 2.64·Sa + 1.14·Si + 1.78·Öz — gerçek YBF değil, dataset projeksiyonu.

---

## Artifacts

- `results/axial_weight_analysis.json`
- `analyze_axial_weights.py`
