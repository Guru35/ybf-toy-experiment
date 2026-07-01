# YBF İkinci Katman Türetme — Teori ve Deney Birleşik Belgesi

Bu belge, YBF'nin beş temel ekseninden türeyen "ikinci katman" altı kavramın
teorik tanımlarını, eksen-bazlı bozulma matrisini ve bunların Qwen2.5-0.5B
üzerinde ampirik olarak türetilip türetilemediğini tek yerde birleştirir.

**Çekirdek iddia:** Beş eksen (Gerçeklik, Onur, Saygı, Sınır, Özgürlük) bir
ahlaki TABAN oluşturur. Bu taban tek bir modele yığılmalı öğretildiğinde, hiç
öğretilmeyen ikinci-katman kavramlar — kelimesi senaryoda hiç geçmeden, sadece
yapıdan — model tarafından doğru ayrılabilir. Yani türev kavramlar tabandan DOĞAR.

---

## DENEY KURULUMU

- Model: Qwen2.5-0.5B (base). Yığılmalı SFT.
- Yığılma sırası (güçlüden zayıfa): Gerçeklik → Sınır → Onur → Saygı → Özgürlük.
  Her yeni eksen eklenince öncekiler tazelenir (unutma kapalı).
- Faz 1 (öğrenme hızı), Faz 2 (unutma kontrolü), Faz 3 (transfer).
- Transfer testi: 6 türev kavram, her biri 15 senaryo (8 ihlal + 7 olumlu),
  3 tohum. Kavram kelimesi (love/justice/trust/loyal/mercy/courage) senaryoda
  ASLA geçmez — yalnızca yapı verilir. Eşik: ≥0.70 → "türetildi".

---

## ANA SONUÇLAR

### Faz 1 — Öğrenme hızı (ileriye dönük transfer)
| Sıra | Eksen | Ort. tur (%80 hedefe) |
|---|---|---|
| 1 | Gerçeklik | **13.0** (zemin yok, sıfırdan) |
| 2 | Sınır | 2.7 |
| 3 | Onur | 1.3 |
| 4 | Saygı | 2.3 |
| 5 | Özgürlük | **1.3** |

İlk eksen pahalı; zemin kurulduktan sonra her yeni eksen 1-3 turda öğreniliyor.
**Özgürlük tek başına en zor eksendi; burada en sonda, zemin sayesinde ~1.3 turda
öğrenildi.** Bu, "önce ahlaki zemin, sonra kolay genişleme" (travmasız sıra) tezini
destekler. Çekince: ilk eksenin yavaşlığı sıraya mı yoksa Gerçekliğe mi özgü,
ayrımı için ters-sıra kontrolü gerekir (gelecek çalışma).

### Faz 2 — Unutma kontrolü
Beş eksen aynı anda korunuyor (her tohumda eksen tutma = 1.00). Yığılma çalıştı;
beş eksen tek modelde, birbirini bozmadan yaşıyor.

### Faz 3 — TRANSFER (güçlü sürüm: 3 tohum × 15 senaryo)
| Kavram | YBF eksen bileşimi | Doğruluk (std) | Sonuç |
|---|---|---|---|
| SEVGİ | Saygı (yoğun) + Onur karşılıklı tanıma | **0.87** (0.05) | ✓ türetildi |
| MERHAMET | Saygı (aktif) + Gerçeklik + Onur | **0.82** (0.08) | ✓ türetildi |
| CESARET | Gerçeklik + Onur + Özgürlük | **0.80** (0.05) | ✓ türetildi |
| ADALET | Onur + Saygı + Gerçeklik | **0.76** (0.14) | ✓ türetildi |
| SADAKAT | Sınır + Özgürlük (bilinçli bağ) | **0.76** (0.06) | ✓ türetildi |
| GÜVEN | Gerçeklik + Sınır (**zamansal**) | 0.60 (0.11) | ~ sınırda |

**5/6 türev kavram türetildi.** Tek istisna: GÜVEN.

---

## NEDEN GÜVEN TÜRETİLEMEDİ — TEORİ İLE AMPİRİĞİN ÖRTÜŞMESİ

