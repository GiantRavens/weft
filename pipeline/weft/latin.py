"""Latin orthography -> syllables -> stress -> IPA and respelling, per pronunciation scheme.

Latin spelling does not mark vowel length, and stress depends on it, so every word must come
through the quantity table (``data/lat_quantities.yaml``): lowercase form -> macronized form,
with ``+`` before an enclitic (``prīmā+que``). A word missing from the table is phonemized
from its bare spelling and reported as ``quantity-unknown``.

Stress (both schemes): one syllable, that one; two, the first; three or more, the penult if it
is heavy (long vowel, diphthong, or closed), otherwise the antepenult. Before an enclitic
(-que, -ne, -ve) the stress falls on the host's last syllable: PRĪ-mā but prī-MĀ-que.

Schemes
-------
classical       Restored pronunciation of the late Republic (after W. S. Allen, *Vox Latina*):
                c and g always hard, v = w, ae = ai, vowel length audible.
ecclesiastical  Italianate church Latin: c and g soften before e, i, ae, oe; v = v; ae = e;
                vowel quality ignores length, but stress still follows the classical rule.
"""
from __future__ import annotations

import unicodedata as ud
from dataclasses import dataclass

VERSION = "0.1"
MACRON = "̄"
VOWELS = set("aeiouy")
DIPHTHONGS = {"ae", "au", "oe"}
ENCLITICS = ("que", "ne", "ve")
STOPS = set("pbtdcgk") | {"ph", "th", "ch"}
LIQUIDS = set("lr")
PUNCT = ",.;:!?()[]“”‘’\"—"


@dataclass
class Seg:
    text: str            # letters as written, lowercase, macrons removed
    vowel: bool
    long: bool = False


def _segments(word: str) -> list[Seg]:
    """Split into consonant units and vowel nuclei. qu, ch, ph, th are single units; x is k+s."""
    s = ud.normalize("NFD", word.lower())
    chars: list[tuple[str, bool]] = []
    for ch in s:
        if ch == MACRON and chars:
            chars[-1] = (chars[-1][0], True)
        elif not ud.combining(ch):
            chars.append((ch, False))
    segs: list[Seg] = []
    i = 0
    while i < len(chars):
        c, mac = chars[i]
        nxt = chars[i + 1][0] if i + 1 < len(chars) else ""
        if c == "q" and nxt == "u":
            segs.append(Seg("qu", False)); i += 2; continue
        if c in "cpt" and nxt == "h":
            segs.append(Seg(c + "h", False)); i += 2; continue
        if c == "x":
            segs.append(Seg("k", False)); segs.append(Seg("s", False)); i += 1; continue
        if c == "i" and i == 0 and nxt in VOWELS and len(chars) > 2:
            segs.append(Seg("j", False)); i += 1; continue      # iūnctus, iam: consonantal i
        if c in VOWELS:
            pair = c + nxt
            if pair in DIPHTHONGS and not mac and not (i + 1 < len(chars) and chars[i + 1][1]):
                segs.append(Seg(pair, True, True)); i += 2; continue
            segs.append(Seg(c, True, mac)); i += 1; continue
        segs.append(Seg(c, False)); i += 1
    return segs


@dataclass
class Syl:
    onset: list[Seg]
    nucleus: Seg
    coda: list[Seg]

    @property
    def heavy(self) -> bool:
        return self.nucleus.long or bool(self.coda)


def syllabify(word: str) -> list[Syl]:
    segs = _segments(word)
    vi = [i for i, s in enumerate(segs) if s.vowel]
    if not vi:
        return []
    syls = [Syl([], segs[i], []) for i in vi]
    syls[0].onset = segs[: vi[0]]
    syls[-1].coda = segs[vi[-1] + 1 :]
    for n in range(len(vi) - 1):
        cl = segs[vi[n] + 1 : vi[n + 1]]
        if not cl:
            continue
        if len(cl) >= 2 and cl[-2].text in STOPS and cl[-1].text in LIQUIDS:
            cut = len(cl) - 2          # muta cum liquida: stays together, syllable stays light
        else:
            cut = len(cl) - 1
        syls[n].coda = cl[:cut]
        syls[n + 1].onset = cl[cut:]
    return syls


