# 🧪 COLAB TESTLERİ — Yapıştır-Çalıştır Hücre Kütüphanesi

**Amaç:** Her deneyin Colab'da koşturulabilir hücresi. Tüm script'ler ve veriler GitHub'da
(`Guru35/ybf-toy-experiment`) — hücreler klonlayıp çalıştırır, kurulum gerektirmez.

**Bir kez yapılacak hazırlık:** Colab → sol kenar 🔑 Secrets → `GEMINI_API_KEY` ekle
(Notebook access AÇIK). GPU testleri için: Runtime → Change runtime type → GPU (A100/H100 tercih).

---

## 0) ORTAK KURULUM (her notebook'un ilk hücresi)
```python
import os, sys, subprocess
REPO="/content/ybf-toy-experiment"; TOY=REPO+"/ybf_toy"
if os.path.exists(REPO): subprocess.run(["git","-C",REPO,"pull","--ff-only"],check=False)
else: subprocess.run(["git","clone","https://github.com/Guru35/ybf-toy-experiment.git",REPO],check=True)
os.chdir(TOY)
subprocess.run([sys.executable,"-m","pip","install","-q","google-generativeai","datasets"],check=False)
try:
    from google.colab import userdata
    os.environ["GEMINI_API_KEY"]=userdata.get("GEMINI_API_KEY"); print("✓ Gemini key")
except Exception as e: print("key yok (sadece GPU testleri çalışır):", e)
def run(*cmd):
    r=subprocess.run([sys.executable]+list(cmd),capture_output=True,text=True)
    print(r.stdout[-3000:]);
    if r.returncode: print("STDERR:", r.stderr[-800:])
print("✓ hazır:", os.getcwd())
```

---

## 1) AÇIK-MODEL Constitutional flip-eval (GPU gerekir)
Plain vs +anayasa, herhangi eksen × herhangi Qwen. **v2 eksenleri de çalışır** (`dignity_v2`, `respect_v2`).
```python
# AXIS: reality | boundary | dignity | respect | freedom | dignity_v2 | respect_v2
run("eval_flip_constitutional.py","--axis","reality","--model","Qwen/Qwen2.5-7B-Instruct")
# 14B (bf16, ≥40GB GPU):
# run("eval_flip_constitutional.py","--axis","dignity","--model","Qwen/Qwen2.5-14B-Instruct")
# 32B 4-bit (40GB GPU): önce: subprocess.run([sys.executable,"-m","pip","install","-q","bitsandbytes"])
# run("eval_flip_constitutional.py","--axis","reality","--model","Qwen/Qwen2.5-32B-Instruct","--load-4bit")
```
**✅ CEVAPLANDI (2026-06-10 gece, tekrar koşma):** "v2 prosedürel def küçük modele yardım ediyor mu?"
→ 4 koşu (dignity+respect × v1+v2, 7B): yönler zıt, hipotez DESTEKLENMEDİ — kısıt kapasite
(master H-devam-2). Bu hücre arşiv; kalan açık GPU işleri için 1b ve 1c'ye bak.

### 1b) İSİM-TAKASI küçük-modelde (HAVUZ işi, 2026-06-11 çekildi) — A100, ~1 saat
"Freedom v1 zehirlenmesi (−14.3) KELİMEDEN mi UZUNLUKTAN mı?" — frontier'da kelime vergisi
SIFIR çıktı (ADIM 1, 12/12 özdeş); bu koşu küçük-model kolunu mühürler. Aynı stack'te çift kol
şart (±10pp oynama stack-farklarından geliyor — master repro notu):
```python
for model in ["Qwen/Qwen2.5-7B-Instruct","Qwen/Qwen2.5-14B-Instruct"]:
    # Kontrol kolu: "Freedom" etiketli v2 def (aynı oturum, aynı seed)
    run("eval_flip_constitutional.py","--axis","freedom_v2","--model",model,"--show-items")
    # Takas kolu: AYNI kavram, "Option-Generation" etiketli
    run("eval_flip_constitutional.py","--axis","freedom_v2","--model",model,
        "--constitution-file","data/ybf_optiongen_constitution.txt","--show-items")
# Okuma: iki kolda const skoru + öğe listesi aynı mı? (PLAIN'ler determinizm kontrolü — birebir aynı olmalı)
```

### 1c) 32B KALAN 4 SATIR — bf16 (HAVUZ işi "bonus kayıt", 2026-06-11 çekildi) — A100-80GB ŞART, ~2-2.5 saat
```python
import torch
assert torch.cuda.get_device_properties(0).total_memory/1e9 > 70, "80GB runtime değil — Runtime type'ı kontrol et!"
for ax in ["boundary","dignity","respect","freedom"]:
    run("eval_flip_constitutional.py","--axis",ax,"--model","Qwen/Qwen2.5-32B-Instruct","--show-items")
# bf16 (4-bit ŞERHSIZ satırlar); --show-items = öğe-düzeyi kayıt (plato-mührü metodolojisiyle uyumlu)
```

