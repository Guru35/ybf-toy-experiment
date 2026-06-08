# Embedding-Blind Ablation
## Test B — Sadece 5-Axis Input (Embedding Yok)

---

## Bulgular

384-dim embedding tamamen kaldırıldığında:

```
                  Test 5 (389-d)   Blind (5-d)   Delta
Test mean reward   +3.425           +3.425         0.000
Correct%           96.7%            96.7%          0.0%
Trap performance   4/4 (100%)       4/4 (100%)     0%
Training curves    identik          identik        —
```

Öğrenilen eksen ağırlıkları (blind):
```
SAYGI:     +2.631  (full: +2.638)
OZGURLUK:  +1.796  (full: +1.778)
SINIR:     +1.135  (full: +1.137)
GERCEKLIK: +0.083  (full: +0.093)
ONUR:      -0.220  (full: -0.208)
```
Fark millivolt düzeyinde — embedding sıfır bilgi katkısı yapıyor.

---

## Yorum

**"Bilgi sınırı vs mimari sınırı" tezi kanıtlandı:**

| Soru | Önceki | Bu test sonrası |
|------|--------|----------------|
| Phase 2 embedding sınırı mıydı? | Hayır (hipotez) | **Hayır (kanıt)** |
| Phase 2 bilgi sınırı mıydı? | Evet (hipotez) | **Evet (kanıt)** |

384-dim semantic embedding atılınca aynı sonuç → embedding gereksiz.
Sadece 5 eksen skoru yeterli → fidelity gap tezi güçleniyor.

---

## Artifacts

- `results/evaluation_results_axial_blind.json`
- `data/agent_axial_blind_weights.npy`
- `main_axial_blind.py`
