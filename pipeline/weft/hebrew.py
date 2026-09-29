"""Biblical Hebrew (Masoretic pointing) -> syllables -> IPA and respelling.

The vowel points and cantillation accents of the Masoretic text record pronunciation directly:
the points give the vowels, dagesh gives gemination and hard b g d k p t, and the accent sits on
the stressed syllable. So no quantity table is needed; the rules below read the marks.

Schemes
-------
tiberian        The Tiberian reading tradition the pointing records (about AD 900), after
                Geoffrey Khan, *The Tiberian Pronunciation Tradition of Biblical Hebrew* (2020):
                qamets is [ɔ], vocal shewa is a short [a], ר is uvular, ו is [v], the gutturals
                ח ע are pharyngeal, ט צ ק are emphatic. The earliest pronunciation preserved in
                full; the text itself is centuries older.
modern-israeli  Modern Israeli Hebrew reading of the same text: gutturals weakened, no emphatics,
                qamets [a], soft ת = t.

Rules for the shewa (vocal or silent) and for begadkefat softening follow the standard
grammars; see the functions below. Both are heuristics where the pointing is ambiguous.
"""
from __future__ import annotations

import unicodedata as ud
from dataclasses import dataclass, field

VERSION = "0.1"

SHEVA, HSEGOL, HPATAH, HQAMATS = "ְ", "ֱ", "ֲ", "ֳ"
HIRIQ, TSERE, SEGOL, PATAH, QAMATS = "ִ", "ֵ", "ֶ", "ַ", "ָ"
HOLAM, HOLAM_HASER, QUBUTS, DAGESH, METEG = "ֹ", "ֺ", "ֻ", "ּ", "ֽ"
RAFE, SHIN_DOT, SIN_DOT, QAMATS_QATAN = "ֿ", "ׁ", "ׂ", "ׇ"
MAQAF, SOF_PASUQ = "־", "׃"
ACCENTS = {chr(c) for c in range(0x0591, 0x05B0)}
# accents written at the word's edge, not on the stressed syllable
POSITIONAL = {"֙", "֒", "֮", "֩", "֚", "֠", "֡"}
VOWEL_POINTS = {HIRIQ: "i", TSERE: "e", SEGOL: "ɛ", PATAH: "a", QAMATS: "ɔ", HOLAM: "o",
                HOLAM_HASER: "o", QUBUTS: "u", QAMATS_QATAN: "ɔ",
                HSEGOL: "ɛ̆", HPATAH: "ă", HQAMATS: "ɔ̆"}
LONG_POINTS = {TSERE, HOLAM, HOLAM_HASER}
BGDKPT = set("בגדכפת")
FINALS = {"ך": "כ", "ם": "מ", "ן": "נ", "ף": "פ", "ץ": "צ"}
GUTTURALS = set("אהחע")


@dataclass
class Letter:
    ch: str                          # base letter, final forms normalized
    marks: set[str] = field(default_factory=set)
    final_form: bool = False

    @property
    def vowel(self) -> str | None:
        for m in self.marks:
            if m in VOWEL_POINTS:
                return m
        return None


def letters(word: str) -> list[Letter]:
    out: list[Letter] = []
    for ch in ud.normalize("NFD", word):
        if "א" <= ch <= "ת":
            out.append(Letter(FINALS.get(ch, ch), final_form=ch in FINALS))
        elif ud.combining(ch) and out:
            out[-1].marks.add(ch)
    return out


def strip_cantillation(word: str) -> str:
    return "".join(c for c in word if c not in ACCENTS and c != METEG)


@dataclass
class Seg:
    ipa: str
    vowel: bool
    stressed: bool = False
    source: int = -1                 # letter index, for stress mapping


def _is_mater(ls: list[Letter], i: int) -> str | None:
    """If letter i is a vowel letter (mater lectionis) rather than a consonant, return the
    vowel it spells (for shureq/holam-waw) or '' (for a silent lengthening letter)."""
    l = ls[i]
    prev = ls[i - 1] if i > 0 else None
    nxt = ls[i + 1] if i + 1 < len(ls) else None
    has_vowel = l.vowel is not None or SHEVA in l.marks
    prev_bare = prev is not None and prev.vowel is None and SHEVA not in prev.marks
    if l.ch == "ו" and (HOLAM in l.marks or HOLAM_HASER in l.marks) and \
            not (l.marks & (set(VOWEL_POINTS) - {HOLAM, HOLAM_HASER})) and prev_bare:
        return "o"                                         # holam waw: the vowel of the letter before
    if l.ch == "ו" and not has_vowel:
        if DAGESH in l.marks and (prev is None or (prev.vowel is None and SHEVA not in prev.marks)):
            return "u"                                     # shureq
    if l.ch == "י" and not has_vowel and DAGESH not in l.marks and prev is not None and \
            prev.vowel in (HIRIQ, TSERE, SEGOL):
        return ""                                          # hiriq-yod, tsere-yod
    if l.ch == "ה" and i == len(ls) - 1 and not has_vowel and DAGESH not in l.marks:
        return ""                                          # final he as a vowel letter
    if l.ch == "א" and not has_vowel and prev is not None and not (
            nxt is not None and nxt.ch == "ו" and (HOLAM in nxt.marks or DAGESH in nxt.marks)):
        return ""                                          # quiescent aleph (not before ô / û)
    return None


