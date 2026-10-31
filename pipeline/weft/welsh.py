"""Middle Welsh (12th and 13th centuries, the language of the manuscripts) from a normalized spelling.

Evidence. The values follow D. Simon Evans, A Grammar of Middle Welsh (1964), the introduction on
orthography and sounds, and John Morris-Jones, A Welsh Grammar (1913), on the sounds of the medieval
language: the stress on the last syllable but one (fixed by the 11th century); y clear (ɨ) in a final
syllable and obscure (ə) before it; ll the voiceless lateral ɬ; ch x; dd ð; f v; ff f; the nasal
mutation written out (ngh, mh, nh are voiceless). The manuscripts write these sounds inconsistently:
u and v for /v/, d for both d and ð, t for d, c for g, u for w, and in the oldest spellings gu for gw
and i for y. So the sound is read from a normalized spelling in each token's n field, written in the
letters of modern Welsh, which the rules read one way each:

n      the word in modern Welsh letters, keeping the medieval form of the word (its vowels and
       endings): dd for ð, f for v, ff for f, w for the vowel and the glide, and the mutations as
       modern spelling writes them (ngh, mh, nh, ch, ph, th). A circumflex marks a long vowel where
       the rules need it (gŵr); a hyphen joins a proclitic to the word it leans on (yng-nghad,
       a-thi), which keeps its own stress and vowels; a proclitic y, yn, yng, fy, dy is ə.

Rules. w is the consonant w before a vowel at the start of a word, after g, and between vowels;
otherwise the vowel u. i is the consonant j before a vowel at the start of a word. y is ɨ in the
last syllable of a word and ə before it; the proclitics y, yr, yn, fy, dy, ym, ys are ə. u is ʉ, a
close rounded vowel still distinct from clear y in this period. Vowel length is not modeled except
where the circumflex marks it.

Where it is weakest. The value of u and of the diphthongs written au and eu, which changed between
the 12th and the 14th centuries; vowel length; and the composition of the oldest poems (the
Gododdin, set around 600) in a language older than the manuscripts', with the stress on the final
syllable. The scheme reads the manuscripts' Welsh, not the poets'.
"""
from __future__ import annotations

import re
import unicodedata as ud

VERSION = "0.1"
SHOW_TRANSLIT = True
TRANSLIT_LABEL = "Normalized spelling"
WANTS_TOKEN = True

LEAD_P = re.compile(r"^([„“(\[«‹\"'‘—–]+)")
TRAIL_P = re.compile(r"((?:[,.;:!?)\]”’»›\"…]|–|—)+)$")

CIRC = {"â": "a", "ê": "e", "î": "i", "ô": "o", "û": "u", "ŵ": "w", "ŷ": "y"}
VOWELS = set("aeiouwy") | set(CIRC)
PROCLITIC_Y = {"y", "yr", "yn", "fy", "dy", "ym", "ys", "yng", "ydd", "yd"}
# digraph consonants, longest first
CONS = ["ngh", "ng", "mh", "nh", "rh", "ch", "dd", "ff", "ll", "ph", "th",
        "b", "c", "d", "f", "g", "h", "j", "k", "l", "m", "n", "p", "r", "s", "t", "v"]
CONS_IPA = {"ngh": "ŋ̊", "ng": "ŋ", "mh": "m̊", "nh": "n̥", "rh": "r̥", "ch": "x", "dd": "ð", "ff": "f", "ll": "ɬ",
            "ph": "f", "th": "θ", "b": "b", "c": "k", "d": "d", "f": "v", "g": "ɡ", "h": "h", "j": "dʒ", "k": "k",
            "l": "l", "m": "m", "n": "n", "p": "p", "r": "r", "s": "s", "t": "t", "v": "v"}
# falling diphthongs: the second letter is a glide
DIPH = {"ae": "ai̯", "ai": "ai̯", "au": "au̯", "aw": "au̯", "ei": "əi̯", "eu": "əɨ̯", "ey": "əɨ̯", "ew": "eu̯",
        "iw": "iu̯", "oe": "oi̯", "oi": "oi̯", "ou": "oɨ̯", "ow": "ou̯", "uw": "ʉu̯", "wy": "ui̯", "yw": "ɨu̯"}
SHORT = {"a": "a", "e": "e", "i": "i", "o": "o", "u": "ʉ", "w": "u"}


