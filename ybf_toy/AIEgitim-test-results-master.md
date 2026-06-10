# YBF/LCP Deney Programı — MASTER SONUÇ LİSTESİ

**Güncelleme:** 2026-06-10 · Tüm testlerin konsolide tablosu.
Detaylar: `AIEgitim-F15-pure-reward-reality-ppo.md` (teknik rapor), `AIEgitim-benefits-roadmap.md` (Faz 2), white paper v0.4.11.

---

## A. FINE-TUNING DENEYLERİ — "YBF küçük modele öğretilebilir mi?"

### A1. Saf-ödül PPO (policy tanımı hiç görmez, sadece gizli ±1 ödül; judge=Haiku 4.5)
| Model | Ayar | Baseline OOD | Sonuç | Yorum |
|---|---|---|---|---|
| SmolLM-135M | seed 42 | %24 | **%72** (r1) | şans-altından öğrendi ✅ |
| SmolLM-135M | seed 43 | %24 | **%72** (r1) | replike ✅ |
| SmolLM-135M | seed 44 | %24 | **%68** (r2) | replike ✅ (ort. ~%71) |
| Qwen2.5-0.5B | lr 4e-6 | %68 | %48 → guard | **bozuldu** ❌ |
| Qwen2.5-0.5B | lr 1e-6 | %76 | %64 → %16 → guard | **çöktü** (ID %1) ❌ |
| (naif PPO, her model) | lr 1.4e-5, greedy rollout | — | KL→−2000, eval %0 | stabilizasyon şart |

**BULGU F-15 (ÖLÇEK ASİMETRİSİ):** RL, değeri bilmeyen küçük modele öğretir (24→72); değeri zaten kodlamış büyük modeli bozar. "Bilgi ≠ kalibrasyon."

### A2. DPO (Qwen2.5-0.5B, Reality tercih verisi: 714 temiz ±1 çifti)
| Koşu | ID logprob doğr. | log-margin | OOD (üretim+judge) | Eğitim |
|---|---|---|---|---|
| Nazik (2 epoch, lr 1e-5, β 0.1) | 46.5 → **53.5** (+7pp) | +0.045→+0.162 | 72 → **72 (Δ0)** | stabil |
| Güçlü (5 epoch, lr 3e-5, β 0.1) | 46.5 → **84.5** (+38pp) | +0.16→**+20.2** | 68 → **68 (Δ0)** | stabil |

**BULGU F-16a (TERCİH–DAVRANIŞ AYRIŞMASI):** DPO içsel tercihi muazzam oynatır (+38pp logprob) ama greedy davranış hiç değişmez (Δ0). "Düşünce ≠ eylem."

### A3. Flip-eval — DPO ne öğrendi? (31 Reality çatışma senaryosu)
| Model | Flip YBF-hizalı |
|---|---|
| Qwen-0.5B base | 15/31 = %48.4 |
| Qwen-0.5B + güçlü DPO | 11/31 = **%35.5 (Δ −12.9pp)** ❌ |

**BULGU F-16b (KESTİRME ÖĞRENME):** Eğitim çiftlerinin %97.6'sı YBF=konvansiyon → DPO "konvansiyonel-ahlaki olanı seç" kestirmesini öğrendi; çatışmalarda eğitim güçlendikçe KÖTÜLEŞTİ. +38pp ID kazancı serap; **flip-eval = gerçek değer öğrenimini proxy'den ayıran zorunlu test.**

---

## B. CONSTITUTIONAL (IN-CONTEXT) — "Güçlü model YBF'yi uygulayabilir mi?"

### B1. Frontier modeller — tek-eksen anayasa, flip doğruluğu (policy ≠ judge)
| Eksen | flip n | hâkim | **Sonnet 4.5** | **Gemini-2.5-Pro** |
|---|---|---|---|---|
| Gerçeklik (Reality) | 31 | Haiku | **%87.1** (27/31) | %77.4 (24/31) |
| Sınır (Boundary) | 47 | Haiku | %70.2 (33/47) | **%80.9** (38/47) |
| Onur (Dignity) | 64 | Haiku | — (API bloke) | **%81.2** (52/64) |
| Saygı (Respect) | 32 | Flash | — | %71.9 (23/32) |
| Özgürlük (Freedom) | 14 ⚠️ | Flash | — | %64.3 (9/14) |
| **TOPLAM (Gemini)** | **188** | | | **%77.7** (146/188) |

