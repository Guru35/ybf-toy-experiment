---
description: "@start — AI Eğitim vault oturum açılışı: tarih anchor + hot.md + son log + bekleyen handoff + nerede kaldık özeti."
---

# @start — Oturum Açılışı

Ok `@start` dediğinde (veya yeni oturum açıldığında) şu sırayı çalıştır. Bu **tek-vault** bir deney vault'u — hub'ın çok-vault sweep'i burada YOK; sadece bu vault'un durumu okunur.

## Adımlar

1. **Tarih anchor.** İlk mesajın başında bugünün tarihini + gününü yaz.

2. **Anlık durumu oku:** `wiki/hot.md` — Aktif State + şu an sıcak konular + bekleyen açık uçlar. (Bu vault'un "nerede kaldık" kaynağı.)

3. **Son oturumu oku:** `wiki/log.md` en üstteki 1-2 girdi — geçen sefer ne yapıldı, ne açık kaldı.

4. **Bekleyen handoff kontrolü:** `Raw/agent-handoffs/` klasöründe `status: ingest edilince benimse` olan ingest edilmemiş dosya var mı? Varsa Ok'a **sun** (özetle) — ama aksiyonu kendi başına alma (bkz. auto-deliver / manual-execute, [handoff README](../../Raw/agent-handoffs/README.md)).

5. **Kompakt özet + tek soru.** 3-4 satırlık durum özeti ver, sonra sor:

   > "Bugün nerede kaldık, ne üstünde çalışıyoruz?"

   Bekle. Ok konuşmadan görev önerme.

## Yapma

- Deney çalıştırma / cache'e dokunma / `rm -rf data/` gibi tehlikeli operasyon — Ok istemeden ASLA (bkz. CLAUDE.md "Üç Tehlikeli Operasyon").
- Uzun rapor dökme — hot.md + son log yeter, kısa tut.

## İlişkili
- `wiki/hot.md` · `wiki/log.md` · `Raw/agent-handoffs/README.md`
- Kapanış eşi: `@done` (`.claude/commands/done.md`)
