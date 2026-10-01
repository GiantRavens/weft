"""Sumerian: an Oracc-lemmatized transliteration -> cuneiform, lemma, morphology and sound.

Sumerian is a language isolate, written in cuneiform from about 3200 BC and spoken until
roughly the early second millennium; it was copied and studied as a written language for
centuries after that. Its sound is known only indirectly: from the values Akkadian scribes gave
the signs, from Sumerian words borrowed into Akkadian and back, and from the Old Babylonian
lexical lists that spell Sumerian words syllabically. Of the sound rows in this library it is
among the most reconstructed.

Token fields (edition.yaml)
---------------------------
  t    the transliteration as Oracc prints it, verbatim, with ⸢ ⸣ around damaged signs
  ref  the Oracc word reference (P346196.3.1); lemma and morphology are read from the
       Oracc JSON through it, and a sensor checks that t matches the Oracc form there
  sg   optional: a sign reading that differs from t, for the cuneiform row
  n    optional: a hand reading for the sound when the spelling misleads (a-a for aya)

Lemma and morphology come from the Oracc lemmatization (epsd2/literary), which plays the part
of the treebank: the lemma is Oracc's citation form and guide word, cf[gw]POS; the morphology is
Oracc's POS and morpheme string mapped to Universal Dependencies features (`ud_morph`). Two
departures from UD codes keep the page readable: cases UD writes as Erg, Com, Equ, Ter, Abs are
spelled out (Case=Comitative), because the page's decoder reads Com as common gender. Oracc
writes one morpheme e for both the ergative (the agent) and the directive ('at, on'); Weft keeps
that ambiguity as Case=Ergative-or-Directive rather than choosing. Oracc's own string is kept
beside it as `oracc_morph`. A word Oracc did not lemmatize is reported as
`oracc-unlemmatized`; a broken sign (x) as `sign-illegible`.

The cuneiform row is generated from the sign reading through the Oracc Sign List value table
(data/akk_osl_values.tsv, CC0), reused from weft.akkadian. A reading the table does not know is
reported as `sign-unmapped`, never guessed.

Schemes
-------
recon-2300  Reconstructed Sumerian of the late third millennium BC. Conjectural throughout.
            Follows the consonant system set out in Jagersma, A Descriptive Grammar of Sumerian
            (2010), in broad agreement with Edzard, Sumerian Grammar (2003): the series written
            b, d, g as voiceless unaspirated stops [p t k], the series written p, t, k as
            aspirated [pʰ tʰ kʰ], z as the affricate [ts], ŋ (also written g̃) as the velar nasal
            [ŋ], h as [x]. A consonant written twice across a sign boundary (an-na) is read
            once, and a vowel repeated across a boundary (bi₂-in) is read once: both are
            spelling conventions of cuneiform. Vowel length is not known and not shown. The
            phoneme conventionally written dr or ř is not applied to any word here.
classroom   The conventional reading of the transliteration in Assyriology teaching: each sign
            said as transliterated, b d g p t k z as in English, š as sh, h as kh, ŋ as ng.
            A modern convention, not a claim about ancient speech.

Stress is not known for Sumerian, so neither scheme marks it (no CAPS).
"""
from __future__ import annotations

import json
import re
import unicodedata as ud
from pathlib import Path

from . import akkadian

VERSION = "0.1"
SCRIPT_LABEL = "Script (cuneiform)"
SCRIPT_WORD = "cuneiform"
SHOW_TRANSLIT = False          # the surface already is the transliteration
REPO = Path(__file__).resolve().parents[2]

LAYERS = {
    "lemma": {"src": "Oracc epsd2/literary lemmatization (CC0): citation form [guide word] and POS"},
    "morph": {"src": f"weft.sumerian {VERSION}: Oracc POS and morpheme string mapped to UD features"},
    "script": {"src": f"weft.sumerian {VERSION}: cuneiform generated from the sign reading via the Oracc "
                      f"Sign List (CC0), commit {akkadian.OSL_COMMIT[:7]}"},
    "signs": {"src": "the Oracc transliteration, damage marks removed"},
}

# ---------------------------------------------------------------- Oracc JSON
_CDL: dict[str, dict[str, dict]] = {}


