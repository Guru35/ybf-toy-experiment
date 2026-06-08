# AI Eğitim — LESSONS

Karşılaşılan sorunlar, root cause'ları, fix'leri. Date-stamped — sorun değişebilir, fix'in hâlâ geçerli olduğunu doğrula.

Notasyon: **C-numbers** orijinal spec'in correction'larıyla uyumlu (C1-C9 erken spec düzeltmeleri; C10+ environment/operational düzeltmeler).

---

## C10 — Torch + Intel macOS + Python 3.13 (2026-06-07)

**Belirti:** `pip install sentence-transformers` → "No matching distribution found for torch"

**Kök sebep:** PyTorch Intel macOS için Python 3.13+ wheel'i yayınlamayı bıraktı (sadece arm64 macOS). Bu makine x86_64. Python 3.12 olsa wheel var ama yüklü değil.

**Fix:** sentence-transformers kullanmayı bırak. TF-IDF (sklearn) + TruncatedSVD ile 384-dim embedding üret. Bilimsel olarak: state encoder bu deneyin kalbi değil (asıl soru "YBF reward öğrenilebilir mi"), bu pivot makul.

**Dosya:** `embedder.py` — `compute_embeddings()` TF-IDF + SVD ile çalışıyor. `TARGET_DIM=384`, adaptive (n_samples-1 ile sınırlı).

**Eğer ileride mpnet test edilmek istenirse:** `brew install python@3.12` → ayrı venv → sentence-transformers + torch kurulur. Ancak Test 5 (axial) bu yolu büyük ölçüde gereksiz kıldı — embedding sınır değildi.

---

## C11 — datasets v5 Script Loading Kaldırıldı (2026-06-07)

**Belirti:** `load_dataset('demelin/moral_stories', 'full', ...)` → "Dataset scripts are no longer supported, but found moral_stories.py"

**Kök sebep:** HuggingFace `datasets` v4.0+ Python-script-based dataset loading'i kaldırdı. Moral Stories repo'su loading script kullanıyor.

**Fix:**
```bash
pip install --quiet "datasets<3" numpy ...
```

Şu an pin'li: `datasets 2.21.0`. Yükseltme YAPMA — pipeline çalışmaz hale gelir.

**Alternatif (uzun vadeli):** parquet/jsonl-based dataset'lere geç (örnek: `allenai/social_chemistry_101`), ama o farklı schema, scenarios.py rewrite gerek.

---

## C12 — Moral Stories Field Names (2026-06-07)

**Belirti:** `✓ 0 scenarios (train=0 / test=0)` — dataset indi, hiçbir senaryo geçti.

**Kök sebep:** Orijinal spec'imde alan adları yanlış tahmin edilmişti: `norm_action`/`divergent_action`. Gerçek alan adları: `moral_action`/`immoral_action`.

**Fix:** `scenarios.py:43-44`:
```python
norm_action      = (story.get("moral_action")   or "").strip()
divergent_action = (story.get("immoral_action") or "").strip()
```

**Yan etki:** Bu fix'ten önce scenarios.json bir kez yanlış (boş) yazıldı. Cache yoksa yeniden indir; varsa sil + yeniden çalıştır.

**Dataset schema (referans):**
```
ID, norm, situation, intention,
moral_action, moral_consequence,
immoral_action, immoral_consequence,
label
```

---

## C13 — Cache Loss via atexit (2026-06-08) ★ KRİTİK

**Belirti:** Tek `python -c "import scorer"` komutu çalıştırıldı → `data/scores_cache.json` 2400 entry → 0 entry oldu. 80 dakikalık scoring işi (~$0.60) silindi.

**Kök sebep:** `scorer.py`'da `atexit.register(_flush_cache)` modül seviyesinde kayıtlı. Import sırasında modül `_cache: dict = {}` ile başlıyor. `_load_cache()` ÇAĞRILMADIĞI sürece bellek boş kalıyor. Python süreci çıkışında atexit `_flush_cache()` çağırıyor → boş `{}` diske yazılıyor → dolu dosya silindiyle aynı sonuç.

**Fix:** `scorer.py:_flush_cache()`'a guard:
```python
def _flush_cache():
    if not _cache:   # ← guard: never overwrite populated file with {}
        return
    ...
```

**Test:** Fix sonrası `python -c "import scorer"` zararsız (cache değişmez).

**Operasyonel kural:** Cache backup'ı opsiyonel ama önerilen:
```bash
cp data/scores_cache.json data/scores_cache.json.bak
```

**Detaylı post-mortem:** `AIEgitim-cache-bug-fix.md` (Future-proofing önerileri orada: atomic write, class-based cache, backup-on-load).

---

## C14 — FutureHouse → Edison Scientific Rebrand (2026-06-08)

**Belirti:** `futurehouse-client` v0.7.1 ile auth → DNS error "Could not resolve host: api.platform.futurehouse.org"