def _units(word: str) -> list[tuple[str, str]]:
    """A word -> [('C', unit) | ('V', letter) | ('-', '-')], with w and i as consonants where they are."""
    w = ud.normalize("NFC", word.lower())
    out: list[tuple[str, str]] = []
    i = 0
    while i < len(w):
        ch = w[i]
        if ch == "-":
            out.append(("-", "-")); i += 1; continue
        if ch in VOWELS:
            nxt = w[i + 1] if i + 1 < len(w) else ""
            start = not out or out[-1][0] == "-"
            after_g = bool(out) and out[-1] in (("C", "g"), ("C", "ng"))
            between = bool(out) and out[-1][0] == "V" and nxt in VOWELS
            if ch == "w" and nxt in VOWELS and nxt != "w" and (start or after_g or between):
                out.append(("C", "w")); i += 1; continue
            if ch == "i" and nxt in VOWELS and start:
                out.append(("C", "i")); i += 1; continue
            out.append(("V", ch)); i += 1; continue
        for c in CONS:
            if w.startswith(c, i):
                out.append(("C", c)); i += len(c); break
        else:
            i += 1                                          # apostrophes and anything else
    return out


def _nuclei(units: list[tuple[str, str]]) -> list[tuple[int, int, str]]:
    """Vowel runs -> (start index, end index, IPA), splitting a run into diphthong-sized nuclei."""
    out = []
    k = 0
    while k < len(units):
        if units[k][0] != "V":
            k += 1; continue
        j = k
        while j < len(units) and units[j][0] == "V":
            j += 1
        p = k
        while p < j:
            pair = (units[p][1] + units[p + 1][1]) if p + 1 < j else ""
            base = "".join(CIRC.get(c, c) for c in pair)
            if pair and base in DIPH and not (base == "wy" and p + 2 < j):
                out.append((p, p + 2, DIPH[base])); p += 2
            else:
                c = units[p][1]
                long_ = c in CIRC
                b = CIRC.get(c, c)
                v = "y" if b == "y" else SHORT[b]
                out.append((p, p + 1, v + ("ː" if long_ else ""))); p += 1
        k = j
    return out


def word_sound(word: str) -> tuple[list[str], int]:
    """A normalized word -> (IPA syllables, the stressed one marked; index of the stressed syllable)."""
    units = _units(word)
    nuc = _nuclei(units)
    if not nuc:
        return ["".join(CONS_IPA.get(u, u) for _, u in units)], 0
    # clear y in the last syllable of each part
    parts_end = [i for i, u in enumerate(units) if u[0] == "-"] + [len(units)]
    # a hyphen joins a proclitic to the word it leans on (yng-nghad, a-thi): the stress is the last
    # part's own, on its last syllable but one, or on its one syllable
    last_part = [k for k, (a_, _, _) in enumerate(nuc) if a_ > (parts_end[-2] if len(parts_end) > 1 else -1)]
    if len(last_part) > 1:
        stress = last_part[-2]
    elif last_part:
        stress = last_part[0]
    else:
        stress = len(nuc) - 2 if len(nuc) > 1 else 0
    plain = ud.normalize("NFC", word.lower()).strip("-")
    sylls: list[str] = []
    for n, (a, b, v) in enumerate(nuc):
        if v == "y":
            end_of_part = next(e for e in parts_end if e >= b)
            last_in_part = not any(a2 >= b and b2 <= end_of_part for a2, b2, _ in nuc[n + 1:])
            starts = [-1] + parts_end[:-1]
            part = next(i for i, e in enumerate(parts_end) if e >= b)
            part_text = "".join(u[1] for u in units[starts[part] + 1:parts_end[part]])
            v = "ə" if (plain in PROCLITIC_Y or part_text in PROCLITIC_Y or not last_in_part) else "ɨ"
        elif v == "yː":
            v = "ɨː"
        sylls.append(v)
    # consonants: an intervocalic single consonant opens the next syllable; a cluster splits after its first
    onsets = [""] * len(nuc)
    codas = [""] * len(nuc)
    prev_end = 0
    for n, (a, b, _) in enumerate(nuc):
        cl = [u for u in units[prev_end:a] if u[0] != "-"]
        hy = any(u[0] == "-" for u in units[prev_end:a])
        ipa = ["w" if u == "w" else "j" if u == "i" else CONS_IPA[u] for _, u in cl]
        if n == 0:
            onsets[0] = "".join(ipa)
        elif hy:
            before = [u for u in units[prev_end:a]]
            cut = next(i for i, u in enumerate(before) if u[0] == "-")
            left = [x for x in before[:cut]]
            right = [x for x in before[cut + 1:]]
            codas[n - 1] += "".join("w" if u == "w" else CONS_IPA[u] for _, u in left)
            onsets[n] = "".join("w" if u == "w" else "j" if u == "i" else CONS_IPA[u] for _, u in right)
        elif len(ipa) <= 1:
            onsets[n] = "".join(ipa)
        else:
            codas[n - 1] += ipa[0]
            onsets[n] = "".join(ipa[1:])
        prev_end = b
    tail = [u for u in units[prev_end:] if u[0] == "C"]
    codas[-1] += "".join("w" if u == "w" else CONS_IPA[u] for _, u in tail)
    out = []
    for n in range(len(nuc)):
        s = onsets[n] + sylls[n] + codas[n]
        out.append(("ˈ" if n == stress and len(nuc) > 1 else "") + s)
    return out, stress


