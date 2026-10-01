"""Old Egyptian: TLA tokens -> hieroglyphs, lemma and morphology; a hand vocalization -> sound.

Weft's first Egyptian work is the opening of Pyramid Text 273 (the "Cannibal Hymn") as carved in
the pyramid of Unas at Saqqara, about 2350 BC. Each token in the edition carries:

  t    the transliteration of the Thesaurus Linguae Aegyptiae (TLA, Berlin-Brandenburg Academy),
       verbatim from the January 2018 database excerpt (CC BY-SA 4.0) as distributed in Simon
       Schweitzer's AES corpus. TLA conventions of that release: j for the reed leaf, a comma
       before the feminine t, .pl and .du for plural and dual endings the script does not write,
       round brackets for sounds the editor restores
  tla  the TLA token id. Through it this module reads the TLA's lemma, part of speech and
       morphological features (the treebank, rule 3) and its Gardiner sign codes
  n    Weft's vocalization, hand-entered: the word in Egyptological letters with the vowels a
       scholar would reconstruct, where evidence exists (pí.t, nā́ṯir, rín), and the bare
       transliteration where it does not (gp, sdꜣ). It drives both sound schemes

The hieroglyph row is generated from the TLA's Gardiner codes. Unicode names the Egyptian
Hieroglyphs block by Gardiner number (EGYPTIAN HIEROGLYPH W011 is W11), so the mapping is
derived from the Unicode character names in Python's unicodedata, with no separate sign list.
A code outside the basic block is reported (`sign-not-in-unicode`), never guessed; a lettered
variant of a sign Unicode encodes (D3B) is shown as its base sign and reported
(`sign-variant-shown-as-base`). Signs are written in a line, without the quadrat grouping of the wall.

Morphology is the TLA's, recoded as Universal Dependencies features: participle VerbForm=Part,
infinitive VerbForm=Inf, relative form VerbForm=Rel, the stative (pseudoparticiple)
Tense=Stative, and the n-morpheme of the suffix conjugation (sḏm.n=f) Tense=Perf, following the
common label "perfect". Person, number and gender of the personal pronouns (=f, =sn, sw) are not
tagged per token in the TLA; they are fixed by the lemma and filled from it.

Pronunciation
-------------
Egyptian writing records consonants only. The vowels have to be inferred from later evidence:
Coptic, the last stage of the language, written in an alphabet with vowels about 2,500 years after
these texts, and Egyptian words and names written in cuneiform and Greek. This is the most
reconstructed sound row in the library, and it is conjectural word by word.

old-egyptian   Reconstructed Old Egyptian, about 2350 BC. Consonant values follow the outline of
               Loprieno (1995) and Allen (2013): ꜣ a uvular r, ꜥ a pharyngeal, ḥ a pharyngeal h,
               ṯ and ḏ palatal stops, and d and ḏ read as ejectives, as Loprieno proposes. Each of
               these values is debated. Vowels and stress come from the vocalization n, entered
               by Weft only where a Coptic descendant of the word, or a Greek rendering of a name,
               gives the vowel and the stressed syllable; the edition names that evidence for each
               form, and the page shows it in the word's provenance. These vocalizations are
               Weft's inference by the sound correspondences in those grammars, not forms quoted
               from them. Where no such evidence was used, the word falls back to the
               Egyptological convention below, and its provenance says so.
egyptological  The conventional pronunciation used in teaching: e inserted between consonants,
               ꜣ and ꜥ said as a, j as i, w as u. It is a modern convention for saying the words
               aloud and makes no claim about ancient speech.
"""
from __future__ import annotations

import html
import json
import re
import unicodedata as ud
from pathlib import Path

VERSION = "0.1"
SCRIPT_LABEL = "Script (hieroglyphs)"
SCRIPT_WORD = "hieroglyphs"
SHOW_TRANSLIT = True
TRANSLIT_LABEL = "Vocalization (conjectural)"