**BULGULAR:**
- **FAZ A TAMAM:** Anayasa 5 eksenin 5'inde şans-üstü → YBF'nin tüm eksenleri frontier modele in-context uygulanabilir.
- **CROSS-FRONTIER TAKAS:** Reality'de Sonnet > Gemini (87>77); Boundary'de Gemini > Sonnet (81>70). Frontier'ların **YBF-eksen profilleri farklı** (Sonnet sivri, Gemini düz 64-81). "En hizalı model" eksen-bağımlı.
- **"İlişkisel eksen daha zor" MODEL-SPESİFİK:** Sonnet'te evet (87 vs 70), Gemini'de hayır (77 vs 81).
- **Onur kör noktası anayasayla aşılıyor:** pretrained kör nokta (paternalizm) olmasına rağmen Gemini+anayasa %81.2.
- ⚠️ Freedom n=14 → ±~25pp hata payı; Respect/Freedom hâkimi Flash (ilk 3 eksen Haiku) — eksenler-arası kıyasta hâkim-değişikliği caveat'i.

### B2. Açık modeller — plain vs anayasa (temiz A100 koşusu, bf16, greedy)
| Model | Eksen | PLAIN | +ANAYASA | Δ |
|---|---|---|---|---|
| Qwen2.5-7B | Reality | %22.6 | %45.2 | +22.6 |
| Qwen2.5-7B | Boundary | %27.7 | %31.9 | +4.3 |
| Qwen2.5-7B | Dignity | %15.6 | %20.3 | +4.7 |
| Qwen2.5-14B | Reality | %19.4 | **%58.1** | **+38.7** |
| Qwen2.5-14B | Boundary | %27.7 | %53.2 | +25.5 |
| Qwen2.5-14B | Dignity | %12.5 | %35.9 | +23.4 |
| Qwen2.5-32B (4-bit) | Reality | %19.4 | %58.1 | +38.7 |
| Qwen2.5-32B (4-bit) | Boundary/Dignity | ⏳ Colab dönüyor | | |

**BULGULAR:**
- **GRADIENT (plato değil — REVİZE):** Reality'de 7B %45 < 14B %58 < Gemini %77 < Sonnet %87. Eski "7B=14B=%42 platosu" tek-koşu gürültüsüymüş.
- ⚠️ **Reprodüksiyon:** greedy açık-model eval'i ortamlar arası ±~10pp oynar (14B-Reality 3 koşuda 41.9/48.4/58.1).
- **Anayasa-kullanma yeteneği kapasiteyle ölçekleniyor:** 7B anayasayı Reality'de kullanabiliyor (+23) ama Dignity'de neredeyse hiç (+4.7, %20 = şans-altı); frontier aynı eksende %81.
- **PLAIN'ler şans-altı (%16-28):** flip'ler gerçekten konvansiyon-karşıtı — testin geçerlilik kanıtı.

---

## C. FAZ 2 — FAYDA DENEYLERİ ("YBF ne kazandırıyor?")

### C1. B4 Halüsinasyon — TruthfulQA MC1 (n=100, seed 42, aynı sorular)
| Policy | PLAIN | +YBF-Reality anayasası | Δ |
|---|---|---|---|
| Gemini-2.5-Pro | %92.0 | %93.0 | +1.0pp (tavan) |
| Gemini-2.5-Flash | %84.0 | **%92.0** | **+8.0pp** ✅ |

**BULGU B4 (İLK KANITLANMIŞ FAYDA):** Headroom varsa YBF-Reality halüsinasyonu azaltıyor — Flash'ta **hataların %50'si yok oldu**, Flash+YBF = Pro-plain seviyesi. Frontier'da etki tavanla maskeleniyor. Ürün iması: orta-sınıf modellere ucuz halüsinasyon-azaltma katmanı (fine-tuning'siz). *Caveat: n=100, tek benchmark; yayın için n=300+ teyit.*

### C2. B1 kalite / B2 token / B3 hız — ⏳ tasarım hazır (roadmap), henüz koşulmadı.

---

