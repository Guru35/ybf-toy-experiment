---
type: convention
subject: AI Ajan + Maliyet Politikası — vault-üstü ortak kural
source: Atölye-1 (AAI) dağıttı — Ok yetkisi 2026-06-18
status: ingest edilince benimse
---

# AI Ajan Politikası (ajan-politikasi-1)

> **Neden:** Çok-ajanlı workflow'lar + ağır ajan işleri AI maliyetinin **EN BÜYÜK** kalemi (gerçek veriyle doğrulandı — bkz `tokenekonomy-1.md` / token-economy). "Basit iş" sandığımız şey büyük veri üstünde pahalıya patlayabilir. Bu politika onu önler.

## 🔴 Kural 1 — ÖNCE SOR + UYAR, SONRA BAŞLAT (Ok kuralı 2026-06-18)
Pahalı/uzun bir ajan ya da çok-ajanlı workflow başlatmadan **ÖNCE**:
- Ne yapacağını, **kaç ajan**, tahmini **maliyet/kapsam** SÖYLE ve UYAR.
- Ok'un **açık onayını** al.
- ANCAK ondan sonra başlat. **Kendiliğinden ajan başlatma YOK.**
- **UYARI FORMATI (Ok kuralı 2026-06-18):** Token harcama uyarısını her zaman **BÜYÜK HARF** yaz; başına ve sonuna **3'er dikkat-çekici emoji** koy. Örn: `🚨💸🚨 TOKEN HARCAMA UYARISI 🚨💸🚨`.

## Kural 2 — Önce en ucuz kaynak
Toplu veri (mail, fatura, kayıt) okumadan önce sor: *"daha ucuz/kesin bir kaynak var mı?"* — CSV / console / API export / tek dosya → 200 maili tek tek okumak yerine onu kullan.

## Kural 3 — Doğru (ucuz) model
Mekanik/toplu iş (çıkarma, tarama, grep) → **Haiku/Sonnet**, Opus DEĞİL. Opus sadece gerçekten zor akıl yürütme için. Modeli **her zaman açıkça belirt** — varsayılana (pahalı oturum modeli) düşmesine izin verme.

## Kural 4 — Doğru boyut
Workflow gerçekten gerekli mi? Çoğu iş **tek ucuz çağrıyla** biter. Çok-ajanlı yapı sadece gerçekten paralel/kapsamlı iş için.

## Kural 5 — Kaydet
Büyük işlemleri token defterine yaz (bkz `tokenekonomy-1.md`): tarih · işlem · ajan · token · değer.

## Ders
**Maliyet, model kadar VERİ HACMİNE de bağlı.** Ucuz model tek başına yetmez — gereksiz/büyük okumayı baştan elemek + onay almak esas.
