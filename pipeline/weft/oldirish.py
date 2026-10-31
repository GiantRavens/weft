"""Old Irish (about 800-850) from a normalized spelling -> syllables -> sound.

Evidence. The consonant and vowel values follow the standard reconstruction of Old Irish as set out
in Rudolf Thurneysen, A Grammar of Old Irish (1946), sections 15-200, and in David Stifter,
Sengoídelc: Old Irish for Beginners (2006), lessons 2-4: every consonant is either broad (velarized)
or slender (palatalized); after a vowel, single c p t are the voiced stops g b d, and single b d g m
are the fricatives β ð ɣ and nasal β̃; ch th ph are x θ f; initial l n r and doubled ll nn rr are
the strong (fortis) sounds, written L N R; stress falls on the first syllable of the word, or of the
part after a pretonic preverb. Unstressed short vowels are reduced to ə (Thurneysen 101-108).

Old Irish spelling does not show everything the sound needs. Lenition of initial b d g m and of l n
r, nasalization of a vowel, and the place of the stress in a compound verb are not written, and a
manuscript divides words by stress groups, not by words. So the sound is read from a normalized
spelling in the edition's n field, written in the notation of modern editions with three additions
that the rules read:

n      the word normalized: long vowels with the acute (á é í ó ú); a dot over b d g m s f marks
       lenition the manuscript does not show (ḃ ḋ ġ ṁ ṡ ḟ; ṡ is h, ḟ is silent); n- before a word
       marks nasalization (n-dorad, a n-glé); a middle dot marks the end of a pretonic preverb
       (do·tuit, stress on tuit); a hyphen joins an enclitic (menma-sam), which is unstressed.
       A prothetic h (huaraib) is not sounded and is left out of n. A diaeresis on the second of
       two vowels marks a hiatus, two syllables (ru·biäm), where the letters would otherwise be read
       as a diphthong.

Consonant quality comes from the vowel letters, as the spelling marks it: a consonant group before
e, é, i, í is slender; at the end of a word, or before another consonant, a group is slender when
the vowel before it ends in i (the glide i of ai, oi, ui, ái). A leading e or i before a back vowel
(ea, iu) marks the consonant before it slender and is not sounded.

Where it is weakest. The quality of a consonant after e (cen, fer) and the value of unstressed
final vowels are the least certain parts; so is the date at which nd and mb became n and m (taken
here as complete: nd is N). The reduction of all unstressed short vowels to ə flattens distinctions
that Old Irish spelling still keeps in the 9th century.
"""
from __future__ import annotations

import re
import unicodedata as ud

VERSION = "0.1"
SHOW_TRANSLIT = True
TRANSLIT_LABEL = "Normalized spelling"
WANTS_TOKEN = True

LEAD_P = re.compile(r"^([„“(\[«‹\"'‘—–]+)")
TRAIL_P = re.compile(r"((?:[,.;:!?)\]”’»›\"…·]|–|—)+)$")

ACUTE = "́"
DOT = "̇"
SHORT = set("aeiou")
LONG = {"á": "a", "é": "e", "í": "i", "ó": "o", "ú": "u"}
FRONT = set("eiéí")
BACK = set("aouáóú")
HIATUS = {"ä": "a", "ë": "e", "ï": "i", "ö": "o", "ü": "u"}   # a diaeresis begins a new syllable (biäm)
VOWEL_LETTERS = SHORT | set(LONG) | set(HIATUS)
# diphthongs, written with or without the acute on their first vowel
DIPH = {"ae": "ai̯", "áe": "ai̯", "oe": "ai̯", "óe": "ai̯", "ia": "iə", "ía": "iə", "ua": "uə", "úa": "uə",
        "au": "au̯", "áu": "au̯", "eu": "eu̯", "éu": "eu̯", "íu": "iu̯"}