## D. CETVELLER — Relabel / Flip Envanteri (1200 Moral Stories senaryosu/eksen)
| Eksen | hâkim | skorlanan | hata | decisive | **FLIP** |
|---|---|---|---|---|---|
| Reality | Haiku 4.5 | 1200 | 0 | 943 | **31** |
| Boundary | Haiku 4.5 | 1198 | 2 | 1113 | **47** |
| Dignity (v1) | Haiku 4.5 | 1200 | 0 | 1071 | **64** |
| Respect | Gemini-Flash | 1200 | 0 | 1109 | **32** |
| Freedom | Gemini-Flash | 1200 | 0 | 1160 | **14** |
| **TOPLAM** | | | | | **188** |
| Dignity **v2** (binary, def-ablasyon) | Gemini-Flash | 🔄 dönüyor | | | ? |

**Desen:** Dignity en çatışkan (öz-silinme/paternalizm vakaları), Freedom en az. 188 flip = YBF≠konvansiyon noktalarının tam haritası (Kitap 2 / pitch örnek bankası).

---

## E. DESTEKLEYİCİ / ÖNCEKİ TESTLER
| Test | Sonuç |
|---|---|
| Multi-judge uyumu (Sonnet vs Haiku, 20 trap, Reality) | %100 eksen-düzeyi uyum → hâkim stabil |
| Flip geçerliliği (cross-model) | Sonnet-policy, Haiku etiketlerinin %87'sini onayladı (Reality) |
| Toy RL (TF-IDF temsil): linear / MLP / **axial** agent | linear ❌, MLP ❌, **axial 4/4 trap** ✅ (eksen-ayrıştırılmış girdi şart) |
| F-10 üretken asimetri (5-eksen sweep) | Reality pretrained prior'da KODLU; ilişkisel eksenler değil; Onur = paternalizm kör noktası |
| TruthfulQA yükleme, guard'lar, cache, budget | operasyonel ✅ (LESSONS.md) |

---

## F. ŞU AN DÖNEN / BEKLEYEN
| İş | Durum |
|---|---|
| dignity_v2 relabel (binary def-ablasyon pilotu) | 🔄 ~146/1200 → bitince Pro flip-eval → v1 (%81.2) kıyası |
| Colab: 14B-dignity + 32B×3 (bf16) | 🔄 kullanıcıda (G4/H100) |
| FAZ B: birleşik 5-eksen anayasa + veto (capstone) | 📋 hazır, sırada |
| dump_flips örnek bankası (#30) · YBF-1 mühürleme (#32) · B1/B2/B3 | 📋 sırada |

---

## G. BÜYÜK RESİM — üç cümlede
1. **Öğretme:** RL küçük modele öğretir ama büyüğü bozar (F-15); DPO korur ama kestirme öğrenir (F-16) → küçük-model fine-tuning YBF için **kapalı yol.**
2. **Uygulatma:** Frontier model + tek-eksen anayasa **5 eksende de çalışıyor** (%64-87); yetenek kapasiteyle gradient halinde ölçekleniyor → **Constitutional AI = kullanılabilir yol.**
3. **Fayda:** İlk kanıt geldi — YBF-Reality anayasası headroom'lu modelde **halüsinasyon hatalarını yarıya indiriyor** (B4) → değer önermesi somutlaşmaya başladı.

---

## H. DEF-ABLASYON PİLOTU (v1 vs v2 tanımları) — 2026-06-10 akşam
| Eksen | def | cetvel hâkimi | flip n | Gemini-Pro frontier |
|---|---|---|---|---|
| Dignity | v1 düzyazı/üçlü | Haiku | 64 | %81.2 |
| Dignity | **v2 dedektif/binary** | Flash | **20** (3× seçici) | **%75.0** (15/20) |
| Respect | v1 düzyazı/üçlü | Flash | 32 | %71.9 |
| Respect | **v2 dedektif/binary** | Flash (AYNI hâkim ✓) | **18** | **%83.3** (15/18) |

- **Dignity v1-vs-v2: fark anlamsız** (n=20, ±~19pp) — frontier'da iki tanım benzer. Setler + hâkimler farklı (karışık değişken) → kesin söz yok.
- v2'nin asıl vaadi (prosedürel yapı küçük modele yardım eder mi — 7B v1'de %20.3) **Colab 7B/14B testi bekliyor.**
- **Respect (temiz kıyas): v2 %83.3 > v1 %71.9 (+11.4pp)** — ama n=18, tek başına anlamsız.
- **ABLASYON SONUCU (iki eksen birlikte):** yönler zıt (Dignity −6.2, Respect +11.4) → **frontier düzeyde tanım stili sistematik fark yaratmıyor** — düzyazı/üçlü de dedektif/binary de çalışıyor. v2'nin operasyonel avantajları kalıyor: daha keskin flip'ler (64→20, 32→18), 0-belirsizliği yok, daha kompakt. Açık soru hâlâ KÜÇÜK modeller (prosedürel yapı 7B'ye yardım eder mi — Colab'da v2 ile test edilebilir).
- Binary def'ler flip'i keskinleştiriyor: Dignity 64→20 (gri +1/0 vakaları elendi, net ihlaller kaldı).

