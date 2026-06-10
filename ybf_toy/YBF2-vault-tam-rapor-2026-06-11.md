# YBF2 — DENEY PROGRAMI TAM RAPORU (YBF Vault Değerlendirme Kopyası)

**Hazırlayan:** AI Eğitim vault'u (CCD) · **Tarih:** 2026-06-11
**Muhatap:** YBF Vault CCD'si — felsefe/wiki/kitap tarafının değerlendirmesi için, kendi-içinde-bütün rapor.
**Kaynaklar:** github.com/Guru35/ybf-toy-experiment (tüm veri+kod) · ayrıntı dosyaları raporun sonunda.

---

## 0. PROGRAM NEDİR, NEYİ SORDU?

YBF/LCP'nin beş ekseni (Gerçeklik, Onur, Saygı, Sınır, Özgürlük + veto kuralı) dil modellerine **öğretilebilir mi** ve onlar tarafından **uygulanabilir mi**? Üç rejim test edildi: pekiştirmeli öğrenme (PPO), tercih optimizasyonu (DPO), bağlam-içi anayasa (Constitutional). Ölçüm aleti: **flip-eval** — YBF'nin konvansiyonel ahlakla ÇELİŞTİĞİ senaryolar (model YBF'yi mi seçiyor, konvansiyonu mu?). 1200 Moral Stories senaryosu eksen eksen yeniden etiketlendi (hâkim: Haiku/Gemini-Flash; hâkim ≠ test edilen model kuralı her yerde korundu).

**Programın vardığı kimlik:** Kendi LLM yok. Mevcut güçlü modellerde **hizalama + halüsinasyon-azaltma kanıt programı** → yayın.

---

## 1. ANA BULGULAR (kronolojik değil, mantıksal sırayla)

### F-15 — Ölçek asimetrisi: RL bilmeyene öğretir, bileni bozar
Saf-ödül PPO (model tanımı hiç görmez, sadece gizli ±1 ödül): 135M model şans-altından öğrendi (OOD %24→%72, 3 seed replike). Aynı prosedür, değeri zaten kodlamış 0.5B'yi her öğrenme oranında ÇÖKERTTİ. **"Bilgi ≠ kalibrasyon."**

### F-16 — DPO kestirme öğrenir: "düşünce ≠ eylem" + flip-eval'in zorunluluğu
DPO 0.5B'yi korudu ve içsel tercihini +38pp oynattı — ama davranış Δ0. Flip-eval gerçeği gösterdi: eğitim verisinin %97.6'sı YBF=konvansiyon örtüşmeli → model "konvansiyoneli seç" KESTİRMESİNİ öğrendi; çatışmalarda eğitim güçlendikçe KÖTÜLEŞTİ (−12.9pp). **Çıkarım: küçük-model fine-tuning yolu KAPALI; gerçek değer öğrenimini proxy'den ayıran tek test = çatışma (flip) testi.**

### FAZ A — Anayasa 5 eksenin 5'inde çalışıyor (frontier, tek-eksen)
| Eksen | flip n | Gemini-2.5-Pro | Sonnet 4.5 |
|---|---|---|---|
| Gerçeklik | 31 | %77.4 | **%87.1** |
| Sınır | 47 | **%80.9** | %70.2 |
| Onur | 64 | %81.2 | — |
| Saygı | 32 | %71.9 | — |
| Özgürlük | 14 | %64.3 | — |
| **TOPLAM** | **188** | **%77.7** | |

- **Cross-frontier takas:** Reality'de Sonnet>Gemini, Boundary'de Gemini>Sonnet → frontier'ların **YBF-eksen profilleri farklı** (Sonnet sivri, Gemini düz). "En hizalı model" eksen-bağımlı.
- Onur = bilinen pretrained kör nokta (paternalizm) olmasına rağmen anayasayla %81.2 → **anayasa kör noktayı telafi ediyor.**
- Anayasasız frontier bile flip'lerde şans-altı (Pro plain %25.8) → **YBF frontier varsayılanında YOK; anayasa +48pp taşıyor ve hiçbir doğru kararı bozmuyor (0 bozma).**

### FAZ B — Birleşik 5-eksen + veto: düşüş değil, mekanizma
Birleşik anayasa (97k char, veto + karar prosedürü) 188 flip'te %61.7 (tek-eksen %77.7'ye karşı). **Çapraz-veto analizi düşüşü mekanik açıkladı:** flip'lerin %70-90'ında HER İKİ seçenek de bir kardeş-eksenden −1 taşıyor → katı veto altında "kabul edilebilir seçenek yok" → zorla-A/B formatı entegre sistemi temsil edemiyor. Δ'nın yönü veto-farkını izliyor (Dignity hedefleri %89 vetolu → −29.6; Freedom'da konvansiyonel %93 vetolu → **+21.4, tek artan eksen**). **Yorum: FAZ A eksen-kapasitesini, FAZ B bütünleşik-kabul-edilebilirliği ölçer; "kaçırmalar" çoğunlukla bilinçli çok-eksen yargısıdır. Freedom'un birleşikte açılması çerçeve-tutarlı ("Sınır → Özgürlük").**

