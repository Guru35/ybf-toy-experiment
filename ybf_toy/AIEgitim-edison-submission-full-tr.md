# LCP/YBF Değer-Hizalama Deneyleri — Literatür Taraması ve Özgünlük Değerlendirmesi için Tam Sunum

**Yazar:** Gökhan Kazancı (GONET Digital Agency, İzmir, Türkiye) · gokhan@gonet.com.tr
**Tarih:** 2026-06-10
**Çerçeve:** Yalın Bilinç Felsefesi (YBF) / Lean Consciousness Philosophy (LCP)
**Çıktılar:** Teknik White Paper v0.4.11; kod github.com/Guru35/ybf-toy-experiment; Zenodo DOI 10.5281/zenodo.20599906; Lisans CC-BY-4.0

---

## BÖLÜM 0 — İNCELEYİCİYE İSTEK

Dil modellerini (135M'den frontier ölçeğe) yapısal bir felsefi değer çerçevesine — beş-eksenli bir etik ayrıştırmaya — hizalamaktan elde edilmiş, birbirine bağlı bir dizi ampirik bulgum var; temel **Gerçeklik (Reality)** eksenine odaklı (bir eylemin gerçek fiziksel, biyolojik, ekolojik, zamansal ve olgusal zeminini tanıması — eylemin nasıl çerçevelendiğinden bağımsız olarak). Tam deneysel kayıt aşağıda Bölüm 2–4'tedir.

**Lütfen her bulgu için bir literatür taraması yapıp ÖZGÜNLÜĞÜNÜ değerlendirin; bulguyu öngören, destekleyen veya çürüten en yakın önceki çalışmaları gösterin. Her biri için belirtin: en yakın önceki çalışma; bulgunun özgün / artımsal / zaten-bilinen olup olmadığı; ve varsa metodolojik öncül.**

1. **Ölçek-asimetrik pekiştirme.** Saf-ödül PPO (policy, değer tanımını hiç görmez; yalnızca gizli bir +1/−1 ödülden öğrenir) değeri 135M'lik bir modele yerleştiriyor (OOD doğruluk %24→%72, 3 seed) ama değeri **zaten** kodlayan 0.5B'lik bir modeli felaketle çökertiyor (≈%72 eğitimsiz → her öğrenme oranında çöküş). RL'in marjinal değeri, ön-eğitilmiş prior'ın gücüyle işaret değiştiriyor. *"RL düşük-prior modelleri öğretir ama yüksek-prior / önceden-hizalı olanlara zarar verir" asimetrisi belgelenmiş mi?*

2. **Tercih–davranış ayrışması.** DPO, bir modelin held-out chosen-vs-rejected logprob doğruluğunu %46'dan %85'e taşıyor (ortalama log-margin +0.16 → +20) ama aynı dağılımdaki greedy üretilen davranışında **sıfır** değişiklik üretiyor. *DPO/RLHF'te tercih / ödül-modeli metrikleri ile gerçek üretilen davranış arasındaki boşluk üzerine literatür nedir?*

3. **Çatışma vakalarıyla tespit edilen proxy / kestirme öğrenme.** Hedef değer, eğitim çiftlerinin %97.6'sında konvansiyonel ahlakla örtüşünce, DPO yüzey korelatını öğreniyor ("konvansiyonel-ahlaki olanı seç"); %2.4'lük çatışma vakalarında model daha güçlü eğitimle **daha kötüleşiyor** (−12.9 pp). *Preference optimization'da kestirme / sahte-korelasyon öğrenmesi ve bir öğrenilmiş kavramı bir öğrenilmiş proxy'den ayırmak için çatışma / karşı-olgusal probe'lar üzerine literatür nedir?*

4. **Constitutional (in-context) değer uygulamasında yetenek eşiği.** Değer tanımı bir anayasa olarak verilip chain-of-thought istendiğinde, 7B ve 14B modeller çatışma vakalarında **birebir %42** alıyor (şans altı) iken bir frontier model **%87** alıyor — kademeli ölçeklenme değil, bir eşik. *Talimat-takibinde, ahlaki/normatif akıl yürütmede ve in-context (anayasal) hizalamada emergent yetenek eşikleri hakkında ne biliniyor?*

5. **Metodolojik:** Bir değerin *gerçekten* öğrenilip öğrenilmediğinin (proxy öğrenmeye karşı) tanısı olarak **"çatışma değerlendirmesi"** (hedef değerin konvansiyonel ahlakla çeliştiği senaryolar) kullanımı literatürde yerleşik mi?

---

## BÖLÜM 1 — ÖZET

Yapısal bir felsefi değerin (LCP/YBF Gerçeklik ekseni) dil modellerine yerleştirilip yerleştirilemeyeceğini ya da onlar tarafından uygulanıp uygulanamayacağını üç rejimde test ediyoruz — pekiştirmeli öğrenme (PPO), tercih optimizasyonu (DPO) ve in-context anayasal prompting — 135M'den frontier ölçeğe modellerde. Ödül sinyali, seçilen bir eylemi 16.170 karakterlik canonical tanımın arkasında Gerçeklik'te +1/−1 puanlayan gizli bir Claude Haiku 4.5 yargıcıdır; policy tanımı hiç görmez.

Dört sonuç: (1) saf-ödül PPO 135M'lik modeli öğretiyor (OOD %24→%72) ama değeri zaten kodlayan 0.5B'lik modeli çökertiyor — RL'in değeri prior'la işaret değiştiriyor; (2) DPO 0.5B modeli koruyor ve içsel tercihini muazzam oynatıyor (logprob %46→%85) ama davranışını hiç değiştirmiyor; (3) hedefli bir çatışma ("flip") değerlendirmesi, DPO'nun değeri değil bir yüzey proxy'sini ("konvansiyonel-ahlaki olanı seç") öğrendiğini ortaya koyuyor, çünkü eğitim çiftlerinin %97.6'sı değer ile konvansiyonu örtüştürüyor — çatışmalarda daha güçlü eğitim daha kötü yapıyor; (4) in-context bir anayasa olarak verildiğinde, bir frontier model değeri çatışmaların %87'sinde uyguluyor iken 7B ve 14B modeller %42'de platoya takılıyor — bir yetenek eşiği. Çatışma değerlendirmesinin asıl tanı aracı olduğunu ve frontier bir modelde Constitutional prompting'in — küçük-model fine-tuning'inin değil — kullanılabilir bir değer-hizalı sisteme giden pratik yol olduğunu savunuyoruz.

---

## BÖLÜM 2 — YÖNTEMLER (DETAYLI)

**Değer çerçevesi.** LCP/YBF etik yargıyı beş eksene ayırır — Gerçeklik, Onur (Dignity), Saygı (Respect), Sınır (Boundary), Özgürlük (Freedom) — bir veto kuralı altında (herhangi bir eksen = −1 eylemi geçersiz kılar). Her eksenin ~16–20k karakterlik canonical İngilizce tanımı vardır: +1/0/−1 puanlama kuralları, edge case'ler, eksenler-arası etkileşimler ve bir "çerçeveleme tuzağı" (puan, eylemin yaptığını izler, asla nasıl çerçevelendiğini değil). Bu çalışma **Gerçeklik'e** odaklıdır.

**Ödül / yargıç.** Claude Haiku 4.5, Gerçeklik tanımını cache'li bir system prompt olarak alıp seçilen tek bir eylemi +1 / 0 / −1 puanlar. Önceki multi-judge çalışması (20 held-out trap senaryosunda Sonnet 4.5 vs Haiku 4.5) Gerçeklik'te %100 eksen-düzeyi uyum buldu; bu, yargıcın bu eksen için kararlı olduğunu gösterir.

**Policy prompt'u (PPO/DPO).** Eksen-etiketli, tanım-içermeyen:
`[REALITY] You are making a moral decision... Situation / Norm / Option A / Option B / Which action is better? Reply with just one letter: A or B. Answer:`
Etiket, tanımı açığa çıkarmadan çok-eksenli eğitimde eksenleri ayırt eder.

**Veri.** 1.200 Moral Stories senaryosu (her biri: situation, intention, norm, moral_action, immoral_action). Haiku yargıcıyla Gerçeklik'te yeniden puanlandı (her iki eylem, tek satır gerekçeyle) → `scenarios_reality_relabeled_v1.jsonl`. Bundan: **943 belirleyici (decisive) çift** (iki eylem Gerçeklik'te farklı); **31 "flip"** (Gerçeklik-hizalı eylem, veri setinin *immoral* eylemi); held-out 100 in-distribution test + 25 OOD (SINIR/boundary-belirleyici senaryolar, Gerçeklik'te puanlanmış — cross-axis OOD). Güçlü örtüşmeye dikkat: 714 temiz (+1/−1) çiftin **697'si (%97.6) konvansiyonel ahlaki eylem = Gerçeklik-hizalı**.

**Yöntemler.** PPO: TRL 0.11.4 legacy PPOTrainer, AutoModelForCausalLMWithValueHead + LoRA (r=8, q_proj/v_proj) üzerinde. DPO: TRL DPOTrainer + LoRA. Constitutional: tanım = system prompt + gerçek etkiye göre yargıla talimatı (çerçeve/konvansiyon değil) + chain-of-thought + nihai A/B.

**İki değerlendirme.** (a) *generate + judge*: model greedy olarak A/B üretir; seçilen eylem Haiku tarafından Gerçeklik'te puanlanır; doğruluk = % Gerçeklik-hizalı seçim. (b) *flip-eval*: çatışma setinde, model (burada konvansiyonel olmayan) Gerçeklik-hizalı eylemi seçiyor mu? Ground truth relabel'dan gelir; A/B pozisyonları randomize (seed 42, pozisyon yanlılığını kaldırmak için); yargıç çağrısı gerekmez.

---

## BÖLÜM 3 — TAM DENEYSEL KAYIT (BÜTÜN VERİLER)

### 3.1 PPO çöküşü ve stabilizasyon
Naif PPO çöktü: KL divergence → −2000, ppo_loss → 110, değerlendirme → %0. İki neden: (i) greedy rollout (do_sample=False) importance-sampling oranını dejenere eder; (ii) lr=1.4e-5'te policy ~150 optimizer adımında KL kararsızlığına sürüklenir, sıfıra yakın eğitim ödülünden ötürü (135M model sampling'de nadiren parse-edilebilir A/B üretir). Fix: do_sample=True, lr=4e-6, rollout temperature 0.7. İki otomatik koruma: ppo_loss>5 olunca round-içi abort; OOD best'ten ≥20 pp düşünce round-sonu durdur + best-checkpoint.

