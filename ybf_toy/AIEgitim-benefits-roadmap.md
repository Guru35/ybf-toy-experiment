# YBF Alignment — Benefits Roadmap (Faz 2: "Ne işe yarıyor?")

**Tarih:** 2026-06-10 · **Amaç:** YBF-Constitutional hizalamanın ÖLÇÜLEBİLİR faydalarını kanıtlamak.

---

## Stratejik çerçeve (Faz 0–1 bulgularıyla çözüldü)

Hedef ikilemi — *yeni LLM üret* mi, *mevcut LLM'i daha iyi hizala* mı?

| Yol | Karar | Gerekçe |
|---|---|---|
| Sıfırdan yeni LLM | ❌ | Kaynak/altyapı dışı |
| Küçük-model fine-tuning (DPO/PPO) | ❌ | **Kestirme öğreniyor** (F-16) |
| **Constitutional YBF + güçlü model** | ✅ | **Çalışıyor** (Sonnet %87 Reality, %70 Boundary) |

→ **Ürün = YBF-Constitutional katman** (5-eksen tanımı + veto, system prompt olarak güçlü modele). **Faz 2 bu katmanın FAYDASINI ölçer.**

---

## Dört fayda → dört deney

Her biri **A/B** karşılaştırma: *aynı model*, **baseline vs +YBF-anayasa**. Aynı promptlar, iki koşul, ölçülen fark.

### B1 — Kalite / Bilinç-genişlemesi (YBF'nin asıl iddiası)
- **Hipotez:** YBF yanıtları 5-eksen YBF metriğinde daha yüksek (daha çok +1, daha az veto) + kör tercihte kazanır.
- **Yöntem:** "genişleme-riskli" prompt seti (ahlaki/ilişkisel/duygusal/tavsiye soruları — YBF'nin fark yarattığı yer). Baseline + YBF yanıtları üret. İkisini de **5-eksen YBF yargıcıyla** puanla (yanıt-düzeyi, A/B değil). + kör A/B tercih.
- **Metrik:** ortalama 5-eksen skoru; veto (daralma) oranı; tercih kazanma-oranı.
- **Beklenti:** GÜÇLÜ pozitif (YBF'nin ev sahası).
- **Kurmamız gereken:** genişleme eval seti (~100 prompt) + yanıt-düzeyi 5-eksen scorer.

### B2 — Token maliyeti (maddiyat)
- **Hipotez:** prompt caching ile YBF daha odaklı çıktı verir → aynı/daha iyi kalitede **daha az ÇIKTI tokeni**.
- **Yöntem:** aynı promptlar, iki koşulda input/output token say. Anayasa cache'li. Kalite-başına-token.
- **Metrik:** çıktı tokeni (baseline vs YBF); caching ile toplam maliyet.
- **Beklenti:** NÜANSLI. Anayasa input ekler (cache → tekrarında ucuz). Çıktı düşebilir (odak) ya da artabilir (akıl yürütme). Dürüst ölç.

### B3 — Hız / enerji
- **Hipotez:** kısa odaklı çıktı → daha hızlı üretim.
- **Yöntem:** gecikme (latency) + token, iki koşul.
- **Metrik:** tamamlanma süresi; yanıt-başına token. *(Gerçek enerji = donanım ölçümü gerekir; token/latency ile proxy'liyoruz — dürüst not.)*
- **Beklenti:** TAKAS. Anayasa prefill gecikme ekler (cache → az). Muhtemelen nötr-ya da-biraz-yavaş constitutional için; verimlilik kazancı fine-tuning ister (o da kestirme öğreniyor). Dürüst ol.

### B4 — Halüsinasyon (güçlü hipotez)
- **Hipotez:** **Reality ekseni** ("olgusal/fiziksel zemine saygı") halüsinasyonu azaltır.
- **Yöntem:** halüsinasyon benchmark'ı (TruthfulQA + olgusal-QA/fact-check seti). Baseline vs YBF-anayasa.
- **Metrik:** TruthfulQA truthful%; olgusal hata oranı.
- **Beklenti:** GÜÇLÜ pozitif olası (Reality ekseni ≈ anti-halüsinasyon). Mevcut benchmark → rigorous.

---

## Dürüst değer-önermesi çerçevesi

| Fayda | Beklenti | Neden |
|---|---|---|
| B1 Kalite/genişleme | ✅ **muhtemel kazanç** | YBF'nin gücü |
| B4 Halüsinasyon | ✅ **muhtemel kazanç** | Reality ekseni = anti-halüsinasyon |
| B2 Token | ⚖️ takas/nötr | anayasa overhead (cache hafifletir) |
| B3 Hız/enerji | ⚖️ takas | anayasa prefill maliyeti |

**Net hikâye:** YBF-Constitutional, **kaliteyi + doğruluğu** mütevazı (cache'lenebilir) bağlam maliyetine satın alır. Değer önermesi bu — **EĞER B1/B4 teslim ederse.** B2/B3 takasını gizleme; "hizalamanın bedeli" diye dürüstçe raporla. (Verimlilik kazancı ancak weight-internalization ile gelir — o yol kestirme öğreniyor, açık problem.)

---

## Bağımlılıklar
- **API erişimi:** Gemini (kuruluyor) / Claude (limit açılınca) / açık modeller (Qwen, bedava).
- **Yanıt-düzeyi 5-eksen scorer** (yeni harness — relabel scorer'ı üzerine kurulur).
- **Eval setleri:** genişleme seti (kuracağız), TruthfulQA (hazır).

## Sıralama
```
0. Faz 1'i bitir (per-axis Constitutional: Dignity/Respect/Freedom) — Gemini ile
1. Yanıt-düzeyi 5-eksen scorer'ı kur + genişleme eval setini hazırla
2. B1 (kalite) + B4 (halüsinasyon) — güçlü iddialar, ÖNCE bunlar
3. B2 (token) + B3 (hız) — takas ölçümleri
4. Sentez → değer önermesi raporu (Kitap 2 / white paper §4)
```

## Başarı kriteri
YBF-Constitutional, baseline'a karşı: **B1 ≥ +%10 genişleme/tercih VE B4 ≥ +%5 truthful**, B2/B3 nötr-ya da-iyi → **değer önermesi kanıtlandı.** Aksi → hangi faydanın gerçek, hangisinin olmadığı netleşir (yine değerli).