def _resolve(rel: str) -> Path:
    """A section's `oracc_json` is relative to its work folder; find it under texts/ or private/."""
    for root in ("texts", "private"):
        hits = sorted((REPO / root).glob(f"*/{rel}"))
        if hits:
            return hits[0]
    raise SystemExit(f"weft.sumerian: {rel} not found; run `weft acquire` for this work")


def oracc_words(rel: str) -> dict[str, dict]:
    """{word ref: Oracc lemma node} for one Oracc corpus JSON file."""
    if rel not in _CDL:
        words: dict[str, dict] = {}

        def walk(n):
            if isinstance(n, list):
                for x in n:
                    walk(x)
            elif isinstance(n, dict):
                if n.get("node") == "l":
                    words[n["ref"]] = n
                walk(n.get("cdl", []))
        walk(json.loads(_resolve(rel).read_text(encoding="utf-8"))["cdl"])
        _CDL[rel] = words
    return _CDL[rel]


# ---------------------------------------------------------------- morphology
UPOS = {"N": "NOUN", "V/t": "VERB", "V/i": "VERB", "V": "VERB", "AJ": "ADJ", "AV": "ADV",
        "DN": "PROPN", "TN": "PROPN", "SN": "PROPN", "PN": "PROPN", "GN": "PROPN", "RN": "PROPN",
        "WN": "PROPN", "NU": "NUM", "PRP": "ADP", "CNJ": "CCONJ", "IP": "PRON", "DP": "DET",
        "MOD": "PART", "NEG": "PART", "XP": "PRON"}
# Oracc nominal case morphemes -> UD Case values (spelled out where the page's decoder lacks them)
CASE = {"ak": "Gen", "ra": "Dat", "a": "Loc", "da": "Comitative", "ta": "Abl", "še": "Terminative",
        "gin": "Equative", "e": "Ergative-or-Directive", "eše": "Terminative", "ene": None}
SPELL = {"Gen": "Genitive", "Dat": "Dative", "Loc": "Locative", "Abl": "Ablative"}
POSS = {"ŋu": ("1", "Sing"), "zu": ("2", "Sing"), "ani": ("3", "Sing"), "bi": ("3", "Sing"),
        "me": ("1", "Plur"), "zunene": ("2", "Plur"), "anene": ("3", "Plur")}


def ud_morph(pos: str | None, morph: str | None) -> str:
    """Oracc POS and morpheme string -> 'UPOS|Feat=Val'. Nominal strings look like '~,zu.ak'
    (base, possessive, case); verbal ones like 'mu.na:~;e' (prefix chain : base ; suffixes)."""
    upos = UPOS.get(pos or "", "X")
    if not morph or morph == "~":
        return upos
    feats: list[str] = []
    if upos in ("NOUN", "PROPN", "ADJ"):
        rest = morph.replace("~", "", 1)
        cases: list[str] = []
        for slot in re.findall(r"[,.][^,.]+", rest):
            m = slot[1:]
            if slot[0] == "," and m in POSS:
                p, nb = POSS[m]
                feats += ["Poss=Yes", f"Person[psor]={p}", f"Number[psor]={nb}"]
            elif m == "ene":
                feats.append("Number=Plur")
            elif m == "am":
                feats.append("Cop=Yes")           # enclitic copula 'it is'
            elif m in CASE and CASE[m]:
                cases.append(CASE[m])
        if cases:
            # two case markers in a row (an anticipatory genitive then a locative) are one feature
            feats.append("Case=" + (cases[0] if len(cases) == 1 else "+".join(SPELL.get(c, c) for c in cases)))
    elif upos == "VERB":
        chain, base = morph.split(":", 1) if ":" in morph else ("", morph)
        prefixes = [x for x in chain.split(".") if x]
        suffix = base.split(";", 1)[1] if ";" in base else ""
        poss = re.search(r",(\w+)$", suffix)
        suffix = re.sub(r",\w+$", "", suffix).lstrip("*")
        finite = any(x != "nu" for x in prefixes)
        if finite:
            feats.append("VerbForm=Fin")
            if prefixes[-1] == "n":
                feats.append("Person=3")         # -n-: 3rd person agent
        elif suffix:
            feats.append("VerbForm=Part")        # -a, -e: a non-finite form ('standing', 'unceasing')
        if "nu" in prefixes:
            feats.append("Polarity=Neg")
        if suffix.startswith("e"):
            feats.append("Aspect=Imp")           # marû (unfinished) stem or ending
        if poss and poss.group(1) in POSS:
            p, nb = POSS[poss.group(1)]
            feats += ["Poss=Yes", f"Person[psor]={p}", f"Number[psor]={nb}"]
    return "|".join([upos] + feats)