# consonant units, longest first; a dotted letter is one unit (lenited)
UNITS = ["ch", "th", "ph", "cc", "tt", "pp", "bb", "dd", "gg", "ll", "nn", "rr", "mm", "ss", "nd", "ng", "mb",
         "ḃ", "ḋ", "ġ", "ṁ", "ṡ", "ḟ", "b", "c", "d", "f", "g", "h", "l", "m", "n", "p", "r", "s", "t"]
LENITED = {"b": "β", "d": "ð", "g": "ɣ", "m": "β̃"}
FORTIS = {"l": "L", "n": "N", "r": "R"}
ECLIPSE = {"b": "m", "d": "n", "g": "ŋ", "c": "g", "t": "d", "p": "b", "f": "β"}


def _nfc(s: str) -> str:
    return ud.normalize("NFC", s)


def _letters(word: str) -> str:
    """NFC, lower case, with the dotted letters kept as single characters."""
    w = _nfc(word.lower())
    return "".join(ch for ch in w if ch.isalpha() or ch in "·-" or ch in "ḃḋġṁṡḟ")


def _vowel_parse(v: str) -> tuple[str, bool, bool]:
    """A written vowel group -> (nucleus IPA, consonant before is slender, consonant after is slender)."""
    if v in DIPH:
        return DIPH[v], v[0] in "ií", False
    lead = trail = False
    if len(v) > 1 and v[0] in "ei" and v[1] in BACK:       # ea, iu, io: a glide marking quality
        lead, v = True, v[1:]
    if len(v) > 1 and v[-1] == "i":                        # ai, oi, ui, ái, ei: the glide i
        trail, v = True, v[:-1]
    if v in DIPH:
        return DIPH[v], lead, trail
    v = v[0] if len(v) > 1 and v[0] in LONG else v[-1] if len(v) > 1 else v
    ipa = LONG[v] + "ː" if v in LONG else v
    return ipa, lead or v in FRONT, trail or v in "ií"


def _units(cons: str) -> list[str]:
    out, i = [], 0
    while i < len(cons):
        for u in UNITS:
            if cons.startswith(u, i):
                out.append(u); i += len(u); break
        else:
            out.append(cons[i]); i += 1
    return out


def _cons(units: list[str], initial: bool, after_vowel: bool, slender: bool, eclipsed: bool) -> list[str]:
    """IPA for one consonant group. initial: begins a word or the stressed part; after_vowel: a vowel
    precedes in the same word."""
    out: list[str] = []
    for k, u in enumerate(units):
        first = k == 0
        prev = units[k - 1] if k else None
        postvoc = first and after_vowel and not initial
        after_liquid = prev in ("l", "r")
        if first and initial and eclipsed:
            if u in ECLIPSE:
                out.append(ECLIPSE[u] + ("ʲ" if slender else "")); continue
            if u in FORTIS or u in ("m", "s"):
                out.append(FORTIS.get(u, u) + ("ʲ" if slender else "")); continue
        if u == "h":
            continue                                       # prothetic or orthographic h: not sounded
        if u in ("ch", "th", "ph"):
            p = {"ch": "x", "th": "θ", "ph": "f"}[u]
        elif u in ("cc", "tt", "pp", "bb", "dd", "gg", "mm", "ss"):
            p = {"cc": "k", "tt": "t", "pp": "p", "bb": "b", "dd": "d", "gg": "ɡ", "mm": "m", "ss": "s"}[u]
        elif u in ("ll", "nn", "rr"):
            p = FORTIS[u[0]]
        elif u == "nd":
            p = "N"
        elif u == "mb":
            p = "m"
        elif u == "ng":
            p = "ŋɡ"
        elif u in "ḃḋġṁ":
            p = LENITED[ud.normalize("NFD", u)[0]]
        elif u == "ṡ":
            p = "h"
        elif u == "ḟ":
            continue                                       # lenited f is silent
        elif u in ("c", "t", "p"):
            p = ({"c": "ɡ", "t": "d", "p": "b"}[u] if postvoc else {"c": "k", "t": "t", "p": "p"}[u])
        elif u in ("b", "d", "g", "m"):
            p = LENITED[u] if (postvoc or after_liquid) else {"g": "ɡ"}.get(u, u)
        elif u in FORTIS:
            p = FORTIS[u] if (first and initial) else u
        else:
            p = u
        out.append(p + ("ʲ" if slender else ""))
    return out


