# Compute Alternatives — Modal Free Tier Sonrası Plan

**Aktif sağlayıcı:** Modal ($30/ay free credit)
**Bu doküman ne için:** Modal credit'i tükendiğinde takip edilecek alternatif yol.
**Son güncelleme:** 2026-06-09
**Status:** Plan iskeleti — Modal bitince detaylar genişletilir.

---

## 1. Şu Ana Kadar Modal Harcaması (canlı takip)

```
2026-06-08  Faz 3 DPO (SmolLM-135M, full)    ~$0.50
           ─────────────────────────────────────
Toplam:                                       $0.50 / $30 limit
Kalan free credit:                            ~$29.50
```

**Beklenti:** Modal free tier ile şu deneyler sığacak:
- TinyLlama-1.1B DPO: ~$2
- SmolLM-360M cross-val: ~$1
- Pythia-1.4B replication: ~$3
- 5-axis sweep cross-LM (Llama/Mistral) ~$3
- Variance bands (3-5 seed): ~$5
- **Toplam:** ~$14 → free tier rahatlıkla kapsıyor

---

## 2. Free Tier Bitince Migration Tetikleyici

Şu durumların biri olduğunda RunPod'a geç:

1. `modal app list` → "Credit exhausted" / billing warning email
2. Yeni deney başlatamıyorsun (quota hata)
3. Aylık $50+ training harcama hedefliyorsun

---

## 3. Alternatif #2: RunPod (önerilen)

### Neden RunPod?

