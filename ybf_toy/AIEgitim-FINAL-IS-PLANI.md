# 🔒 FINAL İŞ PLANI — DONDURULDU (2026-06-10)

**Program kimliği (kabul edilen strateji):** Kendi LLM'imizi yapmıyoruz. Bu program, mevcut güçlü modeller üzerinde **HİZALAMA** (constitutional YBF) ve **HALÜSİNASYON-AZALTMA** kanıtlarını tamamlayıp **yayına** taşıyan bir doğrulama programıdır. (YBF-Judge damıtımı = Kademe-2 kararı, bu planın dışında.)

## DONDURMA KURALI
1. Yeni fikir / yeni veri / danışman önerisi → **BEKLEME HAVUZU'na yazılır** (bu dosyanın sonu), plan bitince değerlendirilir.
2. Plan sırası DEĞİŞMEZ; istisna: (a) bir adım fiilen imkânsızlaşırsa, (b) Gökhan açıkça değişiklik isterse.
3. Her adım bitince master tabloya işlenir + commit; sonra SIRADAKİ adım.

---

## SIRA (kim · maliyet · kapı)

| ADIM | İş | Kim | Maliyet | Çıktı/Kapı |
|---|---|---|---|---|
| **0** | reality_v2 Pro eval (uçuşta) → ablasyon 4. çift | CCD | ~$0.5 | ablasyon tablosu 4/4 |
| **1** | **İsim-değiştirme mührü** (Freedom→Option-Generation, Gemini) | CCD | ~$0.3 | paradigma-çarpışması hipotezi kapanır |
| **2** | **Plato analizi** — 80GB öğe-listeli çıktı GELDİĞİNDE işlenir; gelmezse muhafazakâr ifadeyle kapatılır. Diğer adımları BLOKLAMAZ | Gökhan(çıktı)+CCD | $0 | açık-model hattı RESMEN kapalı |
| **3** | **Boundary v2** yazımı (scope kapısı önerili) → kurulum + relabel + Pro eval | **GÖKHAN**+CCD | ~$1.5 | v2 cetveli 5/5; ablasyon 5. çift |
| **4** | **v2-FAZ B** (beşli v2 anayasası, 5 eksen) + **türetme-v2** | CCD | ~$9 | v1-vs-v2 sistem kıyası + türetme-ablasyonu (Gökhan'ın istediği) |
| **5** | **Türetme hâkimliği** — 12 kavram vs kanonik tablolar (v1+v2 çıktıları birlikte) | **GÖKHAN** | $0 | "eksenler üretkendir" skoru |
| **6** | **B4 teyidi n=300** (Flash, aynı protokol) | CCD | ~$2 | halüsinasyon bulgusu yayın-kalitesi |
| **7** | **B1 kalite deneyi** (yanıt-düzeyi 5-eksen scorer + genişleme seti; Anlam İlkesi şartnamesi) + **B2/B3 bedava sayaçlar** (token/latency log) | CCD | ~$5 | değer önermesinin kalbi + "hizalamanın bedeli" sayıları |
| **8** | **Çekimser-cevaplı yeni-nesil eval pilotu** (üretimsel format; "ikisi de ihlalli" = puanlanabilir doğru cevap; çapraz-veto ground-truth hazır) | CCD | ~$3 | Tespit İlkesi'ne uygun eval formatının ilk verisi |
| **9** | **Sonnet 3 boş eksen** (Dignity/Respect/Freedom) + cross-frontier tablo tamamlama | CCD | ~$1 | 1 Tem (key reset) — takvim kapısı |
| **10** | *(ops.)* Kalibrasyon-tezi ikilileri (Reality→Boundary, Boundary→Freedom) | CCD | ~$2 | zaman kalırsa; yoksa HAVUZ'a |
| **11** | **SENTEZ + YAYIN:** master sentez → white paper v0.5 → **arXiv preprint** (endorsement süreci; gecikirse Zenodo v2 köprüsü) + Edison güncelleme + YBF-1 mühür (#32) | CCD taslak + **GÖKHAN onay** | $0 | **KADEME 2 KARAR TOPLANTISI** |

**Toplam tahmin:** ~$20-25 · ~2-3 hafta (Boundary v2 + 1 Tem key + hâkimlik tempo belirler).
**Gökhan'ın 3 girdisi:** Boundary v2 metni (ADIM 3) · türetme hâkimliği (ADIM 5) · ADIM 11 onayı. (+ 80GB çıktısı gelirse yapıştırma.)

---

## KADEME 2 MENÜSÜ (plan bitince, o gün karar)
(a) **YBF-Judge damıtımı** — kendi yargıç modelimiz (12k+ etiket hazır; DPO-yasağının dışında: denetimli sınıflandırma)
(b) **Ürünleşme** — karar-destek katmanı (anayasa + frontier API; B1/B4 kanıtlı)
(c) **Lab teması** — türetme + anayasa + metodoloji paketiyle (arXiv görünürlüğü sonrası)

---

## BEKLEME HAVUZU (dondurma sonrası gelenler buraya)
- 32B-4bit satırının kalanları (boundary/dignity/respect/freedom) — elendi, biterse bonus kayıt
- Yeni model kıyasları (GPT-4o/Llama/Mistral) — kapalı (negatif alan #3)
- Eksen v3 taslakları — kapalı (negatif alan #4)
- İsim-testi uzantıları (diğer eksenlerde rename), B4 başka benchmark'ta, hâkim-belirsizlik aracı
- (buraya eklenir...)

---

## DANIŞMAN BRİFİNGİ (strateji-Claude'a yapıştırılacak blok — güncel fotoğrafla)

> **YBF programı — güncel durum (2026-06-10 gecesi) ve FINAL plan onayı istiyoruz.**
> Tamamlananlar: FAZ A 5/5 (Gemini-Pro tek-eksen: Freedom 64→Dignity 81, ağırlıklı %77.7, 188 flip) · **FAZ B birleşik+veto YAPILDI** (61.7 vs 77.7; düşüş çapraz-veto analiziyle mekanik açıklandı: flip'lerin %70-90'ında iki seçenek de kardeş-eksenden −1) · B4 halüsinasyon: Flash 84→92 (+8pp, hata yarılanması), Pro tavanda · ölçek: 7B 45 → 14B 58 → **32B-bf16 58 (doygunluk kanıtlandı)** → Gemini 77 → Sonnet 87 · def-ablasyonu 4 çift (stil sistematik fark yaratmıyor; ama şişkin tanım küçük modeli zehirliyor: Freedom v1 −14.3 → v2 0.0; "tanım tabanı, kapasite tavanı belirler") · türetme deneyi: 12 kavram 5 eksenden türetildi (hâkimlik bekliyor) · Reality flip dökümü: Pro plain %25.8 → anayasa %74.2, 0 bozma · 4 tasarım ilkesi mühürlü (Aydınlık/Tespit/Anlam/Çekimserlik).
> **FINAL plan (donduruldu):** 0) reality_v2 eval → 1) Freedom isim-mührü → 2) plato analizi (çıktı gelince) → 3) Boundary v2 → 4) v2-FAZ B + türetme-v2 → 5) türetme hâkimliği → 6) B4 n=300 → 7) B1 kalite (+token/hız sayaçları) → 8) çekimser-cevaplı eval pilotu → 9) Sonnet 3 eksen (1 Tem) → 10) ops. kalibrasyon ikilileri → 11) **sentez → arXiv** → Kademe-2 kararı (judge-damıtım/ürün/lab).
> **Üç soru:** (1) Sıralamada hata var mı? (2) arXiv için bu listeden ÇIKARILABİLECEK bir şey var mı? (3) arXiv hakemliği/görünürlüğü için listede OLMAYAN kritik bir eksik var mı?