def _parse(word: str) -> list[tuple[str, str]]:
    """Split into ('C', letters) and ('V', letters) runs, keeping '·' and '-' as markers."""
    runs: list[tuple[str, str]] = []
    for ch in word:
        kind = "V" if ch in VOWEL_LETTERS else "M" if ch in "·-" else "C"
        if ch in HIATUS:
            runs.append(("V", HIATUS[ch]))
        elif runs and runs[-1][0] == kind and kind != "M":
            runs[-1] = (kind, runs[-1][1] + ch)
        else:
            runs.append((kind, ch))
    return runs


def word_sound(word: str) -> tuple[list[str], int]:
    """A normalized word -> (IPA syllables with the stress mark on the stressed one, stressed index)."""
    w = _letters(word)
    eclipsed = False
    if w.startswith("n-"):
        eclipsed, w = True, w[2:]
    w = w.lstrip("h") if w[:1] == "h" and len(w) > 1 and w[1] in VOWEL_LETTERS else w
    runs = _parse(w)
    vgroups = [i for i, (k, _) in enumerate(runs) if k == "V"]
    stress_v = 0
    if "·" in w:
        pre = w.split("·")[0]
        stress_v = sum(1 for k, _ in _parse(pre) if k == "V")
    clitic_from = None
    if "-" in w:
        clitic_from = sum(1 for k, _ in _parse(w.split("-")[0]) if k == "V")
    vinfo = {i: _vowel_parse(runs[i][1]) for i in vgroups}
    sylls: list[list[str]] = [[] for _ in vgroups]
    onset_pending: list[str] = []
    if eclipsed and runs and runs[0][0] == "V":            # nasalization of a vowel: n is sounded before it
        onset_pending = ["n" + ("ʲ" if vinfo[0][1] else "")]
    vi = -1
    for i, (k, s) in enumerate(runs):
        if k == "M":
            continue
        if k == "V":
            vi += 1
            nucleus = vinfo[i][0]
            unstressed = vi != stress_v or (clitic_from is not None and vi >= clitic_from)
            last = vi == len(vgroups) - 1 and not any(kk == "C" for kk, _ in runs[i + 1:])
            if unstressed and "ː" not in nucleus and "̯" not in nucleus and "ə" not in nucleus:
                nucleus = nucleus if (last and nucleus in ("i", "u")) else "ə"
            sylls[vi] = onset_pending + [nucleus]
            onset_pending = []
            continue
        prev_v = next((j for j in range(i - 1, -1, -1) if runs[j][0] == "V"), None)
        next_v = next((j for j in range(i + 1, len(runs)) if runs[j][0] == "V"), None)
        marker_before = i > 0 and runs[i - 1][0] == "M" and runs[i - 1][1] == "·"
        initial = prev_v is None or marker_before
        if next_v is not None:
            slender = vinfo[next_v][1] or (prev_v is not None and vinfo[prev_v][2] and not initial)
        else:
            slender = prev_v is not None and vinfo[prev_v][2]
        ipa = _cons(_units(s), initial, prev_v is not None, slender, eclipsed and prev_v is None)
        if not ipa:
            continue
        before_marker = i + 1 < len(runs) and runs[i + 1][0] == "M"
        if next_v is None or (before_marker and vi >= 0):  # final, or before - and ·: the coda
            if vi >= 0:
                sylls[vi] += ipa
            else:
                onset_pending += ipa
        elif vi < 0 or initial:
            onset_pending += ipa
        elif len(ipa) == 1:
            onset_pending += ipa
        else:
            sylls[vi] += ipa[:1]
            onset_pending += ipa[1:]
    if not vgroups:
        return ["".join(onset_pending)], 0
    out = [("ˈ" if n == stress_v and len(sylls) > 1 else "") + "".join(s) for n, s in enumerate(sylls)]
    return out, stress_v


