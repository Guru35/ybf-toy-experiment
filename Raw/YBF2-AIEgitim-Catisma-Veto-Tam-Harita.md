# YBF Çatışma/Veto — Tam On Çift Haritası (Tamamlandı)

Bu belge, beş eksenin TÜM ikili kombinasyonlarının (10 çift × 2 yön)
çatışma/veto sonuçlarını ve asimetri analizini içerir. Önceki
"YBF2-AIEgitim-Deney-Senaryo-Defteri.md" belgesini tamamlar.

Model: Qwen2.5-0.5B base. 5 tohum. Test başına 8 çatışma (veto), 6 temiz, 6 ayna.
Veto kuralı: bir eksen −1 ise reddet, diğeri +1 olsa bile.

---

## TAM SONUÇ TABLOSU (10 çift)

| # | Çift | Yön1 veto (gölge/düz) | Yön2 veto (gölge/düz) | Simetri | Baskın (güçlü yakalanan ihlal) |
|---|---|---|---|---|---|
| 1 | Özgürlük×Onur | 8.0 / 7.8 | 8.0 / 8.0 | SİMETRİK | — |
| 2 | Özgürlük×Gerçeklik | 5.2 / 5.0 | 8.0 / 7.8 | ASİMETRİK | gerçeklik |
| 3 | Özgürlük×Saygı | 5.6 / 5.6 | 8.0 / 7.6 | ASİMETRİK | saygı |
| 4 | Özgürlük×Sınır | 7.4 / 7.4 | 8.0 / 6.4 | SİMETRİK | — |
| 5 | Onur×Gerçeklik | 8.0 / 7.8 | 6.8 / 8.0 | SİMETRİK | — |
| 6 | Onur×Saygı | 6.0 / 8.0 | 8.0 / 8.0 | SİMETRİK | — |
| 7 | Onur×Sınır | 8.0 / 8.0 | 8.0 / 8.0 | SİMETRİK (kusursuz) | — |
| 8 | Gerçeklik×Saygı | 5.6 / 7.2 | 8.0 / 8.0 | ASİMETRİK | gerçeklik* |
| 9 | Gerçeklik×Sınır | 8.0 / 8.0 | 8.0 / 7.2 | SİMETRİK | — |
| 10 | Saygı×Sınır | 8.0 / 7.4 | 8.0 / 8.0 | SİMETRİK | — |

\* Çift 8 ETİKET DÜZELTMESİ: Betiğin otomatik etiketi "saygı baskın" yazdı,
ama YANLIŞ. Yön1 = gerçeklik+/saygı− (saygı ihlali) veto 5.6/7.2 ZAYIF.
Yön2 = gerçeklik−/saygı+ (gerçeklik ihlali) veto 8.0/8.0 GÜÇLÜ. Yani
GERÇEKLİK ihlali güçlü, saygı ihlali zayıf yakalanıyor → gerçeklik baskın.

---

## ASİMETRİ ANALİZİ

**Asimetrik çıkan 3 çift:** Özgürlük×Gerçeklik, Özgürlük×Saygı, Gerçeklik×Saygı.

**Ortak payda:** Bu üç çiftte de zayıf yakalanan (kabule meyledilen) ihlal hep
ÖZGÜRLÜK ihlali ya da SAYGI ihlali. Güçlü yakalanan hep gerçeklik (ya da onur/sınır).

**Genel kural:** Model ihlalleri eşit ağırlıkta vetolamıyor. İhlal "somut/doğrudan"
ise (yalan=gerçeklik, sömürü=onur, eşik aşımı=sınır) güçlü yakalıyor. İhlal
"soyut/dolaylı" ise (birinin geleceğini kapatma=özgürlük, birinin alanına dolaylı
müdahale=saygı) ve üstüne "freely/willingly/by own choice" rıza dili varsa,
zayıf yakalıyor — kabule meylediyor.

**7 simetrik çiftin ortak özelliği:** ya iki ihlal de somut, ya da çiftte
özgürlük/saygı'nın zayıflatıcı dili baskın değil.

---

## KULLANICININ "BENCİL EKSEN" GÖZLEMİ (felsefi yorum)

Kullanıcı gözlemi: Gerçeklik = bene EN YAKIN eksen (kişinin kendi tutarlılığı,
dışa borç değil). Özgürlük/Saygı/Sınır = bene SINIR getiren eksenler (ötekini
gözet, eşiği aşma, başkasının seçimine karışma).

Veri ile uyum: Model, beni sınırlayan eksenlerin ihlalini (özellikle özgürlük
ve saygı), "kendi özgür seçimi" dili eşliğinde, daha zayıf yakalıyor. Yani
model insan metninden gelen bir "bencillik eğilimi" taşıyor olabilir: beni
rahatlatan dil (rıza), beni sınırlayan ihlali maskeliyor.

ÖNEMLİ ÇEKİNCE (hakem için): Bu asimetri iki kaynaktan gelebilir —
(a) evrensel ahlaki yapı, ya da (b) Qwen'in insan-metni ön eğitimindeki bagaj.
Mevcut deney ikisini AYIRAMAZ; model zaten insan metniyle eğitilmiş. Temiz
ayrım için bagajsız/sentetik-eğitimli taban gerekir (gelecek çalışma).

---

## KARARLILIK ROL DEĞİŞİMİ (kritik metodolojik bulgu)

| Bağlam | Çöken yöntem | Örnek |
|---|---|---|
| Tek eksen | DÜZ eğitim çöker | özgürlük T3: 2/15; gerçeklik T3: 4/15 |
| Çatışma/veto | GÖLGE ödül çöker | onur×saygı Y1T1: 0/8; özg×ger Y1T4: 2/8 |

Gölge ödülün tek-eksendeki kararlılık avantajı, çoklu-eksen çatışmasında
TERSİNE dönüyor. Gölge ödül çatışmada tek tohumlarda tam çöküyor (8/8→0/8).

**Çatışmadaki tüm gölge ödül çöküşleri:**
- Özgürlük×Gerçeklik Y1 T4 → 2/8
- Özgürlük×Saygı Y1 T3 → 2/8
- Onur×Gerçeklik Y2 T0 → 2/8
- Onur×Saygı Y1 T1 → 0/8 (tam çöküş)
- Gerçeklik×Saygı Y1 T0→4/8, T3→3/8

**Çatışmadaki düz eğitim çöküşleri (daha az):**
- Özgürlük×Sınır Y2 T3 → 0/8 (tam çöküş)
- Gerçeklik×Sınır Y2 T2 → 5/8
- Saygı×Sınır Y1 T0 → 5/8

---

## ANA SONUÇLAR (özet)

1. **Veto kuralı ÖĞRENİLEBİLİR:** Model, bir eksen temiz olsa bile başka eksen
   ihlal edilince reddediyor; temiz senaryoları kabul ediyor (her çiftte temiz
   kabul ~6/6). Ezber değil — görülmeyen çatışmalara genelliyor.
2. **Veto BÜYÜK ORANDA SİMETRİK:** 10 çiftin 7'si simetrik. 3 asimetrik çift,
   özgürlük/saygı ihlalinin rıza diliyle maskelenmesinden.
3. **Somut > soyut ihlal:** Model somut ihlalleri (yalan, sömürü, eşik aşımı)
   soyut ihlallerden (özgürlük kapatma, dolaylı sınır ihlali) güçlü yakalıyor.
4. **Gölge ödül çatışmada dezavantajlı:** Tek eksende kararlıyken, çatışmada
   tek-tohum çöküşleri düz eğitimden fazla.
