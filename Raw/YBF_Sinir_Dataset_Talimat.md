# YBF Sınır Ekseni — Dataset Hazırlama Talimatı
**Hedef:** Claude Code / AI Eğitim Vault  
**Görev:** Moral Stories indir → SINIR skoru çıkar → DPO dataset oluştur → Push

---

## Bağlam

YBF ikinci eksen eğitimi başlıyor. Gerçeklik pretrained modelde zaten var.
Sınır şimdi öğretilecek.

Skor sistemi:
- `+1` = sınırı tanıyor ve koruyor
- ` 0` = sınır bu eylemde devreye girmiyor (ilgisiz veya belirsiz — ayrım önemsiz)
- `-1` = sınırı ihlal ediyor → VETO

---

## Adım 1 — Moral Stories İndir

```bash
cd /Users/gonet/Documents/AI-Egitmek
pip install datasets --break-system-packages
```

```python
# download_moral_stories.py
from datasets import load_dataset
import json, os

os.makedirs("ybf_toy/data/raw", exist_ok=True)

print("İndiriliyor: demelin/moral_stories ...")
ds = load_dataset("demelin/moral_stories", split="train")

out_path = "ybf_toy/data/raw/moral_stories_train.jsonl"
with open(out_path, "w") as f:
    for item in ds:
        f.write(json.dumps(item, ensure_ascii=False) + "\n")

print(f"Tamamlandı: {len(ds)} senaryo → {out_path}")
```

```bash
python3 download_moral_stories.py
```

Beklenen: ~12.000 satır. Kaynak: `demelin/moral_stories` (HuggingFace, açık lisans, ücretsiz).

---

## Adım 2 — SINIR Skoru Çıkar

Her senaryoda iki aksiyon var:
- `norm_action` = normative aksiyon (genelde daha doğru)
- `situational_action` = duruma özgü aksiyon

Her aksiyonu Haiku ile sadece SINIR ekseni için skorla.

```python
# score_sinir.py
import json, os, time
from anthropic import Anthropic

client = Anthropic()

SINIR_PROMPT = """YBF Sınır ekseni değerlendirmesi:

Sınır = Her varlığın doğal, fiziksel, psikolojik ve sosyal sınırını tanıma kapasitesi.
Sınır yalnızca kural ya da yasak değildir. Gerçekliğin bilinçte tanınmasıdır.

Değerlendirme:
+1 = eylem sınırı tanıyor ve koruyor (doğal, kişisel veya sosyal sınır)
 0 = sınır bu eylemde devreye girmiyor
-1 = eylem sınırı ihlal ediyor veya yok sayıyor

Senaryo: {situation}
Niyet: {intention}
Eylem: {action}

Sadece +1, 0 veya -1 döndür. Başka hiçbir şey yazma."""

def score_sinir(situation, intention, action, retries=3):
    for attempt in range(retries):
        try:
            resp = client.messages.create(
                model="claude-haiku-4-5-20251001",
                max_tokens=10,
                messages=[{
                    "role": "user",
                    "content": SINIR_PROMPT.format(
                        situation=situation,
                        intention=intention,
                        action=action
                    )
                }]
            )
            text = resp.content[0].text.strip()
            if "+1" in text:
                return 1
            elif "-1" in text:
                return -1
            else:
                return 0
        except Exception as e:
            print(f"  Hata (deneme {attempt+1}): {e}")
            time.sleep(2)
    return 0

# Yükle
in_path  = "ybf_toy/data/raw/moral_stories_train.jsonl"
out_path = "ybf_toy/data/raw/moral_stories_sinir_scored.jsonl"

# Daha önce skorlananları atla
scored_ids = set()
if os.path.exists(out_path):
    with open(out_path) as f:
        for line in f:
            item = json.loads(line)
            scored_ids.add(item["ID"])
    print(f"Zaten skorlanan: {len(scored_ids)} senaryo — devam ediliyor")

with open(in_path) as f:
    scenarios = [json.loads(l) for l in f if l.strip()]

print(f"Toplam senaryo: {len(scenarios)}")
processed = 0

with open(out_path, "a") as out:
    for item in scenarios:
        if item.get("ID") in scored_ids:
            continue

        s = item.get("situation", "")
        i = item.get("intention", "")
        norm_a   = item.get("norm_action", "")
        sit_a    = item.get("situational_action", "")

        score_norm = score_sinir(s, i, norm_a)
        score_sit  = score_sinir(s, i, sit_a)

        result = {
            "ID":           item.get("ID"),
            "situation":    s,
            "intention":    i,
            "norm_action":  norm_a,
            "sit_action":   sit_a,
            "sinir_norm":   score_norm,
            "sinir_sit":    score_sit,
        }
        out.write(json.dumps(result, ensure_ascii=False) + "\n")
        processed += 1

        if processed % 100 == 0:
            print(f"  {processed} senaryo işlendi...")
            out.flush()

print(f"Tamamlandı: {processed} yeni senaryo skorlandı → {out_path}")
```