RESPELL = [("ai̯", "ai"), ("au̯", "ow"), ("əi̯", "uy"), ("əɨ̯", "uy"), ("eu̯", "eu"), ("iu̯", "iw"), ("oi̯", "oy"),
           ("oɨ̯", "oih"), ("ou̯", "oh"), ("ʉu̯", "üw"), ("ui̯", "ooy"), ("ɨu̯", "ihw"),
           ("ŋ̊", "ngh"), ("m̊", "mh"), ("n̥", "nh"), ("r̥", "rh"), ("ɬ", "hl"), ("x", "kh"), ("ð", "dh"), ("θ", "th"),
           ("ŋ", "ng"), ("ɡ", "g"), ("dʒ", "j"), ("ɨː", "ihh"), ("ɨ", "ih"), ("ʉ", "ü"), ("ə", "uh"),
           ("aː", "aa"), ("eː", "ay"), ("iː", "ee"), ("oː", "oh"), ("uː", "oo"), ("u", "oo"), ("j", "y"), ("ː", "")]


def _respell(ipa: str) -> str:
    out, i = [], 0
    while i < len(ipa):
        for a, b in RESPELL:
            if ipa.startswith(a, i):
                out.append(b); i += len(a); break
        else:
            out.append(ipa[i]); i += 1
    return "".join(out)


def token_fields(surface: str, et: dict, group: dict) -> tuple[dict, list[tuple[str, str]]]:
    """Split punctuation off the printed word; every word needs its normalized spelling."""
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
        fails.append(("normalized-spelling-missing", surface))
    return fields, fails


def phonemize(word: str, scheme: str = "middle-welsh", quantities=None, etok: dict | None = None, **_) -> dict:
    ov = (etok.get("ipa") or {}).get(scheme) if etok else None
    if ov:
        return {"ipa": ov, "respell": _respell(ov.replace("ˈ", "")), "syllables": len(ov.split("."))}
    ipas, rss, n = [], [], 0
    for p in [p for p in re.split(r"\s+", word.strip()) if p]:
        sylls, stress = word_sound(p)
        ipas.append(".".join(sylls))
        rs = [_respell(s.replace("ˈ", "")) for s in sylls]
        if len(rs) > 1:
            rs[stress] = rs[stress].upper()
        rss.append("-".join(rs))
        n += len(sylls)
    return {"ipa": " ".join(ipas), "respell": " ".join(rss), "syllables": n}


SCHEME_LABELS = {"middle-welsh": "Middle Welsh of the 12th and 13th centuries, the language of the manuscripts (approximate)"}

KEY = {
    "middle-welsh": [
        ("", "Welsh as it was most likely spoken when the manuscripts were written, in the 12th and 13th centuries, after D. Simon Evans's Grammar of Middle Welsh and Morris-Jones's Welsh Grammar. The sound is read from the normalized spelling under the text. The oldest poems were composed centuries earlier, in a language with the stress on the last syllable; this is the manuscripts' Welsh, and approximate."),
        ("CAPS", "the stressed syllable: the last but one"),
        ("a e i o", "short vowels; length is not shown except where the spelling marks it (gŵr)"),
        ("oo", "w as a vowel (gŵr, cwm)"),
        ("ih", "clear y, in the last syllable of a word: a close central vowel (dyn)"),
        ("uh", "obscure y, before the last syllable (yn, cyfeillt)"),
        ("ü", "u, a close rounded vowel, not yet merged with clear y"),
        ("hl", "ll, the voiceless l of modern Welsh (Llywarch)"),
        ("kh", "ch, as in Scots loch"),
        ("dh, th", "dd as in this; th as in thin"),
        ("v, f", "f is v; ff and ph are f"),
        ("ngh, mh, nh, rh", "voiceless ng, m, n, r: the nasal mutation and initial rh"),
        ("ow, oy, ooy, ai, uy", "the diphthongs aw/au, oe, wy, ae/ai, and ei/eu (an obscure vowel gliding to i)"),
        ("Normalized spelling", "the row under the text: the manuscript's words in modern Welsh letters, so that each letter has one value; the words' medieval forms are kept"),
    ],
}