REPO = Path(__file__).resolve().parents[2]

LAYERS = {
    "lemma": {"src": "TLA 2018 database excerpt (CC BY-SA 4.0), via the AES corpus: TLA lemma"},
    "morph": {"src": f"TLA 2018 part of speech and features, recoded as Universal Dependencies by weft.egyptian {VERSION}"},
    "script": {"src": f"weft.egyptian {VERSION}: hieroglyphs generated from the TLA Gardiner codes via Unicode character names (Unicode {ud.unidata_version})"},
    "signs": {"src": "TLA 2018: Gardiner codes of the word's writing"},
    "translit": {"src": "Weft edition: hand vocalization where Coptic or Greek evidence was used, bare transliteration otherwise"},
}

# ---------------------------------------------------------------- TLA tokens
_TLA: dict[str, dict[str, tuple[str, dict]]] = {}


def tla_index(rel: str) -> dict[str, tuple[str, dict]]:
    """token id -> (sentence id, token) for an AES JSON file, path relative to the repository."""
    if rel not in _TLA:
        data = json.loads((REPO / rel).read_text(encoding="utf-8"))
        idx = {}
        for sid, s in data.items():
            for t in s.get("token", []):
                if t.get("_id"):
                    idx[t["_id"]] = (sid, t)
        _TLA[rel] = idx
    return _TLA[rel]


UPOS = {"verb": "VERB", "substantive": "NOUN", "entity_name": "PROPN", "pronoun": "PRON",
        "preposition": "ADP", "particle": "PART", "adjective": "ADJ", "epitheton_title": "NOUN",
        "adverb": "ADV", "numeral": "NUM", "interjection": "INTJ"}
FEATS = {
    "numerus": {"singular": "Number=Sing", "plural": "Number=Plur", "dual": "Number=Dual"},
    "genus": {"masculine": "Gender=Masc", "feminine": "Gender=Fem"},
    "status": {"st_absolutus": "State=Abs", "st_constructus": "State=Cons", "st_pronominalis": "State=Pronominal"},
    "inflection": {"participle": "VerbForm=Part", "infinitive": "VerbForm=Inf", "relativeform": "VerbForm=Rel",
                   "pseudoParticiple": "Tense=Stative", "suffixConjugation": "VerbForm=Fin", "imperative": "Mood=Imp"},
    "voice": {"active": "Voice=Act", "passive": "Voice=Pass"},
    "pronoun": {"personal_pronoun": "PronType=Prs", "demonstrative_pronoun": "PronType=Dem"},
    "morphology": {"n-morpheme": "Tense=Perf"},
}
# person, number and gender belong to the pronoun's lemma (TLA lemma id)
PRONOUN_FEATS = {"10050": "Person=3|Number=Sing|Gender=Masc", "10090": "Person=3|Number=Sing|Gender=Fem",
                 "10100": "Person=3|Number=Plur", "10110": "Person=2|Number=Sing|Gender=Masc",
                 "129490": "Person=3|Number=Sing|Gender=Masc", "136190": "Person=3|Number=Plur"}


def ud_morph(t: dict) -> str:
    feats = []
    for field, table in FEATS.items():
        v = table.get(t.get(field, ""))
        if v:
            feats.append(v)
    if t.get("lemmaID") in PRONOUN_FEATS:
        feats = [f for f in feats if not f.startswith(("Number=", "Gender="))] + PRONOUN_FEATS[t["lemmaID"]].split("|")
    return "|".join([UPOS.get(t.get("pos", ""), "X")] + feats)


# ---------------------------------------------------------------- hieroglyphs
_SIGNS: dict[str, str] | None = None