def _cons(l: Letter, scheme: str, hard: bool) -> str:
    c = l.ch
    if c == "ש":
        return "s" if SIN_DOT in l.marks else "ʃ"
    t = {"tiberian": {"א": "ʔ", "ב": "b" if hard else "v", "ג": "ɡ" if hard else "ɣ",
                      "ד": "d" if hard else "ð", "ה": "h", "ו": "v", "ז": "z", "ח": "ħ", "ט": "tˁ",
                      "י": "j", "כ": "k" if hard else "x", "ל": "l", "מ": "m", "נ": "n", "ס": "s",
                      "ע": "ʕ", "פ": "p" if hard else "f", "צ": "sˁ", "ק": "q", "ר": "ʀ",
                      "ת": "t" if hard else "θ"},
         "modern-israeli": {"א": "ʔ", "ב": "b" if hard else "v", "ג": "ɡ", "ד": "d", "ה": "h",
                            "ו": "v", "ז": "z", "ח": "χ", "ט": "t", "י": "j", "כ": "k" if hard else "χ",
                            "ל": "l", "מ": "m", "נ": "n", "ס": "s", "ע": "ʔ", "פ": "p" if hard else "f",
                            "צ": "ts", "ק": "k", "ר": "ʁ", "ת": "t"}}[scheme]
    return t[c]


def _vowel_ipa(point: str, scheme: str, long_: bool) -> str:
    v = VOWEL_POINTS[point]
    if scheme == "modern-israeli":
        v = {"ɔ": "a", "ɛ": "e", "ɛ̆": "e", "ă": "a", "ɔ̆": "o"}.get(v, v)
        if point == QAMATS_QATAN:
            v = "o"
        return v
    return v + ("ː" if long_ and "̆" not in v else "")


def segments(word: str, scheme: str) -> list[Seg]:
    ls = letters(word.replace("/", ""))
    n = len(ls)
    segs: list[Seg] = []
    prev_vowel_long = False
    prev_had_sheva_silent = False
    for i, l in enumerate(ls):
        mater = _is_mater(ls, i)
        if mater is not None:
            if mater in ("u", "o"):
                long_ = scheme == "tiberian"
                segs.append(Seg(mater + ("ː" if long_ else ""), True, source=i))
                prev_vowel_long = True
            elif segs and segs[-1].vowel and scheme == "tiberian" and not segs[-1].ipa.endswith("ː"):
                segs[-1].ipa += "ː"
                prev_vowel_long = True
            prev_had_sheva_silent = False
            continue
        after_vowel = bool(segs) and segs[-1].vowel
        dagesh = DAGESH in l.marks
        forte = dagesh and after_vowel and l.ch not in GUTTURALS
        hard = l.ch in BGDKPT and dagesh
        c = _cons(l, scheme, hard)
        last = i == n - 1 or all(_is_mater(ls, k) is not None for k in range(i + 1, n))
        # furtive patah: a final guttural with patah is sounded after the vowel glide (rûaḥ)
        if last and l.ch in "חע" and PATAH in l.marks or (last and l.ch == "ה" and dagesh and PATAH in l.marks):
            segs.append(Seg("a", True, source=i))
            segs.append(Seg(c, False, source=i))
            continue
        if forte and scheme == "tiberian":
            segs.append(Seg(c, False, source=i))           # gemination closes the previous syllable
        segs.append(Seg(c, False, source=i))
        if l.vowel:
            long_ = l.vowel in LONG_POINTS or (l.vowel == QAMATS and scheme == "tiberian")
            segs.append(Seg(_vowel_ipa(l.vowel, scheme, long_), True, source=i))
            prev_vowel_long = long_
            prev_had_sheva_silent = False
        elif SHEVA in l.marks:
            vocal = (not last) and (i == 0 or forte or prev_had_sheva_silent or
                                    (prev_vowel_long and METEG in (ls[i - 1].marks if i else set())))
            if vocal:
                segs.append(Seg("ă" if scheme == "tiberian" else "e", True, source=i))
                prev_had_sheva_silent = False
            else:
                prev_had_sheva_silent = True
            prev_vowel_long = False
        else:
            prev_had_sheva_silent = False
    return segs


