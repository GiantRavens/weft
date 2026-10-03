"""Portuguese sound layer (weft.portuguese): Lisbon of about 1540, then modern European and Brazilian.

Scope. The first work is the opening of Camões, Os Lusíadas (1572), in the modern spelling of the
Wikisource text. Each word's sound comes from a hand-written lexicon, `pipeline/weft/data/pt_lexicon.yaml`,
keyed by the modern spelling: the value `o` is the word in a normalized spelling of the 1540s, one letter
per sound in the manner of Fernão de Oliveira (Grammatica da lingoagem portuguesa, 1536) and João de
Barros (Grammatica da lingua portuguesa, 1540), with the stressed e and o marked for quality (é ó open,
ê ô closed) and the stress marked where the rule would not place it. All three schemes read that
spelling: the 1540 scheme with the values Oliveira and Barros describe, the modern ones with today's
mergers and reductions. A word missing from the lexicon is reported as `lexicon-missing`; a stressed e or
o without a quality mark is read closed and reported as `mid-vowel-unknown`.

Schemes
-------
lisboa1540  Portuguese as an educated Lisbon reader of the 1540s would have read verse aloud, approximate.
            Evidence: Oliveira (1536) and Barros (1540), the first descriptions of the sounds by native
            grammarians, and the synthesis in Paul Teyssier, História da língua portuguesa (1980), and
            Ivo Castro, Introdução à história do português (2006). What the scheme assumes:
            - Four sibilants, two voiceless and two voiced, which the spelling still kept apart: ç (and c
              before e, i) and z are dental, [s̪] and [z̪]; s at the start of a word or after a consonant,
              and ss, are apical, [s̺]; a single s between vowels is the voiced apical [z̺]. Oliveira
              distinguishes them; Lisbon merged each pair in the 17th and 18th centuries. x = [ʃ].
            - ch is still the affricate [tʃ] (it became [ʃ] in Lisbon in the 17th century); j and g before
              e, i are [ʒ]; lh = [ʎ], nh = [ɲ].
            - Unstressed vowels are not yet reduced: pretonic e and o are [e] and [o], final a is [a],
              final e is [e]; final unstressed o is read [u], a change Teyssier dates to the 16th century
              (this is the least certain point, and the KEY says so).
            - The diphthongs ei and ou are still diphthongs, [ej] and [ow].
            - r at the start of a word and rr are the alveolar trill [r]; single r between vowels the tap
              [ɾ]; l at the end of a syllable is dark [ɫ].
            - Nasal vowels as today; final -em is [ẽ] rather than today's [ẽj̃]; -am and -ão both [ɐ̃w̃].
            - b and v are distinct, v = [v] (the Lisbon norm; northern speakers merged them).
            Camões's own speech is not modelled, nor the metre's elisions: each word is phonemized alone.
europeu     Standard European Portuguese (Lisbon) today: unstressed a [ɐ], e [ɨ], o [u]; ei [ɐj], ou [o];
            initial r and rr the uvular [ʁ]; s at the end of a syllable [ʃ]; ch [ʃ]; final -em [ẽj̃].
brasileiro  Standard Brazilian Portuguese (the São Paulo norm): final unstressed e [i], o [u]; t and d before
            [i] become [tʃ] and [dʒ]; syllable-final l is [w]; initial r and rr [h]; s at the end of a
            syllable [s]; pretonic e and o are [e] and [o]. Broad; regional variation is not shown.

Stress falls by the written rule of modern Portuguese (words ending in a, e, o, am, em, ens, with or
without s, on the last syllable but one; others on the last; accents override), which the normalized
spelling also carries. CAPS mark the stressed syllable; clitics (articles, prepositions, que, se, me) carry none.

Edition token fields (texts/<work>/edition.yaml)
-----------------------------------------------
t      the word as printed, punctuation attached; split off into punct
n      the modern spelling when the print differs from it (the lexicon key); not needed for a modern text
o      the normalized 1540 spelling for this occurrence, overriding the lexicon
ipa    {scheme: ipa} override for this occurrence
"""
from __future__ import annotations

import re
import unicodedata as ud
from pathlib import Path

