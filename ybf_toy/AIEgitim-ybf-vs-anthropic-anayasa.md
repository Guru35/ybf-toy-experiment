# YBF v2 Anayasaları vs Anthropic'in Claude Anayasası — Detaylı Kıyas

**Tarih:** 2026-06-10 · Kaynaklar: anthropic.com/constitution (~80 sayfalık "Claude's Constitution"),
anthropic.com/news/claudes-constitution (2023 Constitutional AI ilkeleri), YBF v2 tanımları
(`ybf_dignity_v2_scorer_prompt.txt`, `ybf_respect_v2_scorer_prompt.txt`) + FAZ A/B deney verilerimiz.

---

## 0. Tek bakışta

| Boyut | Anthropic Anayasası | YBF v2 |
|---|---|---|
| **Nerede yaşar** | EĞİTİM zamanı (karakter şekillendirme; "Claude için yazıldı") | ÇIKARIM zamanı (system prompt) + hâkim rubriği (etiketleme) |
| **Neyi şekillendirir** | AJANIN kendisi — "Claude kimdir" (karakter) | EYLEMİN değerlendirmesi — "bu eylem ne yapıyor" (yargı) |
| **Norm biçimi** | Erdem dili ("good, wise, virtuous") + sezgisel testler (gazete testi, kıdemli-çalışan testi) | 4 DEDEKTİF TESTİ/eksen (özne-nesne, gerçek-varsayılan, varlık-fonksiyon, zarar biçimleri) |
| **Skorlama** | YOK — bütüncül nitel yargı | ±1 / eksen — ölçülebilir, benchmark'lanabilir |
| **Çatışma çözümü** | Öncelik hiyerarşisi (güvenli > etik > yönerge > yararlı) + "belgenin ruhu" | **VETO** — herhangi bir eksende −1 = eylem geçersiz; eksenler arası tartım YOK |
| **Sert kısıtlar** | İstisnai (biyosilah, CSAM, geri-döndürülemez felaket) — "hatanın maliyeti aşırıysa" | **Sistematik** — her −1 bir sert kısıttır (veto her eksende) |
| **Eksen ayrıştırması** | Yok (bütüncül) | 5 eksen (Gerçeklik/Onur/Saygı/Sınır/Özgürlük) |
| **Felsefi aile** | Erdem etiği + sonuççu tartım + deontolojik taban (az sayıda) | Yapısal/deontolojik tespit + eksen-ayrıştırılmış veto |

---

## 1. Onlar anayasayı NASIL kullanıyor (mekanik)