def gardiner_table() -> dict[str, str]:
    """Gardiner code -> character, from the Unicode names of the Egyptian Hieroglyphs block:
    EGYPTIAN HIEROGLYPH AA001 -> Aa1, D003 -> D3, A005A -> A5A."""
    global _SIGNS
    if _SIGNS is None:
        _SIGNS = {}
        for cp in range(0x13000, 0x13430):
            try:
                name = ud.name(chr(cp))
            except ValueError:
                continue
            m = re.fullmatch(r"EGYPTIAN HIEROGLYPH ([A-Z]{1,2})0*(\d+)([A-Z]?)", name)
            if m:
                _SIGNS[f"{m.group(1).capitalize()}{int(m.group(2))}{m.group(3)}"] = chr(cp)
    return _SIGNS


def to_hieroglyphs(codes: str) -> tuple[str, list[tuple[str, str]]]:
    """'W11-Q3' -> '𓊪𓎼' style string, and the failures: unmapped codes, variants shown as base."""
    table = gardiner_table()
    out, fails = [], []
    for c in [x for x in re.split(r"[-:*&]", codes) if x]:
        if c in table:
            out.append(table[c])
            continue
        m = re.fullmatch(r"([A-Z][a-z]?\d+)[A-Z]+", c)
        if m and m.group(1) in table:
            out.append(table[m.group(1)])
            fails.append(("sign-variant-shown-as-base", f"{c} as {m.group(1)}"))
        else:
            fails.append(("sign-not-in-unicode", c))
    return "".join(out), fails


# ---------------------------------------------------------------- vocalization helpers
ACUTE, MACRON = "́", "̄"
VOWELS = set("aiuə")
CLITICS = {"=f": "Coptic suffix -ϥ (f): a consonant joined to the word before",
           "=s": "Coptic suffix -ⲥ (s): a consonant joined to the word before"}


def skeleton(n: str) -> str:
    """The consonantal transliteration under a vocalized form: nā́ṯir -> nṯr."""
    d = ud.normalize("NFD", n).replace(ACUTE, "").replace(MACRON, "")
    return ud.normalize("NFC", "".join(c for c in d if c not in VOWELS))


def vocalized(n: str) -> bool:
    return skeleton(n) != ud.normalize("NFC", n)


def letters(s: str) -> str:
    """Letters only, for comparing TLA's transliteration with Weft's: markers and brackets dropped."""
    s = re.sub(r"[.,](pl|du)\b", "", s).replace("i\u032f", "j").replace("ʾ", "")   # TLA i̯ is Leiden j; ʾ marks no sound here
    return "".join(c for c in ud.normalize("NFC", s).lower() if c.isalpha() or c in "ꜣꜥ")


def _subsequence(a: str, b: str) -> bool:
    it = iter(b)
    return all(c in it for c in a)


def token_fields(surface: str, et: dict, group: dict) -> tuple[dict, list[tuple[str, str]]]:
    fields: dict = {}
    fails: list[tuple[str, str]] = []
    n = et.get("n", surface)
    rel = group.get("tla_file")
    hit = tla_index(rel).get(et.get("tla", "")) if rel else None
    if not hit:
        fails.append(("tla-token-missing", f"{surface} {et.get('tla')}"))
    else:
        sid, t = hit
        if t.get("written_form") != surface:
            fails.append(("edition-differs-from-tla", f"{surface} vs {t.get('written_form')}"))
        fields["lemma"] = t.get("lemma_form", "")
        fields["morph"] = ud_morph(t)
        fields["tb"] = f"{sid}/{t['_id']}"
        codes = t.get("hiero", "")
        if codes:
            fields["signs"] = codes
            glyphs, gf = to_hieroglyphs(codes)
            fields["script"] = glyphs
            fails += [(c, f"{surface}: {s}") for c, s in gf]
            theirs = html.unescape(t.get("hiero_unicode", ""))
            if theirs and theirs != glyphs:
                fails.append(("script-differs-from-tla", f"{surface}: {glyphs} vs {theirs}"))
        else:
            fails.append(("signs-missing", surface))
        # sensor: Weft's vocalization must keep every letter of the TLA transliteration
        if not _subsequence(letters(surface), letters(skeleton(n))):
            fails.append(("vocalization-consonants-differ", f"{surface} vs {n}"))
    basis = (group.get("vocalization") or {}).get(n)
    if vocalized(n) or n in CLITICS:
        if not basis and n not in CLITICS:
            fails.append(("vocalization-without-basis", n))
        fields["prov"] = {"sound": f"reconstructed (conjectural): {basis or CLITICS.get(n)}"}
        fields["conf"] = {"sound": 0.3}
    else:
        fields["prov"] = {"sound": "not reconstructed: no vowel evidence used; the first scheme gives the Egyptological convention"}
    return fields, fails


