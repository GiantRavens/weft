"""Esperanto, as its author described it: spelling -> syllables -> sound, and a reader of its grammar.

Evidence. Zamenhof set out the whole sound system in the Unua Libro (Warsaw, 1887; English edition
by R. H. Geoghegan, 1889, "Complete Grammar", A. The Alphabet) and fixed it in the Fundamento de
Esperanto (1905), rule 9 ("every word is read as it is written") and rule 10 ("the accent is always
on the last syllable but one"). The letters have one value each; the alphabet table gives the sounds
by comparison with other languages (c as ts, ĉ as English ch, ĝ as English j, ĥ as German ch, ĵ as
French j, ŭ as English w, j as English y, r trilled). So this scheme is a statement of the author's
rule, like Tolkien's Appendix E for the Elvish module, and not a reconstruction; what the rule leaves
open (the exact vowel qualities, which Zamenhof gave only by comparison; the division of consonant
clusters between syllables, which he did not give) is said in the KEY.

Scheme (one)
------------
zamenhof  "As Zamenhof described it: Unua Libro (1887), Fundamento (1905)". a e i o u = a e i o u
          (cardinal values, never reduced); c ts, ĉ tʃ, ĝ dʒ, ĥ x, ĵ ʒ, ŝ ʃ, ŭ w, j j, r trilled r,
          g always ɡ, s always s, z z, ĥ the ch of German Bach; aj ej oj uj aŭ eŭ are one syllable
          (a vowel with a glide); stress on the last syllable but one; an elided final o (kor',
          l') leaves the stress where it was, so the elided word is stressed on its last syllable.

Edition token fields (texts/<work>/edition.yaml)
-----------------------------------------------
t      the word as printed. The 1887 Unua Libro prints each word with its parts divided (Patr,o
       ni,a; the English transcription of the 1889 edition writes the division as an apostrophe,
       Patr'o ni'a), so that a reader can find each part in the vocabulary; the sound and the
       morphology are read from this division.
n      the word written as Esperanto has written it since the Fundamento: the parts joined
       (Patro nia). The lexicon is not needed: the sound follows from the letters. An elision
       apostrophe (kor’, l’) is the typographic apostrophe U+2019 and is kept in n.

Morphology (analyze)
--------------------
analyze(t) reads the divided word by the Fundamento's rules: -o noun, -a adjective, -e adverb, -j
plural, -n accusative, -as -is -os -us -u -i the verb; the participles -ant- -int- -ont- -at- -it-
-ot-; the pronouns, the correlatives and the small closed classes by table. It returns the lemma
(root with its class ending: pano, nia, esperi) and a Universal Dependencies feature string. It is
a rule, so a work's overlay declares it as an automatic analysis checked by hand (CLAUDE.md rule 3).
"""
from __future__ import annotations

import re
import unicodedata as ud

VERSION = "0.1"
SHOW_TRANSLIT = True
TRANSLIT_LABEL = "Fundamento spelling"

LEAD_P = re.compile(r"^([„“(\[«‹\"—–]+)")
TRAIL_P = re.compile(r"((?:[,.;:!?)\]”“»›\"…]|–|—)+)$")   # the elision apostrophe ’ stays with the word

VOWELS = "aeiou"
IPA_C = {"c": "ts", "ĉ": "tʃ", "ĝ": "dʒ", "ĥ": "x", "ĵ": "ʒ", "ŝ": "ʃ", "ŭ": "w", "j": "j", "r": "r", "g": "ɡ",
         "b": "b", "d": "d", "f": "f", "h": "h", "k": "k", "l": "l", "m": "m", "n": "n", "p": "p", "s": "s", "t": "t",
         "v": "v", "z": "z"}
RESP_C = {"ts": "ts", "tʃ": "ch", "dʒ": "j", "x": "kh", "ʒ": "zh", "ʃ": "sh", "w": "w", "j": "y", "r": "r", "ɡ": "g"}
RESP_V = {"a": "a", "e": "e", "i": "ee", "o": "o", "u": "oo"}
RESP_D = {"aj": "ai", "ej": "ay", "oj": "oy", "uj": "ooy", "aw": "ow", "ew": "ew"}
# obstruent + liquid clusters stay together as an onset (patro: pa.tro); everything else divides
ONSETS = {"pr", "br", "tr", "dr", "kr", "gr", "fr", "vr", "pl", "bl", "kl", "gl", "fl", "kv", "gv"}   # s + stop divides: es.tas, e.spe.ro is not said


def _letters(word: str) -> str:
    w = ud.normalize("NFC", word.lower())
    return "".join(ch for ch in w if ch.isalpha())


