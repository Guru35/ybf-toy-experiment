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

1. _(CCD: en son üzerinde çalışılan deney/konu buraya — güncelle)_

## Bekleyen / açık uçlar

- _(CCD: yarıda kalan iş, karar bekleyen konu buraya)_

## Gelen handoff (varsa)

- `Raw/agent-handoffs/` — henüz ingest edilmemiş handoff var mı? Bkz. [handoff README](../Raw/agent-handoffs/README.md).
  - `2026-07-13-site-gorunurluk-politikasi.md` — site görünürlük checklist'i (bu deney vault'unu doğrudan ilgilendirmez; kaydedildi).