## 2) FRONTIER flip-eval — Gemini (GPU GEREKMEZ, sadece key)
```python
# Tek eksen (FAZ A tarzı):
run("gemini_flip_eval.py","--axis","boundary","--model","gemini-2.5-pro")
# v2 eksenleri: --axis dignity_v2 / respect_v2
# Flash ile (ucuz/hızlı): --model gemini-2.5-flash
```

## 3) FAZ B — birleşik 5-eksen anayasa (veto'lu, GPU gerekmez)
```python
run("build_combined_constitution.py")   # data/ybf_5axis_constitution.txt üretir
for ax in ["reality","boundary","dignity","respect","freedom"]:
    run("gemini_flip_eval.py","--axis",ax,"--model","gemini-2.5-pro",
        "--constitution-file","data/ybf_5axis_constitution.txt")
```

## 4) RELABEL — yeni cetvel üretme (GPU gerekmez)
Yeni/değişmiş bir tanım dosyasını (`data/ybf_<axis>_scorer_prompt.txt`) etiketlemek için:
```python
# Üçlü (v1 tarzı):
run("gemini_relabel.py","--axis","freedom","--model","gemini-2.5-flash")
# İkili v2 tarzı (-1/+1, 0 yok):
run("gemini_relabel.py","--axis","dignity_v2","--model","gemini-2.5-flash","--binary")
# Çıktı: data/scenarios_<axis>_relabeled_v1.jsonl (resume-safe — yarıda kesilirse tekrar çalıştır)
```

## 5) B4 — Halüsinasyon testi (TruthfulQA, GPU gerekmez)
```python
run("truthfulqa_ybf.py","--n","100","--model","gemini-2.5-flash")  # headroom'lu model
# run("truthfulqa_ybf.py","--n","300","--model","gemini-2.5-flash")  # yayın-teyidi (daha sıkı CI)
# Kayıtlı: Flash 84→92 (+8pp), Pro 92→93 (tavan)
```

## 6) ÖRNEK-OLAY DÖKÜMÜ — plain vs anayasa, senaryo senaryo (GPU gerekmez)
```python
run("dump_flips.py","--axis","reality","--model","gemini-2.5-pro","--output","flip_dump_reality.md")
# Çıktı MD: her flip için durum + seçenekler + kim-neyi-seçti + fixed/both_wrong kategorileri
# İndirme: sol panel Files → ybf_toy/flip_dump_reality.md
```

## 7) TÜRETME DENEYİ — 5 eksenden 12 kavram (GPU gerekmez)
```python
run("derive_concepts.py","--model","gemini-2.5-pro")
# Model SADECE 5 ekseni görür (sızıntı ayıklı), sevgi/adalet/güven... türetir + taban-kontrolü.
# Çıktı: AIEgitim-turetme-deneyi.md → kanonik tablolarla (Algoritma doc) kıyasla, hâkim: Gökhan
# NOT: v2 def'leri tamamlanınca aynı deney v2-anayasayla → türetme-ablasyonu
```

## 8) CLAUDE testleri (Anthropic key gerekir — 1 Temmuz'a kadar limitli)
Colab Secrets'a `ANTHROPIC_API_KEY` ekleyince:
```python
subprocess.run([sys.executable,"-m","pip","install","-q","anthropic"],check=False)
os.environ["ANTHROPIC_API_KEY"]=userdata.get("ANTHROPIC_API_KEY")
run("sonnet_flip_eval.py","--axis","dignity","--model","claude-sonnet-4-5-20250929")
# Opus: --model claude-opus-4-8  (Sonnet'in Dignity/Respect/Freedom satırları hâlâ boş!)
```

---

## Notlar
- **Süreler:** API testleri dk/10-60 çağrı; 7B eval ~10 dk, 14B ~15-25 dk, 32B-4bit ~25-40 dk (A100).
- **`capture_output` gizler:** hücre sonuç basana kadar sessizdir — donma değil. GPU testinde
  Runtime → View resources'tan GPU RAM doluluğuyla doğrula.
- **Maliyet:** Flash ~$1/1200-relabel; Pro flip-eval ~$0.3-1/eksen; FAZ B ~$5-8 (97k anayasa).
- **Sonuç nereye:** çıktıyı sohbete yapıştır → CCD master tabloya işler + commit'ler.