- A100 40GB community cloud saat başı **$0.79** (Modal'ın ~yarısı)
- $10 sign-up credit (~5 küçük deney)
- Setup süresi 15-30 dk (Modal'a göre biraz daha karmaşık ama makul)
- Jupyter notebook UI — kolay
- Persistent pods (kapanmıyor session arası) → debugging kolay

### Setup Adımları (Migration günü)

```bash
# 1. Hesap aç + $10 credit talep et
#    https://runpod.io → sign up → top-up section

# 2. Pod template seç:
#    - "PyTorch 2.4 with CUDA 12.1"
#    - GPU: RTX A4000 (16GB) veya A100 40GB
#    - Storage: 30 GB volume

# 3. Pod başlat → SSH veya Jupyter URL al

# 4. Pod içinde:
git clone https://github.com/Guru35/ybf-toy-experiment.git
cd ybf-toy-experiment/ybf_toy

# Pre-installed olarak torch + transformers + peft + trl + datasets gelir
# (PyTorch image bunları içerir)
pip install --quiet trl peft datasets bitsandbytes

# 5. ANTHROPIC_API_KEY env var olarak set et (RunPod UI'dan)
#    Settings → Secrets → ANTHROPIC_API_KEY

# 6. Training script çalıştır — Modal wrapper YOK, direkt:
python ybf_dpo_train.py --model HuggingFaceTB/SmolLM-360M --epochs 3

# 7. Sonuçları indir:
#    Jupyter file browser → download
#    veya scp ile pod'dan lokal'e
```

### Modal'dan RunPod'a Geçişte Kod Farkı

| Modal | RunPod |
|---|---|
| `@app.function(gpu="T4")` decorator | Decorator YOK — direkt `python script.py` |
| `train_dpo.remote(quick=True)` | `python ybf_dpo_train.py --quick` |
| Modal volume için yazma | Pod'un kendi disk'i (30GB volume) |
| Sonuç indir: `result = train_dpo.remote()` | scp veya Jupyter UI download |

**`ybf_dpo_train.py` orijinal Modal wrapper'sız version** — RunPod'da değiştirmeden çalışır. **`ybf_dpo_modal_v2.py` Modal-specific** — RunPod'da silinir.

### Maliyet Tahminleri (RunPod community A100)

| Deney | Süre | Maliyet |
|---|---|---|
| SmolLM-135M DPO | 10 dk | $0.13 |
| SmolLM-360M DPO | 15 dk | $0.20 |
| TinyLlama-1.1B DPO | 30 dk | $0.40 |
| Pythia-1.4B DPO | 45 dk | $0.60 |
| Llama-3.2-1B DPO | 35 dk | $0.46 |
| Llama-3.2-3B DPO | 2 saat | $1.60 |
| Mistral 7B QLoRA | 6 saat | $4.74 |

$10 sign-up credit → yaklaşık 20-25 küçük deney veya 2 büyük deney.

---

## 4. Alternatif #3: Lambda Labs (eğer RunPod yetmezse)

- A100 40GB **$1.10/saat** (dedicated, RunPod community'den biraz pahalı ama daha stabil)
- En temiz ML-specific dashboard
- 24/7 destek
- Free credit zaman zaman promosyon — gel-git
- Modal'dan migration kolay, RunPod ile aynı (PyTorch image + script)

**Bu adım sadece:** RunPod'da sürekli interrupted oluyorsan veya enterprise-grade SLA gerekiyorsa.

---

## 5. Alternatif #4: GCP $300 Free Credit (eğer ciddi production)

- Yeni Google Cloud hesabı: $300 credit, 90 gün
- A100 40GB Vertex AI: ~$2.93/saat
- $300 / $2.93 = ~100 saat A100 ≈ 200-300 küçük deney
- Setup: 30-60 dk (IAM + Vertex AI workbench)
- Sustainable use discount: %20-30 indirim

**Bu adım sadece:** 
- Düzenli haftalık training yapıyorsan
- Multi-region deploy gerekiyorsa
- Production pipeline'a geçeceksen

---

## 6. Alternatif #5: Vast.ai Spot (en ucuz, en az güvenilir)

- A100 spot saat başı $0.30-0.50 — gerçek spot pricing
- Pod'un sahibi (community user) makinesini istediği zaman alabilir → interrupt riski
- Kısa deneyler için OK, uzun training için risky

**Bu adım sadece:** Eğitim 30 dk altında ve checkpoint kaydedebiliyorsan.

---

## 7. Karar Matrisi — Modal Sonrası Hangi Yol?

| Senaryo | Geçilecek sağlayıcı |
|---|---|
| Birkaç deney daha lazım, hızlı/ucuz | **RunPod community** (~$10 yeter) |
| Düzenli aylık deney, stabil ihtiyaç | **Lambda Labs** (~$50-100/ay) |
| Production'a geçeceğim, ciddi yatırım | **GCP** (Vertex AI + $300 credit) |
| Çok ucuz + interrupt'a katlanabilirim | **Vast.ai spot** |
| Apple ekosistemine taşınmak istiyorum | **M-serisi Mac alımı** (~$2000) |

---

## 8. Bana Sorulması Gereken Detaylar (Migration günü)

Modal credit'i bittiğinde:

1. **Şu ana kadar kaç deney yaptık? Aylık ortalama nedir?**
   → Eğer <5/ay → RunPod yeter
   → Eğer 10+/ay → Lambda Labs veya GCP düşün

2. **Production deploy planı var mı?**
   → Evet → GCP'ye geç (multi-region, stable, enterprise)
   → Hayır → RunPod/Lambda yeter

3. **Maksimum deney boyutu ne olacak?**
   → 7B+ → A100 80GB veya H100 gerek → Lambda/GCP
   → 3B altı → RunPod community yeter

4. **Donanım yatırımı düşünüyor musun?**
   → Bütçe $2000+, sık training yapacaksın → Apple Silicon Mac veya RTX 4090
   → Sadece ara sıra → Cloud'da kal

---

## 9. Yapılacaklar (Modal Free Tier'a Yaklaştığımızda)

- [ ] RunPod hesabı aç (sign-up credit'i kazan)
- [ ] PyTorch CUDA image ile test pod başlat (deney yapmadan)
- [ ] `ybf_dpo_train.py`'ın Modal wrapper-free hâlinin RunPod'da çalıştığını verify et
- [ ] Migration runbook'unu (bu doküman) genişlet

Şu an için **hiçbir aksiyon gerekmiyor** — Modal yeterli.

---

## 10. References

- Modal pricing: https://modal.com/pricing
- RunPod pricing: https://www.runpod.io/pricing
- Lambda Labs pricing: https://lambdalabs.com/service/gpu-cloud
- GCP A100 pricing: https://cloud.google.com/compute/gpus-pricing
- Vast.ai: https://vast.ai

---

*Living document. Modal credit bitmek üzere olduğunda buraya bak, kararını ver, migration başlat.*
