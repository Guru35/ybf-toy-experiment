---
tags: [concept, deney, bulgu, mimari]
updated: 2026-07-22
---

# Bariyer Fonksiyonu — Veto = Gradient Mask (Test 6)

**Bulgu:** Veto'yu **ceza** olarak değil, **optimizasyon-kapatma** olarak kodlamak, agent'ın gerçek YBF reward fonksiyonuna çok daha yakın öğrenmesini sağlıyor. "Veto = gradient o yöne HİÇ gitmiyor" felsefi direktifi ([[muhurlenen-ilkeler]]) sadece doğru değil, deneysel olarak daha iyi.

## Mekanizma
- **Standart TD (Test 5, [[olcek-asimetrisi]] axial):** vetolu eylem reward=−5 alır, gradient W'yi −5'e çeker. Veto'lu örneklerin eksen-profili gradient'e sızar → dataset-bias öğrenilir.
- **Bariyer (Test 6):** vetolu adımda `agent.update()` **atlanır**. Q hiç güncellenmez. Gradient yalnız temiz (non-veto) örneklerden gelir. Eğitimin %27.7'si (1331/4800) atlandı.

## Öğrenilen ağırlıkların dönüşümü
| Eksen | Standart Axial | Bariyer Axial |
|---|---|---|
| Gerçeklik | +0.09 | +0.94 (10× büyüdü) |
| Onur | −0.21 | +0.77 (işaret değişti) |
| Saygı | +2.64 | +0.89 (3× küçüldü) |
| Sınır | +1.14 | +0.97 |
| Özgürlük | +1.78 | +0.95 |
| **Σ** | **+5.44 (asimetrik)** | **+4.51 (~simetrik)** |

Standart axial **dataset projeksiyonu** öğrenmişti (Saygı şişik, Onur negatif — Moral Stories istatistiği). Bariyer **YBF reward'a yakın** lineer yaklaşım (tüm eksenler ~+1, hiçbiri ihmal edilmiyor). Embedding katkısı da 6.6× düştü — temiz sinyal embedding'i gereksizleştirdi.

## Genelleme kanıtı
ID trap 4/4 (kayıp yok), **OOD trap 10/10** (sıfırdan tam puana). OOD başarısı, bariyer'in dataset hilesi değil gerçek YBF öğrendiğinin destekleyici kanıtı. Bariyer, tüm test serisinde (2→6) hem öğrenme kalitesi hem genelleme açısından kazanan.

## Çift-seviye fidelity gap (metodolojik uyarı)
| Seviye | Gap | Test 6 |
|---|---|---|
| **Agent** | Q ≈ dataset projeksiyonu | ✓ bariyer çözdü |
| **Scorer** | Haiku, Gerçeklik'te "konfor verici yalan"ı +1 okuyor (pretrained "duygusal destek=iyi" prior'ı YBF talimatını override ediyor) | ✗ sadece teşhis |

**Ders:** YBF testi yapan, scorer-prompt'un kendi fidelity'sini de doğrulamalı — aksi halde agent-deneyi kör baseline üstüne kurulur. (Bu, [[olculebilir-bilinc]] teorisinin deneysel yüzü: bariyer = donmaya iten hamleyi reddeden negentropik zorunluluk.)

**Çekince:** Σ=+4.51 hâlâ %10 underestimate; truly-novel YBF ihlalleri (çift-veto) test edilmedi. "Büyük adım, tam içselleştirme değil."

(kaynak: `~/Documents/YBF-1/raw/YBF2-test6-barrier-ood-rapor.md`) · ilgili: [[olcek-asimetrisi]] · [[matematiksel-model]] · [[olculebilir-bilinc]] · [[muhurlenen-ilkeler]]