def _stress_letter(word: str, silluq: bool = False) -> int | None:
    """Index of the letter carrying the (non-positional) accent, or the last letter if only a
    positional accent is present, or None if the word is unaccented (joined by maqaf).
    The Leningrad text writes silluq, the accent on a verse's last word, with the meteg sign:
    `silluq=True` makes the meteg count as the stress there."""
    ls = letters(word.replace("/", ""))
    marks = (ACCENTS - POSITIONAL) | ({METEG} if silluq else set())
    idx = [i for i, l in enumerate(ls) if l.marks & marks]
    if idx:
        return idx[-1]
    if any(l.marks & POSITIONAL for l in ls):
        return len(ls) - 1
    return None


RESPELL = {
    "tiberian": [("ɛ̆", "e"), ("ɔ̆", "o"), ("ă", "a"), ("ɔː", "aw"), ("ɔ", "aw"), ("aː", "aa"), ("eː", "ay"),
                 ("iː", "ee"), ("oː", "oh"), ("uː", "oo"), ("ɛː", "eh"), ("ɛ", "e"),
                 ("tˁ", "ṭ"), ("sˁ", "ṣ"), ("ʀ", "r"), ("ħ", "ḥ"), ("ʕ", "ʿ"), ("ʔ", "ʾ"), ("ʃ", "sh"),
                 ("θ", "th"), ("ð", "dh"), ("ɣ", "gh"), ("x", "kh"), ("ɡ", "g"), ("j", "y"), ("u", "u"),
                 ("i", "i"), ("e", "e"), ("o", "o")],
    "modern-israeli": [("χ", "kh"), ("ʁ", "r"), ("ʔ", ""), ("ʃ", "sh"), ("ɡ", "g"), ("j", "y"),
                       ("i", "ee"), ("u", "oo")],
}
KEY = {
    "tiberian": [
        ("aw", "qamets: open o, as in awe"),
        ("a", "patah, and the vocal shewa: a as in father, short"),
        ("e / ay", "segol, e as in pet / tsere, long close e"),
        ("i / ee", "hiriq: short / long (with yod)"),
        ("oh, oo", "holam, shureq: long o, long u"),
        ("ʾ, ʿ", "aleph: a catch in the throat; ayin: a squeeze deep in the throat"),
        ("ḥ", "ḥet: a breathy h from the throat, not kh"),
        ("ṭ, ṣ, q", "emphatic t, s and k: said with the tongue root pulled back"),
        ("r", "uvular r, in the back of the throat, as in French"),
        ("v, gh, dh, kh, f, th", "b g d k p t after a vowel soften, unless a dot (dagesh) hardens them"),
        ("sh / s", "shin / sin, told apart by the dot on the right or left"),
        ("CAPS", "the stressed syllable, marked in the text by its cantillation accent"),
    ],
    "modern-israeli": [
        ("a, e, ee, o, oo", "five plain vowels; qamets and patah are both a"),
        ("kh", "ḥet and soft kaf: as in Bach"),
        ("(silent)", "aleph and ayin are usually not sounded"),
        ("ts", "tsade"),
        ("r", "a French-style r"),
        ("CAPS", "stressed syllable, the same as in the ancient reading"),
    ],
}
SCHEME_LABELS = {
    "tiberian": "Tiberian: the reading the vowel points record, about AD 900 (after Khan)",
    "modern-israeli": "Modern Israeli Hebrew",
}


def _respell(ipa: str, scheme: str) -> str:
    out, i = [], 0
    while i < len(ipa):
        for a, b in RESPELL[scheme]:
            if ipa.startswith(a, i):
                out.append(b); i += len(a); break
        else:
            out.append(ipa[i]); i += 1
    return "".join(out)


def phonemize(word: str, scheme: str = "tiberian", quantities=None, silluq: bool = False, **_) -> dict:
    segs = segments(word, scheme)
    vi = [k for k, s in enumerate(segs) if s.vowel]
    if not vi:
        ipa = "".join(s.ipa for s in segs)
        return {"ipa": ipa, "respell": _respell(ipa, scheme), "syllables": 0}
    # syllables: each vowel with the consonant before it; clusters split before the last consonant
    bounds = [0]
    for n in range(len(vi) - 1):
        a, b = vi[n], vi[n + 1]
        bounds.append(b if b - a == 1 else b - 1)
    bounds.append(len(segs))
    syls = [segs[bounds[j]:bounds[j + 1]] for j in range(len(vi))]
    sl = _stress_letter(word, silluq)
    stress = None
    if sl is not None:
        for j, syl in enumerate(syls):
            if any(s.vowel and s.source >= sl for s in syl) or any(s.source == sl and s.vowel for s in syl):
                stress = j
                break
        if stress is None:
            stress = len(syls) - 1
    ipas = ["".join(s.ipa for s in syl) for syl in syls]
    spells = [_respell(ip, scheme) for ip in ipas]
    if stress is not None and len(syls) > 1:
        spells[stress] = spells[stress].upper()
    ipa = ".".join(("ˈ" if j == stress and len(syls) > 1 else "") + ip for j, ip in enumerate(ipas))
    return {"ipa": ipa, "respell": "-".join(spells), "syllables": len(syls)}