def line_checks(text: str, etoks: list[dict], edition: dict) -> list[tuple[str, str]]:
    """Sensor: one Weft line is one column of the wall; every token must come from that column."""
    rel = next((s.get("tla_file") for s in edition.get("sections", []) if s.get("tla_file")), None)
    if not rel:
        return []
    idx = tla_index(rel)
    cols = {idx[et["tla"]][1].get("lineCount", "").strip() for et in etoks if et.get("tla") in idx}
    return [("column-split", f"{text[:30]}: {sorted(cols)}")] if len(cols) > 1 else []


# ---------------------------------------------------------------- sound: Egyptological convention
CONV_C = {"b": "b", "p": "p", "f": "f", "m": "m", "n": "n", "r": "r", "h": "h", "ḥ": "h", "ḫ": "kh",
          "ẖ": "kh", "z": "s", "s": "s", "š": "sh", "q": "k", "k": "k", "g": "g", "t": "t", "ṯ": "tj",
          "d": "d", "ḏ": "dj"}
CONV_IPA = {"kh": "x", "sh": "ʃ", "tj": "tʃ", "dj": "dʒ", "g": "ɡ"}
CONV_V = {"ꜣ": "a", "ꜥ": "a", "j": "i", "y": "i"}
CONV_EXCEPTIONS = {"ꜥnḫ": "ankh", "gbb": "geb"}     # fixed classroom forms the e-rule would not give


def _conv_units(word: str) -> list[tuple[str, str]]:
    """Letters -> (kind, sound) units: V for the letters said as vowels, C for consonants."""
    segs = [c for c in ud.normalize("NFC", word.lower()) if c in CONV_C or c in CONV_V or c == "w"]
    out = []
    for k, c in enumerate(segs):
        if c == "w":
            nxt = segs[k + 1] if k + 1 < len(segs) else ""
            out.append(("C", "w") if nxt in CONV_V else ("V", "u"))
        elif c in CONV_V:
            out.append(("V", CONV_V[c]))
        else:
            out.append(("C", CONV_C[c]))
    return out


def _conv_word(word: str) -> tuple[str, str, int]:
    key = re.sub(r"[.=]", "", ud.normalize("NFC", word.lower()))
    seq: list[tuple[str, str]] = []
    if key in CONV_EXCEPTIONS:
        seq = _conv_units_plain(CONV_EXCEPTIONS[key])
    else:
        for u in _conv_units(word):
            if seq and seq[-1][0] == "C" and u[0] == "C":
                seq.append(("V", "e"))
            seq.append(u)
    if seq and all(u[0] == "C" for u in seq):          # a lone consonant: m -> em, =f -> ef
        seq.insert(0, ("V", "e"))
    sylls = _syllabify(seq)
    rsp = "-".join("".join(s for _, s in sy) for sy in sylls)
    ipa = ".".join("".join(CONV_IPA.get(s, s) for _, s in sy) for sy in sylls)
    return ipa, rsp, len(sylls)


def _conv_units_plain(s: str) -> list[tuple[str, str]]:
    out, k = [], 0
    while k < len(s):
        two = s[k:k + 2]
        if two in ("kh", "sh", "tj", "dj"):
            out.append(("C", two)); k += 2
        elif s[k] in "aeiou":
            out.append(("V", s[k])); k += 1
        else:
            out.append(("C", s[k])); k += 1
    return out