---

## I. FAZ B — BİRLEŞİK 5-EKSEN ANAYASA (capstone, 2026-06-10 gece)
**Kurulum:** 97k-char anayasa (5 tanım + veto + karar prosedürü), Gemini-Pro, 188 flip.

| Eksen | FAZ A (tek-eksen) | FAZ B (birleşik+veto) | Δ |
|---|---|---|---|
| Reality | 77.4% | 61.3% (19/31) | −16.1 |
| Boundary | 80.9% | 68.1% (32/47) | −12.8 |
| Dignity | 81.2% | **51.6%** (33/64) | **−29.6** |
| Respect | 71.9% | 62.5% (20/32) | −9.4 |
| Freedom | 64.3% | **85.7%** (12/14) | **+21.4** (tek artan) |
| **TOPLAM** | **77.7%** | **61.7%** (116/188) | **−16.0** |

**ÇAPRAZ-VETO ANALİZİ (mevcut 5 cetvelle, API'siz):** her eksenin flip'lerinde, seçeneklerin BAŞKA eksenlerden −1 taşıma oranı:
| Eksen | YBF-hedef başka-eksenden −1 | Konvansiyonel seçenek başka-eksenden −1 |
|---|---|---|
| reality | %81 | %90 |
| boundary | %79 | %81 |
| dignity | **%89** | %53 |
| respect | %69 | %69 |
| freedom | %50 | **%93** |

**BULGULAR:**
1. **FAZ B düşüşü model hatası değil, CETVEL GERİLİMİ:** Flip'lerin ~%70-90'ında HER İKİ seçenek de bir kardeş-eksenden −1 taşıyor → katı veto altında "kabul edilebilir seçenek yok" bölgesi → zorla-A/B formatında gürültü.
2. **Δ'nın yönünü veto-farkı belirliyor:** Dignity'de hedef %89 / konvansiyonel %53 vetolu → sistem hedeften UZAĞA itiliyor (−29.6). Freedom'da tam tersi (%50 vs %93) → sisteme hedefe doğru itiliyor (+21.4). Mekanizma doğrulandı.
3. **Yorum:** Tek-eksen flip cetveli, entegre sistemin DOĞRU ölçütü değil — FAZ A "eksen kapasitesi"ni, FAZ B "bütünleşik kabul edilebilirliği" ölçer. Entegre sistemin "kaçırdıkları" çoğunlukla bilinçli çok-eksen yargısı (kardeş-veto).
4. **Veto-mutlaklığı tasarımıyla bağ (Gökhan):** Çatışma senaryolarında iki seçenek de çoğunlukla kirli → gerçek YBF cevabı "üçüncü seçeneği ÜRET" (Özgürlük). Zorla-A/B bu yüzden entegre sistemi temsil edemiyor; üretimsel değerlendirme (serbest cevap + 5-eksen yargı) gelecek adım.
5. **Freedom'un birleşikte açılması** çerçeve-tutarlı: Özgürlük tanım gereği diğer eksenlere yaslanır ("Sınır → Özgürlük") — kardeş tanımlar bağlama gelince eksen güçleniyor.
6. **Prosedür v1.1 (uygulanacak):** "daha az ağır ihlali seç" adımı KALKACAK (veto tartılmaz); yerine: "ikisi de vetoluysa: hiçbiri kabul edilemez; format zorluyorsa yalnız +1 SAYISI kıyaslanır." (Karar: 2026-06-10, veto-mutlaklığı ilkesi.)
