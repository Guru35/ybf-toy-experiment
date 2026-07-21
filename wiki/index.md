# AI Eğitim — İçerik Kataloğu

> Bu vault'un yol haritası. Anlık durum için `wiki/hot.md`, oturum geçmişi için `wiki/log.md`.

## Kimlik
YBF (Gerçeklik Tanımı) reward-sinyali ile RL deney vault'u. Üç-vault sisteminin **deney** tarafı: YBF-1 (bilgi tabanı) + AI-Egitmek (deney/rapor) + Claude (sentez). Detay: [`../CLAUDE.md`](../CLAUDE.md).

## wiki/ — LLM-bakımlı
- [`hot.md`](hot.md) — anlık durum (cache, kazanan agent, scoring versiyonu, budget)
- [`log.md`](log.md) — oturum geçmişi

## Deney pipeline'ı (`../ybf_toy/`)
- `RUNBOOK.md` — operasyonel komutlar
- `LESSONS.md` — debug + mimari geçmiş
- `agent_axial.py` — güncel kazanan agent (per-axis)
- `config.py · scorer.py · embedder.py · scenarios.py` — çekirdek katmanlar
- `main_axial.py` — güncel run orchestrator
- `results/` — değerlendirme JSON özetleri · `data/` — cache + embeddings + weights

## Kaynaklar (`../Raw/`)
- Karpathy LLM Wiki kaynakları, YBF algoritma dokümanları, deney raporları
- [`agent-handoffs/`](../Raw/agent-handoffs/README.md) — gelen handoff kutusu

## Oturum komutları (`.claude/commands/`)
- `@start` · `@done` · `@karpathy` — bkz. [`../CLAUDE.md`](../CLAUDE.md) komut tablosu
