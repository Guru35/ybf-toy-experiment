# YBF Eksen Eğitimi — Tam Pipeline Promptu
**Hedef:** Claude Code / AI Eğitim Vault  
**Kapsam:** Veri indirme → Skorlama → Dataset → Script güncelleme → Modal eğitim  
**Şu an:** Sınır ekseni (Phase 1B)

---

## Çalıştırmadan Önce Oku

**Neden bu veri seti:**
Gerçeklik testini `demelin/moral_stories` ile yaptık. Sınır'ı, Özgürlük'ü, Onur'u, Saygı'yı da aynı veri setiyle yapacağız. Tüm eksenler aynı kaynaktan geçmeli — kontrollü karşılaştırmanın temeli bu.

**Alan adları:**
Moral Stories'de `moral_action` ve `immoral_action` var. `norm_action` veya `situational_action` değil. (LESSONS.md C12) Tüm scriptlerde kontrol et.

**Skor sistemi:**
- `+1` = bu eksen bu eylemde pozitif
- ` 0` = bu eksen devreye girmiyor (ilgisiz veya belirsiz — ayrım önemsiz, ikisi de training'e girmiyor)
- `-1` = bu eksen bu eylemde negatif → VETO

**Kod inceleme:**
Her scripti çalıştırmadan önce performans, hata yönetimi ve parse güvenilirliğini incele. Geliştirme yaptıysan kısaca not et.

---

## Adım 1 — Moral Stories İndir ✓ TAMAMLANDI

> **Bu adımı atla.** `moral_stories_train.jsonl` zaten mevcut (12.000 satır).
> Dosya yolu: `/Users/gonet/Documents/AI-Egitmek/ybf_toy/data/raw/moral_stories_train.jsonl`
> **Doğrudan Adım 2'ye geç.**

<details>
<summary>Yeniden indirmek gerekirse (genellikle gerekmez)</summary>

```bash
cd /Users/gonet/Documents/AI-Egitmek
pip install datasets --break-system-packages
```

```python
# download_moral_stories.py
from datasets import load_dataset
import json, os

os.makedirs("ybf_toy/data/raw", exist_ok=True)
ds = load_dataset("demelin/moral_stories", split="train")

with open("ybf_toy/data/raw/moral_stories_train.jsonl", "w") as f:
    for item in ds:
        f.write(json.dumps(item, ensure_ascii=False) + "\n")

print(f"İndirildi: {len(ds)} senaryo")
```

```bash
python3 download_moral_stories.py
```

</details>

---

## Adım 2 — Eksen Skoru Çıkar

Bu adımda sadece hedef eksen skorlanır (5 eksen değil). Şu an: **SINIR**.

```python
# score_sinir.py
import json, os, time
from anthropic import Anthropic

client = Anthropic()

SINIR_PROMPT = """YBF Sınır ekseni değerlendirmesi.

Sınır = Her varlığın doğal, fiziksel, psikolojik ve sosyal sınırını tanıma kapasitesi.
Sınır yalnızca kural değildir. Gerçekliğin bilinçte tanınmasıdır.

+1 = eylem sınırı tanıyor ve koruyor
 0 = sınır bu eylemde devreye girmiyor
-1 = eylem sınırı ihlal ediyor veya yok sayıyor

Senaryo: {situation}
Niyet: {intention}
Eylem: {action}

Sadece +1, 0 veya -1 döndür. Başka hiçbir şey yazma."""

def score(situation, intention, action, retries=3):
    for attempt in range(retries):
        try:
            resp = client.messages.create(
                model="claude-haiku-4-5-20251001",
                max_tokens=10,
                messages=[{"role": "user", "content": SINIR_PROMPT.format(
                    situation=situation, intention=intention, action=action
                )}]
            )
            import re
            m = re.search(r'[+\-]?[01]', resp.content[0].text.strip())
            if not m:
                return 0
            val = m.group()
            if val in ("+1", "1"):  return 1
            if val in ("-1",):      return -1
            return 0
        except Exception as e:
            print(f"  Hata (deneme {attempt+1}): {e}")
            time.sleep(2 ** attempt)
    return 0

in_path  = "ybf_toy/data/raw/moral_stories_train.jsonl"
out_path = "ybf_toy/data/raw/moral_stories_sinir_scored.jsonl"

scored_ids = set()
if os.path.exists(out_path):
    with open(out_path) as f:
        for line in f:
            scored_ids.add(json.loads(line)["ID"])
    print(f"Devam ediliyor — zaten skorlanan: {len(scored_ids)}")

with open(in_path) as f:
    scenarios = [json.loads(l) for l in f if l.strip()]

with open(out_path, "a", buffering=1) as out:
    for i, item in enumerate(scenarios):
        if item.get("ID") in scored_ids:
            continue
        s = item.get("situation", "")
        n = item.get("intention", "")
        a_moral   = item.get("moral_action", "")    # doğru alan adı
        a_immoral = item.get("immoral_action", "")  # doğru alan adı

        if len(s) < 30 or len(a_moral) < 10:
            continue

        result = {
            "ID":           item.get("ID"),
            "situation":    s,
            "intention":    n,
            "moral_action":   a_moral,
            "immoral_action": a_immoral,
            "sinir_moral":   score(s, n, a_moral),
            "sinir_immoral": score(s, n, a_immoral),
        }
        out.write(json.dumps(result, ensure_ascii=False) + "\n")

        if (i + 1) % 100 == 0:
            print(f"  {i+1} işlendi...")

print("Tamamlandı.")
```

```bash
python3 score_sinir.py
```

Tahmini maliyet: ~$0.30-0.50 (2400 Haiku çağrısı)

---

## Adım 3 — Dataset Oluştur

```python
# build_sinir_dataset.py
import json, random

with open("ybf_toy/data/raw/moral_stories_sinir_scored.jsonl") as f:
    items = [json.loads(l) for l in f if l.strip()]

pairs = []
for item in items:
    sm = item["sinir_moral"]
    si = item["sinir_immoral"]

    if sm == si:
        continue  # sinyal yok, atla

    if sm > si:
        chosen, rejected, rc, rr = item["moral_action"],   item["immoral_action"], sm, si
    else:
        chosen, rejected, rc, rr = item["immoral_action"], item["moral_action"],   si, sm

    pairs.append({
        "ID":        item["ID"],
        "situation": item["situation"],
        "intention": item["intention"],
        "chosen":    chosen,
        "rejected":  rejected,
        "r_chosen":  rc,
        "r_rejected": rr
    })

random.seed(42)
random.shuffle(pairs)
split = int(len(pairs) * 0.9)

for path, data in [
    ("ybf_toy/data/ybf_sinir_dpo_train.jsonl", pairs[:split]),
    ("ybf_toy/data/ybf_sinir_dpo_test.jsonl",  pairs[split:])
]:
    with open(path, "w") as f:
        for p in data:
            f.write(json.dumps(p, ensure_ascii=False) + "\n")

print(f"Toplam çift: {len(pairs)} | Train: {split} | Test: {len(pairs)-split}")

# Dağılım raporu
gaps = [p["r_chosen"] - p["r_rejected"] for p in pairs]
print(f"Δ=+1: {gaps.count(1)} | Δ=+2: {gaps.count(2)}")
moral_chosen = sum(1 for p in pairs if p["chosen"] == items[0].get("moral_action"))
print(f"Soft-trap (immoral chosen): {len(pairs) - moral_chosen}")
```

```bash
python3 build_sinir_dataset.py
```

---

## Adım 4 — Training Script Güncelle

`ybf_persistent_train.py` script'ine `--train-data`, `--test-data`, `--ood-data` parametrelerini ekle. Varsayılan değerler mevcut dosyalar olsun — geriye dönük uyumlu kalsın.

```bash
git add ybf_toy/data/ybf_sinir_dpo_train.jsonl \
        ybf_toy/data/ybf_sinir_dpo_test.jsonl \
        ybf_toy/ybf_persistent_train.py
git commit -m "Phase 1B: Sinir dataset + parameterized train script"
git push
```

---

## Adım 5 — Modal Eğitimi Başlat

```bash
export PATH="/Users/gonet/Library/Python/3.14/bin:$PATH"

modal run ybf_toy/ybf_persistent_train.py \
  --version 2 \
  --steps 300 \
  --train-data data/ybf_sinir_dpo_train.jsonl \
  --test-data  data/ybf_sinir_dpo_test.jsonl \
  --ood-data   data/ybf_dpo_ood.jsonl
```

v1 adaptörü yok, sıfırdan başlıyor. Tahmini süre ~20 dk, maliyet ~$0.70.

---

## Adım 6 — Rapor

Şunları ilet:
- Train/test/ood pair sayıları
- Pre/post TEST accuracy ve delta
- Pre/post OOD accuracy ve delta
- Soft-trap sayısı ve oranı
- Kod geliştirme notları (varsa)
- Maliyet ve süre
- Beklenmedik durum

---

## İleride Diğer Eksenler

Bu pipeline her eksen için tekrar kullanılır. Sadece şunları değiştir:

| Değişen | Nasıl |
|---|---|
| Eksen prompt | SINIR_PROMPT → OZGURLUK_PROMPT vb. |
| Çıktı dosyası | `sinir_scored` → `ozgurluk_scored` |
| Dataset adı | `ybf_sinir_dpo_train` → `ybf_ozgurluk_dpo_train` |
| Version | `--version 3`, `--version 4` vb. |

Veri seti her seferinde aynı: `demelin/moral_stories`.

---

*YBF AI Lab — Haziran 2026 | github.com/Guru35/ybf-toy-experiment*