# ---------------------------------------------------------------- the sign reading
DAMAGE = re.compile(r"[⸢⸣\[\]#?!*]")


def clean(reading: str) -> str:
    """Oracc form -> plain sign reading: damage brackets and flags removed."""
    return DAMAGE.sub("", ud.normalize("NFC", reading))


SUBS = str.maketrans("", "", "₀₁₂₃₄₅₆₇₈₉ₓ")


def sound_form(reading: str) -> str:
    """Sign reading -> hyphenated syllables to be said: determinatives (unspoken) and index
    digits dropped, lower case, ḫ as h. '{d}en-lil₂-le' -> 'en-lil-le'."""
    r = re.sub(r"\{[^}]*\}", "", clean(reading))
    r = r.translate(SUBS).lower().replace("ḫ", "h").replace("g̃", "ŋ")
    return "-".join(p for p in re.split(r"[-.]", r) if p)


def token_fields(surface: str, et: dict, group: dict) -> tuple[dict, list[tuple[str, str]]]:
    fields: dict = {}
    fails: list[tuple[str, str]] = []
    sg = et.get("sg") or clean(surface)
    fields["signs"] = sg
    if sg == "x" or set(sg.split("-")) == {"x"}:
        fields["script"] = ""
        fails.append(("sign-illegible", surface))
    else:
        cun, missing = akkadian.to_cuneiform(sg)
        fields["script"] = cun
        for s in missing:
            fails.append(("sign-unmapped", f"{s} in {sg}"))
    fields["norm"] = et.get("n") or sound_form(sg)
    ref = et.get("ref")
    if not ref or not group.get("oracc_json"):
        fails.append(("oracc-ref-missing", surface))
        return fields, fails
    node = oracc_words(group["oracc_json"]).get(ref)
    if node is None:
        fails.append(("oracc-ref-missing", f"{ref} {surface}"))
        return fields, fails
    if node.get("frag") != surface:
        # sensor: the edition token must be the Oracc form at that reference, verbatim
        fails.append(("token-not-in-oracc", f"{ref}: edition {surface}, Oracc {node.get('frag')}"))
    f = node.get("f", {})
    fields["tb"] = ref
    if f.get("cf"):
        fields["lemma"] = f"{f['cf']}[{f.get('gw', '')}]{f.get('pos', '')}"
        fields["morph"] = ud_morph(f.get("pos"), f.get("morph"))
        fields["oracc_morph"] = f.get("morph")
        fields["oracc_sense"] = f.get("sense")
    else:
        fields["lemma"] = "not lemmatized"
        fields["morph"] = "X"
        fails.append(("oracc-unlemmatized", f"{ref} {surface}"))
    return fields, fails


# ---------------------------------------------------------------- sound
VOWELS = set("aeiu")
CONS = set("bdgŋhklmnprsštzy")

IPA_C = {
    "recon-2300": {"b": "p", "d": "t", "g": "k", "p": "pʰ", "t": "tʰ", "k": "kʰ", "z": "ts",
                   "s": "s", "š": "ʃ", "h": "x", "ŋ": "ŋ", "l": "l", "m": "m", "n": "n", "r": "r", "y": "j"},
    "classroom": {"b": "b", "d": "d", "g": "ɡ", "p": "p", "t": "t", "k": "k", "z": "z",
                  "s": "s", "š": "ʃ", "h": "x", "ŋ": "ŋ", "l": "l", "m": "m", "n": "n", "r": "r", "y": "j"},
}
RSP_C = {
    "recon-2300": {"z": "ts", "š": "sh", "h": "kh", "ŋ": "ng"},
    "classroom": {"š": "sh", "h": "kh", "ŋ": "ng"},
}


