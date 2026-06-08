# Veto ve Döngü — AI Eğitim Mimari Direktifleri
## YBF_Veto_Dongu_Evrim_Tartisma.md — Teknik Özet

Kaynak: YBF tartışma notu, Haziran 2026
YBF Kitabı direktifleri ayrı dokümanda — bu dosya sadece AI Eğitim için.

---

## KRİTİK MİMARİ BULGU

### Veto = Seçilim Sinyali, Sadece Ceza Değil

Mevcut implementasyon: `-5` → negatif reward → "bu davranışı baskıla"

Gereken: `-5` → o davranış **kategorisinde** artık optimizasyon yapma, **yeni konfigürasyon uzayı aç**

Teknik karşılık: **barrier function** veya **hard constraint** katmanı:
```
Standart ceza:   gradient küçülür, o yönde yavaş gider
Barrier/veto:    gradient o yöne HİÇ gitmiyor
```

---

## META-BİLGİ ADIMI (En Önemli)

Mevcut ajan: toplam reward görüyor (-5 ya da 0-5)  
Sorun: hangi EKSEN veto tetikledi bilmiyor  
Sonuç: kapananı "fark edemiyor" → döngü geçişi yok

**Çözüm önerisi: Per-axis reward feeding**

Şu an ajan tek sayı görüyor. Eğer 5 eksen ayrı feature olarak input'a eklense:
```
Input: [embedding (384-dim)] + [G, O, Sa, Si, Öz] = 389-dim
```
Ajan hangi eksenin negatif olduğunu öğrenebilir.  
Bu meta-bilgi adımını mümkün kılar.

**Bu Phase 2 için en düşük maliyetli değişiklik** — embedding değiştirmiyor, sadece input genişliyor.

---

## DÖNGÜ GEÇİŞİ MİMARİSİ

State machine olarak tasarım:

```
STATE A: Mevcut seçenek uzayında optimizasyon
   ↓ -5 veto tetiklendi
TRANSITION: Döngü tamamlandı, meta-bilgi üretildi
   ↓ Hangi eksen? Hangi bağlam? (per-axis bilgisiyle)
STATE B: Yeni konfigürasyon uzayında yeni döngü
```

Tetikleyici seçeneği (tasarım kararı açık):
- Tek veto → geçiş (agresif)
- N birikimli veto → geçiş (daha stabil)
- Bağlam tespiti → geçiş (en YBF-uyumlu)

---

## PARALEL MODEL SEÇİLİMİ

```
2-3 küçük model paralel eğitiliyor
Her döngü sonunda YBF skorları üzerinden değerlendirme
En düşük YBF skoru alan varyasyon eleniyor
Kalan varyasyonlar sonraki döngüye taşınıyor
```

Asıl mesele paralel sayısı değil: **seçilim kriterinin YBF'den türetilmiş olması**

---

## ETKİLEŞİM YOĞUNLUĞU

Hızlandırma zamanı kısaltmaktan gelmiyor — etkileşim yoğunluğundan:
- Daha kısa feedback döngüsü
- Daha sık değerlendirme  
- Daha keskin seçilim sinyali

Pratik: dataset'i büyütmek yerine, aynı dataset üzerinde daha sık değerlendirme döngüsü.

---

## SOMUT SIRADAKI ADIMLAR

1. Per-axis reward feeding dene (389-dim input) — düşük maliyet, yüksek potansiyel
2. Diagnostic sonucu gelince (🔴/🟡/🟢) bu bilgiyle birleştir
3. Karar: per-axis input + linear Q-net mi, yoksa MLP mi?

---

*Kaynak belge: YBF_Veto_Dongu_Evrim_Tartisma.md §3*