def _syllabify(w: str) -> list[str]:
    """Letters -> syllables. Each vowel is a nucleus; j and ŭ after a vowel close it as a glide;
    one consonant between vowels goes to the next syllable, two or more divide before the last,
    unless they form a permitted onset."""
    # group letters into units: vowel (with a following glide), consonant
    units: list[tuple[str, str]] = []
    i = 0
    while i < len(w):
        ch = w[i]
        if ch in VOWELS:
            if i + 1 < len(w) and w[i + 1] in "jŭ" and not (i + 2 < len(w) and w[i + 2] in VOWELS and w[i + 1] == "j"):
                units.append(("V", ch + w[i + 1])); i += 2; continue
            units.append(("V", ch)); i += 1; continue
        units.append(("C", ch)); i += 1
    sylls, cur = [], ""
    k = 0
    while k < len(units):
        kind, u = units[k]
        if kind == "C":
            # consonants before the next vowel: decide how many belong to this syllable's coda
            run = []
            while k < len(units) and units[k][0] == "C":
                run.append(units[k][1]); k += 1
            if not cur and not sylls:            # word-initial cluster
                cur += "".join(run); continue
            if k >= len(units):                  # word-final cluster
                cur += "".join(run); continue
            if len(run) == 1:
                sylls.append(cur); cur = run[0]
            else:
                tail = "".join(run[-2:])
                cut = len(run) - 2 if tail in ONSETS else len(run) - 1
                sylls.append(cur + "".join(run[:cut])); cur = "".join(run[cut:])
            continue
        cur += u; k += 1
        if k < len(units) and units[k][0] == "V":     # hiatus: two vowels, two syllables (mi.a)
            sylls.append(cur); cur = ""
    if cur:
        sylls.append(cur)
    return [s for s in sylls if s]


def _ipa_syl(s: str) -> str:
    out = ""
    i = 0
    while i < len(s):
        ch = s[i]
        if ch in VOWELS:
            if i + 1 < len(s) and s[i + 1] in "jŭ":
                out += ch + ("j" if s[i + 1] == "j" else "w"); i += 2; continue
            out += ch; i += 1; continue
        out += IPA_C.get(ch, ch); i += 1
    return out


def _resp_syl(s: str) -> str:
    out = ""
    i = 0
    while i < len(s):
        ch = s[i]
        if ch in VOWELS:
            if i + 1 < len(s) and s[i + 1] in "jŭ":
                out += RESP_D[ch + ("j" if s[i + 1] == "j" else "w")]; i += 2; continue
            out += RESP_V[ch]; i += 1; continue
        out += RESP_C.get(IPA_C.get(ch, ch), IPA_C.get(ch, ch)); i += 1
    return out


def word_sound(word: str) -> tuple[str, str, int]:
    """One word -> (ipa, respell, syllable count). An elision apostrophe at the end (kor’) or
    after a clitic article (l’mondo) is a boundary that does not move the stress."""
    w = ud.normalize("NFC", word.lower().replace("'", ""))
    elided = w.endswith("’")
    w = _letters(w)
    if not w:
        return "—", "—", 0
    sylls = _syllabify(w)
    if len(sylls) == 1:
        return _ipa_syl(sylls[0]), _resp_syl(sylls[0]), 1
    st = len(sylls) - 1 if elided else len(sylls) - 2     # the elided o would have been the last syllable
    ipa = ".".join(("ˈ" if k == st else "") + _ipa_syl(s) for k, s in enumerate(sylls))
    resp = "-".join(_resp_syl(s).upper() if k == st else _resp_syl(s) for k, s in enumerate(sylls))
    return ipa, resp, len(sylls)


_CTX: dict = {}


def token_fields(surface: str, et: dict, group: dict) -> tuple[dict, list[tuple[str, str]]]:
    """Split punctuation off the printed word; the word keeps its apostrophe divisions."""
    global _CTX
    fields: dict = {}
    fails: list[tuple[str, str]] = []
    word = surface
    ml = LEAD_P.search(word)
    if ml:
        fields["lead"] = ml.group(1); word = word[ml.end():]
    mt = TRAIL_P.search(word)
    if mt:
        fields["punct"] = mt.group(1); word = word[:mt.start()]
    if word != surface:
        fields["surface"] = word
    if not et.get("n"):
        fails.append(("fundamento-spelling-missing", surface))
    _CTX = {"t": word, "n": et.get("n"), "ipa": et.get("ipa") or {}}
    return fields, fails


def phonemize(word: str, scheme: str = "zamenhof", quantities=None, **_) -> dict:
    ov = (_CTX.get("ipa") or {}).get(scheme) if _CTX.get("n") == word else None
    if ov:
        return {"ipa": ov, "respell": ov, "syllables": len(ov.split("."))}
    parts = [p for p in re.split(r"[-\s]+", word) if p]
    ipas, rss, n = [], [], 0
    for p in parts:
        ipa, rs, k = word_sound(p)
        ipas.append(ipa); rss.append(rs); n += k
    return {"ipa": "-".join(ipas), "respell": "-".join(rss), "syllables": n}


