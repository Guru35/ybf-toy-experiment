# AI Eğitim — İçerik Kataloğu

> Wiki'nin kataloğu. Anlık durum: [`hot.md`](hot.md) · oturum geçmişi: [`log.md`](log.md) · bakım kuralları: [`SCHEMA.md`](SCHEMA.md).
> Query'de önce burayı oku → ilgili sayfaya in.

## Kimlik
YBF (Gerçeklik Tanımı) reward-sinyali RL deney vault'u. Üç-vault sisteminin **deney** tarafı. Detay: [`../CLAUDE.md`](../CLAUDE.md).

## Sentez
- [`synthesis`](synthesis.md) — evrilen tez: YBF RL neyi kanıtladı / neyi kanıtlamadı.

## Kavramlar (`concepts/`)
- [`bes-eksen-veto`](concepts/bes-eksen-veto.md) — 5 eksen + veto çekirdeği; anayasa frontier'da +48pp, 0 bozma.
- [`matematiksel-model`](concepts/matematiksel-model.md) — durum uzayı {-1,0,+1}^5, veto=-5, duygular tablosu, çapraz-doğrulama.
- [`evrimsel-zemin`](concepts/evrimsel-zemin.md) — duygular seçildi; RGB/DNA analojisi; his vs duygu; manipülasyon dayanıklılığı.
- [`olculebilir-bilinc`](concepts/olculebilir-bilinc.md) — süreç ontolojisi (Whitehead/Rovelli) → negentropi → etkin rank; flip-eval'ın teorik zemini.
- [`bariyer-fonksiyonu`](concepts/bariyer-fonksiyonu.md) — Test 6: veto=gradient mask; standart axial dataset-bias, bariyer ~simetrik YBF reward. Çift-seviye fidelity gap.
- [`yigilmali-transfer`](concepts/yigilmali-transfer.md) — sıra deneyi; Gerçeklik özel eksen (13 vs 1 tur); Güven → 6. boyut (zamansallık) adayı.
- [`flip-eval`](concepts/flip-eval.md) — çatışma testi; gerçek değeri proxy'den ayıran tek ölçüt.
- [`olcek-asimetrisi`](concepts/olcek-asimetrisi.md) — F-15: RL bilmeyene öğretir (135M), bileni bozar (0.5B).
- [`dpo-kestirmesi`](concepts/dpo-kestirmesi.md) — F-16: içsel +38pp / davranış Δ0; kestirme öğrenimi.
- [`plato-kapasite-esigi`](concepts/plato-kapasite-esigi.md) — 32B doygunluk; tam YBF frontier şart.
- [`tanim-ablasyonu`](concepts/tanim-ablasyonu.md) — v1/v2 tanım, scope kapısı, isim-mührü (12/12 aynı).
- [`turetme-deneyi`](concepts/turetme-deneyi.md) — "5 eksen üretkendir"; türetim ✅, 🟡 hâkimlik bekliyor (yayın kapısı).
- [`halusinasyon-faydasi`](concepts/halusinasyon-faydasi.md) — B4: TruthfulQA +8pp, hataların %50'si; ilk fayda.
- [`muhurlenen-ilkeler`](concepts/muhurlenen-ilkeler.md) — Aydınlık/Tespit/Anlam/Çekimserlik tasarım ilkeleri.
- [`ybf-vs-anthropic`](concepts/ybf-vs-anthropic.md) — Claude Anayasası kıyası; bağımsız örtüşme = dışsal tutarlılık.
- [`acik-model-emekliligi`](concepts/acik-model-emekliligi.md) — 7B/14B/32B hattı emekliye ayrıldı + 5 kalıcı ders (L kararı).
- [`ft-vs-constitutional`](concepts/ft-vs-constitutional.md) — 🔍 query-türevi: yöntem kararının tam gerekçesi (FT neden kapandı).

## Varlıklar (`entities/`)
- [`bes-eksen`](entities/bes-eksen.md) — 5 eksenin tanımı + türetme zinciri (Gerçeklik→Sınır→Onur→Saygı→Özgürlük) + dörtlü VAR/YOK tablosu.
- [`kapasite-hatti`](entities/kapasite-hatti.md) — 135M→Sonnet test edilen modeller + Reality flip + anayasa Δ tablosu.
- [`turetilmis-kavramlar`](entities/turetilmis-kavramlar.md) — 12 türetilmiş kavram tablosu (Sevgi→Liyakat) + taban-kontrolü.
- [`reality-flip-bankasi`](entities/reality-flip-bankasi.md) — 31 somut Reality flip (nezaket-vs-gerçek örnekleri).

## Kaynaklar (`sources/`)
- [`ybf2-vault-tam-rapor-2026-06-11`](sources/ybf2-vault-tam-rapor-2026-06-11.md) — program tam raporu (ilk ingest).
- [`ybf-turetme-deneyi`](sources/ybf-turetme-deneyi.md) — 5 eksenden 12 kavram türetimi (gemini-2.5-pro).
- [`ybf-vs-anthropic-anayasa`](sources/ybf-vs-anthropic-anayasa.md) — YBF v2 ↔ Claude Anayasası kıyası.
- [`ybf-test-results-master`](sources/ybf-test-results-master.md) — konsolide master sonuç listesi (A→L).
- [`ybf-f15-ppo`](sources/ybf-f15-ppo.md) — F-15/F-16 teknik raporu (PPO/DPO/Constitutional).
- [`reality-flip-dump`](sources/reality-flip-dump.md) — 31 Reality flip tam dökümü (gemini-2.5-pro).

## Ham kaynak hattı (wiki dışı, değişmez)
- Deney kodu + raporlar: `../ybf_toy/` · gelen kutu: `../Raw/` · JSON özetleri: `../ybf_toy/results/`
- Operasyon: `../ybf_toy/RUNBOOK.md` · debug/mimari: `../ybf_toy/LESSONS.md`

## Henüz ingest edilmemiş (kuyruk)
2026-07-22'de YBF-1/raw + Dropbox/Public teori+deney kaynakları ingest edildi (6 sayfa: bes-eksen, matematiksel-model, evrimsel-zemin, olculebilir-bilinc, bariyer-fonksiyonu, yigilmali-transfer). Kalan adaylar: white-paper v03 (287 satır), veto-döngü-evrim tartışması, ikinci-katman-türetme, üç-sistem-rolleri, maliyet/embedding raporları, Public'teki diğer 4 eksen dörtlü-tablosu (Onur/Saygı/Sınır/Özgürlük). Nuremberg/kitap senaryoları deney-wiki'sine uzak.