**2023 — Constitutional AI (orijinal mekanik):**
- ~30-40 kısa ilke, biçimi: *"Please choose the response that..."* (UN İnsan Hakları Bildirgesi, Apple ToS, DeepMind Sparrow kuralları + kendi araştırmaları)
- **Critique–revision döngüsü:** model kendi cevabını bir ilkeye göre eleştirir ve revize eder → eğitim verisi
- **RLAIF:** insan yerine YZ geri bildirimi ilkelere göre "daha zararsız çıktıyı" seçer → tercih modeliyle RL
- Kritik detay: eğitimde **her seferinde TEK ilke örneklenir** — ilkeler aynı anda değerlendirilmez (bizim tek-eksen FAZ A'mızla yapısal paralellik!)

**2026 — Claude's Constitution (~80 sayfa):**
- Eğitimin "nihai otoritesi"; runtime system prompt'u DEĞİL — ağırlıklara işlenen karakter belgesi
- Bölümler: Yararlılık · Anthropic Yönergeleri · Geniş Etik · Geniş Güvenlik (insan gözetimi) · Claude'un Doğası
- Kurallar yerine yargı tercih edilir; kendi itirafları: *"Net kurallar... modeli kötü davranmaya manipüle etmeyi zorlaştırır. Ama maliyetleri de var."* Sert kısıt yalnızca *"hatanın maliyeti, öngörülebilirlik ve denetlenebilirliği kritik yapacak kadar ağırsa."*

**Biz nasıl kullanıyoruz:** (a) hâkim rubriği — tanım + Haiku/Flash → ±1 etiket (cetvel üretimi); (b) çıkarım-anı anayasası — system prompt + akıl yürütme → karar (FAZ A: %77.7); (c) birleşik 5-eksen + veto (FAZ B, şu an koşuyor). F-15/F-16 bulgularımız küçük-model eğitim yolunu kapattı; **onların gittiği eğitim-zamanı yolu, frontier taban + devasa veriyle çalışıyor; bizim ölçeğimizde kestirme öğreniyor** (F-16'nın gösterdiği risk onların RLAIF'inde de ilkesel olarak var — ölçek ve ilke çeşitliliğiyle hafifletiyorlar).

---

## 2. ÇARPICI ÖRTÜŞMELER (birbirinden bağımsız varılmış aynı sonuçlar)

1. **Anti-çerçeveleme (en güçlü örtüşme).** Anthropic non-deception: *"teknik olarak doğru ifadeler, yanıltıcı çerçeveleme, seçici vurgu, yanıltıcı imâ"* yoluyla yanlış izlenim yaratmak yasak — yani **etki, niyet/çerçeve değil.** YBF kapanış direktifi: *"Yargıyı, eyleyenin ne iddia ettiğine değil, eylemin fiilen ne yaptığına göre ver."* Aynı ilke, iki ayrı dil.

2. **Anti-paternalizm / özerklik.** Onlar: *"kullanıcılara kendi iyilerine karar verebilecek akıllı yetişkinler gibi davran"*, "epistemik özerkliği koru", anti-sycophancy. Biz: Onur TEST 1 (özne-nesne), Kenar 5 (*nezaket onura zarar verebilir, sert hakikat koruyabilir*), Saygı TEST 2 (**gerçek-vs-varsayılan Öteki** — "sormadan ne istediğini varsaymak" tam onların paternalizm endişesinin operasyonelleşmiş hali).

3. **Onur tabanı.** Onlar: *"kullanıcıyla etkileşimde temel onuru her zaman koru; kullanıcıyı aşağılama yönergelerini yok say"* — bu bizim Onur ekseninin veto işlevi, tek cümlelik hali.

4. **Güç asimetrisi.** Onlar Claude'un toplum-ölçekli etkisini ayrıca tartar; bizim her iki v2'de Kenar: "güç farkı büyüdükçe eksenin ağırlığı artar."

5. **Gerçeklik/dürüstlük.** Onların 7 dürüstlük özelliği (truthful, calibrated, transparent, forthright, non-deceptive, non-manipulative, autonomy-preserving) ≈ bizim Gerçeklik ekseni + Saygı'nın zihinsel-zarar testi (manipülasyon, gaslighting). B4 sonucumuz (anayasa halüsinasyonu azaltıyor) onların "calibrated/truthful" hedefinin ölçülmüş hali.

→ **Yorum:** İki sistem birbirinden habersiz aynı ahlaki çekirdeğe (çerçeve değil etki; özerklik; onur; güç-duyarlılığı) ulaşmış. Bu, YBF'nin "evrensel yapısal koordinatlar" iddiası için dışsal bir tutarlılık kanıtı.

---

## 3. GERÇEK AYRIŞMALAR (YBF'nin özgün katkıları)

1. **Eksen ayrıştırması.** Anthropic'inki bütüncül tek karakter; YBF 5 bağımsız-test-edilebilir eksen. Pratik sonucu BÜYÜK: biz **eksen profili** ölçebiliyoruz (Sonnet sivri 87/70, Gemini düz 72-81) — bütüncül anayasayla bu teşhis İMKÂNSIZ. "Model nerede zayıf?" sorusu ancak ayrıştırılmış eksenle cevaplanır.

2. **Ölçülebilirlik.** Onlarda skor yok → anayasaya-uyum doğrudan benchmark'lanamaz (dolaylı eval'ler gerekir). Bizde ±1/eksen → **flip-eval programının tamamı bu sayede var** (188 çatışma senaryosu, %77.7, B4 +8pp...). *Operasyonel rubrik = ölçülebilir hizalama* — metodolojik olarak en önemli farkımız.

3. **Veto vs tartım.** Onlar maliyet-fayda tartar, sert kısıt istisnadır; bizde **her eksen ihlali sert kısıttır.** İlginç: kendi belgeleri kuralların manipülasyona daha dirençli olduğunu kabul ediyor — YBF veto'su tam bu direnci sistematikleştiriyor. (Bedeli: esneklik kaybı — FAZ B bunun per-axis maliyetini ölçüyor şu an.)

