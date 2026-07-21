---
description: "@karpathy — Yerel Karpathy denetimi: Raw/ Karpathy kaynakları + gelen handoff sinyalleri + vault'un Karpathy ilkelerine (token-ekonomi / MD-bloat / tek-kaynak) uygunluğu. Bulgular log'a. Ok tetikler."
---

# @karpathy — Yerel Karpathy Denetimi

> **Not:** Hub'daki (`Atolye-1`) `@karpathy` signal-collector'a (Gmail etiketi + RSS) bağlıdır — o altyapı hub'a özeldir, burada YOK. Bu vault'ta `@karpathy` **yerel bir denetimdir**: dışarıdan sinyal çekmez, bu vault'un kendi Karpathy uyumunu gözden geçirir. Bu vault zaten Karpathy LLM-wiki'nin bizzat konusu (Raw/'da kaynakları var).

## Ne zaman
**Ok tetikler** — token-ekonomik, otomatik değil. Ayda bir ya da büyük bir yapısal değişiklikten sonra anlamlı.

## Adımlar

1. **Karpathy kaynaklarını gözden geçir** (immutable, değiştirme — sadece ölçüt olarak kullan):
   - `Raw/Katpathy LLM Wiki.md`, `Raw/Andrej Karpathy - LLM Wiki - X Post.md`
   - Global `~/.claude/CLAUDE.md` — think-before-coding / simplicity / surgical / goal-driven ilkeleri.

2. **Gelen handoff sinyalleri:** `Raw/agent-handoffs/` içinde Karpathy / LLM-wiki / bilgi-yönetimi metodolojisiyle ilgili yeni bir handoff var mı? Varsa özümse ve aşağıdaki denetime kat.

3. **Vault'un Karpathy uygunluğunu denetle** — 3 eksen:
   - **Token ekonomisi:** Gereksiz/tekrar eden büyük dosya var mı? Deney pipeline'ı hâlâ reproducible + cache-dostu mu (spekülatif refactor sızmış mı)?
   - **MD-bloat:** `wc -l` ile CLAUDE.md / wiki/ / RUNBOOK / LESSONS. 400+ satır = split adayı. İdeal <200.
   - **Tek-kaynak (single source of truth):** Aynı bilgi (state, karar, sonuç) birden çok yerde çelişiyor mu? "Aktif State" tek yerde mi (hot.md)? RUNBOOK ↔ LESSONS ↔ CLAUDE.md çelişkisi var mı?

4. **Bulguları işle:**
   - Somut sorun → `wiki/log.md`'ye "karpathy-denetim" girdisi (tarih + bulgular + öneri).
   - Acil/yapısal sorun → `wiki/hot.md`'ye açık-uç olarak ekle.
   - Düzeltme Ok onayı gerektiriyorsa (dosya bölme, taşıma) → öner, kendi başına büyük yapısal değişiklik yapma.

## Ölçüt — neye bakılır / bakılmaz

| Bakılır | Bakılmaz |
|---|---|
| Token ekonomisi, cache-dostu pipeline | Deney sonuçlarının bilimsel yorumu (bu YBF Vault + Claude işi) |
| MD-bloat / dosya boyutu | Kod refactor (spekülatif değişiklik yapma) |
| Çelişen/tekrarlı bilgi, tek-kaynak ihlali | Yeni özellik / kapsam genişletme |

## Token tahmini
Sadece yerel dosya okuma + `wc -l`. Düşük maliyet, dış API yok. Yeni bulgu yoksa log'a "temiz" notu düş.

## İlişkili
- `Raw/Katpathy LLM Wiki.md` — orijinal metin (immutable)
- `wiki/log.md` · `wiki/hot.md`
- `ybf_toy/LESSONS.md` — teknik/mimari geçmiş
