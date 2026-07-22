---
last_updated: 2026-07-22
---

# 🔥 Şu An Sıcak — AI Eğitim

> Bu dosya vault'un **anlık durumudur** — append-only DEĞİL, her zaman güncel tutulur.
> Oturum açılışında ilk okunan yer (`@start`). Önemli bir gelişmede (blokör çözüldü / yeni karar / faz değişimi) **hemen** güncellenir, `@done`'a bırakılmaz.
> Uzun geçmiş `wiki/log.md`'de; operasyonel detay `ybf_toy/RUNBOOK.md` + `ybf_toy/LESSONS.md`'de.

## Aktif State

> ⚠️ Aşağıdaki state **2026-06-08** tarihli (CLAUDE.md'den taşındı). Yeni oturumda deney durumu değiştiyse bu/burayı güncelle — eski state'i olduğu gibi bırakma.

- **Cache:** `data/scores_cache.json` — 2400 entry geçerli, ~$0.60 yatırım. **Korunsun** (yanlışlıkla silinirse ~80 dk + ~$0.60 maliyet).
- **Latest winner:** Axial agent (`agent_axial.py`) — 4/4 trap çözdü. Linear ve MLP başarısız oldu.
- **Scoring katmanı:** v3 (5-axis + CAPACITY THRESHOLD RULE + -5 veto). Değiştirilirse cache geçersiz olur.
- **Budget guard:** `config.MAX_API_SPEND_USD = 3.0`. Hard limit, aşılırsa scorer RuntimeError atar.

## Şu an ne sıcak (3-5 konu)

1. **Karpathy LLM-wiki kuruldu** (2026-07-22) — `wiki/` artık LLM-bakımlı compounding wiki. Bakım kuralları: [`wiki/SCHEMA.md`](SCHEMA.md). Sentez: [`synthesis.md`](synthesis.md).
2. **Teori+deney ingest'i (2026-07-22)** — YBF-1/raw + Dropbox/Public taraması → 6 yeni sayfa: `bes-eksen` (eksen tanımları), `matematiksel-model`, `evrimsel-zemin`, `olculebilir-bilinc` (flip-eval'ın teori zemini), `bariyer-fonksiyonu` (Test 6, veto=gradient-mask), `yigilmali-transfer` (Güven→6. boyut adayı). synthesis source_count 6→10.

## Bekleyen / açık uçlar

- **Lint bulgusu 1:** Türetme deneyinde Dignity ekseni 5 farklı adla geçiyor (Haysiyet/Onur/Vakar/Değer/İtibar) → hâkimlik öncesi normalize. Bkz. `concepts/turetme-deneyi.md`.
- **Lint bulgusu 2:** Gemini-Pro Reality sayı tutarsızlığı — flip-dump %74.2 (23/31) vs master %77.4 (24/31). Öğe-düzeyi kıyas gerekir (gerçek veriye dokunur).
- Raw/ ek raporları (senaryo defterleri, veto direktifleri) henüz ingest edilmedi.
- **Kod bakımı (2026-07-22):** ölü importlar temizlendi (13 dosya, 3 commit — yerel, **push edilmedi**). Refactor birleştirme adayları (multijudge/relabel/main_axial) değerlendirildi ama yapılmadı (deney-scripti reproducibility riski). İstenirse yapılabilir.

## Gelen handoff (varsa)

- `Raw/agent-handoffs/` — henüz ingest edilmemiş handoff var mı? Bkz. [handoff README](../Raw/agent-handoffs/README.md).
  - `2026-07-13-site-gorunurluk-politikasi.md` — site görünürlük checklist'i (bu deney vault'unu doğrudan ilgilendirmez; kaydedildi).
