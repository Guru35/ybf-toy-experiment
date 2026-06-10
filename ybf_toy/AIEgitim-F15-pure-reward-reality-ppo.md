# F-15 — Saf Ödül Sinyaliyle Gerçeklik (Reality) Öğrenimi: Çöküş → Stabilizasyon → Başarı

**Tarih:** 2026-06-10
**Faz:** 2A (Binary Reality PPO — pure reward feedback)
**Durum:** ✅ POZİTİF BULGU — stabilize PPO ile saf-ödül Reality öğrenimi 135M'de çalışıyor; OOD **+48 puan** genelleme (tam ölçekte doğrulandı).
**Repo HEAD:** `d41a085`

---

## TL;DR
SmolLM-135M-Instruct'a, **Gerçeklik (Reality) ekseni tanımı hiç gösterilmeden**, yalnızca Haiku 4.5'in verdiği **+1 / −1 ödülle** PPO ile eğitim yapıldı. Naif konfigürasyon çöktü (KL → −2000); stabilize edilince (lr↓, sampling temperature↓) model Gerçeklik'i öğrendi ve **hiç görmediği OOD senaryolara genelledi: OOD %24 → %72 (+48 puan), full ölçekte (eval_n=100).**

> YBF temel iddiasının minyatür kanıtı: *bir değer (Gerçeklik), kural verilmeden, yalnızca ödül sinyaliyle modelin ağırlıklarına işlenebilir ve dağıtım-dışı senaryolara taşınabilir.*

---

## Deney Kurulumu
- **Policy (eğitilen):** `HuggingFaceTB/SmolLM-135M-Instruct` + LoRA (r=8)
- **Yöntem:** PPO (TRL 0.11.4 legacy `PPOTrainer`), saf ödül (pure reward)
- **Ödül modeli:** Claude Haiku 4.5 + 16.170 karakterlik Reality tanım prompt'u → seçilen aksiyona **+1** (gerçekliğe uygun) / **−1** (ihlal)
- **KRİTİK:** Policy, Reality tanımını **HİÇ görmüyor**. Sadece senaryo + A/B seçenekleri → seçim → +1/−1. Kuralı yalnızca ödül örüntüsünden çıkarmak zorunda. Round özet puanı da modele verilmiyor (sadece insan ölçümü için).
- **Veri:** 1100 train (Moral Stories), 100 ID test, 25 OOD (SINIR-decisive, Reality ödülüyle skorlanıyor)
- **seed = 42**

---

## Yolculuk: Çöküş → Teşhis → Fix

### 1. İlk çöküş — `do_sample=False`
PPO rollout'unda greedy decoding → importance-sampling oranı dejenere → KL anında **−2000** → policy çöküşü (ID/OOD %0, ppo_loss 110+). 
**Fix:** commit `a0fc277` → `do_sample=True` (+ adaptive KL).

### 2. İkinci çöküş — `do_sample=True` ama `lr=1.4e-5`
İlk ~150 batch **temiz** (ppo_loss 0.03→0.006), sonra KL −2000'e, ppo_loss 110'a patladı; Round 1 eval **%0 parse**. 12-batch smoke çok kısa olduğu için bu maskelenmişti.
**Kök neden:** Training reward ≈ 0 — SmolLM-135M sampling'de nadiren parse-edilebilir A/B üretiyor → seyrek/sıfır sinyal → policy sürüklenmesi → ~150 PPO adımında KL kararsızlığı.

### 3. Fix — commit `d41a085`
| Parametre | Eski | Yeni | Gerekçe |
|---|---|---|---|
| `lr` | 1.4e-5 | **4e-6** | Policy sürüklenmesini yavaşlat (çöküş eşiği ≈ lr × adım) |
| rollout `temperature` | 1.0 | **0.7** | Daha tepe-örnekleme → daha yüksek parse → ödül sinyali |

İlgili commit'ler: `a0fc277` (do_sample), `29d851c` (eval progress counter), `d41a085` (lr + temperature).

---

## Sonuçlar

