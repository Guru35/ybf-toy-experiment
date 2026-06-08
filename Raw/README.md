# YBF Dosya Dağıtım Rehberi
## Hangi dosya nereye gidecek?

---

## AIEgitim/ klasörü → AI Eğitim Vault'una at

Bu dosyalar YBF TOY deneyini çalıştıran Claude instance'ına gidecek.

| Dosya | İçerik |
|-------|--------|
| `AIEgitim-sistem-promptu.md` | Bu vault'un rolü ve görevleri |
| `AIEgitim-toy-deney-dokumani.md` | Tam deney dokümantasyonu + full run sonuçları |
| `AIEgitim-uc-sistem-rolleri.md` | Üç sistem arasındaki iş bölümü |
| `AIEgitim-ybf-scorer-prompt.md` | YBF puanlama promptu (scorer.py'dan) |
| `AIEgitim-analyze-traps.py` | Trap senaryo analiz scripti — önce bunu çalıştır |

**Önce yapılacak:** `python AIEgitim-analyze-traps.py` çalıştır, sonuçları Claude'a yapıştır.

---

## YBF2/ klasörü → YBF Vault'una (WALT/RAV) raw/ klasörüne at

Bu dosyalar ikinci kitap kasasına INGEST edilecek.

| Dosya | İçerik |
|-------|--------|
| `YBF2-kitap-plani.md` | İkinci kitap yapısı |
| `YBF2-hipotez.md` | H1/H0 + güncel kanıtlar (full run dahil) |
| `YBF2-evrimsel-zemin.md` | RGB analojisi, evrimsel argüman |
| `YBF2-matematiksel-model.md` | 5 eksen formal tanımı |
| `YBF2-toy-deney.md` | Deney dokümantasyonu (full run güncellenmiş) |
| `YBF2-alignment-implications.md` | RLHF vs Constitutional AI vs YBF |
| `YBF2-bibliyografya.md` | Kaynak listesi |
| `YBF2-llm-wiki-mimari.md` | Karpathy RAG mimarisi |
| `YBF2-ip-arastirma.md` | Patent/marka eylem planı |
| `YBF2-ip-ajan-prompt.md` | IP ajan promptu |
| `YBF2-white-paper-en.md` | AI firmalarına teknik belge (taslak) |
| `YBF2-uc-sistem-rolleri.md` | Üç sistem iş bölümü |
| `YBF2-vault-sistem-promptu.md` | Bu vault'un sistem promptu |
| `YBF2-rag-system-prompt.md` | WALT/RAV için RAG system prompt |
| `YBF2-ingestion-config.md` | INGEST konfigürasyonu |

---

## Kural

**AIEgitim-** ile başlayan → AI Eğitim Vault  
**YBF2-** ile başlayan → YBF Vault (WALT/RAV) raw/

