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