import yaml

VERSION = "0.1"
SHOW_TRANSLIT = False

LEAD_P = re.compile(r"^([(\[«“‘\"']+)")
TRAIL_P = re.compile(r"([,.;:!?)\]»”’\"']+)$")
CLITICS = {"a", "as", "o", "os", "e", "de", "da", "das", "do", "dos", "em", "na", "nas", "no", "nos", "por", "pelo", "pela", "pelos", "pelas",
           "que", "se", "me", "te", "lhe", "lhes", "nos", "vos", "um", "uma", "uns", "umas", "ao", "aos", "à", "às", "com", "sem", "ou", "nem", "mas"}
_LEX: dict | None = None


def lexicon() -> dict:
    global _LEX
    if _LEX is None:
        p = Path(__file__).parent / "data" / "pt_lexicon.yaml"
        _LEX = {ud.normalize("NFC", k): v for k, v in (yaml.safe_load(p.read_text(encoding="utf-8")) or {}).items()} if p.exists() else {}
    return _LEX


def key(word: str) -> str:
    return ud.normalize("NFC", word).lower()


# ---------------------------------------------------------------- normalized spelling -> segments
VOW = "aeiouáéíóúâêôãõà"
QUAL = {"á": ("a", True), "é": ("ɛ", True), "ê": ("e", True), "í": ("i", True), "ó": ("ɔ", True), "ô": ("o", True), "ú": ("u", True), "à": ("a", True),
        "â": ("a", True)}
NASAL = {"a": "ɐ̃", "e": "ẽ", "i": "ĩ", "o": "õ", "u": "ũ"}


def _segments(o: str, scheme: str) -> tuple[list[list], list[tuple[str, str]]]:
    """Normalized spelling -> [[phone, kind, accented, marked_quality]], plus sensor flags.
    kind: V vowel, N nasal vowel, C consonant. Sibilants and ch depend on the scheme."""
    w = ud.normalize("NFC", o.lower())
    old = scheme == "lisboa1540"
    br = scheme == "brasileiro"
    out: list[list] = []
    flags: list[tuple[str, str]] = []
    i, n = 0, len(w)
    at = lambda k: w[k] if 0 <= k < n else ""
    isv = lambda ch: bool(ch) and ch in VOW

    while i < n:
        c, nx, nx2 = w[i], at(i + 1), at(i + 2)
        # nasal vowels: a vowel (plain or accented) before m/n that closes the syllable; ã õ themselves
        if c in "ãõ":
            if nx in ("e", "o", "i") and (c, nx) in (("ã", "e"), ("ã", "o"), ("ã", "i"), ("õ", "e")):
                out.append([{"ã": "ɐ̃", "õ": "õ"}[c] + ("w̃" if nx == "o" else "j̃"), "N", c == "ã" and nx == "o" or True, True]); i += 2; continue
            out.append([{"ã": "ɐ̃", "õ": "õ"}[c], "N", True, True]); i += 1; continue
        if c in QUAL or c in "aeiou":
            base, acc = QUAL.get(c, (c, False))
            marked = c in QUAL
            # vowel + m/n closing the syllable -> nasal vowel; the consonant is absorbed
            if nx and nx in "mn" and (not isv(nx2)) and not (nx == "n" and nx2 == "h"):
                plain = {"ɛ": "e", "ɔ": "o"}.get(base, base)
                nas = NASAL[plain]
                final = i + 2 >= n or (nx2 == "s" and i + 3 >= n)
                if plain == "e" and final and nx == "m":          # -em, -ens
                    nas = "ẽ" if old else "ẽj̃"
                if plain == "a" and final and nx == "m":          # verbal -am
                    nas = "ɐ̃w̃"
                out.append([nas, "N", acc, True]); i += 2; continue
            out.append([base, "V", acc, marked]); i += 1; continue
        if c == "c":
            if nx == "h":
                out.append(["tʃ" if old else "ʃ", "C", False, False]); i += 2; continue
            if nx in "eéêií":
                out.append(["s̪" if old else "s", "C", False, False]); i += 1; continue
            out.append(["k", "C", False, False]); i += 1; continue
        if c == "ç":
            out.append(["s̪" if old else "s", "C", False, False]); i += 1; continue
        if c == "z":
            out.append(["z̪" if old else "z", "C", False, False]); i += 1; continue
        if c == "s":
            if nx == "s":
                out.append(["s̺" if old else "s", "C", False, False]); i += 2; continue
            if isv(at(i - 1)) and isv(nx):
                out.append(["z̺" if old else "z", "C", False, False]); i += 1; continue
            out.append(["s̺" if old else "s", "C", False, False]); i += 1; continue
        if c == "x":
            out.append(["ʃ", "C", False, False]); i += 1; continue
        if c == "q":
            if nx == "u":
                if nx2 in "eéêií":
                    out.append(["k", "C", False, False]); i += 2; continue
                out.append(["k", "C", False, False]); out.append(["w", "G", False, False]); i += 2; continue
            out.append(["k", "C", False, False]); i += 1; continue
        if c == "g":
            if nx == "u" and nx2 in "eéêií":
                out.append(["g", "C", False, False]); i += 2; continue
            if nx in "eéêií":
                out.append(["ʒ", "C", False, False]); i += 1; continue
            out.append(["g", "C", False, False]); i += 1; continue
        if c == "j":
            out.append(["ʒ", "C", False, False]); i += 1; continue
        if c == "l":
            if nx == "h":
                out.append(["ʎ", "C", False, False]); i += 2; continue
            out.append(["l", "C", False, False]); i += 1; continue
        if c == "n":
            if nx == "h":
                out.append(["ɲ", "C", False, False]); i += 2; continue
            out.append(["n", "C", False, False]); i += 1; continue
        if c == "r":
            if nx == "r":
                out.append(["R", "C", False, False]); i += 2; continue       # R: the strong r, valued per scheme below
            strong = i == 0 or at(i - 1) in ("l", "n", "s")
            out.append(["R" if strong else "ɾ", "C", False, False]); i += 1; continue
        if c == "h":
            i += 1; continue
        if c in "bdfkmptv":
            out.append([c, "C", False, False]); i += 1; continue
        if c in "-’'":
            i += 1; continue
        out.append([c, "C", False, False]); i += 1
    return out, flags