def stress_index(syls: list[Syl], host_len: int | None = None) -> int:
    n = len(syls)
    if host_len is not None and host_len < n:
        return host_len - 1              # enclitic: stress the host's last syllable
    if n <= 2:
        return 0
    return n - 2 if syls[n - 2].heavy else n - 3


# ---------------------------------------------------------------- schemes
def _front(seg: Seg | None) -> bool:
    return seg is not None and seg.vowel and seg.text[0] in "eiy" or (seg is not None and seg.text in ("ae", "oe"))


def _vowel_ipa(v: Seg, scheme: str) -> str:
    if scheme == "classical":
        if v.text in DIPHTHONGS:
            return {"ae": "ae", "au": "au", "oe": "oe"}[v.text]   # plain: the non-syllabic mark breaks web fonts
        short = {"a": "a", "e": "ɛ", "i": "ɪ", "o": "ɔ", "u": "ʊ", "y": "ʏ"}[v.text]
        long_ = {"a": "aː", "e": "eː", "i": "iː", "o": "oː", "u": "uː", "y": "yː"}[v.text]
        return long_ if v.long else short
    return {"ae": "ɛ", "oe": "ɛ", "au": "au", "a": "a", "e": "ɛ", "i": "i", "o": "ɔ", "u": "u", "y": "i"}[v.text]


def _cons_ipa(c: Seg, nxt: Seg | None, prev: Seg | None, scheme: str) -> str:
    t = c.text
    if scheme == "classical":
        return {"c": "k", "k": "k", "qu": "kʷ", "v": "w", "j": "j", "ch": "kʰ", "ph": "pʰ",
                "th": "tʰ", "h": "h", "z": "dz", "g": "ɡ"}.get(t, "ŋ" if t == "n" and nxt and nxt.text in ("c", "g", "qu", "k") else t)
    # ecclesiastical
    if t == "c":
        return "tʃ" if _front(nxt) else "k"
    if t == "g":
        if nxt and nxt.text == "n":
            return ""                     # gn = ɲ, sounded with the following syllable
        return "dʒ" if _front(nxt) else "ɡ"
    if t == "n" and prev and prev.text == "g":
        return "ɲ"
    if t == "s" and nxt and nxt.text == "c":
        return "s"
    return {"k": "k", "qu": "kw", "v": "v", "j": "j", "ch": "k", "ph": "f", "th": "t",
            "h": "", "z": "dz", "x": "ks"}.get(t, "ŋ" if t == "n" and nxt and nxt.text in ("c", "g", "qu", "k") else t)


def _syl_ipa(syls: list[Syl], scheme: str) -> list[str]:
    flat: list[tuple[int, Seg]] = []
    for n, s in enumerate(syls):
        for seg in s.onset + [s.nucleus] + s.coda:
            flat.append((n, seg))
    parts = [""] * len(syls)
    for k, (n, seg) in enumerate(flat):
        nxt = flat[k + 1][1] if k + 1 < len(flat) else None
        prev = flat[k - 1][1] if k > 0 else None
        if seg.vowel:
            parts[n] += _vowel_ipa(seg, scheme)
        else:
            # ecclesiastical sc before a front vowel = ʃ
            if scheme == "ecclesiastical" and seg.text == "s" and nxt and nxt.text == "c" and _front(flat[k + 2][1] if k + 2 < len(flat) else None):
                parts[n] += "ʃ"; continue
            if scheme == "ecclesiastical" and seg.text == "c" and prev and prev.text == "s" and _front(nxt):
                continue
            # ecclesiastical ti before a vowel = tsi (natio), except after s, t, x and word-initially
            if (scheme == "ecclesiastical" and seg.text == "t" and nxt and nxt.text == "i" and k > 0
                    and k + 2 < len(flat) and flat[k + 2][1].vowel and not (prev and prev.text in ("s", "t", "k"))):
                parts[n] += "ts"; continue
            parts[n] += _cons_ipa(seg, nxt, prev, scheme)
    return parts


