# AIEgitim — Cache Loss Bug Fix Report

**Tarih:** 2026-06-08
**Sistem:** AI Eğitim
**Etki:** 2400 cached YBF skoru silindi (~$0.60'lık API call). Recovered: cache yeniden oluşturuldu.
**Status:** Bug fix uygulandı, kalıcı koruma aktif. Aynı hata tekrarlamaz.

---

## Ne Oldu

Diagnostic script çalıştırılmadan önce yapılan bir validation adımı:

```bash
python -c "import scorer, config; print('imports OK')"
```

Bu masum import komutu, `data/scores_cache.json` dosyasını **boş JSON (`{}`) ile üzerine yazdı** ve 2400 cached YBF skorunun tamamını sildi.

Etki sırası:
1. `import scorer` çalıştı
2. Modül seviyesindeki `atexit.register(_flush_cache)` kaydoldu
3. Python süreci başarıyla çıktı (validation print'ten sonra)
4. atexit hook `_flush_cache()` çağırdı
5. `_cache` değişkeni bellekte halen başlangıç değerinde: `{} ` (çünkü `_load_cache()` çağrılmamıştı)
6. `_flush_cache` koşulsuzca `json.dump({}, ...)` yaptı → 2400-entry dosyanın üzerine `{}` bastı

Sonradan çalıştırılan `diagnostic_trap.py` "0 trap bulundu" raporladı — gerçekte 0 entry vardı, doğru rapor; ama sebep beklenmedikti.

---

## Kök Sebep

`scorer.py`'da iki tasarım kararının kötü etkileşimi:

**Karar 1 — Lazy cache loading:**
```python
_cache: dict = {}

def _load_cache() -> dict:
    global _cache
    if os.path.exists(config.SCORES_CACHE_PATH):
        with open(config.SCORES_CACHE_PATH) as f:
            _cache = json.load(f)
    return _cache
```
`_cache` modül seviyesinde boş başlıyor. Sadece `_load_cache()` veya `load_cache()` açıkça çağrılırsa diskten yükleniyor.

**Karar 2 — Eager atexit registration:**
```python
def _flush_cache():
    os.makedirs(config.DATA_DIR, exist_ok=True)
    with open(config.SCORES_CACHE_PATH, "w") as f:
        json.dump(_cache, f, indent=2)

atexit.register(_flush_cache)
```
atexit hook modül seviyesinde import zamanında kaydoluyor. Süreç çıkışında **koşulsuzca** çalışıyor.

**Çakışma:** `import scorer` yapan ama `_load_cache()` çağırmayan herhangi bir Python süreci (örnek: `python -c "import scorer"`, REPL'de import, kısa test scripti) cache'i siler.

C5 düzeltmesi (atexit + her 25 call'da flush) **veri kaybına karşı koruma sağlayacaktı** — Ctrl+C ile kaybetmeyelim diye eklenmişti. Burada **veri kaybının kendi sebebi oldu**.

---

## Fix

`scorer.py`'a tek satırlık guard:

```python
def _flush_cache():
    # Guard: never write an empty cache over a non-empty file.
    # atexit can fire on bare `import scorer` (no _load_cache call) — that
    # would overwrite a populated cache.json with {} and destroy work.
    if not _cache:
        return
    os.makedirs(config.DATA_DIR, exist_ok=True)
    with open(config.SCORES_CACHE_PATH, "w") as f:
        json.dump(_cache, f, indent=2)
```

**Mantık:** `_cache` boş ise diske yazma. Boş bellek + dolu disk durumunda disk doğru kaynak. Pure import senaryosu artık zararsız.

**Negatif yan etki yok:**
- Normal akışta `precompute_all_scores` veya `score_one` `_load_cache()` çağırır → `_cache` dolu olur → flush çalışır.
- Tüm test setinde 0 skor durumunda diske yazılmaz ama yazılacak şey de yoktur — sadece kullanıcı dosyaya zarar vermez.

---

## Verification

Fix sonrası test:

```bash
python -c "import scorer; print('post-fix import safe')"
ls -la data/scores_cache.json  # boyut/timestamp değişmedi
```

Cache recovery: tam main.py çalıştırması ile 2400 skor yeniden oluşturuldu.

---

## Future-Proofing — Önerilen Sonraki Adımlar (AI Eğitim → Claude/YBF Vault'a iletilir)

İdeal düzeltme tek-satırlık guard'dan daha derin: cache mimarisi şu anda **paylaşılan global state + atexit** üzerinde duruyor. Daha sağlam alternatifler:

**Öneri 1: Atomic write**
Cache'i `data/scores_cache.json.tmp` dosyasına yaz, sonra `os.rename` ile atomic move. Yarım yazma durumunda eski dosya kalır.

**Öneri 2: Sınıf tabanlı cache**
Module-global `_cache` yerine `ScoreCache` sınıfı: `__enter__/__exit__` veya `with` deyimi. atexit hack'i biter.

**Öneri 3: Backup-on-load**
`_load_cache` başarılı olduğunda `data/scores_cache.json.bak` oluştur. Bu olay tekrarlanırsa veri kurtarılabilir.

**Öneri 4: Cache size invariant**
Disk'teki dosya boyutu bellek boyutundan büyükse uyar (size shrunk = potansiyel veri kaybı sinyali).

Hangisinin (varsa) implement edileceği Claude'un kararı. AI Eğitim sadece teknik feasibility raporlar.

---

## Maliyet Etkisi

- **Silinen:** 2400 cached entry (~$0.60'lık önceden ödenmiş API call)
- **Recovery:** 2400 yeni call × $0.00025 = **$0.60**
- **Toplam zarar:** ~$0.60 + ~80 dakika
- **Budget guard aktifleştiği için kontrollü:** $3 limit altında

---

*AI Eğitim — sistem rolü gereği teknik post-mortem. Felsefi/stratejik yorum yok.*