ONSETS = {"pɾ", "bɾ", "tɾ", "dɾ", "kɾ", "gɾ", "fɾ", "vɾ", "pl", "bl", "kl", "gl", "fl", "tl"}
WEAK = {"i", "u"}


def _syllabify(segs: list[list]) -> tuple[list[list[int]], int | None]:
    """Glides, nuclei, consonant division; returns index lists per syllable and the accented syllable."""
    k = len(segs)
    for j, s in enumerate(segs):
        if s[1] != "V" or s[2] or s[0] not in WEAK:
            continue
        prev = segs[j - 1] if j > 0 else None
        nxt = segs[j + 1] if j + 1 < k else None
        if nxt and nxt[1] in ("V", "N") and not (prev and prev[1] == "V"):
            # i/u before a vowel: a glide only in a few words (ia -> ja in 'glória'); Portuguese usually
            # keeps hiatus (pra-i-a, Lu-si-ta-na), so the first of two vowels stays a vowel unless the
            # second is accented and the pair is written as a rising diphthong (qua, gua handled above)
            continue
        if prev and prev[1] in ("V", "N") and prev[0] not in WEAK:
            segs[j] = [{"i": "j", "u": "w"}[s[0]], "G", False, False]      # falling diphthong: ai, ei, ou, eu, oi, au
    nuclei = [j for j, s in enumerate(segs) if s[1] in ("V", "N")]
    if not nuclei:
        return [list(range(k))], None
    bounds = []
    for a, b in zip(nuclei, nuclei[1:]):
        between = list(range(a + 1, b))
        cons = [j for j in between if segs[j][1] == "C"]
        if not cons:
            gl = [j for j in between if segs[j][1] == "G"]
            bounds.append(gl[-1] + 1 if gl else b)
            continue
        if len(cons) == 1:
            start = cons[0]
        else:
            last2 = segs[cons[-2]][0] + segs[cons[-1]][0]
            start = cons[-2] if (last2 in ONSETS and cons[-1] == cons[-2] + 1) else cons[-1]
        bounds.append(start)
    sylls, idx = [], 0
    for bnd in bounds + [k]:
        sylls.append(list(range(idx, bnd))); idx = bnd
    acc = next((si for si, sy in enumerate(sylls) if any(segs[j][2] for j in sy)), None)
    return sylls, acc