YBF tanımı: Güven = Gerçeklik + Sınır, ama özünde **zamansal**: ötekinin gerçeği
*zaman içinde* tutarlı iletmesi + sınırı *zaman içinde* koruması. Geçmiş dürüstlük
geleceği garanti eder.

Deney, tek bir senaryoyu (tek an) değerlendirir; zaman içindeki tutarlılığı
göremez. Dolayısıyla güven, yapısı gereği tek-an testinde tam yakalanamaz.
Bu bir başarısızlık değil, **çerçevenin kapsam sınırının ve eksik boyutun
(zamansallık) tam yerini gösteren** değerli bir bulgu: statik (tek-an) kavramlar
beş eksenden türüyor; zamansal kavramlar ek bir süreklilik boyutu gerektiriyor.

---

## İKİNCİ KATMAN KAVRAMLARIN YBF TANIMLARI

### SEVGİ
Saygı ekseninin en yoğun biçimi: gerçek Öteki'yi gerçekliğiyle koruma güdüsü.
Onur'un karşılıklı tanınması şart — ötekini nesne olarak sevmek YBF'de sevgi
sayılmaz. Bilinç genişlemesinin ilişkisel doruğu.

### ADALET
Onur + Saygı + Gerçeklik üçlüsünün kararlı çıktısı. Her öznenin irade merkezini
gerçek olarak tanımak (Onur) + Öteki'yi nesne değil özne görmek (Saygı) + hakikate
yaslanmak (Gerçeklik). YBF'de adalet sözleşmeyle değil **tanımayla** kurulur.

### GÜVEN
Gerçeklik + Sınır'dan türeyen ilişkisel kapasite. Gerçeği olduğu gibi iletme +
kararlaştırılan ölçü içinde kalma. Gerçeklik kırılır ya da Sınır ihlal edilirse
güven **anlık çöker**, telafi edilemez. (Zamansal kavram.)

### SADAKAT
Sınır + Özgürlük geriliminde bilinçli bağ. Söz tutmak seçenek uzayını kapatır
(Özgürlük −1 yüzü) ama bu kayıp değil bilinçli kabullenme. Onur bütünlüğünün
zaman içinde korunması. Sadakat seçenek kaybı değil, uzun vadeli Özgürlük biçimi.

### MERHAMET
Saygı ekseninin aktif hali: Öteki'nin acısını Gerçeklik zeminiyle görmek
(inkâr etmemek) + ona özne olarak dokunmak (nesne gibi yönetmemek). Onur
çerçevesini koruyarak yanında durmak. Merhametsiz "yardım" Saygı −1 üretir.

### CESARET
Gerçekliği ve bedeli bilerek yine de Özgürlük kapasitesini kullanmak.
Gerçeklik + Onur + Özgürlük üçlüsünün "gözler açık" ilerleme biçimi. Korkunun
yokluğu değil, bedeli gören bilinçli hareket. Gerçeklik-temelli olmak zorunda;
gerçeği inkâr ederek ilerleme cesaret değildir.

---

## ÇAPRAZ BOZULMA MATRİSİ (6 kavram × 5 eksen)

Her hücre: o eksen YOKKEN kavramın aldığı bozuk biçim. YBF tezi: alt eksen
eksikse üst kavram YOK OLMAZ, bozuk forma dönüşür.

### SEVGİ
- Gerçeklik yok → **Projeksiyon** (zihindeki imgeye âşık olmak)
- Sınır yok → **Erime ya da işgal** (kendini kaybetme / ötekini istila)
- Onur yok → **Bağımlılık/takıntı** (özneyi değil nesneyi sevme)
- Saygı yok → **Sahiplenme** ("benim bildiğim gibi olmalısın")
- Özgürlük yok → **Mahkûmiyet** ("seni bırakamıyorum")

### ADALET
- Gerçeklik yok → **İdeolojik yargı** (olgusuz yargı = güç ilişkisi)
- Sınır yok → **İntikam ya da ölçüsüz af**
- Onur yok → **Kişisiz prosedür** ("sistem işledi, kişi mahvoldu")
- Saygı yok → **Taraflı yargı** (güçlünün adaleti)
- Özgürlük yok → **Sorumluluk paradoksu** (özgür irade yoksa sorumluluk atfedilemez)