def _join_signs(signs: list[str]) -> list[str]:
    """Signs -> phoneme list as said: a consonant or vowel repeated across a sign boundary
    (an-na, bi-in) is one sound, since cuneiform writes a CVC sign plus a CV sign for VCV."""
    out: list[str] = []
    for s in signs:
        seg = [c for c in s if c in VOWELS | CONS]
        if out and seg and seg[0] == out[-1]:
            seg = seg[1:]
        out += seg
    return out


def _syllables(segs: list[str]) -> list[list[str]]:
    vi = [k for k, s in enumerate(segs) if s in VOWELS]
    if not vi:
        return [segs] if segs else []
    bounds = [0]
    for a, b in zip(vi, vi[1:]):
        bounds.append(b if b - a == 1 else b - 1)
    bounds.append(len(segs))
    return [segs[bounds[j]:bounds[j + 1]] for j in range(len(vi))]


def phonemize(word: str, scheme: str = "recon-2300", quantities=None, **_) -> dict:
    """A hyphenated sound form ('ur-saŋ-ŋa') in the given scheme. Stress is not marked."""
    signs = [s for s in sound_form(word).split("-") if s]
    if not signs or all(s == "x" for s in signs):
        return {"ipa": "", "respell": "?", "syllables": 0}
    signs = [s for s in signs if s != "x"]
    if scheme == "classroom":
        # each sign is said whole, as transliterated; a long sign (silig) splits only inside itself
        sylls = [sy for s in signs for sy in _syllables([c for c in s if c in VOWELS | CONS])]
    else:
        sylls = _syllables(_join_signs(signs))
    ipa = ".".join("".join(IPA_C[scheme].get(c, c) for c in sy) for sy in sylls)
    rsp = "-".join("".join(RSP_C[scheme].get(c, c) for c in sy) for sy in sylls)
    return {"ipa": ipa, "respell": rsp, "syllables": len(sylls)}


KEY = {
    "recon-2300": [
        ("", "Sumerian as it may have sounded in the late third millennium BC. Conjectural throughout: Sumerian has no known relatives, and its sounds are inferred from how Akkadian-speaking scribes used the signs, from loanwords between the two languages, and from Old Babylonian word lists that spell Sumerian words out. This is among the most reconstructed sound rows in the library. The consonant values follow Jagersma's grammar (2010)."),
        ("no CAPS", "stress is not known for Sumerian, so no syllable is marked"),
        ("b, d, g", "the letters b, d, g, taken here as p, t, k without a puff of breath, as in spin, stop, skin. English b, d, g at the start of a word are close"),
        ("p, t, k", "the letters p, t, k, taken here as p, t, k with a puff of breath, as in pin, top, kin"),
        ("ts", "the letter z, taken here as the ts of cats"),
        ("ng", "the letter ŋ (also written g̃), the ng of singer, never the ng of finger. It can begin a syllable: sa-nga"),
        ("kh", "the letter h (ḫ), a rasping sound as in Scottish loch"),
        ("sh", "the letter š"),
        ("a, e, i, u", "a as in father, e as in bet, i as in bit, u as in put. Whether vowels were long or short is not known"),
        ("single letters", "a consonant written twice across two signs (an-na) is read once here (a-na), because that spelling is a convention of the script"),
        ("?", "a broken sign: no sound is given"),
    ],
    "classroom": [
        ("", "The conventional reading of the transliteration taught in Assyriology today. Each sign is said as it is transliterated. A modern convention for reading aloud, not a claim about ancient speech."),
        ("no CAPS", "stress is not marked"),
        ("hyphens", "one syllable per sign, as transliterated; a doubled consonant across two signs (an-na) is said twice"),
        ("b d g p t k z", "as in English"),
        ("sh", "the letter š"),
        ("kh", "the letter h (ḫ), as in Scottish loch"),
        ("ng", "the letter ŋ (g̃), as in singer; older books write it g and some teachers say g"),
        ("?", "a broken sign: no sound is given"),
    ],
}
SCHEME_LABELS = {
    "recon-2300": "Reconstructed Sumerian, late third millennium BC (conjectural)",
    "classroom": "Assyriological classroom reading (modern convention)",
}


if __name__ == "__main__":
    import sys
    for w in sys.argv[1:]:
        for s in KEY:
            print(w, s, phonemize(w, s))