RESPELL = {
    "classical": [("ae", "ai"), ("au", "ow"), ("oe", "oy"), ("aː", "aa"), ("eː", "ay"), ("iː", "ee"),
                  ("oː", "oh"), ("uː", "oo"), ("yː", "üü"), ("kʷ", "kw"), ("kʰ", "kʰ"), ("pʰ", "pʰ"),
                  ("tʰ", "tʰ"), ("ɛ", "e"), ("ɪ", "i"), ("ɔ", "o"), ("ʊ", "u"), ("ʏ", "ü"), ("ŋ", "ng"), ("ɡ", "g"),
                  ("j", "y")],
    "ecclesiastical": [("au", "ow"), ("tʃ", "ch"), ("dʒ", "j"), ("ʃ", "sh"), ("ɲ", "ny"), ("ɡ", "g"),
                       ("ɛ", "e"), ("ɔ", "o"), ("i", "ee"), ("u", "oo"), ("ŋ", "ng"), ("j", "y")],
}
KEY = {
    "classical": [
        ("a / aa", "a as in father, short / held long"),
        ("e / ay", "e as in pet / long close e, as in they without the glide"),
        ("i / ee", "i as in pit / ee as in machine"),
        ("o / oh", "o as in pot / oh as in go without the glide"),
        ("u / oo", "u as in put / oo as in food"),
        ("ai, ow, oy", "ae, au, oe: aisle, cow, boy"),
        ("k, g", "c and g are always hard: Kikero, not Sisero"),
        ("w", "v is w: weni, widi, wiki"),
        ("y", "consonantal i, as in yes: iūnctus = yoonk-tus"),
        ("kw", "qu"),
        ("kʰ pʰ tʰ", "Greek loans: k, p, t with a puff of breath"),
        ("CAPS", "stressed syllable, by the penultimate rule"),
    ],
    "ecclesiastical": [
        ("a e ee o oo", "pure Italian vowels; length changes stress, not quality"),
        ("e", "ae and oe are both e: caelum = CHE-loom"),
        ("ch", "c before e, i, ae, oe: as in church"),
        ("j", "g before e, i, ae, oe: as in gem"),
        ("sh", "sc before e, i"),
        ("ny", "gn, as in canyon"),
        ("v", "v as in English"),
        ("y", "consonantal i, as in yes"),
        ("CAPS", "stressed syllable, same position as classical"),
    ],
}
SCHEME_LABELS = {
    "classical": "Classical: restored pronunciation of Cicero's and Ovid's Rome",
    "ecclesiastical": "Ecclesiastical: Italianate church Latin",
}


def _respell_one(ipa: str, scheme: str) -> str:
    out, i = [], 0
    table = RESPELL[scheme]
    while i < len(ipa):
        for a, b in table:
            if ipa.startswith(a, i):
                out.append(b); i += len(a); break
        else:
            out.append(ipa[i]); i += 1
    return "".join(out)


def apply_quantity(word: str, table: dict[str, str]) -> tuple[str, bool]:
    key = ud.normalize("NFC", word.lower())
    if key in table:
        return ud.normalize("NFC", table[key]), True
    return word, False


def phonemize(word: str, scheme: str, quantities: dict[str, str] | None = None) -> dict:
    w = "".join(ch for ch in word if ch not in PUNCT)
    known = False
    if quantities is not None:
        w, known = apply_quantity(w, quantities)
    host_len = None
    if "+" in w:
        host, enc = w.split("+", 1)
        host_len = len(syllabify(host))
        w = host + enc
    # An enclitic is never guessed from spelling ("bene", "quisque" would break); only the
    # table's "+" marks one.
    syls = syllabify(w)
    if not syls:
        return {"ipa": w, "respell": w, "syllables": 0, "known": known}
    si = stress_index(syls, host_len)
    ipas = _syl_ipa(syls, scheme)
    spells = []
    for n, ip in enumerate(ipas):
        r = _respell_one(ip, scheme)
        spells.append(r.upper() if n == si and len(syls) > 1 else r)
    ipa = ".".join(("ˈ" if n == si and len(syls) > 1 else "") + ip for n, ip in enumerate(ipas))
    return {"ipa": ipa, "respell": "-".join(spells), "syllables": len(syls), "known": known}
