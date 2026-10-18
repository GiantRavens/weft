"""Cherokee in Sequoyah's syllabary: sign -> syllable -> sound, with a generated romanization row.

The text is printed in the syllabary as the New Echota press set it from 1828. Each sign stands for a syllable (Ꮳ tsa,
Ꮃ la, Ꭹ gi), for a lone vowel (Ꭰ a), or for s alone (Ꮝ). The romanization under the text is generated from the signs,
one syllable per sign, in the transliteration that descends from Samuel Worcester's chart (ᏣᎳᎩ tsalagi). The table
is read from the Unicode character names (CHEROKEE LETTER TSA), which use it, so no sign value is typed by hand.
Ᏽ, which the press omitted for want of type, is mv after its Unicode name. The romanization is not reversible in
every case: Ꮐ nah before a vowel sign spells the same letters as Ꮎ na before an h-row sign. The lowercase letters of Unicode 8 are read as their capitals.

What the syllabary does not write, and the sound row therefore cannot give:
- tone and pitch accent: Cherokee distinguishes words by pitch, and no mark records it. The sound row has no
  capitals for that reason; it does not claim an accent.
- vowel length.
- a syllable-final h or glottal stop: Ꮡ is both suu and suh.
- whether a written vowel is said: a sign may carry a vowel only to write a consonant cluster (ᏧᎾᏍᏗ, said with
  no vowel after n). The sound row says every written vowel.
- voicing in the qu-row (gw and kw are one sign).

Schemes
-------
c1828    Cherokee as the New Echota press wrote it in 1828, approximate. What rests on Samuel Worcester's answer to
         Rafinesque's questions (Cherokee Phoenix, vol. 1 no. 23, 6 August 1828, p. 2, as transcribed by Western
         Carolina University): of the gi in the nation's name, "G. as pronounced by Germans represents it best",
         and of five g-signs "the sound of German G is most common", so the g-row is read as an unaspirated stop;
         of six signs for English D, "the consonant sound of the three first of which is always, and that of the
         three latter often, better represented by D. than by T." (taken here to be da, de, di and do, du, dv, an
         inference from the recitation order: the letter does not name them); v has "nearly the sound of un
         French"; English J, Ch and soft G in proper names are written with the ts-row (Tsa-tsi, George), so it
         was the nearest Cherokee sound to them; the press's dialect has l where "one dialect" has r. The ts-row
         is read as [ts], the value Worcester's spelling Ts suggests, but the letter does not settle it, and
         present descriptions give [ts] or [dʒ] by dialect. What rests on present descriptions of the syllabary
         instead: ka and the t-row (ta, te, ti) as aspirated stops, hna as a voiceless n, the laterals tl and dl,
         and w, y, h, l, m, n, s. Worcester's remark that many syllables "are sometimes aspirated" (hwi, hli, and
         no "as if written hno") is not modeled.
modern   Cherokee as the syllabary is read in Oklahoma today: the same values, with ts as [dʒ] (the j of jam), the
         g- and d-rows as plain unaspirated k and t, and w as a glide made without rounding the lips ([ɰ]).

Edition token fields (texts/<work>/edition.yaml)
-----------------------------------------------
t          the word in the syllabary as printed, punctuation attached
ocr        the OCR witness's reading of this word where the print differs (see weft.ocr.witness_check)
uncertain  {alt, why}: a sign the scan cannot settle; alt is the other reading. Shown in the word's detail and
           marked on the page
sound      {scheme: {ipa, respell}}: the sound given outright, for a word the syllabary does not spell
           (a number such as 1827)
"""
from __future__ import annotations

import re
import unicodedata as ud

VERSION = "0.1"
INDIGENOUS = True          # weft check requires a stewardship block (pipeline/weft/stewardship.py)
SHOW_TRANSLIT = True
TRANSLIT_LABEL = "Romanization"
LAYERS = {"translit": {"src": f"weft.cherokee {VERSION}: generated from the syllabary, one syllable per sign "
                              "(the transliteration of the Unicode character names)"}}

LEAD_P = re.compile(r"^([(\[“‘\"«—]+)")
TRAIL_P = re.compile(r"([,;:!?.)\]”’\"»—-]+)$")

VOWELS = "aeiouv"
ONSETS = ("", "g", "k", "h", "l", "m", "n", "hn", "qu", "s", "d", "t", "dl", "tl", "ts", "w", "y")


def _table() -> dict[str, tuple[str, str, str]]:
    """Every capital sign in U+13A0..U+13F5 -> (onset, vowel, coda), read from its Unicode name."""
    out = {}
    for cp in range(0x13A0, 0x13F6):
        syl = ud.name(chr(cp)).removeprefix("CHEROKEE LETTER ").lower()
        if syl == "s":
            out[chr(cp)] = ("s", "", "")
        elif syl == "nah":                     # Ꮐ: na closed by h
            out[chr(cp)] = ("n", "a", "h")
        else:
            out[chr(cp)] = (syl[:-1], syl[-1], "")
    return out