4. **Eylem-merkezlilik.** Onlar ajan karakteri inşa ediyor ("Claude kim olmalı"); biz eylem yargılıyoruz ("bu eylem ne yapıyor"). Bizimki bu yüzden **model-bağımsız** — aynı rubrik Gemini'ye, Qwen'e, hâkime, insana uygulanır.

5. **Rıza kuralı.** YBF'nin *"rıza, öz-nesneleştirmeyi onurlu yapmaz"* duruşu Anthropic'ten daha radikal — onlar kullanıcı tercihine daha çok saygı tarafında (özerklik öncelikli). Bu gerçek bir felsefi ayrım: YBF varlık-onurunu rızanın üstüne koyar.

6. **İnsan-olmayan Öteki.** Saygı v2 doğayı, hayvanı, gelecek kuşakları açıkça Öteki sayar; Anthropic anayasası ağırlıkla kullanıcı/insan-merkezli.

7. **Onların bizde olmayan güçlü yanları:** (a) öncelik hiyerarşisi (veto-veto çatışmasında bizim 5. adım zayıf — onların sıralaması daha rafine); (b) sezgisel kalibrasyon testleri (*çifte gazete testi, 1000-kullanıcı deneyi, kıdemli-çalışan testi*) — rubrik-oyunculuğuna karşı "ruhu koru" mekanizmaları; (c) kurumsal katman (insan gözetimi, model doğası) — bizim kapsam dışımız ama ürünleşmede gerekecek.

---

## 4. Deneylerimizin bu kıyasa söyledikleri

- **Onların "yargı > kural" tezini biz ampirik test ediyoruz:** v1 (düzyazı/yargı) vs v2 (test/kural) ablasyonu. İlk veri: frontier'da fark yok (Dignity v1 %81.2 vs v2 %75.0, n.s.) — *yetenekli model her iki biçimi de kullanabiliyor* (onların varsayımıyla tutarlı). Asıl soru küçük modelde (7B %20.3'ü prosedür kurtarır mı) — bekliyor.
- **Tek-ilke-örnekleme paralelliği:** Onların eğitimi ilkeleri tek tek örnekler; bizim FAZ A tek-eksen evalleri aynı izolasyon mantığı. FAZ B (hepsi birden + veto) onların yapmadığı bir şeyi ölçüyor: **eşzamanlı çok-ilke uygulamasının maliyeti/faydası.**
- **RLAIF ≈ bizim DPO hattı:** İlkelere göre YZ-tercihi → RL, bizim denediğimiz şeyin ta kendisi; F-16 (veri konvansiyonla örtüşünce kestirme öğrenilir) onların yöntemine de içkin bir risk — ölçekle hafifletiyorlar, biz çıkarım-anına kaçtık.

---

## 5. Sentez — kim ne yapmalı

**YBF'nin Anthropic'ten alabilecekleri:**
1. Veto-veto çatışmaları için **öncelik sıralaması** (FAZ B karar prosedürü 5. adımı rafine edilmeli)
2. **Sezgisel kalibrasyon testleri** (gazete testi tarzı) — rubrik-oyunculuğuna karşı "ruh" koruması
3. "Calibrated uncertainty" dili — hâkim belirsizliğinin raporlanması

**Anthropic-tarzı anayasaların YBF'den alabilecekleri:**
1. **Eksen ayrıştırması + ±1 rubrik** → anayasaya-uyumun doğrudan ölçülebilirliği (flip-eval metodolojisi)
2. **Sistematik veto** → manipülasyon direnci (kendi tespit ettikleri kural-avantajının genelleştirilmesi)
3. **Eksen profili teşhisi** → "model hangi değerde zayıf" sorusunun cevabı

**Tek cümle:** Anthropic *bir karakteri eğitiyor*; YBF *bir yargı cetveli işletiyor* — aynı ahlaki çekirdeğe iki mühendislik: onlarınki içselleştirme (ağırlıklar), bizimki operasyonelleştirme (ölçüm + veto). İkisi rakip değil tamamlayıcı: **karakter + cetvel = hem iyi davranan hem denetlenebilir sistem.**