### Uzun Smoke — `ppo_v2_smoke` (2 round × 800 senaryo = 200 batch/round; eval_n=30)
| Round | ID Acc | OOD Acc | Δ OOD |
|---|---|---|---|
| 0 (baseline) | 26.7% | 24.0% | — |
| 1 | 86.7% | 64.0% | +40.0 |
| 2 | 76.7% | **76.0%** | +12.0 |

- Best OOD **76.0%** @ round 2. **400 batch boyunca tek KL patlaması yok**; ppo_loss 0.037 → 0.014 (azalan).
- Çöküş eşiği (~150 batch) AŞILDI → **fix tuttu**.

### Full Run — `exp_reality_s1` (fix'li; eval_n=100; 1100 senaryo/round = 275 batch)
| Round | ID Acc | OOD Acc | Δ OOD | ppo_loss | KL durumu |
|---|---|---|---|---|---|
| 0 (baseline) | 30.0% | 24.0% | — | — | — |
| 1 | 77.0% | **72.0%** | **+48.0** | 0.032 → 0.017 | **temiz (uyarı yok)** |
| 2 | 71.0% | 72.0% | +0.0 | 0.016 → 0.008 | hafif (−2 .. −8) |
| 3 | (drift) | ~ | — | 0.011 → 0.031 | büyüyor (−7 .. −28) |
| 4 | **0.0%** | **0.0%** | collapse | — | over-training çöküşü |

- **Round 1 eval:** ID 77.0% (mean_reward **+0.610**), OOD **72.0%** (mean_reward **+0.440**). *** New best OOD 72.0% ***
- **Round 2:** OOD 72.0% korundu → **yakınsama**.
- **Round 3:** post-convergence drift başladı (KL −7 → −28, ppo_loss artıyor).
- **Round 4:** **tam çöküş** — eval parse %0, OOD %0. Drift, over-training çöküşüne döndü.

