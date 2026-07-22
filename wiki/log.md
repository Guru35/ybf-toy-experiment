# AI Eğitim — Oturum Log

> Append-only oturum geçmişi. En yeni **üstte**. Her `@done`'da bir girdi eklenir.
> Anlık durum için `wiki/hot.md`'ye bak. Operasyonel/teknik geçmiş `ybf_toy/LESSONS.md`'de.

---

## [2026-07-22] ingest | YBF-1/raw + Dropbox/Public çok-kaynak tarama → 6 yeni sayfa

- **Kapsam:** Ok "wiki+Raw+Drive+YBF-1+Public derinlemesine tara, ingest edilmemişlerden makale üret" dedi (ajan yok, token-ekonomik). Public = Dropbox/Public olarak netleşti.
- **Kaynak taraması:** AI-Egitmek/Raw (~25 MD), YBF-1/raw (106 dosya), YBF-1/wiki (ayrı), Google Drive (YBF-tam-kitap, Bilinç Kuramı vb.), Dropbox/Public (YBF 5-eksen dörtlü-tabloları + kitap + white-paper). Boşluk analizi: mevcut wiki "5 eksen" diyor ama **eksenleri tanımlamıyor**; teori tarafı (matematiksel model, evrimsel zemin, ölçülebilir bilinç, bariyer, yığılmalı transfer) wiki'de yoktu.
- **Yazılan 6 sayfa:** `entities/bes-eksen` · `concepts/matematiksel-model` · `concepts/evrimsel-zemin` · `concepts/olculebilir-bilinc` · `concepts/bariyer-fonksiyonu` · `concepts/yigilmali-transfer`. index + synthesis (source_count 6→10) güncellendi.
- **En değerli bulgular:** (1) bariyer fonksiyonu = veto'yu gradient-mask yapmak → standart axial'in dataset-bias'ını YBF reward'a çeviriyor (Test 6). (2) ölçülebilir-bilinç, flip-eval'ı etkin-rank çöküşü teorisine bağlıyor. (3) yığılmalı-transfer: Güven → olası 6. boyut (zamansallık).
- **Açık uç:** kaynak atıfları wiki-içi `sources/` sayfasına değil ham dosya yoluna verildi (token-ekonomi; SCHEMA'nın "her kaynak sources/'a" idealinden sapma — istenirse 5 source sayfası eklenebilir). Public'teki diğer 4 eksen dörtlü-tablosu (Onur/Saygı/Sınır/Özgürlük) okunmadı, bes-eksen'de linklendi. Ingest kuyruğunda white-paper v03 + veto-döngü + üç-sistem-rolleri kaldı.

## [2026-07-22] Oturum kapanışı | @karpathy + ölü-import temizliği + SMH sınırı

- **Yapıldı:**
  - @karpathy denetim → 1 tek-kaynak ihlali (`ybf_toy/CLAUDE.md` bayat "Aktif State" bloğu) düzeltildi → hot.md pointer'ı.
  - Kod optimizasyon taraması (2 alt-ajan): 5 yakın-kopya küme + ~20 ölü import raporlandı.
  - Ölü import temizliği: **13 dosya, 3 commit** (`aa1c439` 12 dosya + `46fe233` ybf_ppo_train + `a249602` karpathy). Hepsi `py_compile` ✓, davranış/reproducibility etkilenmedi.
- **Karar:**
  - Refactor birleştirmeleri (multijudge/relabel/main_axial, ~150-450 satır) **yapılmadı** — tek-kullanımlık deney scriptleri, çalıştırıp eşdeğerlik doğrulanamıyor (API+cache+budget), reproducibility riski > kazanç.
  - "Haber/makale üret" talebi → **SMH'nin işi** (`~/Documents/SosyalMedyaOrg/`), bu vault değil. Çift-taraflı vault-sınırı gereği buradan üretilmedi; Ok SMH oturumunu açacak.
- **Açık uç:**
  - Commit'ler yerel, **push edilmedi**.
  - Refactor birleştirme adayları istenirse yapılabilir (deney-scripti reproducibility'si dikkat ister).
  - Önceki oturumların wiki-ingest işi (`hot.md`/`index.md` M + `sources/concepts/entities` untracked) hâlâ commit bekliyor — ayrı iş.

---

## [2026-07-22] karpathy-denetim | 1 tek-kaynak ihlali, kalan temiz

- **Token ekonomisi:** ✓ temiz. En büyük dosya LESSONS.md (253) / RUNBOOK (194) — hepsi <300. Karpathy kaynakları (`Katpathy LLM Wiki.md` + X-Post) yerinde, immutable. Pipeline reproducible.
- **MD-bloat:** ✓ temiz. Hiçbir dosya 400+ değil. wiki sayfaları granüler (17–44 satır) — "one page one concept" ideali tutuyor.
- **Tek-kaynak ihlali (1):** `ybf_toy/CLAUDE.md` hâlâ tam bir **"Aktif State (2026-06-08)"** bloğu taşıyor (Cache/Latest winner/Scoring/Budget) — root `CLAUDE.md` bu state'i `wiki/hot.md`'ye taşıyıp "tek yerde" demiş ama alt-dizin kopyası geride kalmış. Aynı state şu an 2 yerde (hot.md + ybf_toy/CLAUDE.md), duplike + bayat tarihli.
  - **Öneri (Ok onayı bekliyor):** `ybf_toy/CLAUDE.md`'deki Aktif State bloğunu root CLAUDE.md gibi tek satırlık hot.md pointer'ıyla değiştir. Üç-Tehlikeli-Operasyon + Environment blokları kalsın (onlar operasyonel, state değil).
- **Handoff:** Karpathy/LLM-wiki metodolojisiyle ilgili yeni handoff yok (tek dosya site-görünürlük, alakasız).

---

## [2026-07-22] Oturum kapanışı | Karpathy LLM-wiki TAM kuruldu

- **Yapıldı:** Ok'un verdiği iki Karpathy dokümanıyla (fikir dosyası + pratik yazı) `wiki/` bu vault'ta eksiksiz kuruldu. Oturum-iskeleti (hot/index/log) üzerine büyütüldü — üzerine yazılmadı. 26 sayfa, 6 kaynak ingest, 4 operasyon (ingest/lint/query+filing/output-format) çalışır.
- **Karar:** Wiki bu vault'ta yaşayacak — deney-wiki'si vault'un doğal çıktısı ("deney çalıştır + raporla" ile uyumlu). Ingest stratejisi: denetimli seri (Ok "sen seç" → CCD sürücü).
- **Açık uç (2 lint bulgusu, çözülmedi):**
  1. Dignity ekseni türetimde 5 farklı adla (Haysiyet/Onur/Vakar/Değer/İtibar) — hâkimlik öncesi normalize.
  2. Gemini-Pro Reality sayı tutarsızlığı: flip-dump %74.2 (23/31) vs master %77.4 (24/31) — öğe-düzeyi kıyas gerek.
- **Bellek:** `project-llm-wiki` memory yazıldı/güncellendi (gelecek oturum önce `wiki/SCHEMA.md` okusun).

---

## [2026-07-22] lint + query | wiki sağlık kontrolü + ilk Q&A demo

- **Lint:** 25 sayfa, **0 kırık link, 0 orphan** ✓. Hub'lar: bes-eksen-veto (13 gelen link), synthesis/flip-eval (12), plato (10). 2 tutarsızlık bayraklandı (bkz. üstteki ingest girdisi) — silinmedi, not düşüldü.
- **Query demo:** "YBF neden fine-tuning'i bırakıp Constitutional'a geçti?" → 5 sayfadan sentezlendi → yeni `concepts/ft-vs-constitutional` olarak **geri-dosyalandı** (Karpathy filing-back). Böylece Q&A operasyonu + compounding kanıtlandı.
- **Durum:** 4 operasyon da çalışır (ingest ✅ · lint ✅ · query+filing ✅ · output-formatları SCHEMA'da tanımlı). Kurulum **tam**.

---

## [2026-07-22] ingest | Master + F15-PPO + Reality Flip Dump (3 kaynak) — kaynak tarafı tükendi

- **Yapıldı:** "Tam kur" hedefi — çekirdek YBF-domain kaynakları ingest edildi. SCHEMA tamamlandı (output formatları + "Ölçek büyünce" bölümü: CLI-search / sentetik-veri-FT / Dataview).
- **3 kaynak → 5 yeni + 6 güncelleme:**
  - Yeni: `sources/ybf-test-results-master` · `sources/ybf-f15-ppo` · `sources/reality-flip-dump` · `concepts/acik-model-emekliligi` (L kararı + 5 ders) · `entities/reality-flip-bankasi` (31 somut flip).
  - Güncellenen: `plato-kapasite-esigi` (gradient↔plato nüansı) · `kapasite-hatti` (anayasa Δ tablosu) · `flip-eval` (banka linki) · `dpo-kestirmesi`/`olcek-asimetrisi` (teknik kaynak) · `synthesis` (source_count 3→6, emeklilik).
- **Lint bulguları yakalandı (çözülmedi, bayraklandı):**
  1. **Sayısal tutarsızlık:** Gemini-Pro Reality → `reality-flip-dump` %74.2 (23/31) vs `master` %77.4 (24/31). Bir öğe farkı, koşu-varyansı olası. Not `flip-eval` + `reality-flip-dump`'a düşüldü.
  2. **Plato anlatısı:** master'da 2× revize (gradient→plato→gradient). Nihai hal `plato-kapasite-esigi`'ye yazıldı (7B↔14B gradient, 14B↔32B plato).
- **Kuyruk:** çekirdek tükendi; Raw/ ek raporları gerekince.

---

## [2026-07-22] ingest | Türetme Deneyi + Anthropic Anayasası Kıyası (2 kaynak)

- **Yapıldı:** Denetimli seri ingest, 2. tur. İki yüksek-değerli kaynak işlendi.
- **Kaynak 1 — `AIEgitim-turetme-deneyi.md`:** 5 sayfaya dokundu → `sources/ybf-turetme-deneyi` + yeni entity `turetilmis-kavramlar` (12 kavram tablosu: Sevgi→Liyakat) + `concepts/turetme-deneyi` güncellendi (türetim ✅ tamam → hâkimlik bekliyor).
- **Kaynak 2 — `AIEgitim-ybf-vs-anthropic-anayasa.md`:** yeni boyut → `sources/ybf-vs-anthropic-anayasa` + yeni concept `ybf-vs-anthropic` (bağımsız örtüşme = dışsal tutarlılık). `synthesis` güncellendi (source_count 1→3).
- **Lint adayı yakalandı:** türetimde Dignity ekseni 5 farklı Türkçe adla geçiyor (Haysiyet/Onur/Vakar/Değer/İtibar) → hâkimlik öncesi normalize edilmeli. Not `turetme-deneyi` + `turetilmis-kavramlar`'a düşüldü.
- **Kuyruk:** `test-results-master` · `F15-ppo` · `flip_dump_reality_model` (mevcut concept'lerle örtüşme yüksek → ayrı tur).

---

## [2026-07-22] ingest | YBF2 Deney Programı Tam Raporu (2026-06-11)

- **Yapıldı:** Karpathy LLM-wiki pattern'i bu vault'ta instantiate edildi. Mevcut oturum-iskeleti (hot/index/log) üzerine wiki katmanı büyütüldü.
- **Kurulan yapı:** `SCHEMA.md` (ingest/query/lint kuralları) + `sources/ entities/ concepts/` dizinleri + `synthesis.md`.
- **İlk ingest — tek kaynak:** `ybf_toy/YBF2-vault-tam-rapor-2026-06-11.md` → 13 sayfaya dokundu:
  - source özeti + synthesis + 8 concept (bes-eksen-veto, flip-eval, olcek-asimetrisi, dpo-kestirmesi, plato-kapasite-esigi, tanim-ablasyonu, turetme-deneyi, halusinasyon-faydasi, muhurlenen-ilkeler) + 1 entity (kapasite-hatti).
  - `index.md` katalog formatına evrildi (hot/log korundu).
- **Korundu:** `hot.md` + eski ritüel log girdisi + `../CLAUDE.md` (dokunulmadı).
- **Açık uç:** Kuyrukta 5+ kaynak (index'te listeli). Pattern onaylanınca tek tek ingest edilir. Query yanıtları da wiki'ye geri dosyalanacak.

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