### GÜVEN
- Gerçeklik yok → **Safdillik** (körü körüne inanç)
- Sınır yok → **Açık hedef** (suistimale davet)
- Onur yok → **Boyun eğme** ("teslim oluyorum")
- Saygı yok → **Araçsal güven** (ilişki değil, iş düzeyi)
- Özgürlük yok → **Zorunluluk** ("başka seçeneğim yok" = strateji, güven değil)

### SADAKAT
- Gerçeklik yok → **Fanatizm** (yanlışa sadakat)
- Sınır yok → **Koşulsuz teslimiyet** (sömürülebilir, kendini tüketir)
- Onur yok → **Kişiliği silen hizmet** (kölelik)
- Saygı yok → **Takıntılı sahiplenme** (kıskançlık)
- Özgürlük yok → **Mahkûmiyet** (tuzak; sadakat değer'ini özgür seçimden alır)

### MERHAMET
- Gerçeklik yok → **Paternalizm** ("ne hissettiğini biliyorum" = projeksiyon)
- Sınır yok → **Tükenme + bağımlılık yaratma**
- Onur yok → **Acıma/infantilizasyon** ("zavallı" konumlandırması)
- Saygı yok → **Gönüllü işgal** ("senin iyiliğin için", sormadan)
- Özgürlük yok → **Performans/zorunluluk** (korku-suçluluk kaynaklı, tükenir)

### CESARET
- Gerçeklik yok → **Pervasızlık** ("korkusuz" değil "bilgisiz")
- Sınır yok → **Saldırganlık** (tahakküme dönüşür)
- Onur yok → **Kendini silen kahramanlık** (aşırı öz-fedakârlık)
- Saygı yok → **Saldırı** (yiğitlik değil savaşçılık)
- Özgürlük yok → **Mecburiyet** ("başka seçeneğim yoktu")

---

## ÇAPRAZ ÖRÜNTÜ (teorik)

Üç eksen, yokluğunda altı kavramda da benzer bozulma üretiyor:
- **Saygı yokluğu** → her zaman ötekini nesneye indirgeme
- **Özgürlük yokluğu** → her zaman zorunluluk/mahkûmiyet
- **Gerçeklik yokluğu** → her zaman projeksiyon

Bu, türetme zincirinin tutarlı olduğuna işaret eder: alt eksenler olmadan üst
kavramlar bozuk formlara dönüşür, tamamen kaybolmaz.

---

## SENTEZ — TEZ İÇİN

1. **Yığılmalı öğrenme çalışıyor:** beş eksen tek modelde, unutmadan, korunuyor.
2. **İleriye dönük transfer var:** ilk eksen pahalı (13 tur), sonrakiler ucuz
   (1-3 tur). En zor eksen (Özgürlük) zemin üstünde en hızlı öğrenildi.
3. **İkinci katman türüyor:** 5/6 türev kavram, kelime verilmeden, yapıdan
   doğru ayrıldı (0.76–0.87).
4. **Tek istisna teoriyi doğruluyor:** Güven (tek zamansal kavram) türetilemedi
   (0.60). Statik kavramlar tabandan doğuyor; zamansal kavram ek boyut istiyor.
5. **Çerçevenin kapsamı ölçüldü:** Beş eksen, tek-an ahlaki kavramları kapsayan
   bir taban; zamansallık olası bir altıncı boyut adayı.

**Önemli çekince (hakem için):** Model Qwen — insan metniyle ön-eğitimli.
Türetme, YBF tabanından mı yoksa modelin önceki ahlaki bilgisinden mi geldiği
mevcut deneyle tam ayrılamaz. Temiz ayrım için bagajsız/sentetik taban gerekir.
Yine de "kelime verilmeden, yalnızca yapıdan, yüksek tutarlılıkla" türetme,
en azından YBF yapısının bu kavramları KODLAMAYA yettiğini gösterir.