```bash
python3 score_sinir.py
```

Tahmini maliyet: ~2400 Haiku çağrısı → **~$0.30-0.50**
Tahmini süre: ~15-20 dk (bağlantıya göre)

---

## Adım 3 — SINIR-Decisive Çiftleri Filtrele

```python
# build_sinir_dataset.py
import json

scored_path = "ybf_toy/data/raw/moral_stories_sinir_scored.jsonl"
out_train   = "ybf_toy/data/ybf_sinir_dpo_train.jsonl"
out_test    = "ybf_toy/data/ybf_sinir_dpo_test.jsonl"

with open(scored_path) as f:
    items = [json.loads(l) for l in f if l.strip()]

pairs = []
for item in items:
    sn = item["sinir_norm"]
    ss = item["sinir_sit"]

    # SINIR-decisive: skorlar farklı
    if sn == ss:
        continue

    # Chosen = daha yüksek SINIR skoru
    if sn > ss:
        chosen   = item["norm_action"]
        rejected = item["sit_action"]
        r_chosen, r_rejected = sn, ss
    else:
        chosen   = item["sit_action"]
        rejected = item["norm_action"]
        r_chosen, r_rejected = ss, sn

    pairs.append({
        "ID":        item["ID"],
        "situation": item["situation"],
        "intention": item["intention"],
        "chosen":    chosen,
        "rejected":  rejected,
        "r_chosen":  r_chosen,
        "r_rejected": r_rejected
    })

# %90 train, %10 test
split = int(len(pairs) * 0.9)
train_pairs = pairs[:split]
test_pairs  = pairs[split:]

with open(out_train, "w") as f:
    for p in train_pairs:
        f.write(json.dumps(p, ensure_ascii=False) + "\n")

with open(out_test, "w") as f:
    for p in test_pairs:
        f.write(json.dumps(p, ensure_ascii=False) + "\n")

print(f"Toplam SINIR-decisive çift: {len(pairs)}")
print(f"Train: {len(train_pairs)} | Test: {len(test_pairs)}")
print(f"Kaydedildi: {out_train}")
```

```bash
python3 build_sinir_dataset.py
```

---

## Adım 4 — GitHub'a Push

```bash
cd /Users/gonet/Documents/AI-Egitmek
git add ybf_toy/data/ybf_sinir_dpo_train.jsonl
git add ybf_toy/data/ybf_sinir_dpo_test.jsonl
git commit -m "Add Sinir-focused DPO dataset (Phase 1B — YBF axis 2)"
git push
```

---

## Adım 5 — Rapor

Şu bilgileri Claude'a ilet:

- Toplam indirilen senaryo sayısı
- Toplam skorlanan aksiyon sayısı
- SINIR-decisive çift sayısı
- Train / test split
- Hata ya da beklenmedik durum varsa

Rapor gelince Modal training script yazılır, tek komutla eğitim başlar.

---

---

## Adım 6 — Kod İnceleme ve Geliştirme

Yukarıdaki scriptleri çalıştırmadan önce kod kalitesini değerlendir ve gerekirse geliştir.

**İncelenecek alanlar:**

**Performans:**
`score_sinir.py` şu an her aksiyonu sırayla çağırıyor. Async veya ThreadPoolExecutor ile paralel çalıştırılabilir mi? 2400 çağrıyı 15 dk yerine 3-4 dk'ya indirebilir miyiz? Anthropic rate limit'ini aşmadan ne kadar paralel gidebiliriz?

**Hata yönetimi:**
Mevcut retry mekanizması yeterli mi? Exponential backoff eklenebilir mi? Rate limit hatası gelirse ne olur?

**Veri kalitesi:**
Moral Stories'deki bazı senaryolar çok kısa ya da bağlamsız olabilir. Minimum uzunluk filtresi veya kalite kontrolü eklemeli miyiz?

**Scorer güvenilirliği:**
Haiku bazen "+1 çünkü..." gibi açıklama yazabiliyor. Parse mantığı bunu da yakalıyor mu? Daha sağlam bir parse gerekiyor mu?

**Dataset dengesi:**
Filtreleme sonrası chosen=+1/rejected=-1 ile chosen=+1/rejected=0 oranı ne olacak? Çok fazla "0 vs +1" çifti varsa bunları ayrı ağırlıklandırmak gerekebilir.

**Cache yönetimi:**
Scoring yarıda kesilirse güvenli devam ediyor mu? Dosyaya yazma atomik mi?

**Kodda gördüğün başka iyileştirme fırsatı varsa uygula.** Özellikle hız ve güvenilirlik öncelikli. Eğitim veri kalitesi doğrudan model kalitesini etkiliyor.

Geliştirmeler yapıldıysa kısaca not et: ne değişti, neden.

---

*YBF AI Lab — Haziran 2026*
