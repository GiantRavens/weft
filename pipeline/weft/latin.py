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
        # stop + liquid begins the next syllable, except tl and dl, which Latin never allows
        if len(cl) >= 2 and cl[-2].text in STOPS and cl[-1].text in LIQUIDS and cl[-2].text + cl[-1].text not in ("tl", "dl"):
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
    if scheme == "anglo-latin":
        # Latin as read in England around 1215, in the French manner: soft c = ts (becoming s
        # during the 1200s), soft g and consonantal i/j = dʒ, h silent, v = v
        if t == "c":
            return "ts" if _front(nxt) else "k"
        if t == "g":
            return "dʒ" if _front(nxt) else "ɡ"
        return {"k": "k", "qu": "kw", "v": "v", "j": "dʒ", "ch": "k", "ph": "f", "th": "t",
                "h": "", "z": "dz", "x": "ks"}.get(t, "ŋ" if t == "n" and nxt and nxt.text in ("c", "g", "qu", "k") else t)
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
            if (scheme in ("ecclesiastical", "anglo-latin") and seg.text == "t" and nxt and nxt.text == "i" and k > 0
                    and k + 2 < len(flat) and flat[k + 2][1].vowel and not (prev and prev.text in ("s", "t", "k"))):
                parts[n] += "ts"; continue
            if scheme == "anglo-latin" and seg.text == "s" and prev and prev.vowel and nxt and nxt.vowel:
                parts[n] += "z"; continue                  # French-style: s between vowels = z
            # n before a soft c or g stays n (incipit, quinci, angelus); ŋ only before a hard velar
            if (scheme in ("ecclesiastical", "anglo-latin") and seg.text == "n" and nxt and nxt.text in ("c", "g")
                    and k + 2 < len(flat) and _front(flat[k + 2][1])):
                parts[n] += "n"; continue
            parts[n] += _cons_ipa(seg, nxt, prev, scheme)
    return parts


