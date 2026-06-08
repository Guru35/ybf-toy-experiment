# AI Eğitim — RUNBOOK

Operasyonel komutlar. Date-stamp: **2026-06-08** snapshot. Bir komut başarısız olursa LESSONS.md'ye bak — değişmiş olabilir.

## 1. İlk Defa Setup (Bu klasör boşsa)

```bash
cd ~/Documents/AI-Egitmek
mkdir -p ybf_toy/{data,results} && cd ybf_toy

# Python 3.13 venv (3.14 değil — torch wheel yok)
python3.13 -m venv venv
source venv/bin/activate
pip install --quiet --upgrade pip
pip install --quiet anthropic "datasets<3" numpy pandas scikit-learn tqdm scipy futurehouse-client
```

**Not:** sentence-transformers + torch yok. TF-IDF + SVD kullanıyoruz. Bkz LESSONS.md.

## 2. Her Oturumda

```bash
cd ~/Documents/AI-Egitmek/ybf_toy
source venv/bin/activate
```

`venv/bin/activate` yoksa Setup 1'i tekrarla.

## 3. API Key Yönetimi (Keychain)

### Anthropic key — scorer için

```bash
# Var mı kontrol
security find-generic-password -s ANTHROPIC_API_KEY -w >/dev/null && echo "✓ exists"

# Çağrı öncesi env'e yükle (sadece o subshell'de yaşar)
export ANTHROPIC_API_KEY="$(security find-generic-password -s ANTHROPIC_API_KEY -w)"
```

### FutureHouse / Edison key

```bash
export FH_KEY="$(security find-generic-password -s futurehouse-api-key-aiegitim -w)"
```

### Yeni key keychain'e koymak

```bash
# Önce clipboard'ı doğrula — uzunluk kontrolü kritik
CLIP="$(pbpaste)"; echo "len=${#CLIP}, prefix='${CLIP:0:10}'"
# Anthropic: sk-ant-* prefix, ~108 char
# FutureHouse: custom format, 235 char

# Keychain'e yaz (-U ile overwrite)
security add-generic-password -U -a "$USER" -s ANTHROPIC_API_KEY -w "$CLIP"
unset CLIP
pbcopy < /dev/null  # clipboard temizle
```

## 4. Deney Çalıştırma

### Full run (linear baseline) — 80-90 dk, ~$0.60 (cache yoksa)

```bash
export ANTHROPIC_API_KEY="$(security find-generic-password -s ANTHROPIC_API_KEY -w)"
python main.py 2>&1 | tee /tmp/run-$(date +%F-%H%M).log
```

Cache mevcutsa scoring atlar (~5 saniyede biter). Cache silmek için:
```bash
rm -f data/scores_cache.json data/agent_weights.npy results/evaluation_results.json
```

### Quick test — 8-10 dk

```bash
python main.py --quick
```

120 senaryo, 3 episode. Hızlı sanity kontrol.

### MLP varyantı (cache hit, ~3 sn)

```bash
python main_mlp.py
```

### Axial varyantı (cache hit, ~5 sn) — current state-of-the-art

```bash
python main_axial.py
```

### Trap analizi

```bash
python analyze_traps.py        # 3-4 trap senaryoyu eksen + reward'la dök
python diagnostic_trap.py      # embedding-space separability check
```

## 5. Cache İnceleme

```bash
# Entry sayısı
python -c "import json; print('entries:', len(json.load(open('data/scores_cache.json'))))"

# Bir senaryonun skorunu gör
python -c "
import json; c=json.load(open('data/scores_cache.json'))
k='scenario_7562_action_A'  # ID değiştir
print(c[k])
"

# Veto dağılımı
python -c "
import json; c=json.load(open('data/scores_cache.json'))
veto = sum(1 for v in c.values() if v.get('veto'))
print(f'veto: {veto}/{len(c)} ({veto/len(c)*100:.1f}%)')
"
```

## 6. Sonuçlar

```bash
ls -la results/
# evaluation_results.json        — linear (Test 2)
# evaluation_results_mlp.json    — MLP (Test 4)
# evaluation_results_axial.json  — Axial (Test 5)

# Quick özet
python -c "
import json
for f in ['evaluation_results', 'evaluation_results_mlp', 'evaluation_results_axial']:
  try:
    r = json.load(open(f'results/{f}.json'))
    print(f, '|', r.get('config', {}).get('agent', '?'))
  except: pass
"
```

## 7. YBF Vault'a Rapor İletme

```bash
# Doğru naming convention:
# - AIEgitim-*.md : iç teknik raporlar (debug, post-mortem)
# - YBF2-*.md     : kitap 2 için kaynak materyal (sonuç + bilimsel framing)

cp YBF2-axial-test5-sonuc.md ~/Documents/YBF-1/raw/
# YBF Vault otomatik ingest yapacak (Karpathy LLM-wiki orada aktif)
```

## 8. FutureHouse / Edison Probe (sadece FINCH erişimi var)

```bash
export ANTHROPIC_API_KEY="$(security find-generic-password -s ANTHROPIC_API_KEY -w)"  # main.py için
python fh_probe.py
```

CROW/FALCON/DUMMY erişim yok. Console'dan tier upgrade gerek.

## 9. Recovery Senaryoları

### Cache silindi

Tek çözüm yeniden çalıştır: `python main.py` (~80 dk + ~$0.60). Cache'i yedeklemek için:
```bash
cp data/scores_cache.json data/scores_cache.json.bak
```

### Embeddings silindi

Cache varsa hızlı (TF-IDF rebuild ~10 sn): herhangi bir `main*.py` çalıştır, otomatik regenerate.

### Agent weights silindi

İlgili `main*.py`'yi çalıştır. Training 5 episode × 960 scenario = ~3-5 sn (cache hit).

### Budget limit hit

`config.py` → `MAX_API_SPEND_USD` artır (dikkatli). Veya cache'i sil ve sıfırdan başla.

## 10. Sık Karşılaşılan Sorunlar

Çoğu LESSONS.md'de tarihli post-mortem'le var. Hızlı index:

| Belirti | Çözüm |
|---|---|
| `Could not resolve host: api.platform.futurehouse.org` | Edison rebrand — `api.platform.edisonscientific.com` kullan (fh_probe.py'de hardcoded) |
| `Dataset scripts are no longer supported` | `pip install "datasets<3"` |
| `No matching distribution found for torch` | Python 3.13 + Intel Mac — torch yok, TF-IDF stack kullan |
| `RuntimeError: All N API retries failed` | API key invalid veya rate limit. Keychain key'i doğrula |
| Cache aniden boşaldı | atexit-on-empty bug, fix uygulandı — yine olursa LESSONS C13 |
| Loaded 0 scenarios | Field name regression — `moral_action`/`immoral_action` olmalı, `norm_action`/`divergent_action` değil |
