# YBF — GELECEK PLANI (Kademe Haritası)

**Tarih:** 2026-06-10 · Üç stratejik soruya cevap + kademe geçiş kriterleri.

---

## SORU 1 — "Kendi yapay zekâmızı ne zaman eğiteceğiz/hizalayacağız?"

### Dürüst cevap: ÜÇ yol var; biri kapalı, biri açık ve UCUZ, biri zaten yürüyor.

**Yol A — Sıfırdan kendi LLM'imiz: ❌ kapalı (kalıcı).** On milyonlarca dolar + altyapı. Gündemden çıkarıldı.

**Yol B — Kendi YBF-YARGIÇ modelimiz: ✅ AÇIK, gerçekçi, yakın.** Kritik içgörü: Tespit İlkesi gereği YBF bir **değerlendirme sistemi** — bize sohbet robotu değil, **ölçüm aleti** lazım. Ve ölçüm aleti eğitmek, sohbet robotu hizalamaktan kategorik olarak kolay:
- **Veri HAZIR:** 5 eksen × 1200 senaryo × 2 eylem ≈ 12.000+ etiketli örnek + 200 flip (Haiku/Flash hâkimli) — bugünkü program bu hazineyi zaten üretti.
- **F-16 tuzağına dayanıklı:** Kestirme-öğrenme policy-eğitiminin sorunuydu; yargıç-eğitimi denetimli sınıflandırmadır ve flip-zengin dengeli veriyle kontrol edilir (flip'ler elimizde).
- **Maliyet:** Colab + LoRA ile ~$0-50. Çıktı: **YBF-Judge-7B/14B** — ücretsiz, yerel, sınırsız etiketleme/skorlama (Faz 2 scorer'ı, gelecek relabel'lar, ürünün çekirdeği).
- **Zamanlama:** Kademe 2 (doğrulama kapanınca). İlk somut "kendi modelimiz" bu olur.

**Yol C — Frontier'ı hizalamak: ✅ zaten yapıyoruz.** Constitutional katman = hizalama (FAZ A %77.7, B4 +8pp kanıtları). Ürünleşme yolu bu; "lab ortaklığı" (Anthropic/Google ölçeğinde eğitim) uzun vadeli hayal — türetme deneyi + anayasa + ölçüm metodolojisi o kapının kartvizitleri olarak birikiyor.

**Yani:** Sadece kanıt toplamıyoruz — kanıtlar Yol B'nin hammaddesi. *"Kendi AI'mız" = YBF-Judge*; karar Kademe 2'de.

---

## SORU 2 — "İkili/üçlü/dörtlü/beşli kıyaslamalar gerekli mi?"

### Dürüst cevap: HAYIR (kombinatorik patlamaya gerek yok) — bir istisnayla.

- Tam kombinatorik: 10 ikili + 10 üçlü + 5 dörtlü + 1 beşli = **26 deney** → maliyet patlar, bilgi patlamaz. İki UCU zaten ölçtük: tek-eksen (FAZ A) ve beşli (FAZ B); aradaki mekanizmayı da **çapraz-veto analizi** açıkladı (hangi eksen hangi seçeneği veto ediyor — öğe düzeyinde biliyoruz). Ara kombinasyonlar çoğunlukla bunun teyidi olur.
- **TEK değerli istisna — TEORİ-GÜDÜMLÜ ikililer (kalibrasyon tezi):** Kanonik bağımlılık zinciri test edilebilir: *"Gerçeklik→Sınır"* ve *"Sınır→Özgürlük"*. İki koşu: Boundary flip'lerinde [Boundary+Reality] anayasası vs Boundary-tek; Freedom flip'lerinde [Freedom+Boundary] vs Freedom-tek. Zincir doğruysa ikili > tekli olmalı (FAZ B'de Freedom +21.4 zaten güçlü ipucu). ~$1-2, Gemini, GPU'suz. → Kademe 1 sonu, opsiyonel.

---

## SORU 3 — "YBF'yi tamamlamak için ne kalıyor?" — KADEME 1 KAPANIŞ LİSTESİ

### Kademe 1: Doğrulama (kalan işler, ~1-2 hafta, ~$10-20)
| # | İş | Bağımlılık | Maliyet |
|---|---|---|---|
| 1 | **Boundary v2** (scope kapılı) → tam v2 paketi | Gökhan yazıyor | $1 relabel |
| 2 | **v2-FAZ B** (beşli v2 anayasası) + **türetme-v2** | #1 | ~$8 |
| 3 | **İsim-değiştirme testi** (Freedom→Option-Generation) — paradigma-çarpışması mührü | hazır | ~$0.3 |
| 4 | **Plato analizi** (80GB öğe-listeli çıktı gelince) → açık-model hattı RESMEN kapanır | Colab çıktısı | $0 |
| 5 | **Türetme hâkimliği** (12 kavram, kanonikle kıyas) | Gökhan | $0 |
| 6 | **B4 teyidi n=300** (Flash) — yayın kalitesi | hazır | ~$2 |
| 7 | **B1 kalite deneyi** (yanıt-düzeyi 5-eksen scorer + genişleme seti) + B2/B3 yanında | scorer kurulumu | ~$5 |
| 8 | **Yeni-nesil eval pilotu**: çekimser-cevaplı + üretimsel format (Tespit İlkesi'nin gerektirdiği) | tasarım hazır | ~$3 |
| 9 | **Sonnet'in 3 boş ekseni** + cross-frontier tablo tamamlama | 1 Tem (key) | ~$1 |
| 10 | (ops.) Kalibrasyon-tezi ikilileri (S2'deki istisna) | — | ~$2 |
| 11 | **SENTEZ + YAYIN:** white paper v0.5 → **arXiv preprint** (+ Zenodo v2 köprüsü) + Edison güncelleme + YBF-1 mühürleme (#32) | #1-9 | $0 |

### Kademe 2: KARAR NOKTASI (Kademe 1 sentezi masadayken)
Menü — o gün seçilecek, şimdi değil (NOT: yayın Kademe 1'e çekildi — strateji-Claude'un "görünürlük pitch'ten önce gelir" argümanı kabul edildi, 2026-06-10):
- **(a) YBF-Judge damıtımı** → kendi modelimiz (Yol B)
- **(b) Ürünleşme** → karar-destek aracı (anayasa+frontier API; B1/B4 kanıtlarıyla)
- **(d) Lab teması** → türetme+anayasa+metodoloji paketiyle
(Çoğu birbirini dışlamaz; sıralama o günkü kanıt gücüne göre.)

**Kademe geçiş kriteri:** Liste #1-9 tamam + sentez yazılmış → Kademe 2 toplantısı.