# ---------------------------------------------------------------- morphology by rule
PRON = {"mi": (1, "Sing"), "vi": (2, None), "li": (3, "Sing"), "ŝi": (3, "Sing"), "ĝi": (3, "Sing"), "ni": (1, "Plur"), "ili": (3, "Plur"), "oni": (3, None), "si": (3, None)}
CORREL = {  # the table words: (lemma, morph)
    "kiu": ("kiu", "PRON|PronType=Rel"), "kio": ("kio", "PRON|PronType=Int"), "kia": ("kia", "DET|PronType=Int"), "kiel": ("kiel", "ADV|PronType=Rel"),
    "kial": ("kial", "ADV|PronType=Int"), "kiom": ("kiom", "ADV|PronType=Int"), "kiam": ("kiam", "ADV|PronType=Rel"), "kie": ("kie", "ADV|PronType=Rel"),
    "tiu": ("tiu", "DET|PronType=Dem"), "tio": ("tio", "PRON|PronType=Dem"), "tia": ("tia", "DET|PronType=Dem"), "tiel": ("tiel", "ADV|PronType=Dem"), "tiam": ("tiam", "ADV|PronType=Dem"),
    "ĉiu": ("ĉiu", "DET|PronType=Tot"), "ĉio": ("ĉio", "PRON|PronType=Tot"), "ĉiam": ("ĉiam", "ADV|PronType=Tot"), "io": ("io", "PRON|PronType=Ind"), "iu": ("iu", "PRON|PronType=Ind"),
    "nenio": ("nenio", "PRON|PronType=Neg"), "neniu": ("neniu", "PRON|PronType=Neg"),
}
CLOSED = {
    "la": ("la", "DET|Definite=Def|PronType=Art"), "kaj": ("kaj", "CCONJ"), "sed": ("sed", "CCONJ"), "aŭ": ("aŭ", "CCONJ"), "ĉar": ("ĉar", "SCONJ"), "ke": ("ke", "SCONJ"),
    "se": ("se", "SCONJ"), "ĉu": ("ĉu", "PART|PartType=Int"), "ne": ("ne", "PART|Polarity=Neg"), "en": ("en", "ADP"), "sur": ("sur", "ADP"), "al": ("al", "ADP"), "de": ("de", "ADP"),
    "el": ("el", "ADP"), "kun": ("kun", "ADP"), "sub": ("sub", "ADP"), "pri": ("pri", "ADP"), "por": ("por", "ADP"), "post": ("post", "ADP"), "antaŭ": ("antaŭ", "ADP"), "ĉe": ("ĉe", "ADP"),
    "sen": ("sen", "ADP"), "per": ("per", "ADP"), "da": ("da", "ADP"), "je": ("je", "ADP"), "inter": ("inter", "ADP"), "super": ("super", "ADP"), "ĉirkaŭ": ("ĉirkaŭ", "ADP"),
    "ankaŭ": ("ankaŭ", "ADV"), "hodiaŭ": ("hodiaŭ", "ADV"), "almenaŭ": ("almenaŭ", "ADV"), "jam": ("jam", "ADV"), "nur": ("nur", "ADV"), "tuj": ("tuj", "ADV"), "for": ("for", "ADV"),
    "mem": ("mem", "PRON|PronType=Emp"), "plej": ("plej", "ADV|Degree=Sup"), "pli": ("pli", "ADV|Degree=Cmp"), "nun": ("nun", "ADV"), "ho": ("ho", "INTJ"), "ha": ("ha", "INTJ"),
    "amen": ("amen", "INTJ"), "eĉ": ("eĉ", "ADV"), "tre": ("tre", "ADV"), "ja": ("ja", "ADV"), "ĝis": ("ĝis", "ADP"), "do": ("do", "ADV"), "ol": ("ol", "SCONJ"), "ju": ("ju", "ADV"),
}
VERB_END = {"as": "Mood=Ind|Tense=Pres|VerbForm=Fin", "is": "Mood=Ind|Tense=Past|VerbForm=Fin", "os": "Mood=Ind|Tense=Fut|VerbForm=Fin", "us": "Mood=Cnd|VerbForm=Fin", "u": "Mood=Imp|VerbForm=Fin", "i": "VerbForm=Inf"}
PART = {"ant": "Tense=Pres|Voice=Act", "int": "Tense=Past|Voice=Act", "ont": "Tense=Fut|Voice=Act", "at": "Tense=Pres|Voice=Pass", "it": "Tense=Past|Voice=Pass", "ot": "Tense=Fut|Voice=Pass"}


