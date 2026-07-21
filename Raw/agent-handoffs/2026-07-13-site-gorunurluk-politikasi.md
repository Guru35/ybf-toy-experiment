---
type: convention
subject: Site Görünürlük Checklist'i (AEO/GEO + analitik) — vault-üstü ortak kural
source: Atölye-1 (AAI) dağıttı — Ok yetkisi 2026-07-13
status: ingest edilince benimse
---

# Site Görünürlük Checklist'i (site-gorunurluk-politikasi-1)

> **Neden:** Her web sitesi (Gonet/Pigme A.Ş. ekosisteminde) doğuştan görünür ve ölçülebilir olmalı. Bu 5 madde açılışta atlanırsa site hem AI cevap motorlarına (ChatGPT/Claude/Perplexity/Gemini) hem geleneksel analitik/arama konsoluna görünmez doğar — sonradan fark edilmesi maliyetlidir.

## 5 Madde — Her Web Sitesinde (yeni + mevcut)

1. **Cloudflare — AI botlar ENGELLENMEYECEK.** CF, yeni zone'larda AI tarayıcılarını (GPTBot, ClaudeBot, PerplexityBot vb.) varsayılan olarak engelliyor. Her sitenin Cloudflare zone ayarı kontrol edilir: "Block AI Bots" / "AI Crawl Control" kapalı/izinli olmalı. Amaç: siteler LLM'ler tarafından listelenip cevap üretiminde kaynak gösterilebilsin (AEO/GEO).
2. **Site haritası (sitemap.xml) her sitede olacak.** Yoksa oluşturulur, Search Console'a gönderilir.
3. **Google Search Console mülkü etkinleştirilecek.** DNS/HTML doğrulama ile mülk kurulur, sitemap gönderilir.
4. **Google Tag Manager (GTM) yüklenecek.** Şablon yuvasına container ID'si girilir (Astro/Laravel başlangıç şablonlarında yuva zaten gömülü — bkz. `@proje-ac` Faz 2).
5. **GA4 yüklenecek.** GTM container üzerinden veya direkt gtag.js ile.
6. **Yandex Metrica yüklenecek.** Şablon yuvasına sayaç ID'si girilir.

## Kim yapar

- **CCD yapar (mekanik):** robots.txt/CF ayarı kontrolü ve düzeltmesi (API varsa), sitemap.xml oluşturma, şablon yuvalarına ID girme (ID sağlanınca).
- **Ok'ta kalır (hesap/kimlik gerektiren):** GSC mülk sahipliği onayı, GTM/GA4/Yandex Metrica hesap+ID oluşturma, Cloudflare hesap-seviyesi ayar onayı (zaten çoğu Cloudflare işlemi hassas → Ok).

## Ne zaman uygulanır

- **Yeni site açılışında:** `@proje-ac` Faz 2'nin (Görünürlük Katmanı) parçası — otomatik kontrol listesi, ID yoksa madde `wiki/acilis-plani.md`'de "⏳ bekliyor" düşer.
- **Mevcut sitelerde:** Periyodik/isteğe bağlı denetim — kaç site, kim tetikler, kapsam Ok'un vereceği talimatla netleşir (bu doğası gereği çok-site denetimi, tek seferde tüm ekosistemi taramak büyük iştir — önce kapsam sorulur).

## İlgili
- `Atolye-1/research/proje-ac/taslak.md` — Faz 2 (Görünürlük Katmanı), bu politikanın kaynağı olan orijinal tasarım
- `Atolye-1/wiki/hosting-strategy.md` — hosting/CF stratejik kararları
- `Atolye-1/wiki/api-services-registry.md` — hangi vault'ta hangi servis aktif/planlı