def _stress(o: str, sylls: list, acc: int | None) -> int | None:
    if acc is not None:
        return acc
    w = key(o).strip("-’'")
    if w in CLITICS:
        return None
    if len(sylls) == 1:
        return 0
    # paroxytone if the word ends in a, e, o (with or without s), am, em, ens; otherwise oxytone
    if re.search(r"(?:[aeo]s?|am|em|ens)$", w):
        return len(sylls) - 2
    return len(sylls) - 1


def _value(seg: list, scheme: str, stressed: bool, final_syll: bool, nxt: str, prev: str) -> str:
    """One segment's IPA in the scheme, after stress is known (vowel reduction, r, l, s, t/d)."""
    p, kind = seg[0], seg[1]
    old, eu, br = scheme == "lisboa1540", scheme == "europeu", scheme == "brasileiro"
    if kind == "V":
        if stressed:
            return p
        # unstressed vowels
        if old:
            if p in ("o", "ɔ") and final_syll:
                return "u"
            return {"ɛ": "e", "ɔ": "o"}.get(p, p)
        if eu:
            return {"a": "ɐ", "e": "ɨ", "ɛ": "ɨ", "o": "u", "ɔ": "u"}.get(p, p)
        if final_syll:
            return {"e": "i", "ɛ": "i", "o": "u", "ɔ": "u"}.get(p, p)
        return {"ɛ": "e", "ɔ": "o"}.get(p, p)
    if kind == "N":
        return p
    if p == "R":
        return "r" if old else ("ʁ" if eu else "h")
    if p == "l":
        coda = not nxt or nxt == "C"
        if coda:
            return "ɫ" if (old or eu) else "w"
        return "l"
    if p in ("s", "z") and not old:
        coda = not nxt or nxt == "C"
        if coda:
            return "ʃ" if eu else "s"
        return p
    return p


def word_ipa(o: str, scheme: str) -> tuple[str, int, list[tuple[str, str]]]:
    segs, flags = _segments(o, scheme)
    sylls, acc = _syllabify(segs)
    st = _stress(o, sylls, acc)
    # a stressed e or o whose quality the lexicon did not mark: read closed, and say so
    if st is not None:
        for j in sylls[st]:
            if segs[j][1] == "V" and segs[j][0] in ("e", "o") and not segs[j][3]:
                flags.append(("mid-vowel-unknown", o))
    parts = []
    for si, sy in enumerate(sylls):
        chunk = ""
        for pos, j in enumerate(sy):
            nxt_kind = segs[sy[pos + 1]][1] if pos + 1 < len(sy) else ("C" if si + 1 < len(sylls) and segs[sylls[si + 1][0]][1] == "C" else "")
            v = _value(segs[j], scheme, si == st, si == len(sylls) - 1, nxt_kind if segs[j][1] == "C" and pos + 1 == len(sy) else ("V" if pos + 1 < len(sy) else ""), "")
            chunk += v
        if scheme == "brasileiro":
            chunk = chunk.replace("ti", "tʃi").replace("di", "dʒi").replace("tĩ", "tʃĩ").replace("dĩ", "dʒĩ")
        parts.append(("ˈ" if si == st else ("." if parts else "")) + chunk)
    ipa = "".join(parts)
    if scheme == "europeu":
        ipa = ipa.replace("ej", "ɐj").replace("ow", "o")
    if scheme == "brasileiro":
        ipa = ipa.replace("ow", "o")
    return ipa, len(sylls), flags


