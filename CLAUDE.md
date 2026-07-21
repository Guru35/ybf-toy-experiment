# AI Eğitim — Project Context

Bu doküman bu klasörde her Claude oturumuna otomatik yüklenir.
Kısa tutuldu: detaylar `ybf_toy/RUNBOOK.md` ve `ybf_toy/LESSONS.md`'de.

## Üç-Vault Mimarisi

Bu klasör (**AI Eğitim**), üç-vault sisteminin bir tarafı:

| Vault | Konum | Rol |
|---|---|---|
| **YBF Vault** | `~/Documents/YBF-1/` | Bilgi tabanı, wiki (Karpathy LLM-wiki çalışıyor), kitap kaynakları |
| **AI Eğitim** | `~/Documents/AI-Egitmek/` (burası) | Deney çalıştırma + teknik rapor |
| **Claude** | (sohbet) | Strateji + MD sentezleme |

**AI Eğitim'in işi:** YBF reward-sinyali RL deneylerini çalıştır, sonuçları raporla.
**Yapmayacakların:** Kitap yazma, felsefi yorum, wiki bakımı. Bunlar YBF Vault + Claude işi.

## Dosya Haritası

```
ybf_toy/
├── config.py, scorer.py, embedder.py, scenarios.py
├── agent.py        — linear Q-net (baseline)
├── agent_mlp.py    — 2-layer MLP (Test 4)
├── agent_axial.py  — per-axis input (Test 5, current winner)
├── train.py, evaluate.py, report.py
├── main.py         — full run orchestrator
├── main_mlp.py     — MLP variant runner
├── main_axial.py   — axial variant runner (latest)
├── analyze_traps.py, diagnostic_trap.py, fh_probe.py
├── data/           — cache + embeddings + scenarios + agent weights
├── results/        — evaluation JSON summaries (per variant)
├── Raw/            — INCOMING klasör (Claude/YBF Vault dosya bırakıyor)
├── venv/           — Python 3.13 sanal env (TF-IDF stack, no torch)
├── RUNBOOK.md      — operasyonel komutlar
├── LESSONS.md      — debug + mimari geçmiş
└── YBF2-*, AIEgitim-* — çıkış raporları (YBF Vault'a iletilenler)
```

## Aktif State

> Anlık durum artık **tek yerde**: [`wiki/hot.md`](wiki/hot.md) (cache, latest winner, scoring versiyonu, budget guard). Oturum açılışında `@start` orayı okur. Tek-kaynak (single source of truth) — state'i buraya kopyalama, hot.md'yi güncelle.

## Environment

- **Python:** 3.13 (3.14'te torch wheel yok — Intel Mac).
- **venv:** `ybf_toy/venv` (datasets<3, scikit-learn, anthropic, futurehouse-client). Torch YOK, mpnet yok.
- **Embedding:** TF-IDF + TruncatedSVD (LESSONS.md'de C10 notu).
- **Keychain services:**
  - `ANTHROPIC_API_KEY` — scorer için
  - `futurehouse-api-key-aiegitim` — Edison/FutureHouse için (sadece FINCH ajanı erişimli)

## Üç Tehlikeli Operasyon — Yapmadan Önce LESSONS.md Oku

1. **`import scorer`** taze süreçte — atexit cache'i siler (fixed, ama tarih bilinçli kalsın)
2. **`rm -rf data/`** — 2400 entry + embeddings + agent weights. Geri alınamaz.
3. **`security delete-generic-password`** — keychain key'i siler, FutureHouse hesabından yeniden kopyalama gerekir

## Oturum Ritüelleri + Komutlar

Bu vault'un CCD'si hub (Atölye-1) gibi düzenli açılıp kapanır. Komutlar `.claude/commands/` altında; anlık durum `wiki/hot.md`, geçmiş `wiki/log.md`.

| Ok yazınca | CCD ne yapar |
|---|---|
| `@start` | Oturum açılışı: tarih anchor + `wiki/hot.md` + son log + bekleyen handoff kontrolü + "nerede kaldık" özeti. [detay](.claude/commands/start.md) |
| `@done` | Oturum kapanışı: `wiki/log.md` girdisi + `wiki/hot.md` güncelle + handoff status + MD-bloat kontrol. Seremoni yok. [detay](.claude/commands/done.md) |
| `@karpathy` | Yerel Karpathy denetimi: token-ekonomi / MD-bloat / tek-kaynak uygunluğu → log'a. Ok tetikler, ayda bir. [detay](.claude/commands/karpathy.md) |

**Gelen handoff kutusu:** [`Raw/agent-handoffs/`](Raw/agent-handoffs/README.md) — başka AI'ların (çoğunlukla hub) ilettiği vault-üstü kurallar. `@start`'ta taranır. 🔴 **Auto-deliver / manual-execute:** iletim otomatik, ama içindeki aksiyon UYGULANMADAN önce Ok onayı şart.

## Karpathy Guidelines

`~/.claude/CLAUDE.md` (global) zaten yüklü: think-before-coding, simplicity-first, surgical changes, goal-driven execution. Bu proje'de bunlara ek olarak: **deney pipeline'ı reproducible olmalı** (seed=42, sabit hyperparam'lar, cache hit'ler). Spekülatif refactor yapma, deneyler arasında karşılaştırılabilirlik kaybolur.