def _syllabify(seq: list[tuple[str, str]]) -> list[list[tuple[str, str]]]:
    """One consonant before a vowel opens its syllable; other consonants close the syllable before."""
    vi = [k for k, u in enumerate(seq) if u[0] == "V"]
    if not vi:
        return [seq] if seq else []
    bounds = [0]
    for a, b in zip(vi, vi[1:]):
        bounds.append(b if b - a == 1 else b - 1)
    bounds.append(len(seq))
    return [seq[bounds[j]:bounds[j + 1]] for j in range(len(vi))]


def conventional(word: str) -> dict:
    parts = [_conv_word(p) for p in re.split(r"[-\s]+", skeleton(word).lstrip("=")) if p]
    return {"ipa": " ".join(p[0] for p in parts), "respell": " ".join(p[1] for p in parts),
            "syllables": sum(p[2] for p in parts)}


# ---------------------------------------------------------------- sound: reconstructed Old Egyptian
OE_IPA = {"ꜣ": "ʀ", "j": "j", "y": "j", "ꜥ": "ʕ", "w": "w", "b": "b", "p": "p", "f": "f", "m": "m",
          "n": "n", "r": "r", "h": "h", "ḥ": "ħ", "ḫ": "x", "ẖ": "ç", "z": "z", "s": "s", "š": "ʃ",
          "q": "q", "k": "k", "g": "ɡ", "t": "t", "ṯ": "c", "d": "tʼ", "ḏ": "cʼ"}
OE_RSP = {"ꜣ": "ʀ", "j": "y", "y": "y", "ꜥ": "ʕ", "ḥ": "hh", "ḫ": "kh", "ẖ": "hy", "š": "sh",
          "ṯ": "ty", "d": "t'", "ḏ": "ty'", "g": "g"}
OE_V_RSP = {("a", False): "a", ("i", False): "i", ("u", False): "u", ("ə", False): "uh",
            ("a", True): "aa", ("i", True): "ee", ("u", True): "oo"}


def _oe_segments(word: str) -> list[dict]:
    """Vocalized form -> segments {kind V/C, base, long, stress}. A j or w with no vowel beside it
    is read as the vowel i or u (Wánjs -> wa.nis)."""
    d = ud.normalize("NFD", word.lower())
    segs: list[dict] = []
    k = 0
    while k < len(d):
        c = d[k]
        k += 1
        marks = ""
        while k < len(d) and ud.combining(d[k]):
            marks += d[k]
            k += 1
        if c in VOWELS:
            segs.append({"kind": "V", "base": c, "long": MACRON in marks, "stress": ACUTE in marks})
        else:
            base = ud.normalize("NFC", c + marks.replace(ACUTE, "").replace(MACRON, ""))
            if base in OE_IPA:
                segs.append({"kind": "C", "base": base})
    for k, s in enumerate(segs):
        if s["kind"] == "C" and s["base"] in "jw":
            prev = segs[k - 1]["kind"] if k else None
            nxt = segs[k + 1]["kind"] if k + 1 < len(segs) else None
            if prev != "V" and nxt != "V":
                segs[k] = {"kind": "V", "base": "i" if s["base"] == "j" else "u", "long": False, "stress": False}
    return segs


def reconstruct(word: str) -> dict:
    segs = _oe_segments(word)
    sylls = _syllabify([(s["kind"], s) for s in segs])
    ipa, rsp = [], []
    for sy in sylls:
        i, r, stressed = "", "", False
        for kind, s in sy:
            if kind == "V":
                i += s["base"] + ("ː" if s["long"] else "")
                r += OE_V_RSP[(s["base"], s["long"])]
                stressed = stressed or s["stress"]
            else:
                i += OE_IPA[s["base"]]
                r += OE_RSP.get(s["base"], s["base"])
        if stressed:
            i = "ˈ" + i
            r = "".join(ch.upper() if ch.isascii() else ch for ch in r)
        ipa.append(i)
        rsp.append(r)
    return {"ipa": ".".join(ipa), "respell": "-".join(rsp), "syllables": len(sylls)}