# ---------------------------------------------------------------- IPA -> respelling
RESPELL = [("tʃ", "ch"), ("dʒ", "j"), ("aj", "ai"), ("ej", "ay"), ("ɐj", "uhy"), ("ɛj", "ey"), ("oj", "oy"), ("ɔj", "oy"), ("uj", "ooy"), ("aw", "ow"), ("ew", "ayoo"), ("ɛw", "eoo"), ("iw", "eew"), ("ow", "ohw"), ("ɐ̃w̃", "owⁿ"), ("ɐ̃j̃", "uhyⁿ"), ("ẽj̃", "ayⁿ"), ("õj̃", "oyⁿ"), ("ɐ̃", "uhⁿ"), ("ẽ", "ehⁿ"), ("ĩ", "eeⁿ"), ("õ", "ohⁿ"), ("ũ", "ooⁿ"),
           ("s̪", "s"), ("z̪", "z"), ("s̺", "s"), ("z̺", "z"), ("ʃ", "sh"), ("ʒ", "zh"), ("ʎ", "ly"), ("ɲ", "ny"), ("ʁ", "r"), ("ɾ", "r"), ("r", "rr"), ("ɫ", "l"),
           ("j", "y"), ("w", "w"), ("ɐ", "uh"), ("ɨ", "ih"), ("ɛ", "e"), ("ɔ", "o"), ("a", "a"), ("e", "ay"), ("i", "ee"), ("o", "oh"), ("u", "oo")]


def _respell_syll(s: str) -> str:
    out, i = "", 0
    while i < len(s):
        for a, b in RESPELL:
            if s.startswith(a, i):
                out += b; i += len(a); break
        else:
            out += s[i]; i += 1
    return out


def respell(ipa: str) -> str:
    words = []
    for w in ipa.split(" "):
        parts = []
        for sy in re.split(r"(?=ˈ)|\.", w):
            if not sy:
                continue
            parts.append(_respell_syll(sy[1:]).upper() if sy.startswith("ˈ") else _respell_syll(sy))
        words.append("-".join(parts))
    return " ".join(words)


# ---------------------------------------------------------------- hooks
_CTX: dict = {}


def phon_ipa(n: str, scheme: str, override: str | None = None) -> tuple[str, int, list]:
    """The sound of a modern-spelled word (one or more words) through the lexicon's normalized spelling."""
    ipas, syl, flags = [], 0, []
    for w in n.split():
        o = override or (lexicon().get(key(w)) or {}).get("o")
        if not o:
            return "?", 0, [("lexicon-missing", w)]
        ipa, k, fl = word_ipa(o, scheme)
        ipas.append(ipa); syl += k; flags += fl
    return " ".join(ipas), syl, flags


def token_fields(surface: str, et: dict, group: dict) -> tuple[dict, list[tuple[str, str]]]:
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
    n = et.get("n") or word
    # n may be two words for a contraction (doutras: de outras); each must be in the lexicon
    os_ = [et.get("o")] if et.get("o") else [(lexicon().get(key(w)) or {}).get("o") for w in n.split()]
    if not all(os_) and not et.get("ipa"):
        fails.append(("lexicon-missing", n))
    elif all(os_):
        for o in os_:
            _, _, fl = word_ipa(o, "lisboa1540")
            fails += fl
        fields["prov"] = {"sound": f"weft.portuguese {VERSION}, from the lexicon's normalized 1540 spelling {' '.join(os_)}"}
    _CTX = {"n": n, "o": et.get("o"), "ipa": et.get("ipa") or {}}
    return fields, fails


def bare(word: str) -> str:
    """The printed word without its leading or trailing punctuation."""
    return TRAIL_P.sub("", LEAD_P.sub("", word or ""))


def phonemize(word: str, scheme: str = "lisboa1540", quantities=None, **_) -> dict:
    """`word` is the token's modern spelling (n) or, for a modern text, the printed word."""
    word = bare(word)
    ctx = _CTX if _CTX.get("n") == word else {}
    ov = (ctx.get("ipa") or {}).get(scheme)
    if ov:
        return {"ipa": ov, "respell": respell(ov), "syllables": len([p for p in re.split(r"[.ˈ ]", ov) if p])}
    ipa, syl, _ = phon_ipa(word, scheme, ctx.get("o"))
    return {"ipa": ipa, "respell": respell(ipa) if ipa != "?" else "?", "syllables": syl}