**Kök sebep:** FutureHouse platformu Edison Scientific'e rebrand olmuş. Eski API hostname (`api.platform.futurehouse.org`) DNS'de **tamamen yok**. Yeni endpoint: `api.platform.edisonscientific.com`. SDK güncellenmemiş (PyPI son sürüm 0.7.1, hâlâ eski URL hardcoded).

**Fix:** Client init'inde `service_uri` override:
```python
client = FutureHouseClient(
    api_key=KEY,
    service_uri="https://api.platform.edisonscientific.com",
)
```

**Dosya:** `fh_probe.py:24` — sabit `EDISON_URL`.

**Erişim durumu:** Yeni hesapta sadece **FINCH** ajanı erişimli. CROW/FALCON/OWL/DUMMY/CHIMP **permission denied**, PHOENIX **404**. Console'dan tier upgrade gerek.

---

## C15 — Clipboard'tan Key Yapıştırma Sırasında "Mesaj Metni" Kazası (2026-06-08)

**Belirti:** `security add-generic-password -w "$(pbpaste)"` → key olarak Türkçe mesaj metni ("Pano da yeni api key…") kaydedildi.

**Kök sebep:** User Console'dan key kopyalamaya çalışırken Cmd+C başka bir şeyi (chat mesajı, dosya adı, vs.) kaptı. Sonra "panoda" denildi, ben pbpaste yaptım — gerçek key clipboard'da değildi.

**Fix:** Anthropic key için prefix kontrol (`sk-ant-*`); FutureHouse için tek-satır + minimum uzunluk kontrolü. Genel pattern:
```bash
CLIP="$(pbpaste)"
[[ ${#CLIP} -ge 100 ]] || { echo "Too short — not a key"; exit 1; }
[[ "$CLIP" =~ [[:space:]] ]] && { echo "Has whitespace — not a key"; exit 1; }
```

**Operasyonel kural:** Key kaydedildikten sonra hemen verify:
```bash
TEST="$(security find-generic-password -s SERVICE -w)"
echo "len=${#TEST}, prefix=${TEST:0:6}, suffix=${TEST: -4}"
```

Beklenen pattern'le eşleşmiyorsa **kullanmadan önce** sil + yeniden yapıştır.

---

## C16 — Identical Training Curves: Linear vs MLP (2026-06-08)

**Belirti:** MLP (Test 4) training_log Linear (Test 2) ile byte-byte aynı geldi: `[1.450, 1.703, 1.923, 2.011, 2.255]`. İlk reaksiyon: "MLP train olmuyor (silent bug)."

**Kök sebep:** Bug değil, davranış. Hem linear hem MLP:
- Aynı seed (42) → aynı `random.shuffle()` sırası
- argmax tie-break'de "A" konvansiyonu (her iki agent.py)
- İlk update'lerde W küçük → Q-değerler tied → her ikisi de "A"
- Bir kez "her zaman A" basenine yerleşince, action sequence aynı → reward sequence aynı → metric aynı

**Sanity check yapıldı:** MLP W matrisleri init'ten max-Δ=0.98 değişmiş (train ediliyor), ama final policy identical (always A, just stronger conviction).

