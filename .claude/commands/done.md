---
description: "@done — AI Eğitim vault oturum kapanışı: log girdisi + hot.md güncelle + handoff status + MD-bloat kontrol. Seremoni yok."
---

# @done — Oturum Kapanışı

Ok kapanış sinyali verdiğinde ("bitti", "kapatıyorum", "@done") şu adımları çalıştır.

## Adımlar

### 1. `wiki/log.md`'ye girdi ekle (en üste)

```
## [YYYY-MM-DD] <kısa başlık>
- Yapıldı: ...
- Karar: ...
- Açık uç: ...
- (varsa) Deney/sonuç: <hangi run, hangi sonuç dosyası — ör. results/...json>
```

### 2. `wiki/hot.md`'yi güncelle

- "Aktif State" değiştiyse (yeni winner agent, cache durumu, scoring versiyonu, budget) → **güncelle**. Eski state'i olduğu gibi bırakma.
- "Şu an sıcak" listesini bugünün gerçeğine getir.
- Çözülen açık uçları çıkar, yeni açılanları ekle.

> Not: Önemli bir gelişme oturum ortasında olduysa (blokör çözüldü / faz değişti) hot.md zaten o an güncellenmiş olmalı — `@done`'a bırakma kuralı.

### 3. Handoff status'ü kapat (varsa)

Bu oturumda bir `Raw/agent-handoffs/` dosyası ingest edilip benimsendiyse, o dosyanın frontmatter `status:`'ünü güncelle (ör. `benimsendi 2026-...`) ve log'a not düş.

### 4. MD-bloat kontrol (Karpathy)

Hızlı `wc -l`: `CLAUDE.md`, `wiki/*.md`, `ybf_toy/RUNBOOK.md`, `ybf_toy/LESSONS.md`. 400+ satır → bir sonraki oturuma "split adayı" diye not bırak (log'a). Şimdi bölme, sadece işaretle.

### 5. Kapanış

Seremoni cümlesi YOK ("yarın devam ederiz" vб. yazma). Log girdisi + hot.md güncellemesi kapanışın kendisidir. İstersen tek satır olgusal kapanış: "Kapanış: log + hot güncel."

## Tetikleyici
Ok açıkça: "bitti", "kapatıyorum", "@done", "session bitsin".

## Anti-tetik
Ok hâlâ aktif çalışıyorsa çalıştırma — sadece açık sinyalde.

## İlişkili
- `wiki/log.md` · `wiki/hot.md` · Açılış eşi: `@start`
