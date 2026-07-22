---
last_updated: 2026-07-22
purpose: LLM-wiki bakım şeması (ingest / query / lint)
---

# wiki/ Şeması — LLM'e Talimat

> Bu dosya, `wiki/`'yi disiplinli bir bilgi tabanı olarak nasıl işleteceğini söyler.
> **Sen (LLM) yazarsın, Ok okur.** Ok kaynak getirir + soru sorar; sen özetler, çapraz-referanslar, dosyalarsın.
> Ana `CLAUDE.md` şişmesin diye workflow buraya ayrıldı (token-ekonomi / MD-bloat koruması — bkz. `@karpathy`).

## Domain

**YBF (Gerçeklik Tanımı) reward-sinyali RL deney programı.** Kaynaklar `../ybf_toy/*.md`, `../Raw/`, `../ybf_toy/results/`. Bunlar **değişmez** — okunur, düzenlenmez.

## Katmanlar

| Katman | Konum | Kim yazar |
|---|---|---|
| Ham kaynak | `../ybf_toy/`, `../Raw/`, `../results/` | Ok / dış ajanlar (değişmez) |
| Wiki | `wiki/` (bu klasör) | **Yalnız LLM** |
| Şema | bu dosya | Ok + LLM birlikte evriltir |

## Sayfa tipleri

- `sources/<kaynak-adı>.md` — bir ham kaynağın özeti. Frontmatter: `source: <yol>`, `ingested: <tarih>`.
- `entities/<ad>.md` — somut şey (model, agent, dataset, anayasa). "Nedir + rolü + bulgular".
- `concepts/<ad>.md` — kavram/mekanizma/bulgu (flip-eval, plato, veto…). "Tanım + kanıt + çıkarım".
- `synthesis.md` — evrilen tez. Program bir bütün olarak **neyi kanıtladı / neyi kanıtlamadı**.
- `index.md` — içerik kataloğu (her sayfa + tek satır özet). Her ingest'te güncellenir.
- `log.md` — kronolojik kayıt (ingest/query/lint). En yeni üstte.
- `hot.md` — anlık durum (Karpathy pattern'inde yok; oturum ritüeli için korunur).

## Konvansiyonlar

- **Dosya adı:** kebab-case, Türkçe/sade (`olcek-asimetrisi.md`). ASCII tercih (aksan yok) → link kırılmasın.
- **Çapraz-referans:** `[[sayfa-adı]]` (uzantısız). Henüz olmayan sayfaya link vermek serbest — açılacak sayfayı işaretler.
- **Atıf zorunlu:** her iddia kaynağına bağlanır — `(kaynak: [[YBF2-vault-tam-rapor-2026-06-11]])`.
- **Kısa tut:** her sayfa tek konu, ~15-30 satır. Şişerse böl. Tekrar etme, linkle.
- **Frontmatter:** `tags`, `updated`, (source sayfasında) `source`+`ingested`.

## Operasyon: INGEST

Ok bir kaynağı işaret edince:
1. Kaynağı oku, Ok'la ana çıkarımları konuş.
2. `sources/`'a özet sayfası yaz.
3. İlgili `entities/` + `concepts/` sayfalarını **güncelle veya oluştur**. Çelişki varsa **bayrakla** (eski iddiayı silme, "X kaynağı bunu şöyle güncelledi" diye not düş).
4. Gerekirse `synthesis.md`'yi revize et.
5. `index.md`'yi güncelle, `log.md`'ye girdi ekle (`## [tarih] ingest | <kaynak>`).
6. Tek kaynak tipik olarak 8-15 sayfaya dokunur.

## Operasyon: QUERY

Ok soru sorunca:
1. Önce `index.md` oku → ilgili sayfaları bul → oku.
2. Atıflı sentez yanıt ver.
3. **Çıktı formatı soruya göre:** md sayfası (varsayılan) · Marp slide (`marp: true` frontmatter) · matplotlib görsel (`data/` altına PNG) · karşılaştırma tablosu. Obsidian'da görüntülenebilir olsun.
4. **Değerli yanıtları wiki'ye geri dosyala** (yeni concept/karşılaştırma sayfası + index + log). Sohbette kaybolmasın — keşifler kaynaklar gibi "birikir".

## Operasyon: LINT

Ok "sağlık kontrolü" deyince: çelişkiler · bayat iddialar (yeni kaynak geçersiz kıldı mı) · orphan sayfalar (gelen link yok) · kendi sayfası olmayan önemli kavramlar · eksik çapraz-referanslar · web araması ile kapatılabilecek veri boşlukları. Bulguları `log.md`'ye yaz, Ok'a yeni soru/kaynak öner.

## Ölçek büyünce (henüz gerek yok — yön işareti)

Karpathy'nin pratik yazısından, ~20 sayfada gerekmeyen ama büyüdükçe gelecek araçlar:
- **CLI arama motoru** (ör. `qmd` — BM25+vektör, on-device). Index.md ~100 sayfaya kadar yetiyor; sonrası için LLM'e CLI tool olarak verilir.
- **Sentetik veri + fine-tuning:** wiki büyüyünce içeriği ağırlıklara yazma. Bu vault için **özel ilgi**: YBF zaten fine-tuning deniyor ([[dpo-kestirmesi]]/[[olcek-asimetrisi]]) → wiki, DPO/PPO veri kaynağı olabilir. Meta-döngü.
- **Dataview** (Obsidian): frontmatter'dan dinamik tablo. Sayfalar `tags`/`updated`/`source_count` taşıyor — hazır.