def analyze(printed: str) -> tuple[str, str]:
    """(lemma, UD features) for a word as the Unua Libro divides it (Pan'o'n, ŝuld'ant'o'j, est'u,
    kor’). A word printed without division is read from its ending."""
    w = ud.normalize("NFC", printed)
    w = LEAD_P.sub("", w); w = TRAIL_P.sub("", w)
    low = w.lower()
    elided = low.endswith("’")
    low = low.rstrip("’")
    clitic = ""
    if low.startswith("l’"):                       # l’mondo: the elided article on its noun
        clitic, low = "la ", low[2:]
    segs = [s for s in low.split("'") if s]
    joined = "".join(segs)
    if joined in CORREL:
        return CORREL[joined]
    if joined in CLOSED:
        return CLOSED[joined]
    feats: list[str] = []
    if segs and segs[-1] == "n":
        feats.insert(0, "Case=Acc"); segs = segs[:-1]
    else:
        feats.insert(0, "Case=Nom")
    if segs and segs[-1] == "j":
        feats.append("Number=Plur"); segs = segs[:-1]
    else:
        feats.append("Number=Sing")
    base = "".join(segs)
    if len(segs) == 1:                             # an undivided word: read the ending
        m = re.match(r"^(.+?)(as|is|os|us|u|i|o|a|e)$", base)
        if m and base not in PRON:
            segs = [m.group(1), m.group(2)]
    # pronouns and their possessives
    core = segs[0] if segs else base
    if core in PRON and len(segs) == 1:
        p, n = PRON[core]
        f = [f"Person={p}", "PronType=Prs"] + ([f"Number={n}"] if n else []) + ([feats[0]] if feats[0] == "Case=Acc" else ["Case=Nom"])
        if core == "si": f.append("Reflex=Yes")
        return core, "PRON|" + "|".join(f)
    if core in PRON and len(segs) == 2 and segs[1] == "a":
        p, _ = PRON[core]
        return core + "a", "DET|" + "|".join(["Poss=Yes", "PronType=Prs", f"Person={p}"] + feats)
    if elided:                                     # kor’ = koro
        return clitic.strip() + (" " if clitic else "") + base + "o", ("DET|Definite=Def|PronType=Art + " if clitic else "") + "NOUN|" + "|".join(feats)
    end = segs[-1] if segs else ""
    root = "".join(segs[:-1])
    part = segs[-2] if len(segs) >= 2 and segs[-2] in PART else None
    if end in VERB_END:
        return root + "i", "VERB|" + VERB_END[end]
    if end == "o":
        if part:
            return root + "o", "NOUN|VerbForm=Part|" + PART[part] + "|" + "|".join(feats)   # ŝuldanto, the participle as a noun
        return clitic + root + "o", ("DET|Definite=Def|PronType=Art + " if clitic else "") + "NOUN|" + "|".join(feats)
    if end == "a":
        if part:
            return root[: -len(part)] + "i", "VERB|VerbForm=Part|" + PART[part] + "|" + "|".join(feats)
        return root + "a", "ADJ|" + "|".join(feats)
    if end == "e":
        if part:
            return root[: -len(part)] + "i", "VERB|VerbForm=Conv|" + PART[part]
        return root + "e", "ADV"
    return base, "X"


SCHEME_LABELS = {"zamenhof": "As Zamenhof described it: Unua Libro (1887), Fundamento (1905)"}

KEY = {
    "zamenhof": [
        ("", "The sounds as Zamenhof set them out in the Unua Libro (1887) and fixed in the Fundamento (1905): one letter, one sound; the accent always on the last syllable but one. This is the author's own rule, not a reconstruction."),
        ("CAPS", "the stressed syllable: always the last but one (rule 10). A word with its final o cut off (kor’, l’) keeps the stress where it was, now on its last syllable"),
        ("a, e, ee, o, oo", "the five vowels, a e i o u, each one sound, never reduced; Zamenhof gave them only by comparison with other languages, so their exact quality is open"),
        ("ai, ay, oy, ooy, ow, ew", "aj, ej, oj, uj, aŭ, eŭ: a vowel with the glide j or ŭ, one syllable (kaj, ankaŭ)"),
        ("ts", "c, as in bits"),
        ("ch", "ĉ, as in church"),
        ("j", "ĝ, as in judge"),
        ("kh", "ĥ, the ch of German Bach or Scots loch"),
        ("zh", "ĵ, the j of French jour, the s of pleasure"),
        ("sh", "ŝ, as in she"),
        ("y", "j, as in yes"),
        ("w", "ŭ, as in wind; written only after a or e"),
        ("r", "trilled, in every position"),
        ("g, s", "always hard g as in give; always s as in so (z is the voiced one)"),
        ("Fundamento spelling", "the row under the text joins the parts the 1887 print divides (Patr'o ni'a: Patro nia); it is the spelling every later text uses"),
    ],
}