KEY = {
    "lisboa1540": [
        ("", "Portuguese as an educated Lisbon reader of the 1540s would have read verse aloud, after the grammars of Fernão de Oliveira (1536) and João de Barros (1540); approximate. Each word is said alone."),
        ("CAPS", "the stressed syllable; hyphens divide syllables. Articles, prepositions, que and the object pronouns carry none"),
        ("a, e, ay, ee, o, oh, oo", "the vowels: a as in father; e open as in bet and ay closed as in French été; o open as in for and oh closed as in French eau; ee and oo as in see and too. Unstressed vowels keep their full values, which modern Lisbon has reduced"),
        ("final o = oo", "a final unstressed o is read u, the one reduction the 16th century already shows (Teyssier); the least certain point of the scheme"),
        ("uhⁿ ehⁿ eeⁿ ohⁿ ooⁿ", "nasal vowels: the vowel said through the nose with no consonant after it"),
        ("owⁿ, uhyⁿ, oyⁿ", "the nasal diphthongs ão (and verbal -am), ãe, õe"),
        ("ehⁿ at the end", "final -em is a plain nasal e, not yet today's nasal diphthong"),
        ("ay, ow", "the diphthongs ei and ou, both still diphthongs"),
        ("s, z", "four sibilants, two of each letter: ç and z are made with the tongue tip down (dental); s and ss with the tip up (apical, as in northern Portugal today). The respelling cannot show the difference; the IPA marks it"),
        ("ch", "as in church: the affricate the 16th century still had"),
        ("zh", "j, and g before e and i: the s of measure"),
        ("sh", "x"),
        ("ly, ny", "lh and nh, as in million and canyon"),
        ("rr", "a trilled r (at the start of a word and for rr); single r between vowels is a tap"),
        ("l at the end of a syllable", "dark, as in English full"),
        ("v", "v as in English; distinct from b in Lisbon"),
    ],
    "europeu": [
        ("", "Standard European Portuguese (Lisbon) today, each word said alone."),
        ("CAPS", "the stressed syllable; hyphens divide syllables"),
        ("uh, ih, oo", "unstressed a, e and o: a reduced to uh, e to a short ih (often barely heard), o to oo"),
        ("a, e, ay, ee, o, oh, oo", "the stressed vowels, as in the first scheme"),
        ("uhⁿ ehⁿ eeⁿ ohⁿ ooⁿ; owⁿ, uhyⁿ, oyⁿ, ayⁿ", "nasal vowels and diphthongs; final -em is ayⁿ"),
        ("uhy, oh", "the old diphthongs ei and ou: ei has moved to uhy in Lisbon, ou has become a plain oh"),
        ("sh", "s at the end of a syllable (mares, está), ch and x"),
        ("r", "initial r and rr: a uvular r at the back of the throat; single r between vowels a tap"),
        ("ly, ny, zh", "lh, nh; j and g before e, i"),
    ],
    "brasileiro": [
        ("", "Standard Brazilian Portuguese (the São Paulo norm), each word said alone; regional variation is not shown."),
        ("CAPS", "the stressed syllable; hyphens divide syllables"),
        ("ee, oo at the end", "final unstressed e and o are ee and oo; pretonic e and o keep ay and oh"),
        ("ch, j", "t and d before ee: the ch of church and the j of judge (gente, cidade)"),
        ("w", "l at the end of a syllable (Brasil, alto)"),
        ("h", "initial r and rr: an h-like sound"),
        ("s", "s at the end of a syllable keeps its s"),
        ("uhⁿ ehⁿ eeⁿ ohⁿ ooⁿ; owⁿ, uhyⁿ, oyⁿ, ayⁿ", "nasal vowels and diphthongs"),
        ("ly, ny, sh, zh", "lh, nh, x and ch, j"),
    ],
}
SCHEME_LABELS = {"lisboa1540": "Lisbon about 1540: Oliveira's and Barros's day (approximate)",
                 "europeu": "Modern European Portuguese (Lisbon)",
                 "brasileiro": "Modern Brazilian Portuguese (São Paulo norm)"}
