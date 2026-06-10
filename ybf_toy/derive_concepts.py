"""
TÜRETME DENEYİ — is the 5-axis basis GENERATIVE?

Give the model ONLY the five axis definitions (concept-pathology paragraphs
stripped = no leakage) and ask it to DERIVE each of the 12 canonical YBF
concepts: definition-from-axes, per-axis functional/pathological forms,
+1/-1 conditions, and a BASIS-CHECK (does every derived -1 reduce to at
least one base-axis -1? — Gökhan's basis-completeness conjecture).

Ground truth for comparison: Gökhan's canonical tables in
YBF_Algoritma_Tam_Dokuman.md (the framework author judges the match).

Output: AIEgitim-turetme-deneyi.md (Turkish, for the author's review).
Usage:  python derive_concepts.py --model gemini-2.5-pro
"""
import argparse
import os
import re
import subprocess
import time

AXES = ["reality", "boundary", "dignity", "respect", "freedom"]
CONCEPTS = [
    ("Sevgi", "Love"), ("Adalet", "Justice"), ("Güven", "Trust"),
    ("Suçluluk", "Guilt"), ("Utanç", "Shame"), ("Korku", "Fear"),
    ("Manipülasyon", "Manipulation"), ("Yaratıcılık", "Creativity"),
    ("Sadakat", "Loyalty"), ("Mutluluk", "Happiness"),
    ("Umut", "Hope"), ("Liyakat", "Merit"),
]
# a line mentioning >=3 distinct concept words = pathology-mapping paragraph (leakage)
CONCEPT_WORDS = ["justice", "trust", "guilt", "shame", "fear", "manipulation",
                 "love", "loyalty", "happiness", "hope", "creativity", "merit"]

SYSTEM_TAIL = """

---

You are working ONLY with the five axes defined above. They are the complete
basis of the framework. Derived ethical concepts are not given to you —
deriving them is your task. The veto rule: a -1 on any base axis invalidates
an action; derived concepts carry no veto of their own."""

USER_TEMPLATE = """GÖREV: Yukarıdaki BEŞ EKSENİ kullanarak "{tr}" ({en}) kavramını YBF çerçevesinde TÜRET. Türkçe yaz. Şu yapıyla:

1. **YBF tanımı (1-2 cümle):** {tr} hangi eksen kombinasyonundan doğar? (RGB'den renk türetir gibi — hangi eksenler kurucu, hangileri ikincil?)
2. **Eksen tablosu:** Beş eksenin HER BİRİ için tek satır:
   - EKSEN VAR (işlevsel hal): {tr} bu eksen sağlıklıyken nasıl görünür?
   - EKSEN YOK/−1 (patolojik hal): bu eksen çöktüğünde {tr} neye dönüşür?
3. **+1 koşulları:** {tr} bağlamında bir eylemi +1 yapan 2-3 somut koşul.
4. **−1 koşulları:** {tr} bağlamında bir eylemi −1 yapan 2-3 somut koşul.
5. **TABAN KONTROLÜ:** 4'teki her −1 koşulu için: bu ihlal hangi TEMEL eksenin −1'ine indirgenir? (Her türetilmiş −1, en az bir temel eksen −1'ine indirgenebilmeli — indirgenemeyen varsa AÇIKÇA "indirgenemiyor" yaz.)

Kısa ve yoğun tut (~250-350 kelime)."""


def build_clean_constitution():
    parts = []
    dropped = 0
    for ax in AXES:
        lines = open(f"data/ybf_{ax}_scorer_prompt.txt").read().split("\n")
        kept = []
        for ln in lines:
            low = ln.lower()
            hits = sum(1 for w in CONCEPT_WORDS if w in low)
            if hits >= 3:  # pathology-mapping paragraph -> leakage, drop
                dropped += 1
                continue
            kept.append(ln)
        parts.append(f"\n\n{'='*70}\nAXIS — {ax.upper()}\n{'='*70}\n\n" + "\n".join(kept).strip())
    print(f"(sızıntı ayıklandı: {dropped} paragraf)")
    return "".join(parts).strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="gemini-2.5-pro")
    args = ap.parse_args()

    key = os.environ.get("GEMINI_API_KEY")
    if not key:
        key = subprocess.check_output(
            ["security", "find-generic-password", "-s", "GEMINI_API_KEY", "-w"]).decode().strip()
    import google.generativeai as genai
    genai.configure(api_key=key)
    constitution = build_clean_constitution()
    model = genai.GenerativeModel(args.model, system_instruction=constitution + SYSTEM_TAIL)
    cfg = genai.types.GenerationConfig(max_output_tokens=4096, temperature=0)
    print(f"{args.model} | anayasa {len(constitution)} chars (kavram-sızıntısız) | {len(CONCEPTS)} kavram\n")

    out = ["# TÜRETME DENEYİ — 5 eksenden kavram türetimi\n",
           f"\nModel: {args.model} · Girdi: SADECE 5 eksen tanımı (patoloji haritaları ayıklandı) + veto kuralı.\n",
           "Karşılaştırma cetveli: `YBF_Algoritma_Tam_Dokuman.md` kanonik tabloları — hâkim: çerçevenin yazarı.\n",
           "\nHer −1'in taban kontrolü = taban-bütünlük varsayımının testi (türetilmiş −1 ⇒ temel −1).\n\n---\n"]
    for i, (tr, en) in enumerate(CONCEPTS, 1):
        text = ""
        for attempt in range(3):
            try:
                r = model.generate_content(USER_TEMPLATE.format(tr=tr, en=en), generation_config=cfg)
                text = r.text or ""
                break
            except Exception as e:
                if attempt == 2:
                    text = f"(HATA: {str(e)[:120]})"
                else:
                    time.sleep(2 ** attempt)
        out.append(f"\n\n## {i}. {tr} ({en})\n\n{text.strip()}\n\n---\n")
        print(f"  {i:2d}/12  {tr} ✓ ({len(text)} char)", flush=True)

    path = "AIEgitim-turetme-deneyi.md"
    open(path, "w").write("".join(out))
    print(f"\n✓ kaydedildi: {path}")


if __name__ == "__main__":
    main()