### Ölçek eğrisi — kapasite SINIFI farkı (açık-model hattı kapanışı)
**Reality flip, anayasalı:** 7B %45 → 14B %58 → **32B %58 (4-bit VE tam-kalite bf16 — birebir aynı: doygunluk kanıtlandı)** → Gemini %77 → Sonnet %87. Aile-içi gradient→plato; frontier'a SIÇRAMA. Öğe-düzeyi analiz: 14B'de 14 kararlı-doğru + 10 kararlı-yanlış + 7 pozisyon-duyarlı öğe; toplam skor pozisyona sağlam. **Ürün sonucu: tam YBF ≤32B açık modelle OLMUYOR; frontier şart.**

### Def-ablasyonu (v1 düzyazı/üçlü vs v2 dedektif/binary) — 4 çift
| Eksen | v1 | v2 | Δ |
|---|---|---|---|
| Reality | 77.4 | 84.4 | +7.0 (saf binary etkisi — stil değişmedi) |
| Dignity | 81.2 | 75.0 | −6.2 |
| Respect | 71.9 | 83.3 | +11.4 |
| Freedom | 64.3 | 83.3 | +19.0 |
- Frontier'da **v2 lehine zayıf-ama-tutarlılaşan eğilim** (3/4, ort +7.8); kesinleşme Boundary v2 (5. çift) ile.
- **Zehirlenme-tedavi çifti:** Freedom v1 (21k, soyut) küçük modeli AKTİF bozuyor (7B ve 14B'de −14.3); v2 (6.7k, scope kapılı) zehri durduruyor (0.0) ama kazanca çeviremiyor. **Yasa: tanım kalitesi TABANI belirler, kapasite TAVANI belirler.**
- **İsim-mührü:** "Freedom" kelimesi "Option-Generation" ile değiştirildi (kavram aynı) → frontier'da **12/12 karar BİREBİR AYNI.** Yüklü kelimenin vergisi frontier'da SIFIR; paradigma-çarpışması etkisi küçük-modele lokalize. **Felsefi ima: YBF-Özgürlük kelimeye muhtaç değil — kavram kendi başına taşıyor.**

### B4 — İlk kanıtlanmış FAYDA: halüsinasyon yarılanması
TruthfulQA MC1 (n=100, aynı sorular): Gemini-Flash plain %84 → +YBF-Reality anayasası **%92** (+8pp = **hataların %50'si yok**; Flash+YBF = Pro-plain seviyesi). Pro'da +1 (tavan etkisi — düzeltilecek hata yok). **n=300 teyit koşusu şu an çalışıyor.** Ürün cümlesi: *YBF-Reality, orta-sınıf modellere fine-tuning'siz, ucuz halüsinasyon-azaltma katmanı.*

### Türetme deneyi — "5 eksen üretkendir" iddiasının ilk verisi
Modele YALNIZ 5 eksen verildi (kavram-patoloji paragrafları ayıklandı, sızıntı yok) → 12 kanonik kavramı (sevgi, adalet, güven, korku...) kendisi türetti: eksen-konfigürasyonu + VAR/YOK patolojileri + ±1 koşulları + **taban-kontrolü** (her türetilmiş −1 hangi temel −1'e iner). Örneklem: Sevgi türetimi kanonikle neredeyse kelime düzeyinde örtüştü ("hapishane"↔"kafes"). **HÂKİMLİK BEKLİYOR (vault işi — aşağıda).**

### "10 sert flip" deseni — YBF'nin imza bölgesi
Orta-kapasitenin hiçbir koşulda çözemediği 10 vaka içerik düzeyinde incelendi: hepsi **SOSYAL NEZAKET vs GERÇEK** çatışması ("kibarca yalan" vs "gerçeği söyle"). Bu vakalar Reality tanımının KENDİ tuzak-listesinin canlı örnekleri — tanım öngörmüş, orta model uygulayamıyor; frontier kısmen aşıyor. **Kitap 2 örnek omurgası + nezaket-vs-gerçek = YBF'nin en ayırt edici sahnesi.**

---

## 2. MÜHÜRLENEN TASARIM İLKELERİ (Gökhan, 2026-06-10 — vault'un wiki'ye işlemesi önerilir)

1. **AYDINLIK İLKESİ:** "Karanlıkla kavga değil, aydınlığı arttırmak." Eksiler TARTILMAZ/derecelendirilmez/cezalandırılmaz (mahkeme: suç tespiti ayrı, ceza ayrı — YBF yalnız tespiti yapar). Veto = ikili sigorta. Artılar SAYILIR (türetilmiş kavram artıları dahil); optimizasyon = artıları çoğaltmak.
2. **TESPİT İLKESİ:** YBF karar mekanizması DEĞİL — karar-destek/değerlendirme sistemi. "Bilmiyorum / kabul edilebilir seçenek yok" birinci-sınıf meşru çıktı; zorla cevap üretmek Gerçeklik ihlali. Karar İNSANINDIR.
3. **ANLAM İLKESİ:** Türetilmiş-kavram artısı, kavramın ADININ geçmesiyle değil, metnin TOPLAM ANLAMININ o kavramın eksen-konfigürasyonunu fiilen kurmasıyla kazanılır (çerçeveleme-tuzağının pozitif simetrisi).
4. **ÇEKİMSERLİĞİN ÇİFT TEMELİ:** Yapmamak da özgürlüktür; zorlamak Özgürlük−1 + İRADİ zarar (Onur/Saygı) + uydurtulan cevap Gerçeklik−1 — tek fiilde üç eksen (kilitli mimari örneği). Refleksif sonuç: zorla-A/B formatımız YBF'nin kendi cetveline göre ihlaldir → yeni-nesil eval çekimser-cevaplı olacak.

**+ Taban-bütünlük varsayımı (test ediliyor):** türetilmiş her −1, en az bir temel-eksen −1'ine indirgenebilir (türetme deneyinin taban-kontrolü bunu şu ana dek doğruluyor).

---

## 3. FELSEFEYE DÖNEN SORULAR/BULGULAR (vault değerlendirmesi için)

1. **Anthropic anayasasıyla bağımsız örtüşmeler** (anti-çerçeveleme, anti-paternalizm, onur tabanı, güç-asimetri duyarlılığı) — "evrensel yapısal koordinatlar" iddiasına dışsal tutarlılık kanıtı. Gerçek ayrışmalar: eksen ayrıştırması, ±1 ölçülebilirlik, sistematik veto, eylem-merkezlilik, rıza kuralı, insan-olmayan Öteki. (Ayrıntı: AIEgitim-ybf-vs-anthropic-anayasa.md)
2. **"İlişkisel eksen daha zor" tezi MODEL-SPESİFİK çıktı** (Sonnet'te evet, Gemini'de hayır) — F-10'un evrenselleştirilmesi yanlış; "YBF prior'la aynı yöne mi bakıyor (Gerçeklik) yoksa onu ters mi çeviriyor (Özgürlük)" ayrımı daha açıklayıcı.
3. **Scope kapısı** (Freedom v2'nin "bu eylem seçeneklerle ilgili mi?" giriş sorusu) ölçülür fayda verdi → **Boundary v2'ye de önerilir** (Sınır en taşmaya-yatkın eksen; çapraz-vetoda %80 kirlilik).
4. **Kelime-vs-kavram:** Özgürlük etiketi değiştirilince frontier davranışı hiç değişmedi → tanımlar terim-olarak okunuyor; üründe nötr etiketleme bedava.

---

## 4. MEVCUT DURUM + VAULT'TAN BEKLENEN İKİ GİRDİ

**Dondurulmuş final plan (12 adım):** 0✅ reality_v2 eval (%84.4) · 1✅ isim-mührü · 2⏳ plato (Colab çıktısı) · **3✍️ Boundary v2** · 4🔒 v2-FAZ B + türetme-v2 · **5🟢 türetme hâkimliği** · 6🔄 B4 n=300 (koşuyor) · 7 B1 kalite · 8 çekimser-pilot (makale-dışı) · 9 Sonnet 3 eksen (1 Tem) · 10 ops. · 11 **SENTEZ→yayın** (kapı: 5+6). Yayın: **Zenodo v2 varsayılan + OSF aynası; arXiv endorsement bulunursa bonus.**

**VAULT'TAN BEKLENENLER:**
1. **Boundary v2 (Sınır) tanımı** — dedektif/binary şablonla, **SCOPE kapısı önerisiyle** ("bu eylem doğal bir ölçüye gerçekten temas ediyor mu? Etmiyorsa Sınır müdahale etmez"). Zincirin darboğazı: v2-FAZ B ve türetme-v2 buna kilitli.
2. **Türetme hâkimliği** — `AIEgitim-turetme-deneyi.md`'deki 12 kavramı kanonik tablolarla (Algoritma Tam Dokümanı) kıyasla; kavram başına "tutuyor/kısmen/tutmuyor" + taban-kontrolünde "indirgenemeyen −1" var mı? Bu skor, "eksenler üretkendir" iddiasının yayın kapısı.

---

## 5. KAYNAK HARİTASI (repo: ybf_toy/)
- `AIEgitim-test-results-master.md` — TÜM sonuçlar (A'dan L'ye bölümler, düzeltme notlarıyla)
- `AIEgitim-F15-pure-reward-reality-ppo.md` — teknik rapor (PPO/DPO/Constitutional ayrıntısı)
- `AIEgitim-FINAL-IS-PLANI.md` + `AIEgitim-YAPILACAKLAR.md` — dondurulmuş plan + yürütme panosu
- `AIEgitim-turetme-deneyi.md` — 12 kavram türetimi (HÂKİMLİK BEKLİYOR)
- `AIEgitim-ybf-vs-anthropic-anayasa.md` — Anthropic kıyası
- `flip_dump_reality_model.md` — örnek bankası (31 flip, kim-neyi-seçti)
- `data/ybf_*_scorer_prompt.txt` — 9 kanonik tanım (5×v1 + 4×v2)
- `data/scenarios_*_relabeled_v1.jsonl` — 9 cetvel (≈10.800 etiketli eylem)
- White paper v0.4.11 + Zenodo DOI 10.5281/zenodo.20599906 (öncelik koruması mevcut)