RESPELL = [("ai̯", "ai"), ("au̯", "ow"), ("eu̯", "eu"), ("iu̯", "iu"), ("iə", "ee-a"), ("uə", "oo-a"),
           ("aː", "aa"), ("eː", "ay"), ("iː", "ee"), ("oː", "oh"), ("uː", "oo"), ("ə", "uh"),
           ("β̃", "v"), ("β", "v"), ("ð", "dh"), ("ɣ", "gh"), ("θ", "th"), ("x", "kh"), ("ŋɡ", "ng"), ("ŋ", "ng"),
           ("ɡ", "g"), ("L", "l"), ("N", "n"), ("R", "r"), ("ʲ", "")]


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


def phonemize(word: str, scheme: str = "old-irish", quantities=None, etok: dict | None = None, **_) -> dict:
    ov = (etok.get("ipa") or {}).get(scheme) if etok else None
    if ov:
        return {"ipa": ov, "respell": _respell(ov.replace("ˈ", "")), "syllables": len(ov.split("."))}
    parts = [p for p in re.split(r"\s+", word.strip()) if p]
    ipas, rss, n = [], [], 0
    for p in parts:
        sylls, stress = word_sound(p)
        ipas.append(".".join(sylls))
        rs = [_respell(s.replace("ˈ", "")) for s in sylls]
        if len(rs) > 1:
            rs[stress] = rs[stress].upper()
        rss.append("-".join(rs))
        n += len(sylls)
    return {"ipa": " ".join(ipas), "respell": " ".join(rss), "syllables": n}


SCHEME_LABELS = {"old-irish": "Old Irish of the 9th century (reconstructed, approximate)"}

KEY = {
    "old-irish": [
        ("", "Old Irish as it was most likely spoken in the 9th century, after Thurneysen's Grammar of Old Irish and Stifter's Sengoídelc. The sound is read from the normalized spelling under the text, which marks what the manuscript leaves unwritten. It is a reconstruction, and approximate."),
        ("CAPS", "the stressed syllable: the first of the word, or the first after a pretonic preverb (do·tuit). Enclitics (-sam, -se) are unstressed"),
        ("a e i o u", "short vowels in the stressed syllable"),
        ("aa ay ee oh oo", "long á é í ó ú"),
        ("uh", "ə, the reduced vowel of every unstressed short syllable"),
        ("ai, ee-a, oo-a, ow, eu", "the diphthongs áe/óe, ía, úa, áu, éu"),
        ("v", "after a vowel, b (β, a v made with both lips) and m (β̃, the same sound nasalized)"),
        ("dh", "after a vowel, d: th as in this"),
        ("gh", "after a vowel, g: a g without closure, as in Spanish agua"),
        ("g, d, b", "after a vowel, c t p are g d b; doubled cc tt pp keep k t p"),
        ("kh", "ch, as in Scots loch"),
        ("th", "th, as in thin"),
        ("l, n, r", "the IPA row writes L N R for the strong sounds (at the start of a word, and doubled ll nn rr) and l n r for the weak ones after a vowel"),
        ("ʲ (IPA row)", "a slender consonant, said with the tongue raised toward the palate, before or after e and i; the others are broad. The respelling does not show the difference"),
        ("Normalized spelling", "the row under the text: the manuscript's words in the spelling of modern editions, with long vowels marked, a dot for lenition (ḃ ḋ ġ ṁ), n- for nasalization and · after a pretonic preverb"),
    ],
}