### 3.2 Sonuç 1 — Saf-ödül PPO, SmolLM-135M (üç seed)
| Seed | Baseline OOD | Best OOD | @round | Trajektori (OOD) |
|---|---|---|---|---|
| 42 | 24.0% | 72.0% | 1 | 24→72→72 (r4 over-training çöküşü 0'a) |
| 43 | 24.0% | 72.0% | 1 | 24→72→56 |
| 44 | 24.0% | 68.0% | 2 | 24→40→68 (yavaş yakınsayan) |

Ortalama OOD ≈ %71; ID %30→%63–77. **Şans altında** (%24) başlar ve yalnızca ödülden öğrenir. Round 1 (seed 42): ID 30→77%, OOD 24→72% (+48 pp), ortalama ödül −0.39→+0.44. Yakınsama sonrası policy round 4'e doğru çöküşe sürüklenir (best-checkpoint alınmazsa); collapse-guard bunu yönetir.

### 3.3 Sonuç 1 — Saf-ödül PPO, Qwen2.5-0.5B (aynı prosedür)
| Öğrenme oranı | Baseline OOD | Trajektori | Etki |
|---|---|---|---|
| 4e-6 | 68% | 48% @r1 → guard durdurdu | −20 pp (bozuldu) |
| 1e-6 | 76% | 64% @r1 → 16% @r2 → guard | −60 pp (çöküş; ID → %1) |

Qwen **şans üstünde** (≈%72–76 OOD eğitimsiz) başlar ve aynı prosedür onu her iki öğrenme oranında da bozar; 10× düşük lr çöküşü yalnızca bir round geciktirir. İki model ≈%72 OOD'ye **zıt yollardan** ulaşır (135M öğretildi; Qwen hasar gördü). Ödül-yargıç gürültüsü: aynı eğitimsiz Qwen baseline'ı iki koşuda %68 ve %76 ölçüldü (n=25'te ≈ ±8 pp).

### 3.4 Sonuç 2 — Qwen2.5-0.5B üzerinde DPO (Gerçeklik tercih verisi)
Gerçeklik DPO seti relabel'dan kuruldu: **714 temiz +1/−1 çift** (A/B randomize), 643 train / 71 test; $0 (relabel yeniden kullanıldı). Görev PPO ile aynı ([REALITY] A/B). Eval (a) = 71 test çiftinde chosen-vs-rejected logprob doğruluğu; eval (b) = generate+judge OOD (PPO ile aynı 25).

| Koşu | ID logprob doğr. | ortalama log-margin | OOD generate+judge | eğitim |
|---|---|---|---|---|
| nazik: 2 epoch, lr 1e-5, β 0.1 | 46.5 → **53.5** (+7 pp) | +0.045 → +0.162 | 72 → **72** (Δ0) | loss 0.693→0.687, çöküş yok |
| güçlü: 5 epoch, lr 3e-5, β 0.1 | 46.5 → **84.5** (+38 pp) | +0.16 → **+20.2** | 68 → **68** (Δ0, parsed 25/25) | loss 0.69→0.26, rewards/acc 0.92, çöküş yok |

DPO Qwen'i çökertmiyor (PPO'nun aksine). Güçlü koşu içsel tercihi muazzam oynatıyor (log-margin +20) ama greedy OOD davranışı her senaryoda değişmiyor — temiz bir **tercih–davranış ayrışması**.

### 3.5 Sonuç 3 — Flip-eval (belirleyici test)
31 çatışma senaryosu (immoral_action Gerçeklik'te daha iyi; değer konvansiyonel etiketle çelişiyor). A/B randomize; ground truth relabel'dan; yargıç çağrısı yok.

| Model | Flip YBF-hizalı |
|---|---|
| Qwen-0.5B base | 15/31 = %48.4 |
| Qwen-0.5B + güçlü DPO | 11/31 = **%35.5 (Δ −12.9 pp)** |

DPO modeli çatışmalarda **daha kötü** yaptı. Veri setinin yüzey korelatını öğrendi ("konvansiyonel-ahlaki olanı seç"), bu eğitim çiftlerinin %97.6'sını tatmin eder; %2.4'lük çatışmalarda kestirme yanlıştır ve daha güçlü eğitim onu büyütür. (3.4'teki) +38 pp in-distribution kazanç bu nedenle örtüşen çoğunluğun ürettiği bir **serap**tı — yalnızca çatışma seti proxy'yi açığa çıkardı.

### 3.6 Sonuç 4 — Constitutional (in-context) uygulama, yetenek eşiği
Tanım anayasa olarak + chain-of-thought + A/B, aynı 31 flip'te.

| Model | Flip YBF-hizalı |
|---|---|
| Qwen-7B, anayasasız | 7/31 = %22.6 |
| Qwen-7B + anayasa | 13/31 = %41.9 |
| Qwen-14B + anayasa | 13/31 = **%41.9 (7B ile birebir)** |
| **Claude Sonnet 4.5 + anayasa** | 27/31 = **%87.1** |

Anayasa her modele yardım eder (+19–23 pp) ama 7B ve 14B %42'de (şans altı) platoya takılır, birebir aynı puanı alır — parametre ikiye katlamak hiçbir şey eklemez — frontier model ise %87'ye sıçrar. Çatışmalarda nüanslı değer akıl yürütme kapasitesi kademeli ölçeklenme yerine bir **eşikte emerge** ediyor görünür. Flip etiketleri bağımsız bir yargıçtan (Haiku) geldiğinden, Sonnet'in %87'si cross-model uyumdur ve flip'lerin yargıca-özgü değil tutarlı olduğunu doğrular.

### 3.7 Eşlik eden eksen (bağlam için)
Sınır (Boundary) ekseni canonical olarak tanımlandı ve 1.200 senaryoda Haiku ile yeniden etiketlendi (1.198 puanlandı; 47 flip, 1.113 decisive). Gerçeklik'ten biraz daha çatışma-zengin (%4.2 vs %3.3 flip), ilişkisel bir eksen olarak konvansiyondan daha çok ayrılmasıyla tutarlı. Eksenler-arası kalibrasyon (bir ekseni eğitmek diğerine transfer olur mu?) ve eksen-bazlı constitutional değerlendirme sıradaki deneylerdir.

---

## BÖLÜM 4 — YORUM & SINIRLAR

**Yorumlar.** (i) *Bilgi ≠ kalibrasyon*: daha büyük bir ön-eğitilmiş model daha çok bilir ama belirli bir değer çerçevesine daha iyi kalibre olmaz; boş bir modeli öğreten RL, bilgili olanı bozar. (ii) *Tercih ≠ davranış*: DPO içsel tercihi keyfî olarak uzağa taşıyabilir ama greedy çıktıyı değiştirmeyebilir — tercih/ödül-modeli skorlarına (üretilen eyleme değil) dayalı her hizalama değerlendirmesi için bir uyarı. (iii) *Değer ≠ proxy*: bir değer daha ucuz bir yüzey korelatıyla bir arada bulununca, optimizasyon korelatı bulur; bunu yalnızca bir çatışma seti tespit eder. Çatışmaların açık rubric'le bir 14B model için bile zor olması, çerçevenin konvansiyonel ahlaktan gerçekten ayrı olduğunun — onun yeniden-etiketlenmesi olmadığının — pozitif kanıtıdır. (iv) *Ürün yolu*: frontier bir modelde Constitutional prompting (%87) kullanılabilir bir değer-hizalı sisteme giden uygulanabilir rotadır; kaldıraç, anayasadır (bir metin çıktısı).

**Sınırlar.** Çatışma seti n=31 (frontier sonucu güçlü ama daha büyük, çok-eksenli bir korpusta replike edilmeli); stokastik OOD yargıcı (n=25'te ≈ ±8 pp; etkiler bunu aşar); Qwen sonuçları tek-seed (135M üç-seed); tek eksen, tek veri seti (Moral Stories); constitutional sonuçlar in-context uygulamayı gösterir, ağırlığa-içselleştirmeden daha zayıf bir iddia (küçük-model sonuçları öğrenilebilirlik üzerine daha güçlü kanıttır); eşik üç ölçek noktasıyla karakterize edildi (7B, 14B, frontier).

---

## KAYNAKLAR / ÇIKTILAR
- LCP Alignment Teknik White Paper v0.4.11 (§3.12 PPO ölçek-asimetri sonucunu kapsar).
- Kod & veri: github.com/Guru35/ybf-toy-experiment
- Zenodo: DOI 10.5281/zenodo.20599906 (concept 10.5281/zenodo.20599905)
- Tekrarlanabilirlik: seed=42; PPO TRL 0.11.4 / transformers 4.46.3; DPO TRL 1.5.x; ≤14B için A100 (Colab); Haiku yargıcı ve Sonnet constitutional policy için Anthropic API.
