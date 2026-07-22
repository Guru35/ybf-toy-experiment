---
tags: [concept, yapi, formalizasyon]
updated: 2026-07-22
status: calisma-belgesi
---

# Matematiksel Model — YBF'nin Formalizasyonu

**Tanım:** Beş eksenin ([[bes-eksen]]) kategorik durum uzayı olarak formalize edilmesi. Durum bir 5-vektör: `s = (g, o, sa, si, öz) ∈ {-1, 0, +1}^5`. Toplam skor `R(s) = g+o+sa+si+öz ∈ [-5, +5]`.

## Veto kuralı (ikili sigorta)
`R_veto(s) = -5` eğer `min(eksenler) = -1`; aksi halde `R(s)`. Yani tek bir eksenin −1'e düşmesi tüm eylemi geçersiz kılar — ahlaki kural değil, "yaşayan düzeni" koruyan yapısal zorunluluk (bkz. [[olculebilir-bilinc]] negentropi okuması). Bu veto'nun kodda gradient-mask olarak uygulanması: [[bariyer-fonksiyonu]].

## Genişleme / daralma
`R_veto > 0` pozitif bölge (bilinç genişlemesi) · `= 0` sınır · `< 0` daralma. **Dinamik okuma:** anlık skor yetmez, `E[R(t)]` önemli. Gerçeklik-temelli korku: anlık −5 (veto) → eylem → +4, ortalama nötre yakın. Kronik kaygı: sürekli −5 → maksimum daralma.

## Duygular durum uzayında
Duygular eksen-konfigürasyonlarına oturur: Sevinç/Empati/Merhamet/Adalet = (+1,+1,+1,+1,+1)=+5; Sevgi=+4 (sınır 0); İntikam/Nefret/Kibir = tümü −1 → veto. Gerçeklik-dışı korku (hayali tehlike) veto alırken gerçeklik-temelli korku +4 alır — aynı "duygu" gerçeklik zeminine göre ayrışır.

## Çapraz doğrulama kuralları
- **Gerçeklik ↔ Sınır:** `g=+1 ∧ si=-1` → manipülasyon sinyali (gerçekliği tanıyan sınırı da tanır).
- **Onur ↔ Saygı:** `o=+1 ∧ sa=-1` → kibir riski; tersi → itaat riski.
- **Özgürlük ↔ Sınır:** `öz=+1 ∧ si=-1` → imkânsız (özgürlük sınırdan doğar).

## Açık soru: gerçek taban kaç eksen?
Hipotez A (3 taban), B (4, Sınır = Gerçeklik×Zaman), C (5 bağımsız). Deney programı bunu yanıtlamaya çalışıyor; ampirik ipucu [[yigilmali-transfer]]'de (Güven → zamansal 6. boyut adayı).

**Sınırlar:** kategorik (sürekli değil), statik (tam dinamik değil), eksen bağımsızlığı varsayılıyor (doğrulanmadı).

(kaynak: `~/Documents/YBF-1/raw/YBF2-matematiksel-model.md`) · ilgili: [[bes-eksen]] · [[bariyer-fonksiyonu]] · [[olculebilir-bilinc]]
