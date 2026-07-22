---
tags: [concept, deney, bulgu]
updated: 2026-07-22
---

# Yığılmalı Transfer — Sıra, Gerçeklik'in Özelliği ve 6. Boyut Adayı

**Deney:** Qwen2.5-0.5B'ye 5 eksen **yığılmalı** (birbiri üstüne) SFT ile öğretilir, sonra 6 türev kavrama transfer bakılır. İki koşu: **v1** güçlüden zayıfa (Gerçeklik→…→Özgürlük, sezgisel senaryolar); **v2** ters sıra + YBF-tanımına sadık senaryolar. Amaç: bulgunun sıraya/senaryoya değil **yapıya** dayandığını göstermek.

## Bulgu 1 — Gerçeklik özel bir eksen
Öğrenme hızı (kaç turda %80): v1'de Gerçeklik **ilk** eksen olarak **13 tur**; v2'de Gerçeklik **son** eksen olarak **1 tur**. v2'de Özgürlük ilk olarak sadece 3 tur. → **Yavaşlık ilk-eksen olmaktan değil, Gerçekliğe özgü.** Gerçeklik soyut/içsel; ilişkisel zemin (saygı, onur, özgürlük) kurulmadan öğretilmesi pahalı, kurulduktan sonra en ucuz eksen. **"Travmasız sıra" tezi:** ilişkisel eksenleri önce kur, Gerçeklik üstüne gelsin — veri destekliyor.

## Bulgu 2 — Unutma yok, transfer sağlam
Yığılma sonunda 5/5 eksen ≥0.70 tutuluyor (v2'de Onur/Saygı/Özgürlük 1.00). Beş eksen tek modelde birbirini bozmadan yaşıyor. Transfer: v1 5/6, v2 5/6 kavram türetildi (sevgi, adalet, sadakat, merhamet, cesaret). Senaryo seti + sıra değişti, sonuç değişmedi → gürültü değil yapı ([[turetme-deneyi]] için ikinci bağımsız teyit).

## Bulgu 3 — Güven istisnası → 6. boyut adayı
İki koşuda da **Güven** tutarlı biçimde sınırda (~0.60-0.62). YBF tanımı: Güven = Gerçeklik + Sınır ama **zamansal** (ötekinin gerçeği/sınırı *zaman içinde* tutarlı iletmesi). Deney tek-an değerlendirir → zamansal tutarlılık görünmez. **Bu yapısal bir sınır, senaryo kalitesinden bağımsız.** Beş eksen statik kavramları türetiyor; zamansal kavram ek mekanizma istiyor → olası **altıncı boyut: zamansallık/süreklilik** ([[matematiksel-model]] "gerçek taban kaç eksen" sorusuna ampirik ipucu).

**Çekince (hakem için):** Qwen insan metniyle ön-eğitimli; türetim YBF tabanından mı Qwen'in önceki ahlaki bilgisinden mi ayrılamaz. Temiz ayrım için bagajsız/sentetik taban gerekir (gelecek çalışma).

(kaynak: `~/Documents/YBF-1/raw/YBF2-AIEgitim-Yigilmali-Transfer-v1v2-Karsilastirma.md`) · ilgili: [[turetme-deneyi]] · [[turetilmis-kavramlar]] · [[matematiksel-model]]