RESPELL = {
    "classical": [("ae", "ai"), ("au", "ow"), ("oe", "oy"), ("aː", "aa"), ("eː", "ay"), ("iː", "ee"),
                  ("oː", "oh"), ("uː", "oo"), ("yː", "üü"), ("kʷ", "kw"), ("kʰ", "kʰ"), ("pʰ", "pʰ"),
                  ("tʰ", "tʰ"), ("ɛ", "e"), ("ɪ", "i"), ("ɔ", "o"), ("ʊ", "u"), ("ʏ", "ü"), ("ŋ", "ng"), ("ɡ", "g"),
                  ("j", "y")],
    "ecclesiastical": [("au", "ow"), ("tʃ", "ch"), ("dʒ", "j"), ("ʃ", "sh"), ("ɲ", "ny"), ("ɡ", "g"),
                       ("ɛ", "e"), ("ɔ", "o"), ("i", "ee"), ("u", "oo"), ("ŋ", "ng"), ("j", "y")],
    "anglo-latin": [("au", "ow"), ("dʒ", "j"), ("ts", "ts"), ("ɡ", "g"),
                    ("ɛ", "e"), ("ɔ", "o"), ("i", "ee"), ("u", "oo"), ("ŋ", "ng")],
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
KEY_ANGLO = [
    ("a e ee o oo", "plain vowels; long and short no longer differ in sound, only in stress"),
    ("e", "ae and oe are both e: the medieval spelling terre for terrae records this"),
    ("ts", "c before e and i, as in bits; by the late 1200s it became s"),
    ("j", "g before e and i, and the letter j: as in judge"),
    ("(silent)", "h is not sounded: homo = omo"),
    ("v", "v as in English"),
    ("z", "s between vowels, as in French prison"),
    ("CAPS", "stressed syllable, by the classical penultimate rule, which medieval readers kept"),
    ("caution", "reconstructed from spelling and from French and English sound history; approximate"),
]

SCHEME_LABELS = {
    "anglo-latin": "Anglo-Latin: as a clerk in England read Latin around 1215 (approximate)",
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


def phonemize(word: str, scheme: str, quantities: dict[str, str] | None = None, dialect: str | None = None, **_) -> dict:
    if scheme == "as-first-read":
        return national(word, dialect or "english", quantities)
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

KEY["anglo-latin"] = KEY_ANGLO


# ---------------------------------------------------------------- national pronunciations, 1600s
# "As first read" for early-modern Latin depends on the reader's country. The scheme
# `as-first-read` takes a `dialect`: english (Newton, Cambridge, 1680s) or french (Descartes,
# 1640s). Both are reconstructions from contemporary grammars and later accounts (W. S. Allen,
# Vox Latina, appendix); treat them as approximate.

_ENG_LONG = {"a": ("eɪ", "ay"), "e": ("iː", "ee"), "i": ("aɪ", "eye"), "y": ("aɪ", "eye"),
             "o": ("oʊ", "oh"), "u": ("juː", "yoo"), "ae": ("iː", "ee"), "oe": ("iː", "ee"), "au": ("ɔː", "aw")}
_ENG_SHORT = {"a": ("æ", "a"), "e": ("ɛ", "e"), "i": ("ɪ", "i"), "y": ("ɪ", "i"),
              "o": ("ɒ", "o"), "u": ("ʌ", "u"), "ae": ("iː", "ee"), "oe": ("iː", "ee"), "au": ("ɔː", "aw")}
_ENG_FINAL = {"a": ("ə", "uh"), "e": ("iː", "ee"), "i": ("aɪ", "eye"), "o": ("oʊ", "oh"), "u": ("juː", "yoo")}
_FR_V = {"a": ("a", "a"), "e": ("e", "e"), "i": ("i", "ee"), "y": ("i", "ee"), "o": ("o", "o"),
         "u": ("y", "ü"), "ae": ("e", "e"), "oe": ("e", "e"), "au": ("o", "o")}
_FR_NASAL = {"a": ("ɑ̃", "an"), "e": ("ɑ̃", "an"), "i": ("ɛ̃", "in"), "o": ("ɔ̃", "on"), "u": ("ɔ̃", "on")}


def _national(syls: list[Syl], stress: int, dialect: str) -> list[tuple[str, str]]:
    """(ipa, respell) per syllable for the English or French method."""
    flat: list[tuple[int, Seg]] = []
    for n, s in enumerate(syls):
        for seg in s.onset + [s.nucleus] + s.coda:
            flat.append((n, seg))
    ipa = [""] * len(syls)
    sp = [""] * len(syls)
    last = len(syls) - 1
    for k, (n, seg) in enumerate(flat):
        nxt = flat[k + 1][1] if k + 1 < len(flat) else None
        nxt2 = flat[k + 2][1] if k + 2 < len(flat) else None
        prev = flat[k - 1][1] if k > 0 else None
        t = seg.text
        if seg.vowel:
            syl = syls[n]
            if dialect == "english":
                open_ = not syl.coda
                if n == stress:
                    antepenult = len(syls) >= 3 and stress == len(syls) - 3
                    # antepenults shorten (VI-ri-bus), except before a single consonant plus i or e
                    # and another vowel, which keeps them long (RAY-di-us, kon-TRAY-ri-as)
                    before_hiatus = (n + 2 < len(syls) and syls[n + 1].nucleus.text in ("i", "e")
                                     and not syls[n + 1].coda and not syls[n + 2].onset)
                    shorten = antepenult and t != "u" and not before_hiatus
                    table = _ENG_LONG if open_ and not shorten else _ENG_SHORT
                elif n == last and open_:
                    table = _ENG_FINAL if t in _ENG_FINAL else _ENG_SHORT
                elif open_ and t == "u":
                    table = _ENG_LONG                      # u stays yoo in open syllables: mū-TAY-ree
                else:
                    table = _ENG_SHORT
                if n == last and t == "e" and syl.coda and syl.coda[-1].text == "s" and len(syl.coda) == 1:
                    a, b = ("iː", "ee")                    # final -es = eez: actiones, partes
                else:
                    a, b = table.get(t, (t, t))
                if b == "eye" and sp[n]:
                    b = "ye"                               # after a consonant: NYE-sye, SEN-dye
            else:
                nxt_onset = syls[n + 1].onset[0].text if n + 1 < len(syls) and syls[n + 1].onset else ""
                nasal = (syl.coda and syl.coda[0].text in ("m", "n") and n != last
                         and nxt_onset not in ("m", "n"))    # no nasal vowel before another m or n: omnium
                a, b = _FR_NASAL[t] if nasal and t in _FR_NASAL else _FR_V.get(t, (t, t))
                if n == last and t == "u" and syl.coda and syl.coda[0].text in ("m", "n"):
                    a, b = ("ɔ", "o")                      # final -um = om: sum, dominum
            ipa[n] += a; sp[n] += b
            continue
        front = nxt is not None and nxt.vowel and (nxt.text[0] in "eiy" or nxt.text in ("ae", "oe"))
        if t == "c":
            a, b = ("s", "s") if front else ("k", "k")
        elif t == "g":
            if front:
                a, b = ("dʒ", "j") if dialect == "english" else ("ʒ", "zh")
            else:
                a, b = ("ɡ", "g")
        elif t == "j":
            a, b = ("dʒ", "j") if dialect == "english" else ("ʒ", "zh")
        elif t == "qu":
            a, b = ("kw", "kw") if dialect == "english" else ("k", "k")
        elif t == "t" and nxt is not None and nxt.text == "i" and nxt2 is not None and nxt2.vowel and k > 0 \
                and not (prev is not None and prev.text in ("s", "t", "k")):
            a, b = ("ʃ", "sh") if dialect == "english" else ("s", "s")
        elif t == "s" and dialect == "french" and prev is not None and prev.vowel and nxt is not None and nxt.vowel:
            a, b = ("z", "z")
        elif t == "s" and dialect == "english" and nxt is None and prev is not None and prev.text == "e" and n == last:
            a, b = ("z", "z")                              # English method: final -es = eez
        elif t == "h":
            a, b = ("h", "h") if dialect == "english" else ("", "")
        elif t == "ph":
            a, b = ("f", "f")
        elif t in ("ch", "th"):
            a, b = (t[0], t[0])
        elif t == "k" and dialect == "french" and nxt is not None and nxt.text == "s" and k <= 2 \
                and flat[0][1].text == "e":
            a, b = ("ɡ", "g")                              # ex- before a vowel = egz: existere
        elif t == "s" and dialect == "french" and prev is not None and prev.text == "k" and k <= 3 \
                and nxt is not None and nxt.vowel and flat[0][1].text == "e":
            a, b = ("z", "z")
        elif t in ("m", "n") and dialect == "french" and prev is not None and prev.vowel and seg in syls[n].coda \
                and n != last and _FR_NASAL.get(prev.text) \
                and not (n + 1 < len(syls) and syls[n + 1].onset and syls[n + 1].onset[0].text in ("m", "n")):
            a, b = ("", "")                                # absorbed into the nasal vowel
        else:
            a, b = (t, t)
        ipa[n] += a; sp[n] += b
    return list(zip(ipa, sp))


def national(word: str, dialect: str, quantities: dict[str, str] | None = None) -> dict:
    w = "".join(ch for ch in word if ch not in PUNCT)
    known = False
    if quantities is not None:
        w, known = apply_quantity(w, quantities)
    host_len = None
    if "+" in w:
        host, enc = w.split("+", 1)
        host_len = len(syllabify(host))
        w = host + enc
    syls = syllabify(w)
    if not syls:
        return {"ipa": w, "respell": w, "syllables": 0, "known": known}
    stress = len(syls) - 1 if dialect == "french" else stress_index(syls, host_len)
    parts = _national(syls, stress, dialect)
    one = len(syls) == 1
    ipa = ".".join(("ˈ" if j == stress and not one else "") + p[0] for j, p in enumerate(parts))
    resp = "-".join(p[1].upper() if j == stress and not one else p[1] for j, p in enumerate(parts))
    return {"ipa": ipa, "respell": resp, "syllables": len(syls), "known": known}


KEY["as-first-read"] = [
    ("", "Each author's Latin as read in his own country: Newton's in the English manner of the 1680s, Descartes's in the French manner of the 1640s. Reconstructed from contemporary grammars; approximate."),
    ("ay, ee, eye, oh, yoo", "English method: a stressed vowel in an open syllable takes its English long value, so statu = STAY-tyoo"),
    ("sh", "English method: ti before a vowel, as in mutation"),
    ("ee (final e), eye (final i)", "English method: omne = OM-nee, dirigi = DI-ri-jye"),
    ("ü", "French method: u as in French tu"),
    ("an, on, in", "French method: nasal vowels before m or n"),
    ("zh", "French method: g before e and i, and j, as in measure"),
    ("CAPS", "stress: Latin position in the English method; always the last syllable in the French method"),
]
# as-first-read reads each section in its author's national manner (the section's `dialect`); a work
# shows only the key rows for the dialects it uses (key_for), so a page on Descartes does not explain
# the English method
KEY_BY_DIALECT = {"as-first-read": {
    "english": [
        ("", "Latin as read in England in the 1680s: the English method. Reconstructed from contemporary grammars; approximate."),
        ("ay, ee, eye, oh, yoo", "a stressed vowel in an open syllable takes its English long value, so statu = STAY-tyoo"),
        ("sh", "ti before a vowel, as in mutation"),
        ("ee (final e), eye (final i)", "omne = OM-nee, dirigi = DI-ri-jye"),
        ("CAPS", "stress: in the Latin position"),
    ],
    "french": [
        ("", "Latin as read in France in the 1640s: the French method. Reconstructed from contemporary grammars; approximate."),
        ("ü", "u as in French tu"),
        ("an, on, in", "nasal vowels before m or n"),
        ("zh", "g before e and i, and j, as in measure"),
        ("CAPS", "stress: always the last syllable"),
    ],
}}
SCHEME_LABELS["as-first-read"] = "As first read: in the author's own country's manner (approximate)"


def key_for(scheme: str, dialects: set[str]) -> list:
    """The key for a scheme, narrowed to the dialects a work uses where the scheme is read by dialect.
    A work with a dialect the narrowed key does not cover gets the whole key."""
    by = KEY_BY_DIALECT.get(scheme)
    if not by or not dialects or not dialects <= set(by):
        return KEY[scheme]
    if len(dialects) == 1:
        return by[next(iter(dialects))]
    return KEY[scheme]


# ---------------------------------------------------------------- humanist readings, 1480s to 1510s
# Three more national manners of reading Latin, for humanist authors of the generation before
# the reforms of pronunciation. Each is its own scheme, so each has its own key; the same rules
# are also reachable through `as-first-read` with a section `dialect` (dutch, tudor, italian).
# All three keep the classical stress position (the penultimate rule), as readers of the time
# did. Vowel quantity sets only the stress; vowel quality follows the reader's own language.
#
#   low-countries     Latin in the Low Countries around 1500 (Erasmus): Dutch vowel values,
#                     long in open syllables and short in closed ones; u as Dutch uu (front
#                     rounded); g a fricative everywhere; soft c = s; ti before a vowel = tsi;
#                     ch = kh. Reconstructed from Middle Dutch sound history and the later
#                     Dutch school tradition; approximate.
#   tudor-english     Latin in England around 1516 (More): the English method at an earlier stage
#                     of the Great Vowel Shift. Stressed open vowels take English long values,
#                     but a is still aa, o is still aw, i is a glide ei, and short u is u as in
#                     put; ti before a vowel = si, not yet sh. Approximate.
#   italian-humanist  Latin in northern Italy in the 1480s (Pico): Italian vowels, soft c = ch,
#                     soft g = j, gn = ny, sc before e and i = sh, ti before a vowel = tsi, h
#                     silent, s between vowels = z (a northern trait). Close to the later
#                     ecclesiastical reading, which descends from it. Approximate.

HUMANIST = {"low-countries": "dutch", "tudor-english": "tudor", "italian-humanist": "italian"}

_NL_LONG = {"a": ("aː", "aa"), "e": ("eː", "ay"), "i": ("iː", "ee"), "y": ("iː", "ee"), "o": ("oː", "oh"),
            "u": ("yː", "üü"), "ae": ("eː", "ay"), "oe": ("eː", "ay"), "au": ("ɑu", "ow")}
_NL_SHORT = {"a": ("ɑ", "a"), "e": ("ɛ", "e"), "i": ("ɪ", "i"), "y": ("ɪ", "i"), "o": ("ɔ", "o"),
             "u": ("ʏ", "ü"), "ae": ("eː", "ay"), "oe": ("eː", "ay"), "au": ("ɑu", "ow")}
_TU_LONG = {"a": ("aː", "aa"), "e": ("iː", "ee"), "i": ("əi", "ei"), "y": ("əi", "ei"), "o": ("ɔː", "aw"),
            "u": ("iu", "yoo"), "ae": ("iː", "ee"), "oe": ("iː", "ee"), "au": ("au", "ow")}
_TU_SHORT = {"a": ("a", "a"), "e": ("ɛ", "e"), "i": ("ɪ", "i"), "y": ("ɪ", "i"), "o": ("ɔ", "o"),
             "u": ("ʊ", "u"), "ae": ("iː", "ee"), "oe": ("iː", "ee"), "au": ("au", "ow")}
_TU_FINAL = {"a": ("a", "a"), "e": ("iː", "ee"), "i": ("əi", "ei"), "y": ("əi", "ei"), "o": ("ɔː", "aw"), "u": ("iu", "yoo")}
_IT_V = {"a": ("a", "a"), "e": ("e", "e"), "i": ("i", "ee"), "y": ("i", "ee"), "o": ("o", "o"),
         "u": ("u", "oo"), "ae": ("ɛ", "e"), "oe": ("ɛ", "e"), "au": ("au", "ow")}


def _humanist(syls: list[Syl], stress: int, dialect: str) -> list[tuple[str, str]]:
    """(ipa, respell) per syllable for the dutch, tudor and italian readings."""
    flat: list[tuple[int, Seg]] = []
    for n, s in enumerate(syls):
        for seg in s.onset + [s.nucleus] + s.coda:
            flat.append((n, seg))
    ipa = [""] * len(syls)
    sp = [""] * len(syls)
    last = len(syls) - 1

    def front(seg: Seg | None) -> bool:
        return seg is not None and seg.vowel and (seg.text[0] in "eiy" or seg.text in ("ae", "oe"))

    for k, (n, seg) in enumerate(flat):
        nxt = flat[k + 1][1] if k + 1 < len(flat) else None
        nxt2 = flat[k + 2][1] if k + 2 < len(flat) else None
        prev = flat[k - 1][1] if k > 0 else None
        t = seg.text
        if seg.vowel:
            syl = syls[n]
            open_ = not syl.coda
            if dialect == "dutch":
                a, b = (_NL_LONG if open_ else _NL_SHORT).get(t, (t, t))
            elif dialect == "tudor":
                if n == stress:
                    antepenult = len(syls) >= 3 and stress == len(syls) - 3
                    before_hiatus = (n + 2 < len(syls) and syls[n + 1].nucleus.text in ("i", "e")
                                     and not syls[n + 1].coda and not syls[n + 2].onset)
                    # i stays short here even before hiatus (Fabricius = fa-BRI-si-us)
                    shorten = antepenult and t != "u" and not (before_hiatus and t not in ("i", "y"))
                    table = _TU_LONG if open_ and not shorten else _TU_SHORT
                elif n == last and open_:
                    table = _TU_FINAL if t in _TU_FINAL else _TU_SHORT
                elif open_ and t == "u":
                    table = _TU_LONG
                else:
                    table = _TU_SHORT
                if n == last and t == "e" and len(syl.coda) == 1 and syl.coda[0].text == "s":
                    a, b = ("iː", "ee")                    # final -es = eez
                else:
                    a, b = table.get(t, (t, t))
            else:
                a, b = _IT_V.get(t, (t, t))
            ipa[n] += a; sp[n] += b
            continue
        ti = (t == "t" and nxt is not None and nxt.text == "i" and nxt2 is not None and nxt2.vowel and k > 0
              and not (prev is not None and prev.text in ("s", "t", "k")))
        if t == "c" and prev is not None and prev.text == "s" and front(nxt):
            a, b = ("", "")                                # sc before e, i: one sound, written at the s
        elif t == "s" and nxt is not None and nxt.text == "c" and front(nxt2):
            a, b = ("ʃ", "sh") if dialect == "italian" else ("s", "s")
        elif t == "c":
            if front(nxt):
                a, b = ("tʃ", "ch") if dialect == "italian" else ("s", "s")
            else:
                a, b = ("k", "k")
        elif t == "g":
            if dialect == "dutch":
                a, b = ("ɣ", "gh")
            elif dialect == "italian" and nxt is not None and nxt.text == "n":
                a, b = ("", "")                            # gn = ny, written at the n
            elif front(nxt):
                a, b = ("dʒ", "j")
            else:
                a, b = ("ɡ", "g")
        elif t == "n" and dialect == "italian" and prev is not None and prev.text == "g":
            a, b = ("ɲ", "ny")
        elif t == "j":
            a, b = ("dʒ", "j") if dialect == "tudor" else ("j", "y")
        elif t == "qu":
            a, b = ("kw", "kw")
        elif ti:
            a, b = ("s", "s") if dialect == "tudor" else ("ts", "ts")
        elif t == "s" and prev is not None and prev.vowel and nxt is not None and nxt.vowel:
            a, b = ("z", "z")                              # s between vowels is voiced in all three
        elif t == "s" and dialect == "tudor" and nxt is None and prev is not None and prev.text == "e" and n == last:
            a, b = ("z", "z")
        elif t == "h":
            a, b = ("", "") if dialect == "italian" else ("h", "h")
        elif t == "ch":
            a, b = ("x", "kh") if dialect == "dutch" else ("k", "k")
        elif t == "ph":
            a, b = ("f", "f")
        elif t == "th":
            a, b = ("t", "t")
        elif t == "z":
            a, b = ("dz", "dz") if dialect == "italian" else ("z", "z")
        elif t == "n" and nxt is not None and nxt.text in ("c", "g", "qu", "k") and not (dialect == "italian" and nxt.text == "g" and nxt2 is not None and nxt2.text == "n"):
            a, b = ("ŋ", "ng")
        else:
            a, b = (t, t)
        ipa[n] += a; sp[n] += b
    return list(zip(ipa, sp))


def humanist(word: str, dialect: str, quantities: dict[str, str] | None = None) -> dict:
    w = "".join(ch for ch in word if ch not in PUNCT)
    known = False
    if quantities is not None:
        w, known = apply_quantity(w, quantities)
    host_len = None
    if "+" in w:
        host, enc = w.split("+", 1)
        host_len = len(syllabify(host))
        w = host + enc
    syls = syllabify(w)
    if not syls:
        return {"ipa": w, "respell": w, "syllables": 0, "known": known}
    stress = stress_index(syls, host_len)
    parts = _humanist(syls, stress, dialect)
    one = len(syls) == 1
    ipa = ".".join(("ˈ" if j == stress and not one else "") + p[0] for j, p in enumerate(parts))
    resp = "-".join(p[1].upper() if j == stress and not one else p[1] for j, p in enumerate(parts))
    return {"ipa": ipa, "respell": resp, "syllables": len(syls), "known": known}


_phonemize_v01 = phonemize


def phonemize(word: str, scheme: str, quantities: dict[str, str] | None = None, dialect: str | None = None, **kw) -> dict:  # noqa: F811
    """Adds the humanist schemes; every other scheme and dialect goes through unchanged."""
    if scheme in HUMANIST:
        return humanist(word, HUMANIST[scheme], quantities)
    if scheme == "as-first-read" and dialect in HUMANIST.values():
        return humanist(word, dialect, quantities)
    return _phonemize_v01(word, scheme, quantities, dialect=dialect, **kw)


KEY["low-countries"] = [
    ("", "Latin as read in the Low Countries around 1500, Erasmus's own country and generation. Reconstructed from Middle Dutch sound history and the later Dutch school tradition; approximate."),
    ("aa, ay, ee, oh, üü", "a vowel in an open syllable is long: a as in father, e as in they (no glide), i as in machine, o as in go (no glide), u as Dutch uu or French u"),
    ("a, e, i, o, ü", "a vowel in a closed syllable is short; ü is short Dutch u, as in Dutch put"),
    ("ay", "ae and oe are both long e"),
    ("gh", "g is a voiced throat fricative, as in Dutch goed, before every vowel"),
    ("kh", "ch, as in Scottish loch"),
    ("s", "c before e and i"),
    ("ts", "ti before a vowel: gratia = GHRAA-tsee-aa"),
    ("z", "s between vowels"),
    ("y", "consonantal i, as in yes"),
    ("CAPS", "stressed syllable, by the classical penultimate rule"),
]
KEY["tudor-english"] = [
    ("", "Latin as read in England around 1516, Thomas More's generation: the English method at an earlier stage of the Great Vowel Shift than Newton's. Approximate."),
    ("aa, ee, ei, aw, yoo", "a stressed vowel in an open syllable takes its English long value of the time: a as in father, e as in see, i as a glide from uh to ee, o as in law, u as you"),
    ("u", "short u as in put; the vowel of cut came later"),
    ("ee (final e), ei (final i)", "a final e is ee and a final i is ei"),
    ("s", "c before e and i; also ti before a vowel, as si (later sh)"),
    ("j", "g before e and i, and consonantal i, as in judge"),
    ("z", "s between vowels and in final -es, as in English Caesar"),
    ("CAPS", "stressed syllable, by the classical penultimate rule"),
]
KEY["italian-humanist"] = [
    ("", "Latin as read in northern Italy in the 1480s, Pico's country and decade. Close to the later ecclesiastical reading; approximate."),
    ("a e ee o oo", "Italian vowels; length changes the stress, not the quality"),
    ("e", "ae and oe are both e"),
    ("ch", "c before e, i, ae, oe, as in church"),
    ("j", "g before e, i, ae, oe, as in gem"),
    ("sh", "sc before e and i"),
    ("ny", "gn, as in canyon"),
    ("ts", "ti before a vowel: gratia = GRA-tsee-a"),
    ("z", "s between vowels, as in northern Italian rosa"),
    ("(silent)", "h is not sounded: homo = O-mo"),
    ("CAPS", "stressed syllable, by the classical penultimate rule"),
]
SCHEME_LABELS["low-countries"] = "As first read: Latin in the Low Countries around 1500 (approximate)"
SCHEME_LABELS["tudor-english"] = "As first read: Latin in England around 1516 (approximate)"
SCHEME_LABELS["italian-humanist"] = "As first read: Latin in northern Italy in the 1480s (approximate)"


# ---------------------------------------------------------------- German reading, about 1517
# Latin as read in Saxony around 1517 (Luther at Wittenberg). Added as its own scheme, after the
# humanist ones, so that no existing scheme changes. The evidence is indirect: the later German
# school pronunciation of Latin (which kept c = ts, qu = kv, hard g, ti = tsi into the 1800s), the
# sound system of Early New High German (open-syllable lengthening, final devoicing, z = ts, the
# letter v = f), and humanist complaints about German habits of reading, such as Erasmus's in
# De recta pronuntiatione (1528). No description of Luther's own Latin survives. Approximate.
#
#   german-humanist   stressed vowels in open syllables long, all others short (the German
#                     lengthening rule); ae and oe = long e; c before e, i, y, ae, oe = ts, so sc
#                     there = sts; g always hard; qu = kv; consonantal u/v = f (the weakest point:
#                     v or w is also possible); z = ts; ti before a vowel = tsi; s before a vowel at
#                     the start of a word or between vowels = z; final b, d, g devoiced to p, t, k;
#                     h sounded; ch = k, ph = f, th = t. Stress by the classical penultimate rule.
#
# Abbreviations in early prints (.i. for id est, S. for sacrae, R. P. for reverendo patre) are read
# through the quantity table. A work may key the printed form with its punctuation or capital
# (".i", "S"); this lookup applies only when such a key exists, so works without one are unchanged.

_DE_LONG = {"a": ("aː", "aa"), "e": ("eː", "ay"), "i": ("iː", "ee"), "y": ("yː", "üü"), "o": ("oː", "oh"),
            "u": ("uː", "oo"), "ae": ("eː", "ay"), "oe": ("eː", "ay"), "au": ("au", "ow")}
_DE_SHORT = {"a": ("a", "a"), "e": ("ɛ", "e"), "i": ("ɪ", "i"), "y": ("ʏ", "ü"), "o": ("ɔ", "o"),
             "u": ("ʊ", "u"), "ae": ("eː", "ay"), "oe": ("eː", "ay"), "au": ("au", "ow")}
_DE_DEVOICE = {"b": ("p", "p"), "d": ("t", "t"), "g": ("k", "k")}


def _german(syls: list[Syl], stress: int) -> list[tuple[str, str]]:
    """(ipa, respell) per syllable for the German reading of about 1517."""
    flat: list[tuple[int, Seg]] = []
    for n, s in enumerate(syls):
        for seg in s.onset + [s.nucleus] + s.coda:
            flat.append((n, seg))
    ipa = [""] * len(syls)
    sp = [""] * len(syls)

    def front(seg: Seg | None) -> bool:
        return seg is not None and seg.vowel and (seg.text[0] in "eiy" or seg.text in ("ae", "oe"))

    for k, (n, seg) in enumerate(flat):
        nxt = flat[k + 1][1] if k + 1 < len(flat) else None
        nxt2 = flat[k + 2][1] if k + 2 < len(flat) else None
        prev = flat[k - 1][1] if k > 0 else None
        t = seg.text
        if seg.vowel:
            open_ = not syls[n].coda
            a, b = (_DE_LONG if (n == stress and open_) else _DE_SHORT).get(t, (t, t))
            ipa[n] += a; sp[n] += b
            continue
        if t == "c":
            a, b = ("ts", "ts") if front(nxt) else ("k", "k")
        elif t in ("v", "u"):
            a, b = ("f", "f")
        elif t == "qu":
            a, b = ("kv", "kv")
        elif t == "j":
            a, b = ("j", "y")
        elif t == "z":
            a, b = ("ts", "ts")
        elif t == "t" and nxt is not None and nxt.text == "i" and nxt2 is not None and nxt2.vowel and k > 0 \
                and not (prev is not None and prev.text in ("s", "t", "k")):
            a, b = ("ts", "ts")
        elif t == "s" and nxt is not None and nxt.vowel and (prev is None or prev.vowel):
            a, b = ("z", "z")
        elif t in _DE_DEVOICE and nxt is None:
            a, b = _DE_DEVOICE[t]
        elif t == "g":
            a, b = ("ɡ", "g")
        elif t == "ch":
            a, b = ("k", "k")
        elif t == "ph":
            a, b = ("f", "f")
        elif t == "th":
            a, b = ("t", "t")
        elif t == "n" and nxt is not None and nxt.text in ("c", "g", "qu", "k"):
            a, b = ("ŋ", "ng")
        else:
            a, b = (t, t)
        ipa[n] += a; sp[n] += b
    return list(zip(ipa, sp))


def german(word: str, quantities: dict[str, str] | None = None) -> dict:
    w = "".join(ch for ch in word if ch not in PUNCT)
    known = False
    if quantities is not None:
        w, known = apply_quantity(w, quantities)
    host_len = None
    if "+" in w:
        host, enc = w.split("+", 1)
        host_len = len(syllabify(host))
        w = host + enc
    syls = syllabify(w)
    if not syls:
        return {"ipa": w, "respell": w, "syllables": 0, "known": known}
    stress = stress_index(syls, host_len)
    parts = _german(syls, stress)
    one = len(syls) == 1
    ipa = ".".join(("ˈ" if j == stress and not one else "") + p[0] for j, p in enumerate(parts))
    resp = "-".join(p[1].upper() if j == stress and not one else p[1] for j, p in enumerate(parts))
    return {"ipa": ipa, "respell": resp, "syllables": len(syls), "known": known}


def _printed_key(word: str, quantities: dict[str, str] | None):
    """A table may key an abbreviation as printed (".i", "S", "XII"). Only such keys change the
    lookup: the entry is moved under the plain form for this one word."""
    if not quantities:
        return quantities
    plain = "".join(ch for ch in word if ch not in PUNCT).lower()
    for raw in (word, word.lower()):
        if raw != plain and raw in quantities:
            from collections import ChainMap
            return ChainMap({plain: quantities[raw]}, quantities)
    return quantities


_phonemize_v02 = phonemize


def phonemize(word: str, scheme: str, quantities: dict[str, str] | None = None, dialect: str | None = None, **kw) -> dict:  # noqa: F811
    """Adds the German reading and printed-form abbreviation keys; everything else unchanged."""
    quantities = _printed_key(word, quantities)
    if scheme == "german-humanist" or (scheme == "as-first-read" and dialect == "german"):
        return german(word, quantities)
    return _phonemize_v02(word, scheme, quantities, dialect=dialect, **kw)


KEY["german-humanist"] = [
    ("", "Latin as read in Saxony around 1517, Luther's country and decade. Reconstructed from the later German school pronunciation of Latin and from the sound history of Early New High German; no description of Luther's own Latin survives. Approximate."),
    ("aa, ay, ee, oh, oo", "a stressed vowel in an open syllable is long: a as in father, e as in they (no glide), i as in machine, o as in go (no glide), u as in food"),
    ("a, e, i, o, u", "every other vowel is short: u as in put"),
    ("ay", "ae and oe are both long e; the prints often write plain e (pena for poena)"),
    ("ts", "c before e, i, y, ae, oe, as in German Zeit: Cicero = TSEE-tse-ro; also z, and ti before a vowel (gratia = GRAA-tsi-a)"),
    ("sts", "sc before e and i: scilicet = stsi-LI-tset"),
    ("g", "g is always hard, as in get, even before e and i"),
    ("kv", "qu, as in German Quelle"),
    ("f", "consonantal u or v, as German v in Vater: vita = FEE-ta. The least certain point: v or w is also possible"),
    ("z", "s before a vowel at the start of a word or between vowels, as in German Sonne"),
    ("t, p, k (final)", "final d, b, g lose their voice, as in German: ad = at, quod = kvot"),
    ("ü", "y, as in German über"),
    ("CAPS", "stressed syllable, by the classical penultimate rule"),
]
SCHEME_LABELS["german-humanist"] = "As first read: Latin in Saxony around 1517 (approximate)"


# ---------------------------------------------------------------- Norman reading, about 1070
# Latin as a cleric trained in Normandy, or in England after 1066, most likely read it around
# 1070 (the captions of the Bayeux Tapestry). Added as its own scheme, after all the others, so no
# existing scheme changes. The evidence is indirect and later than the text in several places:
#
#   - Old French sound history. Latin c before e and i had become [ts] in French (cent, cire),
#     and g before e and i, with consonantal i, had become [dʒ] (gent, jeune); both kept those
#     values until the 1200s, when they simplified to [s] and [ʒ]. Clerks are assumed to have read
#     Latin letters with the values the same letters had in their French (Roger Wright's argument
#     that Latin was read aloud in the vernacular manner until the Carolingian reform, and that
#     the reform restored one sound per letter but not Roman values).
#   - Anglo-Norman and Old French spelling, which write ce/ci for [ts] and g/j for [dʒ], drop
#     Latin h (ome, ore), and write e for Latin ae and oe; the captions themselves write
#     PRELIUM and EDIFICARE for proelium and aedificare.
#   - Later descriptions of French reading of Latin (the French method of the 1500s to 1800s,
#     W. S. Allen, Vox Latina, appendix), which keeps soft c as s, soft g as zh, u as French u,
#     and final stress. Of these only u as [y] is projected back here: French had fronted Latin u
#     to [y] well before 1066, so a French-speaking reader most likely said [y] in Latin too.
#     Final stress is not projected back: rhythmic Latin verse and the cursus of 11th-century
#     prose still depend on the Latin penultimate accent, so clerks of this date kept it.
#
#   anglo-norman   c before e, i, y, ae, oe = ts; g there and the letter j = dʒ; h silent;
#                  consonantal u/v = v; w (VV on the tapestry) = w; qu = kw; ti before a vowel
#                  = tsi; s between vowels = z; ae and oe = e; u = y (French u); length is not
#                  heard, only stress; ch = k, ph = f, th = t, x = ks, ð (Old English) = ð.
#                  Stress by the classical penultimate rule.
#
# Weakest points: u as [y] (some scholars date the fronting later or doubt it carried over to
# Latin); h, which Norman French kept in Germanic words (hache, haste), so Harold may have
# kept his h; and whether qu was still [kw]. Names (Harold, Willelm, Bagias, Pevenese, Hestinga)
# are read as written, through the same rules.

_NOR_V = {"a": ("a", "a"), "e": ("ɛ", "e"), "i": ("i", "ee"), "y": ("i", "ee"), "o": ("ɔ", "o"),
          "u": ("y", "ü"), "ae": ("ɛ", "e"), "oe": ("ɛ", "e"), "au": ("au", "ow")}


def _norman(syls: list[Syl]) -> list[tuple[str, str]]:
    """(ipa, respell) per syllable for the Norman reading of about 1070."""
    flat: list[tuple[int, Seg]] = []
    for n, s in enumerate(syls):
        for seg in s.onset + [s.nucleus] + s.coda:
            flat.append((n, seg))
    ipa = [""] * len(syls)
    sp = [""] * len(syls)

    def front(seg: Seg | None) -> bool:
        return seg is not None and seg.vowel and (seg.text[0] in "eiy" or seg.text in ("ae", "oe"))

    for k, (n, seg) in enumerate(flat):
        nxt = flat[k + 1][1] if k + 1 < len(flat) else None
        nxt2 = flat[k + 2][1] if k + 2 < len(flat) else None
        prev = flat[k - 1][1] if k > 0 else None
        t = seg.text
        if seg.vowel:
            a, b = _NOR_V.get(t, (t, t))
            ipa[n] += a; sp[n] += b
            continue
        if t == "c":
            a, b = ("ts", "ts") if front(nxt) else ("k", "k")
        elif t == "g":
            a, b = ("dʒ", "j") if front(nxt) else ("ɡ", "g")
        elif t == "j":
            a, b = ("dʒ", "j")
        elif t == "qu":
            a, b = ("kw", "kw")
        elif t == "t" and nxt is not None and nxt.text == "i" and nxt2 is not None and nxt2.vowel and k > 0 \
                and not (prev is not None and prev.text in ("s", "t", "k")):
            a, b = ("ts", "ts")
        elif t == "s" and prev is not None and prev.vowel and nxt is not None and nxt.vowel:
            a, b = ("z", "z")
        elif t == "h":
            a, b = ("", "")
        elif t in ("ch", "k"):
            a, b = ("k", "k")
        elif t == "ph":
            a, b = ("f", "f")
        elif t == "th":
            a, b = ("t", "t")
        elif t == "ð":
            a, b = ("ð", "dh")
        elif t == "z":
            a, b = ("dz", "dz")
        elif t == "n" and nxt is not None and nxt.text in ("c", "g", "qu", "k"):
            a, b = ("ŋ", "ng")
        else:
            a, b = (t, t)
        ipa[n] += a; sp[n] += b
    return list(zip(ipa, sp))


def norman(word: str, quantities: dict[str, str] | None = None) -> dict:
    w = "".join(ch for ch in word if ch not in PUNCT)
    known = False
    if quantities is not None:
        w, known = apply_quantity(w, quantities)
    host_len = None
    if "+" in w:
        host, enc = w.split("+", 1)
        host_len = len(syllabify(host))
        w = host + enc
    syls = syllabify(w)
    if not syls:
        return {"ipa": w, "respell": w, "syllables": 0, "known": known}
    stress = stress_index(syls, host_len)
    parts = _norman(syls)
    one = len(syls) == 1
    ipa = ".".join(("ˈ" if j == stress and not one else "") + p[0] for j, p in enumerate(parts))
    resp = "-".join(p[1].upper() if j == stress and not one else p[1] for j, p in enumerate(parts))
    return {"ipa": ipa, "respell": resp, "syllables": len(syls), "known": known}


_phonemize_v03 = phonemize


def phonemize(word: str, scheme: str, quantities: dict[str, str] | None = None, dialect: str | None = None, **kw) -> dict:  # noqa: F811
    """Adds the Norman reading of about 1070; every other scheme goes through unchanged."""
    if scheme == "anglo-norman" or (scheme == "as-first-read" and dialect == "norman"):
        return norman(word, _printed_key(word, quantities))
    return _phonemize_v03(word, scheme, quantities, dialect=dialect, **kw)


KEY["anglo-norman"] = [
    ("", "Latin as a cleric trained in Normandy, or in England after 1066, most likely read it around 1070. Reconstructed from Old French and Anglo-Norman sound history and spelling, and from later accounts of French reading of Latin; no description of the period survives. Approximate."),
    ("a e ee o", "plain vowels; long and short no longer differ in sound, only in where the stress falls"),
    ("ü", "u, as in French tu: the French fronting of Latin u, assumed to carry over into Latin. The least certain point; oo is also possible"),
    ("e", "ae and oe are both e; the captions themselves write PRELIUM and EDIFICARE"),
    ("ts", "c before e and i, as in bits: Old French cent was tsent until the 1200s; also ti before a vowel"),
    ("j", "g before e and i, and the letter j, as in judge: Old French gent was jent"),
    ("(silent)", "h is not sounded: hic = eek. Norman French kept h in Germanic words, so Harold may have kept his"),
    ("v, w", "v as in English; w (written VV on the tapestry) as in English"),
    ("z", "s between vowels, as in French rose"),
    ("dh", "ð, the Old English letter in GYRÐ, as th in this"),
    ("CAPS", "stressed syllable, by the classical penultimate rule, which clerks of this date still kept"),
]
SCHEME_LABELS["anglo-norman"] = "As first read: Latin in Normandy and Norman England around 1070 (approximate)"
