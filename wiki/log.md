# AI Eğitim — Oturum Log

> Append-only oturum geçmişi. En yeni **üstte**. Her `@done`'da bir girdi eklenir.
> Anlık durum için `wiki/hot.md`'ye bak. Operasyonel/teknik geçmiş `ybf_toy/LESSONS.md`'de.

---

## [2026-07-22] Oturum ritüelleri kuruldu (AAI, Ok talebiyle)

- **Yapıldı:** Bu vault'a hub-benzeri oturum mekaniği kuruldu — `@start`, `@done`, `@karpathy` komutları + `agent-handoffs` ingest protokolü.
- **Kurulan dosyalar:**
  - `wiki/hot.md` (anlık durum) + `wiki/log.md` (bu dosya)
  - `.claude/commands/start.md`, `done.md`, `karpathy.md`
  - `Raw/agent-handoffs/README.md` (handoff ingest protokolü)
  - `CLAUDE.md`: komut tablosu + ritüel pointer'ları eklendi; "Aktif State" → `hot.md`'ye taşındı.
- **Karar (Ok):** Oturum temeli = hafif kanonik `wiki/`; `@karpathy` = yerel Karpathy denetimi (hub signal-collector'a bağlanmadı, o altyapı hub'a özel).
- **Bozulmadı:** Üç-Vault Mimarisi, Dosya Haritası, Environment, Üç Tehlikeli Operasyon bölümleri aynen korundu (süreç yozlaşma koruması).
- **Açık uç:** `hot.md`'deki Aktif State hâlâ 2026-06-08 tarihli — deney durumu güncellenince CCD tazeleyecek.