SIGNS = _table()
assert len(SIGNS) == 86 and all(o in ONSETS and (v in VOWELS or o == "s") for o, v, _ in SIGNS.values())
ROMAN = {s: o + v + c for s, (o, v, c) in SIGNS.items()}
FROM_ROMAN = sorted(((r, s) for s, r in ROMAN.items()), key=lambda x: -len(x[0]))

# (ipa, respelling) per scheme
VOWEL_SOUND = {"a": ("a", "ah"), "e": ("e", "ay"), "i": ("i", "ee"), "o": ("o", "oh"), "u": ("u", "oo"), "v": ("ə̃", "uhn")}
ONSET_SOUND = {
    "c1828": {"": ("", ""), "g": ("ɡ̊", "g"), "k": ("kʰ", "k"), "h": ("h", "h"), "l": ("l", "l"), "m": ("m", "m"),
              "n": ("n", "n"), "hn": ("n̥", "hn"), "qu": ("kʷ", "kw"), "s": ("s", "s"), "d": ("d̥", "d"),
              "t": ("tʰ", "t"), "dl": ("d͡ɮ", "dl"), "tl": ("t͡ɬ", "tl"), "ts": ("t͡s", "ts"), "w": ("w", "w"), "y": ("j", "y")},
}
ONSET_SOUND["modern"] = dict(ONSET_SOUND["c1828"], g=("k", "g"), d=("t", "d"), ts=("d͡ʒ", "j"), w=("ɰ", "w"))

_CTX: dict = {}


def capital(ch: str) -> str:
    """A Unicode 8 lowercase Cherokee letter as its capital; anything else unchanged."""
    up = ch.upper()
    return up if len(up) == 1 and up in SIGNS else ch


def signs(word: str) -> list[str]:
    return [capital(c) for c in word]


def romanize(word: str) -> str:
    return "".join(ROMAN.get(c, c) for c in signs(word))


def from_roman(word: str) -> list[str]:
    """A romanized word back to signs, longest syllable first; nah before a vowel is read as na + h-row."""
    out, i = [], 0
    while i < len(word):
        for r, s in FROM_ROMAN:
            if r == "nah" and word[i + 3:i + 4] in tuple(VOWELS):      # na + an h-row sign, not Ꮐ
                continue
            if word.startswith(r, i):
                out.append(s); i += len(r); break
        else:
            i += 1
    return out


def syllables(sg: list[str]) -> list[tuple[str, str, str]]:
    """Signs -> spoken syllables (onset, vowel, coda). Ꮝ, s with no vowel, closes the syllable before it
    (ᎾᏍᎩ nas-gi) or, at the start of a word, begins the first (ᏍᎩ sgi)."""
    out: list[list[str]] = []
    pending_s = ""
    for c in sg:
        o, v, coda = SIGNS[c]
        if not v:                              # Ꮝ
            if out:
                out[-1][2] += "s"
            else:
                pending_s += "s"
            continue
        out.append([pending_s + o, v, coda])
        pending_s = ""
    if pending_s:                              # a word of Ꮝ alone
        out.append([pending_s, "", ""])
    return [tuple(x) for x in out]


def word_sound(sg: list[str], scheme: str) -> tuple[str, str, int]:
    table = ONSET_SOUND[scheme]
    ipas, rss = [], []
    for o, v, coda in syllables(sg):
        rest = o.lstrip("s")
        if o.startswith("s") and rest != o and rest in table and o not in table:     # word-initial s before a consonant (ᏍᎩ)
            k = len(o) - len(rest)
            oi, orr = "s" * k + table[rest][0], "s" * k + table[rest][1]
        else:
            oi, orr = table.get(o, (o, o))
        vi, vr = VOWEL_SOUND.get(v, ("", ""))
        ipas.append(oi + vi + coda)
        rss.append(orr + vr + coda)
    return ".".join(ipas), "-".join(rss), len(ipas)


# ---------------------------------------------------------------- language hooks
def token_fields(surface: str, et: dict, group: dict) -> tuple[dict, list[tuple[str, str]]]:
    """Split punctuation off the printed word, generate the romanization, flag a character outside the syllabary,
    and carry an uncertain sign into the word's provenance."""
    global _CTX
    fields: dict = {}
    fails: list[tuple[str, str]] = []
    word = surface
    ml = LEAD_P.search(word)
    if ml:
        fields["lead"] = ml.group(1)
        word = word[ml.end():]
    mt = TRAIL_P.search(word)
    if mt:
        fields["punct"] = mt.group(1)
        word = word[:mt.start()]
    if word != surface:
        fields["surface"] = word
    sg = signs(word)
    outside = "".join(c for c in sg if c not in SIGNS)
    if outside and not et.get("sound"):
        fails.append(("not-syllabary", f"{word} ({outside})"))
    if not outside:
        fields["norm"] = romanize(word)
    unc = et.get("uncertain")
    if unc:
        if not (isinstance(unc, dict) and unc.get("alt") and unc.get("why")):
            fails.append(("uncertain-malformed", word))
        else:
            fields["uncertain"] = True
            fields["prov"] = {"text": f"an uncertain sign; the scan also allows {unc['alt']} ({romanize(unc['alt'])}); {unc['why']}"}
    _CTX = {"norm": fields.get("norm"), "word": word, "signs": sg, "sound": et.get("sound") or {}}
    return fields, fails


