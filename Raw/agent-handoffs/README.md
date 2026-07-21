# agent-handoffs/ — Gelen Handoff Kutusu

Bu klasör, **başka bir AI'ın (çoğunlukla hub = Atölye-1 / AAI) bu vault'a ilettiği vault-üstü ortak kuralların / kararların** bırakıldığı yerdir. Tek yönlü giriş kutusu: dışarıdan gelir, bu vault'un CCD'si okur, özümser, uygular.

## Dosya formatı

Her handoff bir `.md` dosyası, ismi `YYYY-MM-DD-<konu>.md`. Frontmatter:

```yaml
---
type: convention          # convention | decision | note
subject: <tek satır özet>
source: <kim gönderdi + Ok yetkisi + tarih>
status: ingest edilince benimse   # → sonra: benimsendi YYYY-MM-DD
---
```

Örnek: `2026-07-13-site-gorunurluk-politikasi.md`.

## Ingest akışı (CCD ne yapar)

1. **Fark et:** `@start`'ta bu klasör taranır; `status: ingest edilince benimse` olan işlenmemiş dosya varsa Ok'a **sunulur**.
2. **Oku + özümse:** Handoff'un içeriğini anla — bu vault'u ilgilendiriyor mu, neyi değiştiriyor?
3. **🔴 Auto-deliver / manual-execute (HARD kural):**
   - **İletim otomatik** — dosya zaten burada, okumak/sunmak için Ok onayı gerekmez.
   - **Aksiyon manuel** — handoff'un içindeki iş/karar UYGULANMADAN önce Ok'un açık onayı şart. CCD okur + Ok'a sunar; kendi başına aksiyon almaz.
4. **Benimse + kaydet:** Ok onaylayıp uygulanınca:
   - Dosyanın `status:`'ünü `benimsendi YYYY-MM-DD` yap.
   - `wiki/log.md`'ye kısa girdi (hangi handoff, ne benimsendi).
   - Kalıcı bir kural olduysa CLAUDE.md'ye pointer eklemeyi öner.

## Sınır

- Bu klasör **gelen kutusudur** — buradan dışarı mesaj GÖNDERİLMEZ. Bu vault sadece kendi dosyalarına yazar (vault boundary HARD kuralı).
- Bu vault'u ilgilendirmeyen bir handoff gelirse: silme, `status`'e "bu vault kapsamı dışı — kayıtlı" not düş, log'a bir satır.

## İlişkili
- `.claude/commands/start.md` — açılışta handoff taraması
- `ajan-politikasi-1.md` (vault kökü) — daha önce gelmiş bir vault-üstü kural örneği
