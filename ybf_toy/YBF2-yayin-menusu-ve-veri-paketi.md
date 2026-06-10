# YBF2 — YAYIN MENÜSÜ + VERİ PAKETİ (Vault CCD'si için)

**Tarih:** 2026-06-11 · **Amaç:** Zenodo/OSF'de yayınlanabilecek makale adaylarının tam menüsü — her aday için iddia, destekleyen veri (içeride), güç analizi, eksikler. Vault'ta yazım için yeterli malzeme bu dosyada + kaynak haritasında.
**Yayın altyapısı:** Zenodo (DOI 10.5281/zenodo.20599906 concept-DOI mevcut — v2 olarak eklenir) + OSF Preprints aynası (davetiyesiz). arXiv: endorsement bulunursa bonus.

---

# BÖLÜM I — VERİ PAKETİ (tüm sonuçlar, tek yerde)

## V1. Fine-tuning deneyleri
| Deney | Sonuç |
|---|---|
| PPO, SmolLM-135M (3 seed) | OOD %24 → %72/%72/%68 — şans-altından öğrendi ✅ |
| PPO, Qwen-0.5B (lr 4e-6 / 1e-6) | %68→%48 guard · %76→%16 ÇÖKÜŞ ❌ |
| DPO nazik / güçlü (0.5B) | ID logprob 46.5→53.5 / **84.5 (+38pp)**; OOD davranış **Δ0 / Δ0** |
| Flip-eval, DPO sonrası | %48.4 → **%35.5 (−12.9pp)** — kestirme kanıtı (eğitim verisinin %97.6'sı YBF=konvansiyon) |

## V2. Constitutional — frontier (tek-eksen, FAZ A)
| Eksen | flip n | Gemini-Pro | Sonnet 4.5 |
|---|---|---|---|
| Gerçeklik | 31 | %77.4 | **%87.1** |
| Sınır | 47 | **%80.9** | %70.2 |
| Onur | 64 | %81.2 | — |
| Saygı | 32 | %71.9 | — |
| Özgürlük | 14 | %64.3 | — |
| **TOPLAM** | **188** | **%77.7** | |
+ Plain'ler şans-altı (Pro Reality plain %25.8; açık modeller %12-33) · anayasa 0 doğru kararı bozdu (15 düzeltme / 0 bozma).

## V3. FAZ B — birleşik+veto & çapraz-veto analizi
| Eksen | FAZ A | FAZ B | Δ | hedef başka-eksenden −1 | konvansiyonel −1 |
|---|---|---|---|---|---|
| Reality | 77.4 | 61.3 | −16.1 | %81 | %90 |
| Boundary | 80.9 | 68.1 | −12.8 | %79 | %81 |
| Dignity | 81.2 | 51.6 | −29.6 | **%89** | %53 |
| Respect | 71.9 | 62.5 | −9.4 | %69 | %69 |
| Freedom | 64.3 | **85.7** | **+21.4** | %50 | **%93** |
Δ'nın yönü veto-farkını izliyor → düşüş model hatası değil, cetvel-gerilimi mekaniği.

## V4. Ölçek eğrisi (Reality, anayasalı) + plato yapısı
7B %45.2 → 14B %58.1 → 32B-4bit %58.1 → **32B-bf16 %58.1 (doygunluk kanıtı)** → Gemini %77.4 → Sonnet %87.1.
14B öğe-yapısı (2 pozisyon-seed): 14 kararlı-doğru + 10 kararlı-yanlış + 7 pozisyon-duyarlı; toplam skor sağlam (58.1↔54.8). 10 kararlı-yanlış = **nezaket-vs-gerçek** vakaları.

## V5. Def-ablasyonu (v1 vs v2) + zehirlenme + isim-mührü
| Eksen | v1 | v2 | Δ |
|---|---|---|---|
| Reality | 77.4 | 84.4 | +7.0 (saf binary etkisi) |
| Dignity | 81.2 | 75.0 | −6.2 |
| Respect | 71.9 | 83.3 | +11.4 |
| Freedom | 64.3 | 83.3 | +19.0 |
+ Küçük-model: dignity çifti v2 lehine (Δ+4.7→+10.0), respect çifti v1 lehine (+18.8→+5.6) → stil küçükte de sistematik değil.
+ **Zehirlenme-tedavi:** Freedom v1 7B/14B'de Δ−14.3 (anayasa ZARAR); v2 Δ0.0 → "tanım TABANI, kapasite TAVANI belirler."
+ **İsim-mührü:** "Freedom"→"Option-Generation": frontier'da **12/12 karar özdeş** — kelime vergisi sıfır.

## V6. B4 — Halüsinasyon (TruthfulQA MC1, n=100, aynı sorular)
Flash: %84.0 → **%92.0 (+8.0pp = hataların %50'si)** · Pro: %92→%93 (tavan). **n=300 teyit koşusu sürüyor.**

## V7. Türetme deneyi
12 kavram yalnız-5-eksenden türetildi (sızıntı ayıklı): tanım + VAR/YOK patolojileri + ±1 + taban-kontrolü. Sevgi örneği kanonikle ~kelime-düzeyi örtüşme. **Hâkimlik bekleniyor (vault).** Taban-bütünlük: incelenen −1'ler temel eksenlere indirgendi.

## V8. Destekleyici
Multi-judge %100 uyum (Sonnet↔Haiku, 20 trap) · cross-model flip doğrulaması (%87) · 4 tasarım ilkesi (Aydınlık/Tespit/Anlam/Çekimserlik) · Anthropic anayasa kıyası (örtüşme+ayrışma haritası) · 9 cetvel ≈ 10.800 etiketli eylem + 250 flip (v1+v2).

---

# BÖLÜM II — MAKALE MENÜSÜ (7 aday, güç sırasıyla)

## M1 ⭐ ANA MAKALE — "Öğretme vs Uygulatma: Bir Felsefi Değer Çerçevesinin Dil Modellerinde Ölçek-Asimetrisi, Kestirme Öğrenme ve Anayasal Yol"
*(EN: Teaching vs Applying a Philosophical Value Framework: Scale Asymmetry, Shortcut Learning, and the Constitutional Path)*
- **İddia:** Değer çerçevesi küçük modele RL ile öğretilebilir ama bileni bozar (F-15); DPO proxy öğrenir (F-16); kullanılabilir yol = frontier+anayasa (FAZ A %77.7); yetenek kapasite SINIFI ile gelir (V4 doygunluk).
- **Veri:** V1+V2+V4 (+V8 doğrulamalar).
- **Güç:** ⭐⭐⭐⭐⭐ — programın omurgası; Edison ön-incelemesinde ölçek-asimetrisi+proxy bulguları "literatürde karşılığı sorulmaya değer" çıktı.
- **Eksik:** yok — bugün yazılabilir. (ADIM 11 sentezinin kendisi.)
- **Mecra:** Zenodo v2 + OSF; arXiv cs.CL/cs.AI (endorsement gelirse).

## M2 ⭐ METODOLOJİ — "Çatışma Değerlendirmesi (Flip-Eval): Değer-Hizalamada Proxy Öğrenmeyi Yakalamak"
- **İddia:** Değer, eğitim verisinde ucuz bir korelatla örtüştüğünde optimizasyon korelatı öğrenir; bunu yalnız ÇATIŞMA vakaları yakalar. Yöntem: relabel→flip çıkarımı→judge≠policy→plain-şans-altı geçerlilik kanıtı.
- **Veri:** V1 (DPO −12.9), V2 plain'ler, V4 öğe-yapısı, 10-sert-flip içerik deseni.
- **Güç:** ⭐⭐⭐⭐⭐ — Edison'un "novel" bulduğu çekirdek bu; alana taşınabilir genel yöntem.
- **Eksik:** yok. M1'den ayrı, kompakt yöntem makalesi olarak güçlü.
- **Mecra:** Zenodo/OSF; arXiv cs.CL.

## M3 ⭐ KISA RAPOR — "Gerçeklik-Ekseni Anayasası Orta-Sınıf Modellerde TruthfulQA Hatalarını Yarılıyor"
- **İddia:** 16k'lık Reality tanımı system-prompt olarak Flash'ın halüsinasyon hatalarını %50 azaltır; frontier'da tavan etkisi (iki-nokta deseni).
- **Veri:** V6 (+n=300 teyidi — KAPI).
- **Güç:** ⭐⭐⭐⭐ — somut, ticari değeri net, kısa "letter" formatı.
- **Eksik:** **n=300 sonucu (ADIM 6, koşuyor)** + tek-benchmark sınırlılığı dürüstçe yazılmalı.
- **Mecra:** Zenodo/OSF; hızlı görünürlük adayı.

## M4 — "Tanım Mühendisliği: Bağlam-içi Değer Hizalamada Taban ve Tavan Etkileri"
- **İddia:** İki iyi tanım stili frontier'da eşdeğer (4 çift); ama şişkin/soyut tanım KÜÇÜK modele aktif zarar verir (zehirlenme −14.3) ve kompakt+scope'lu yeniden-yazım zehri durdurur (0.0); yüklü kelimenin vergisi frontier'da sıfır (12/12 özdeş). **Yasa: tanım kalitesi tabanı, kapasite tavanı belirler.**
- **Veri:** V5 (4 çift + zehirlenme + isim-mührü) + V4 bağlamı.
- **Güç:** ⭐⭐⭐⭐ — prompt-engineering literatürüne özgün katkı ("definition floor effect").
- **Eksik:** Boundary v2 (5. çift) hükmü sağlamlaştırır; onsuz da yazılabilir (n-küçük caveat'larıyla).
- **Mecra:** Zenodo/OSF; arXiv cs.CL.

## M5 — "Tartmadan Veto: Çok-İlkeli Anayasalarda Çapraz-Eksen Girişimi" *(FAZ B makalesi)*
- **İddia:** Veto-mutlak çok-eksen sistemi zorla-A/B'de per-axis skoru düşürür — ama bu cetvel-gerilimi mekaniğidir (çapraz-veto kanıtı), hata değil; çatışma vakalarının çoğunda "kabul edilebilir seçenek yok" doğru cevaptır → değerlendirme formatı ÇEKİMSER-CEVAPLI olmalıdır (Tespit İlkesi). Freedom'un birleşikte +21.4 açılması eksen-bağımlılık zincirinin ("Sınır→Özgürlük") davranışsal izi.
- **Veri:** V3 (+ FAZ A referansı, tasarım ilkeleri).
- **Güç:** ⭐⭐⭐⭐ — alignment-mimarişi tartışmasına özgün katkı; Anthropic'in tartım-yaklaşımına yapısal alternatifin ilk ölçümü.
- **Eksik:** çekimser-pilot verisi (ADIM 8) eklenirse güçlenir; onsuz "tasarım çıkarımı" olarak yazılabilir. Sunum riski: düşüşün doğru çerçevelenmesi şart (danışman uyarısı).
- **Mecra:** Zenodo/OSF.

## M6 — "Etiğin Üretken Tabanı: Beş Eksenden Ahlaki Kavramları Türetmek" *(felsefe amiral gemisi — VAULT'UN DOĞAL MAKALESİ)*
- **İddia:** RGB/DNA analojisi ampirik: yalnız 5 eksen verilen model, 12 kanonik kavramı (sevgi, adalet, güven...) yazarın ayrıştırmalarıyla örtüşür biçimde türetir; türetilmiş her −1 temel-eksen −1'ine indirgenir (taban-bütünlük).
- **Veri:** V7 + hâkimlik skoru (KAPI: ADIM 5, vault işi) + türetme-v2 kolu (ADIM 4 sonrası, opsiyonel güçlendirme).
- **Güç:** ⭐⭐⭐⭐(+) — en özgün felsefi katkı; lab-pitch'inin kartviziti. Hâkimliksiz yayınlanırsa saldırıya açık (danışman uyarısı).
- **Eksik:** **hâkimlik şart**; v2-kolu ve kör-değerlendirme (hâkimliğin bir kısmını üçüncü göz yapsın) güçlendirir.
- **Mecra:** Zenodo + felsefe tarafı için PhilPapers da düşünülebilir.

## M7 — DENEME/BÖLÜM — "İki Anayasa: YBF ve Claude Anayasasının Karşılaştırmalı Mimarisi"
- **İddia:** Eğitim-zamanı karakter (Anthropic) vs çıkarım-zamanı eylem-cetveli (YBF); bağımsız örtüşmeler (anti-çerçeveleme, anti-paternalizm, onur) evrensellik sinyali; ayrışmalar (eksen ayrıştırma, ±1 ölçülebilirlik, sistematik veto, rıza kuralı, insan-olmayan Öteki) tasarım-uzayını tanımlar; "yargı>kural" varsayımı ampirik testte berabere.
- **Veri:** AIEgitim-ybf-vs-anthropic-anayasa.md + V5.
- **Güç:** ⭐⭐⭐ — Kitap 2 bölümü/uzun-form deneme olarak ideal; akademik makaleden çok kamusal-entelektüel metin.
- **Eksik:** yok. **Mecra:** Kitap 2 / blog / Zenodo deneme.

---

# BÖLÜM III — YAYIN STRATEJİSİ ÖNERİSİ

**Sıralama (kanıt-hazırlığına göre):**
1. **Önce M1+M2 birlikte** (ana + metodoloji — birbirine atıf vererek; ikisi de bugün yazılabilir) → Zenodo v2 + OSF.
2. **M3** B4-n300 düşünce hemen (kısa, hızlı görünürlük).
3. **M6** hâkimlik + türetme-v2 sonrası (felsefe amiral gemisi — vault yazar, AI-Eğitim veri sağlar).
4. **M4, M5** Boundary v2 / çekimser-pilot verisiyle güçlenince.
5. **M7** kitapla eşzamanlı.

**Pratikler:** Tek Zenodo concept-DOI altında versiyonlama (mevcut: 10.5281/zenodo.20599905) · CC-BY-4.0 · her makalede repo+veri linki (tekrarlanabilirlik) · caveat'lar gizlenmez (n-küçük, tek-benchmark, hâkim-değişimi, env-varyans ±10pp) — programın güveni dürüstlüğünden geliyor.
**Hakem-savunma notu:** "herhangi bir tanım da işe yaramaz mıydı?" sorusuna karşı plasebo-anayasa kontrolü HAVUZ'da hazır bekliyor (~$3) — M1/M3 yazımında gerek görülürse çekilir.