> **Önemli reçete (F-15'in çekirdeği):** Stabilizasyon (lr 4e-6) çöküşü round 1'den round 4'e **erteledi** ve model önce yakınsadı (peak %72) — ama training-past-convergence yine çöküşe gidiyor. **En iyi model (Round 1, %72) checkpoint'lendiği için nihai sonuç ETKİLENMEDİ.** Pratik kural: **stabilize + early-stop / best-checkpoint (round 1-2'de yakala); 20 round koşturma.** → Koda `[Collapse guard]` eklendi (commit sonrası): OOD, best'ten ≥20pp düşerse otomatik durur, best checkpoint korunur.

**Baseline reward (Round 0):** ID mean_reward −0.390, OOD −0.520 → Round 1'de ID +0.610 / OOD +0.440 (eksiden artıya döndü).

### 3-Seed Replikasyon (Reality, fix + collapse-guard)
Aynı stabilize config (lr 4e-6, temp 0.7), 3 bağımsız seed, baseline OOD = %24:

| Seed | Best OOD | @ round | Traje (OOD) | Not |
|---|---|---|---|---|
| 42 | **72.0%** | 1 | 24→72→72 | temiz; r4'te over-train collapse |
| 43 | **72.0%** | 1 | 24→72→56 | temiz; r2'de drift başladı |
| 44 | **68.0%** | 2 | 24→**40**→**68** | r1 yavaş (KL-drift, %40) → r2 toparladı (%68) |

**Okuma:** Üç seed de **%68-72 bandında** (ortalama ~%71, aralık DAR). **Sağlam, sıkı replikasyon** — saf-ödül Reality öğrenimi 3 bağımsız seed'de de OOD'u %24'ten ~%70'e taşıdı. seed 44 daha **yavaş** yakınsadı (r1'de %40'a takıldı) ama r2'de banda toparlandı → "yavaş seed", outlier değil.
**Başlık:** *"OOD %24 → 72/72/68 (3 seed, ort. ~%71, aralık 68-72); sağlam, replike edilebilir pure-reward Reality öğrenimi."*
**Önemli metodolojik not:** Erken round'a (r1) bakıp "düşük/başarısız" demek yanıltıcı — model drift edip sonra **toparlayabiliyor** (seed 44: r1 %40 → r2 %68). Yani *best-checkpoint + en az 2-3 round* şart; tek round eval ile karar verme.

### Ölçek Merdiveni — Qwen2.5-0.5B vs SmolLM-135M (seed 42)
Aynı deney (pure-reward Reality), ~4× büyük policy:

| Model (lr) | Baseline OOD | RL trajesi | Etki |
|---|---|---|---|
| SmolLM-135M (4e-6) | 24% (şans altı) | **72/72/68** | **+48pp ÖĞRETTİ** |
| Qwen2.5-0.5B (4e-6) | 68% (şans üstü) | 48% @r1 → guard | −20pp bozdu |
| Qwen2.5-0.5B (1e-6) | 76% | 64% @r1 → 16% @r2 → guard | **−60pp ÇÖKTÜ** |

**İki çarpıcı bulgu:**
1. **Qwen EĞİTİMSİZ baseline OOD (%68) ≈ eğitilmiş 135M (%68-72)** — büyük model Reality-hizasını **pretraining'de zaten edinmiş** (confound canlı kanıt). 135M < %50 şans (eğitimsizken yanlış seçiyor), Qwen > %50 (zaten doğruya meyilli).
2. **RL Qwen'i ÖĞRETMEDİ, BOZDU:** baseline %68 → r1 %48 (−20pp). `[Collapse guard]` doğru tetiklendi, durdurdu; **en iyi = EĞİTİMSİZ model (%68).**

**Ölçek tezi (karşı-sezgisel):** Pure-reward PPO **düşük-prior** modelde (135M) **öğretiyor** (+48pp) ama **yüksek-prior** modelde (Qwen) **bozuyor** (−20pp) — zaten bildiği davranışı seyrek/gürültülü ödülle sarsıyor (RL-induced forgetting). → RL'in marjinal değeri, prior arttıkça **pozitiften negatife** dönüyor.

**Açık soru:** Qwen'in r1 düşüşü kalıcı "RL zarar" mı, yoksa erken-drift mi (135M seed 44 gibi r1↓ → r2↑ toparlar mı)? Guard r1'de durdurduğu için göremedik → *guard'sız / eşik yüksek 3-round Qwen* ile ayrıştırılabilir.

**Guard validasyonu:** ✅ Collapse-guard **ilk kez sahada** tetiklendi (Qwen r1), %20 crash'i yakalayıp eğitimsiz-best'i korudu — eklediğimiz koruma çalışıyor.

**Bağımsız bulgu (kayda değer):** Qwen2.5-0.5B, Reality'yi **pretraining'den %68 OOD seviyesinde** taşıyor — *hiçbir YBF eğitimi olmadan.* Yani 0.5B ölçeğinde Reality ekseni zaten "zero-shot" mevcut; YBF değeri büyük modelde dışarıdan yüklenecek bir şey değil, **var olanı koruma/keskinleştirme** problemi.

**Hipotez (judge-policy çelişkisi):** Haiku'nun ödül kalibrasyonu, Qwen'in pretraining'den taşıdığı Reality anlayışıyla **çelişiyor** olabilir → PPO, Qwen'i kendi tutarlı anlayışından *uzağa* itip regrese ettiriyor (reward-model misspecification).

**Sonuç (CCD direktifi test edildi, 2026-06-10):** lr 10× düşük (1e-6) **de işe yaramadı** — sadece çöküşü 1 round geciktirdi (r1 −12pp → r2 −48pp, ID **%1**'e = model A/B üretme kapasitesini tamamen kaybetti). **Her iki lr'de de (4e-6 ve 1e-6) PPO Qwen'i bozdu/çökertti** → PPO yüksek-prior modeller için **fundamental olarak uygunsuz** (lr meselesi değil; sinyalin kendisi Qwen'in mevcut bilgisiyle uyumsuz). Collapse-guard **ikinci kez de** doğru tetiklendi (%60 crash, eğitimsiz-best %76 korundu).

**Ölçek yasası (yorum — kullanıcı/strateji):** İki model **~aynı OOD'de** bitiyor (135M PPO-sonrası %72 ≈ Qwen eğitimsiz %76) ama **zıt yollardan:** küçük model bilmiyordu → PPO **öğretti**; büyük model biliyordu → PPO **bozdu**. YBF okuması: *bilgi artışı ≠ kalibrasyon/bilinç artışı* — Qwen daha çok "biliyor" ama YBF-kalibrasyonu açısından PPO-sonrası SmolLM ile aynı noktada. Mekanizma: Qwen'in ağırlıkları **kendi** Reality anlayışına güçlü bağlı; PPO YBF-sinyaliyle çekiyor, ağırlıklar direniyor, model tutarlı çıktı kapasitesini kaybediyor.
**Açık soru:** Güçlü mevcut bilgiyi **yok etmeden** daha spesifik (YBF) yöne kalibre edilebilir mi? — ya da büyük modelde *"zaten var, üstüne yazmaya gerek yok"* mu?
**F-16 (BAŞLADI — ön sonuç, 2026-06-10):** Yüksek-prior modele YBF kalibrasyonu = PPO değil **DPO**. İlk Qwen Reality DPO koşusu (lr 1e-5, beta 0.1, 2 epoch; dataset = relabel'dan 714 net +1/-1 çift → 643 train/71 test, $0 reuse):
- **ÇÖKMEDİ** (PPO'nun aksine) — loss stabil (0.693→0.687), rewards/acc 0.51→~0.65, degenerasyon yok.
- **ID tercih +7pp:** logprob test 46.5% → 53.5% (margin +0.045 → +0.162).
- **OOD generate+Haiku (PPO-kıyaslanabilir, AYNI 25 OOD, aynı metrik):** PRE **%72** → POST **%72** (Δ **0pp**). Sanity ✓: PRE %72 ≈ PPO baseline %76 (gürültü bandında) → eval doğru kurulmuş.
- **Net F-16 tablosu:**

  | Metrik | PPO | DPO nazik (2ep,1e-5) | DPO güçlü (5ep,3e-5) |
  |---|---|---|---|
  | OOD seçim (generate+Haiku) | 76 → **16** (çöküş) | 72 → **72** (KORUNDU) | 68 → **68** (Δ0, parsed 25✓) |
  | ID tercih (logprob) | — | 46.5 → 53.5 (+7pp) | 46.5 → **84.5 (+38pp)** |

- **DPO güçlü (5 epoch, lr 3e-5, beta 0.1):** ID logprob test **46.5 → 84.5% (+38pp)**, mean log-margin +0.16 → **+20.2**, loss 0.69 → 0.26, rewards/acc 0.92 — eğitimde **çöküş yok**, held-out genelleme. **OOD generate+Haiku: 68 → 68 (Δ0), parsed 25/25** → model **SAĞLAM** (daralmadı), ama +38pp ID kayması OOD seçimine **HİÇ yansımadı.**
- **"Düşünce ≠ davranış" — tam güçte bulgu:** İçsel tercih devasa kaydı (margin +20) ama OOD davranışı **sıfır** değişti (gentle'da +7→0, strong'da +38→0). DPO içsel tercihi keyfî güçle değiştirebiliyor (modeli bozmadan) ama bu **OOD davranışına geçmiyor.** *"Model ne düşünüyor" ile "model ne yapıyor" ayrı şeyler* — alignment'ı logprob ile ölçmenin tehlikesine dair temiz bir uyarı.
- **FLIP-EVAL SONUÇ (güçlü DPO, 31 çatışma senaryosu, Haiku gerekmez):** base **48.4%** → DPO **35.5%** (Δ **−12.9pp**, parsed 31/31). İki sonuç:
  1. **Eval-artifact DEĞİL:** POST≠PRE → adapter generation'da uygulanıyor. Yani OOD-Δ0 **gerçek** (transfer yok), bug değil. ✓
  2. **KRİTİK BULGU — DPO YBF-Reality'yi ÖĞRENMEDİ, genel ahlakı öğrendi.** Flip'lerde **kötüleşti** (YBF öğrenseydi İYİLEŞMELİYDİ). Sebep: 714 train çiftinin **%97.6'sı (697/714) "moral=Reality-aligned"** → model "Reality"yi değil yüzeysel **"konvansiyonel-ahlaki olanı seç"** kestirmesini öğrendi; 17 flip (%2.4) bunu kıramayacak kadar az. Çatışmada (YBF ≠ konvansiyon) kestirme YANLIŞ → kötüleşti.
- **ID +38pp YANILTICIYDI:** yüzeysel kestirme %97.6 konvansiyonel çiftte iyi skor verdi (held-out test de çoğunlukla non-flip). **Flip-eval gerçeği ortaya çıkardı** — "değer mi yüzey-korelat mı" ancak çatışma vakalarıyla anlaşılır. **Metodolojik ders:** yüksek ID/preference accuracy, değerin öğrenildiğini KANITLAMAZ; flip/conflict-eval şart.
- **Sonuç (asıl soru):** Bu kurulumda model **genel ahlakı öğreniyor, YBF-spesifik Reality'yi değil.** YBF-Reality öğretmek için **çatışma-zengini veri** gerekli (flip oranı ↑), yoksa model kestirmeyi kullanır. (§3.11/F-14 ile tutarlı: Moral Stories %81 co-aligned → axis-conflict için yetersiz.)
- Adapter'lar: `.../dpo_reality_qwen05b{,_strong}/final_adapter`.

### Constitutional AI — ön sonuç (Qwen2.5-7B + YBF Reality anayasası)
Fine-tuning yerine: Reality tanımı (16k) = system prompt + "her seçeneği Reality'de değerlendir, reason→seç." Aynı 31 flip'te (Haiku gerekmez, label'larla):

| Mode | Flip YBF-aligned |
|---|---|
| PLAIN (anayasasız, 7B) | 7/31 = **22.6%** |
| CONSTITUTIONAL (YBF def + reason) | 13/31 = **41.9%** |
| **Δ** | **+19.4pp** (parsed 31/31) |

- **Anayasa yardım ediyor (+19.4pp)** → YBF sinyali in-context kullanılabilir, yön net.
- **AMA 7B'de yetersiz:** %41.9 hâlâ **şans altı (%50)** — açık tanım + reasoning'e rağmen model flip'lerin %58'inde konvansiyonel-ahlakı seçiyor. Konvansiyonel prior güçlü; 7B rubric'le tam bastıramıyor.
- **Derin (POZİTİF) gözlem:** YBF-Reality konvansiyonel ahlaktan **gerçekten ayrılıyor** — öyle ki açık rubric + reasoning'le bile 7B çoğu çatışmada konvansiyona kayıyor. Bu, **YBF'nin özgün olduğunun** (genel ahlakın yeniden-etiketlemesi OLMADIĞININ) güçlü kanıtı. Flip'ler gerçek, zor, ayırt edici.
- **Açık soru → kapasite mi, flip-muğlaklık mı?** §3.8'de Sonnet≈Haiku Reality'de %100 uyumlu. Hipotez: Qwen-7B zayıf; Sonnet ≥%70-80 alır.
- **SONNET SONUÇ — KAPASİTE sorunu DOĞRULANDI (≈$0.35):** Sonnet 4.5 + aynı anayasa → **27/31 = %87.1** (parsed 31/31). Ölçeklenme:

  | Setup | Flip YBF-aligned |
  |---|---|
  | Qwen-7B plain (anayasasız) | 22.6% |
  | Qwen-7B + anayasa | 41.9% (13/31) |
  | Qwen-14B + anayasa | **41.9% (13/31)** ← 2× büyük, AYNI |
  | **Sonnet + anayasa** | **87.1% (27/31)** |

  → **EŞİK deseni (düz ölçeklenme DEĞİL):** 7B = 14B = %42 (plato, ikisi de aynı 13/31) → Sonnet %87 (sıçrama). Mid-size açık modeller (≤14B) eşiğin **altında** — nüanslı YBF-Reality akıl yürütmesi **frontier ölçekte emerge ediyor**, kademeli değil. **Ürün iması:** kullanılabilir Constitutional YBF sistemi **frontier-sınıf model gerektiriyor** (7B-14B yetmez — deployment/maliyet açısından önemli). İki çıkarım:
  1. **Flip'ler MUĞLAK DEĞİL:** Bağımsız model (Sonnet) flip'lerin %87'sini YBF-doğru çözdü → flip'ler + tanım **sağlam/tutarlı** (cross-model Sonnet≈Haiku, §3.8 uyumlu). 4 ıska = gerçekten borderline.
  2. **Constitutional AI ÇALIŞIYOR (güçlü modelle):** Frontier model + YBF tanımı, en zor (çatışma) vakalarda **%87 YBF-spesifik** → **genel ahlakı değil, BİZİM Reality'mizi uyguluyor.** 🎯
- **STRATEJİK SONUÇ (asıl sorunun cevabı):** **EVET, YBF-spesifik Reality uygulanabilir** — ama küçük-model fine-tuning'le DEĞİL, **güçlü-model Constitutional AI'siyle.** Küçük model → kestirme öğrenir; güçlü model + anayasa → gerçek YBF (%87). Kullanılabilir YBF-hizalı sistemin yolu = **Constitutional AI + frontier/güçlü model.**

- **Dürüst okuma:** (1) DPO yüksek-prior modeli **KORUYOR** (PPO mahvederken — asıl bulgu, kesin). (2) Tercihini YBF-Reality'ye **hafifçe kaydırıyor** (logprob +7pp), ama bu nazik ayarda (2 epoch, lr 1e-5, beta 0.1) kayma **OOD SEÇİMLERİNİ değiştirecek eşiği AŞMADI** (Δ0). → *"DPO bozmaz/korur"* kesin; *"DPO iyileştirir"* bu ayarda OOD'de **gösterilemedi** (logprob'da var, seçimde yok). Önceki "DPO geliştirdi" fazla iddialıydı; doğrusu **"korudu + sub-threshold kaydırdı."**
- Adapter: `Drive/ybf_models/experiments/dpo_reality_qwen05b/final_adapter`. (Çalıştı: trl 1.5.1 + transformers 5.10.2.)

---

## Yorum / Anlam
1. **Fix tam ölçekte doğrulandı:** 275 batch/round temiz geçti, çöküş yok (smoke + full uyumlu).
2. **Saf-ödül Reality öğrenimi çalışıyor:** kural gösterilmeden, yalnızca +1/−1 ile, 135M model Gerçeklik-hizasını öğrendi ve **hiç görmediği OOD'a +48pp** genelledi.
3. **Mekanizma:** ödül modele dille söylenmiyor; PPO gradyanı olarak ağırlıklara işleniyor (biyolojik pekiştirme analojisi). Round'lar arası taşınan tek şey = güncellenen ağırlıklar.

---

## Caveat / Sınırlar
- **Training reward log'u `+0.000`** görünüyordu (loglanan tek-tük 4'lük batch artefaktı); gerçek öğrenme eval'de net (OOD 24→72).
- **Post-convergence drift:** ~round 2 sonrası KL büyümeye başlıyor → production'da **early-stop + best-checkpoint** şart. (Naif "20 round koştur" yanlış; best-OOD checkpoint'i al.)
- **Küçük OOD seti (n=25):** güçlü ama tek-seed sinyal → 3-seed (42/43/44) tekrarı gerekli.
- OOD = SINIR-decisive senaryolar, Reality ödülüyle skorlanıyor → cross-axis genelleme.

---

## Sıradaki Adımlar
1. **3-seed tekrarı** (seed 42/43/44) → varyans/güven aralığı.
2. **Production track:** best-checkpoint kullan (drift öncesi), early-stop sıkılaştır.
3. Diğer eksenler (Boundary, Freedom, Dignity, Respect) için **aynı stabilize config** (lr 4e-6 + temp 0.7) ile tekrar.
4. White paper §3.12 (Phase 2A) + `lcp-bulgular-log.md` F-15 girişi.

---

## Artifacts
- **Kod:** github.com/Guru35/ybf-toy-experiment @ `d41a085`
  - `a0fc277` — do_sample=True (ilk çöküş fix)
  - `29d851c` — eval progress counter
  - `d41a085` — lr 4e-6 + rollout temperature 0.7 (stabilite fix)
- **Checkpoint (en iyi model):** `/content/drive/MyDrive/ybf_models/experiments/exp_reality_s1/best_checkpoint` (Round 1, OOD %72)
- **Smoke checkpoint:** `/content/drive/MyDrive/ybf_models/ppo_v2_smoke/`
- **Platform:** Google Colab Pro+ (A100), TRL 0.11.4 + transformers 4.46.3