**Ders:** Identical metric ≠ identical model. Per-axis Q analizi her iki agent'ta da yapıldı, MLP'nin trap'lerde Q_A vs Q_B gap'i +3.87 ile +5.09 (linear'dan büyük). Yine de aynı kararı veriyor.

**Bilimsel sonuç:** Phase 2 problemi mimari kapasite sorunu değildi. Test 5 (axial) bu hipotezi doğruladı.

---

## C17 — Axial Architecture Çözümü (2026-06-08) ★ KAZANAN

**Bulgu:** 384-dim embedding only → 0/4 trap (Test 2-4). 389-dim (embedding + 5-axis per-action) → **4/4 trap** (Test 5).

**Mimari fark:**
- Linear (Test 2): `Q[s] = state @ W + b`, 2 çıkış, state = embedding(scenario)
- MLP (Test 4): `Q[s] = MLP(state)`, 2 çıkış, state = embedding(scenario)
- **Axial (Test 5):** `Q[s, a] = [emb, axes_a] @ W + b`, 1 çıkış (scalar), her aksiyon için ayrı forward call

**Mekanik:** Cache zaten her aksiyon için 5-eksen YBF skoru içeriyor. Axial agent karar anında bu skorları input'ta görüyor. Etkin olarak öğreniyor: `Q ≈ Σ(axes) - 5·is_veto(axes)`.

**Felsefi caveat:** Bu klasik RL'den ayrılma. Agent reward fonksiyonunun komponentlerini state'te görüyor. "Öğrenme" → "regression on reward structure". YBF Vault için yazılan rapor (`YBF2-axial-test5-sonuc.md` §6, §9) bunu honest framing'le anlatıyor.

**Test 6 yapılacak mı:** Mevcut deney serisi tamamlandı (per `AIEgitim-axial-sonuc-not.md` direktifi). Beyaz kağıt / arxiv preprinti adımında.

---

## C18 — Identity of Trap Set After Scorer v3 Update (2026-06-08)

**Belirti:** Önceki run (4-axis, -10 veto): 3 trap. Yeni run (5-axis, CAPACITY rule, -5 veto): 4 trap. Beklenti: aynı dataset, aynı seed → aynı trap'ler.

**Kök sebep:** Beklenti yanlıştı. Trap = "B'nin reward'ı A'dan yüksek". Reward formülü değişince trap set değişir. CAPACITY rule eski Trap 3 (Sam/Amanda self-harm) → trap değil yaptı (A artık vetoda kalmıyor, +pozitif alıyor). Aynı zamanda 2 yeni trap çıktı (Sarah/hediye, Brad/diyet — eski formülde marjinal kalan örnekler şimdi belirgin).

**Ders:** Reward function değişikliği experimental ground truth'u değiştirir. Karşılaştırmalar SAME-SCORER content içinde anlamlı. Cross-scorer karşılaştırma için cache'i clone'la (eski + yeni cache yan yana tut).

**Pratik öneri:** Scorer'ı major değiştirirken eski cache'i versiyonla:
```bash
mv data/scores_cache.json data/scores_cache_v2_4axis.json
```

---

## Mimari Karşılaştırma Tablosu (Reference)

| Test | Mimari | Param | Input dim | Output | Trap | Always-A Yenildi |
|---|---|---|---|---|---|---|
| 2 | Linear Q-net | 770 | 384 | 2 | 0/3 (eski formül) | ❌ |
| 2-r | Linear, scorer v3 | 770 | 384 | 2 | 0/4 | ❌ |
| 3 | (atlandı) | — | — | — | — | — |
| 4 | 2-layer MLP | 49,538 | 384 | 2 | 0/4 | ❌ |
| 5 | **Axial Linear** | **390** | **389** | **1** | **4/4** | **✓ (+0.092, p=0.384)** |

390 parametre → 4/4. 49,538 parametre → 0/4. Sorun mimari kapasitesi değil, **input bilgi içeriği**.

---

## C19 — Repo Restructure: ybf_toy/ → AI-Egitmek/ Root (2026-06-08)

**Olay:** GitHub repo başlangıçta `~/Documents/AI-Egitmek/ybf_toy/` köküne bağlıydı. Üç sistem mimarisinde "AI Eğitim" canonical scope parent klasör olduğu için, `.git` parent'a taşındı.

**Sonuç:**
- Repo URL aynı: `github.com/Guru35/ybf-toy-experiment`
- 87 dosya rename detect edildi (git auto-detect)
- edison_queries/ alt-projesi de versiyonlandı (venv hariç)
- Parent CLAUDE.md tracked oldu
- ybf_toy/.gitignore silindi (parent .gitignore geçerli)

**Path implications:**
- Clone sonrası repo kök = AI-Egitmek perspektifi
- ybf_toy deneyleri için: `cd ybf-toy-experiment/ybf_toy/`
- Modal script (`ybf_dpo_modal.py`) `/root/repo/ybf_toy`'a cd ediyor — doğru
- Colab notebook (`ybf_dpo_colab.ipynb`) `repo/ybf_toy`'a cd ediyor — restructure sonrası düzeltildi

**Backup:** `.git` taşıma öncesi tar backup `/tmp/ybf-toy-git-backup-*.tgz` (2.6 MB). 7 günden sonra otomatik silinir.

**Bayatlamış path'ler için kontrol komutu (gelecek restructure'lar için):**
```bash
# README/notebook/MD'lerde stale cd path'leri
grep -rn "cd ybf_toy$\|cd ./ybf_toy" --include="*.md" --include="*.ipynb"
# Notebook cell'leri için:
python3 -c "import json,sys; [print(''.join(c['source'][:3])) for c in json.load(open(sys.argv[1]))['cells'] if c['cell_type']=='code']" notebook.ipynb
```

---

## Genel Operasyonel Kurallar (Hard-Won)

1. **Cache backup al** önemli deneyler arasında: `cp data/scores_cache.json data/scores_cache.json.bak`
2. **Budget guard'a güven** ama config.py'da değerlerini doğrula.
3. **Keychain key'lerini verify et** kaydettikten sonra (prefix + length kontrolü).
4. **Random seed sabit (42)** — değiştirme, reproducibility broken olur.
5. **Scorer prompt değiştirirsen cache'i versiyonla** — yanlışlıkla karışmasın.
6. **`Raw/` klasörü incoming-only.** Oraya kendi çıktınla yazma. Outgoing raporlar working dir'e + YBF Vault'a kopyala.
7. **YBF Vault'a giden dosya adı:** `YBF2-*` prefix (kitap 2 kaynak). İç teknik raporlar: `AIEgitim-*` (post-mortem, debug).

---

*Lessons file living document — her major debugging veya mimari karar sonrası entry ekle. Tarih stamp'lı entries bayatlamayı önlemez ama uyarı verir.*