def phonemize(word: str, scheme: str = "old-egyptian", quantities=None, **_) -> dict:
    """The edition's n (a vocalized form, or a bare transliteration) in the given scheme."""
    if scheme == "egyptological":
        return conventional(word)
    if word in CLITICS:
        c = skeleton(word).lstrip("=")
        return {"ipa": "".join(OE_IPA[x] for x in c), "respell": "-" + "".join(OE_RSP.get(x, x) for x in c), "syllables": 0}
    if vocalized(word):
        return reconstruct(word)
    return conventional(word)


KEY = {
    "old-egyptian": [
        ("", "Old Egyptian as it may have sounded about 2350 BC. This is the most reconstructed sound row in the library. Hieroglyphic writing records consonants only; the vowels are inferred from Coptic, the language's last stage, written with vowels about 2,500 years later, and from Egyptian names written in Greek and cuneiform. Weft vocalizes a word only where such evidence was used, and names it in the word's provenance. Every other word is given in the Egyptological convention (second scheme), in lower case without a stress mark, and its provenance says so."),
        ("CAPS", "the stressed syllable, inferred from the stressed vowel of the word's Coptic descendant"),
        ("aa, ee, oo", "long vowels, ā ī ū, held about twice as long"),
        ("a, i, u", "short vowels: a as in father but short, i as in bit, u as in put"),
        ("ʀ", "the letter ꜣ, taken here as an r made at the back of the mouth, like a French r. Its value is debated; by the Middle Kingdom it seems to have weakened to a glottal stop or a y"),
        ("ʕ", "the letter ꜥ, a squeeze in the throat like Arabic ʿayn. Some scholars argue it was still a d-like stop in the earliest texts"),
        ("hh", "ḥ, a breathy h made deep in the throat, like Arabic ḥ"),
        ("kh", "ḫ, as in Scottish loch"),
        ("hy", "ẖ, the sound at the start of English hue, said with more friction"),
        ("ty", "ṯ, a t made with the tongue against the hard palate, close to the t in tune in British speech"),
        ("t', ty'", "d and ḏ, read here as ejectives (said with the throat closed and a popping release), as Loprieno proposes; others read them as voiced d and j"),
        ("y", "the reed-leaf letter j where it is a consonant. Between two consonants j and w are read as the vowels i and u"),
        ("-f, -s", "the pronoun suffixes =f (he, his) and =s (she, her), single consonants joined to the word before, as in Coptic"),
    ],
    "egyptological": [
        ("", "The conventional pronunciation used in Egyptology teaching. It inserts an e between consonants and says ꜣ and ꜥ as a, j as i, and w as u, so that the consonants can be said aloud. It is a modern convention, not a reconstruction of ancient speech; no stress is marked because the convention has none."),
        ("e", "a vowel supplied by the convention; the script writes none"),
        ("a", "ꜣ or ꜥ, both said as a"),
        ("i, u", "j and y said as i, and w said as u (as w before a vowel letter)"),
        ("kh", "ḫ and ẖ, as in Scottish loch"),
        ("sh", "š"),
        ("tj, dj", "ṯ and ḏ, said as ch in church and j in judge"),
        ("h, s, k", "ḥ said as h, z as s, and q as k"),
    ],
}
SCHEME_LABELS = {
    "old-egyptian": "Reconstructed Old Egyptian, about 2350 BC (conjectural)",
    "egyptological": "Egyptological convention (not a reconstruction)",
}


if __name__ == "__main__":
    import sys
    for w in sys.argv[1:]:
        for s in KEY:
            print(w, s, phonemize(w, s))