def phonemize(word: str, scheme: str = "c1828", quantities=None, **_) -> dict:
    """`word` is the token's romanization (draft passes the norm row), its printed form when it has none, the
    syllabary itself, or a romanized word. The signs and any sound override token_fields stored apply only when the
    word is the token token_fields just read."""
    mine = _CTX.get("norm") == word
    ov = (_CTX.get("sound") or {}).get(scheme)
    if ov and (mine or word == _CTX.get("word")):
        return {"ipa": ov["ipa"], "respell": ov["respell"], "syllables": len(re.split(r"[. ]", ov["ipa"]))}
    ipas, rss, n = [], [], 0
    for w in word.split():
        sg = _CTX["signs"] if mine and len(word.split()) == 1 else (
            signs(w) if any(capital(c) in SIGNS for c in w) else from_roman(w.lower()))
        sg = [c for c in sg if c in SIGNS]
        ipa, rs, k = word_sound(sg, scheme)
        ipas.append(ipa); rss.append(rs); n += k
    return {"ipa": " ".join(ipas), "respell": " ".join(rss), "syllables": n}


def line_checks(text: str, etoks: list[dict], edition: dict) -> list[tuple[str, str]]:
    """Sensor: with `ocr_check` in the edition, each line must occur in the OCR witness, every difference declared
    on its token (weft.ocr.witness_check)."""
    from .ocr import witness_check
    return witness_check(etoks, edition, "chr")


KEY = {
    "c1828": [
        ("", "Cherokee as the New Echota press wrote it in 1828, approximate: the g, d, v and ts values follow what Samuel Worcester wrote in the Cherokee Phoenix of 6 August 1828; the rest follow present descriptions of the syllabary. Tone, pitch accent and vowel length are not written in the syllabary, so this row cannot give them; there are no capitals because no accent is claimed."),
        ("hyphens", "divide the syllables, one per sign; s alone (Ꮝ) joins the syllable before it"),
        ("ah ay ee oh oo", "the vowels a, e, i, o, u: a as in father, e as in they, i as in machine, o as in go, u as in rule, each without a glide"),
        ("uhn", "the vowel v: the u of but said through the nose, \"nearly the sound of un French\" (Worcester)"),
        ("g d", "between English g and k, d and t: no puff of breath. Worcester on g: \"G. as pronounced by Germans represents it best\"; on d: \"better represented by D. than by T.\""),
        ("k t", "ka and the t-row (ta, te, ti): with a puff of breath, as in English"),
        ("hn", "an n breathed through, without voice (the sign hna)"),
        ("kw", "the qu-row; it sometimes writes the p and b of English names"),
        ("tl dl", "a t or d released into a lateral hiss: the tongue on the ridge behind the teeth, air past its sides"),
        ("ts", "ts as in cats, the value Worcester's spelling suggests; English j, ch and soft g in names were written with this row (Tsa-tsi, George), and some dialects say it as the j of jam"),
        ("w y h l m n s", "much as in English"),
        ("nahh", "the sign nah: na closed by a breathed h"),
    ],
    "modern": [
        ("", "Cherokee as the syllabary is read in Oklahoma today, each word said alone. Tone, pitch accent and vowel length are not written in the syllabary, so this row cannot give them."),
        ("hyphens", "divide the syllables, one per sign; s alone (Ꮝ) joins the syllable before it"),
        ("ah ay ee oh oo", "the vowels a, e, i, o, u: a as in father, e as in they, i as in machine, o as in go, u as in rule"),
        ("uhn", "the vowel v: the u of but said through the nose"),
        ("g d", "a plain k and t, without the puff of breath of English k and t"),
        ("k t", "ka and the t-row: k and t with a puff of breath"),
        ("j", "the ts-row, said as j in jam by most speakers"),
        ("w", "a glide like w, made without rounding the lips"),
        ("hn", "an n breathed through, without voice"),
        ("kw", "the qu-row"),
        ("tl dl", "a t or d released into a lateral hiss"),
        ("y h l m n s", "much as in English"),
    ],
}
SCHEME_LABELS = {"c1828": "Cherokee of the New Echota press, 1828 (approximate)",
                 "modern": "Cherokee as read in Oklahoma today"}
