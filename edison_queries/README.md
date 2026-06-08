# YBF × Edison Test Sorguları

Edison Scientific (FutureHouse'un AI-for-Science platformu) ile YBF'nin temel iddialarını bilimsel literatürde test etme scripts'i.

**Konum:** `~/Documents/AI-Egitmek/edison_queries/`
**YBF wiki referansı:** [[YBF-1/wiki/sources/ybf-edison-test-script]] · [[YBF-1/wiki/sources/futurehouse-edison]]
**Kuruluş:** Faz 1 ilk başarılı test — 2026-06-08

---

## Kurulum

```bash
cd ~/Documents/AI-Egitmek/edison_queries

# 1. Venv oluştur (mevcut Python 3.14 — ilk test için yeter; Phase 2 mimari Python 3.12'ye geçebilir)
python3 -m venv venv
source venv/bin/activate

# 2. Paket kurulumu
pip install --upgrade pip
pip install -r requirements.txt

# 3. API key resolution (3 yol):
# (a) Env var manuel:
export EDISON_API_KEY="paste_your_key_here"

# (b) Env var keychain'den (önerilen — script bu fallback'i de yapar):
export EDISON_API_KEY=$(security find-generic-password -s futurehouse-api-key -w)

# (c) Hiçbir şey set etme — script keychain'den otomatik alır (futurehouse-api-key service'inden)
```

---

## Çalıştırma

```bash
source venv/bin/activate

# Tek sorgu test (VETO_KURALI PRECEDENT, ~8-10 dk)
python3 test_single.py

# 6 sorgu full run (~40-60 dk, dikkat: maliyet bilinmiyor — FutureHouse non-profit
# muhtemelen sübvanse ama ilk full run'da dashboard'dan harcamayı izle)
python3 ybf_edison_test.py    # raw/ybf_edison_test-1.py'den uyarlanmış sürüm
```

---

## Çıktılar

- `test_single_result.json` — tek sorgu yanıtı (test_single.py)
- `ybf_edison_results.json` — 6 sorgu full run (ybf_edison_test.py)
- Stdout: özet + ilk 1500-2000 karakter yanıt önizleme

Bu çıktıların **wiki INGEST hedefi:** YBF-1/wiki/ciktilar/ + sentez olarak YBF-1/wiki/sentezler/.

---

## Önemli Notlar

### Key bilgisi (2026-06-08 doğrulandı)

- `EDISON_API_KEY` = aynı `futurehouse-api-key` (keychain). Ayrı key gerekmiyor.
- 235 karakter custom format

### Response yapısı (paket v0.11.1)

`client.run_tasks_until_done({...})` **liste döndürür** (`list[PQATaskResponse]`), tek obje değil. Defensive handling:

```python
raw_response = client.run_tasks_until_done({...})
if isinstance(raw_response, list):
    response = raw_response[0]
else:
    response = raw_response
answer = response.answer  # ya da response.formatted_answer
```

Mevcut attributes: `agent_name, answer, answer_reasoning, build_owner, created_at, environment_name, formatted_answer, has_successful_answer, job_name, json, ...`

### 6 Job tipi (JobNames)

`ANALYSIS, DUMMY, LITERATURE, LITERATURE_HIGH, MOLECULES, PHOENIX, PRECEDENT`

Bizim scriptte 2 tip kullanılıyor:
- `PRECEDENT` — yenilik/prior art aramaları (patent için kritik)
- `LITERATURE` — genel literatür taraması

### Süre tahmin

- PRECEDENT VETO_KURALI: ~8.4 dk (2026-06-08 ilk test)
- LITERATURE muhtemelen 5-15 dk arası (içerik derinliğine göre)

---

## Stratejik Bağlam

Bu sorgular YBF'nin **patent başvurusu öncesi prior art** araştırması rolünü oynar (YBF-1 yapilacaklar §8.3). Eğer Edison bir YBF kavramı için "bu zaten yapılmış" cevabı verirse:

1. **Kötü değil** — bilim böyle ilerler; yeni olduğunu zannettiklerimiz ataları var
2. **Patent stratejisi rafine olur:** YBF'nin **kombinasyon** değeri vurgulanır (tek tek değil, beraber yenilik)
3. **White paper güçlenir:** "We build on Krakovna et al., Gollier..." formülasyonu defensif değil özgüvenli

### İlk bulgu (2026-06-08, VETO_KURALI)

Irreversibility ZATEN formalize edilmiş:
- **Gollier 2003** — decision analysis, option value of waiting
- **Krakovna 2018** — AI safety, relative reachability penalty

YBF'nin yeni boyutu: **evrimsel-grounded + çok-eksenli + cross-validation pair'ler + capacity threshold**.

---

## See also

- YBF-1 wiki: `~/Documents/YBF-1/wiki/sources/ybf-edison-test-script.md` (script kaynak kart)
- YBF-1 wiki: `~/Documents/YBF-1/wiki/sentezler/edison-prior-art-vetokurali-2026-06-08.md` (ilk bulgu)
- API key envanteri: `~/Documents/API_KEYS.md`
- Future-House GitHub: https://github.com/Future-House
- Edison Scientific: https://edisonscientific.com (support email)
