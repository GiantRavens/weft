"""Old English (late West Saxon, c. 1000) orthography -> IPA and respelling.

Vowel length comes from, in order:
  1. the quantity table (``data/ang_quantities.yaml``): manuscript form -> normalized form
     with macrons (also fixes scribal spellings like u for v: oluendes -> olvendes);
  2. the treebank lemma, whose macrons carry over to the form along their shared prefix
     (hǣr -> hærum = hǣrum). A form that diverges from its lemma before the last macron is
     reported as ``quantity-uncertain``;
  3. nothing: the bare spelling, reported as ``quantity-unknown``.

Stress falls on the first syllable of the root. The prefixes ge- and be- are never stressed;
on verbs (and participles) a-, for-, of-, on-, to-, un-, ymb- are unstressed too. The caller
passes the part of speech and lemma so this can be decided.

Consonant rules (after Mitchell and Robinson, *A Guide to Old English*):
  c  = ch (tʃ) before e, i, æ, ea, eo, ie at the start of a word, and after i at the end (ic);
       otherwise k. sc = sh (ʃ). cg = j (dʒ).
  g  = y (j) before e, i, æ, ea, eo, ie at the start of a word and after a front vowel;
       gh (ɣ) between back vowels or after l, r; otherwise g. ng = ŋg.
  f, s, ð/þ are voiced (v, z, ð) between voiced sounds inside a word; otherwise f, s, θ.
  h  = h at the start of a syllable, x after a back vowel, ç after a front vowel.
  Doubled consonants are long.
"""
from __future__ import annotations

import re
import unicodedata as ud
from dataclasses import dataclass

VERSION = "0.1"
MACRON = "̄"
VOWELS = set("aæeiouy")
FRONT = set("eiæy")
DIPHTHONGS = ("ea", "eo", "ie", "io")
VERB_PREFIXES = ("ymb", "for", "un", "on", "of", "to", "ā", "a")
ALWAYS_PREFIXES = ("ge", "be")
PUNCT = ",.;:!?()[]“”‘’\"—·"

HEYNE = {"â": "ā", "ê": "ē", "î": "ī", "ô": "ō", "û": "ū", "ý": "ȳ", "ŷ": "ȳ",
         "Â": "Ā", "Ê": "Ē", "Î": "Ī", "Ô": "Ō", "Û": "Ū", "Ý": "Ȳ", "Ŷ": "Ȳ",
         "á": "ā", "é": "ē", "í": "ī", "ó": "ō", "ú": "ū",
         "Á": "Ā", "É": "Ē", "Í": "Ī", "Ó": "Ō", "Ú": "Ū"}


def heyne_to_macron(word: str) -> str:
    """Harrison and Sharp's Heyne-style accents -> modern macrons.

    Circumflex marks a long vowel; plain æ is long ǣ and ä is short æ; a long diphthong carries
    an acute (or circumflex) on its second vowel: eá, eó, geâr -> ēa, ēo, gēar."""
    w = ud.normalize("NFC", word)
    for a, b in (("eá", "ēa"), ("eó", "ēo"), ("eâ", "ēa"), ("eô", "ēo"), ("ió", "īo"), ("ié", "īe"),
                 ("Eá", "Ēa"), ("Eó", "Ēo"), ("Eâ", "Ēa"), ("Eô", "Ēo")):
        w = w.replace(a, b)
    w = w.replace("æ", "ǣ").replace("Æ", "Ǣ").replace("ä", "æ").replace("Ä", "Æ")
    return ud.normalize("NFC", "".join(HEYNE.get(c, c) for c in w))


@dataclass
class Seg:
    text: str
    vowel: bool
    long: bool = False


def _chars(word: str) -> list[tuple[str, bool]]:
    out: list[tuple[str, bool]] = []
    for ch in ud.normalize("NFD", word.lower().replace("þ", "ð")):
        if ch == MACRON and out:
            out[-1] = (out[-1][0], True)
        elif not ud.combining(ch):
            out.append((ch, False))
    return out


def _segments(word: str) -> list[Seg]:
    chars = _chars(word)
    segs: list[Seg] = []
    i = 0
    while i < len(chars):
        c, mac = chars[i]
        nxt = chars[i + 1][0] if i + 1 < len(chars) else ""
        if c == "s" and nxt == "c":
            segs.append(Seg("sc", False)); i += 2; continue
        if c == "c" and nxt == "g":
            segs.append(Seg("cg", False)); i += 2; continue
        if c == "i" and i == 0 and nxt in VOWELS and len(chars) > 2:
            segs.append(Seg("j", False)); i += 1; continue           # Latin names: Iohannes, Iordane
        if c in VOWELS:
            pair = c + nxt
            if pair in DIPHTHONGS:
                segs.append(Seg(pair, True, mac or chars[i + 1][1])); i += 2; continue
            segs.append(Seg(c, True, mac)); i += 1; continue
        if c == "x":
            segs.append(Seg("k", False)); segs.append(Seg("s", False)); i += 1; continue
        segs.append(Seg(c, False)); i += 1
    return segs


@dataclass
class Syl:
    onset: list[Seg]
    nucleus: Seg
    coda: list[Seg]


def _syllabify(segs: list[Seg]) -> list[Syl]:
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
        cut = len(cl) - 2 if len(cl) >= 2 and cl[-2].text in "pbtdcgfð" and cl[-1].text in "lr" else len(cl) - 1
        syls[n].coda = cl[:cut]
        syls[n + 1].onset = cl[cut:]
    return syls


def _split_prefix(word: str, pos: str | None, lemma: str | None,
                  prefixes: dict | None = None) -> tuple[str, str]:
    """Return (unstressed prefix, rest). Only strips a prefix the lemma, the rules, or the
    stress table justify. The table wins: {"oftēah": "of"}, or "" to forbid a false ge- (geong)."""
    key = ud.normalize("NFC", word.lower())
    if prefixes is not None and key in prefixes:
        p = prefixes[key] or ""
        return word[: len(p)], word[len(p):]
    w = word.lower()
    lem = _strip_macrons((lemma or "").lower())
    for p in ALWAYS_PREFIXES:
        if w.startswith(p) and len(w) > len(p) + 2 and not lem.startswith(p):
            return word[: len(p)], word[len(p):]
    if pos in ("VERB", "AUX"):
        for p in VERB_PREFIXES:
            pp = _strip_macrons(p)
            if _strip_macrons(w).startswith(pp) and lem.startswith(pp) and len(w) > len(pp) + 2:
                return word[: len(pp)], word[len(pp):]
    return "", word


def _strip_macrons(s: str) -> str:
    return ud.normalize("NFC", "".join(c for c in ud.normalize("NFD", s) if c != MACRON))


def clean_lemma(raw: str) -> tuple[str, str | None, bool]:
    """'fullian(ge) ‘to baptize’' -> ('fullian', 'to baptize', True). Third value: takes ge-."""
    raw = (raw or "").strip()
    gloss = None
    m = re.search(r"[‘'](.+?)[’']", raw)
    if m:
        gloss = m.group(1)
        raw = raw[: m.start()].strip()
    raw = re.sub(r"\s*\([A-Z]+\)\s*$", "", raw).strip()
    ge = "(ge)" in raw
    raw = raw.replace("(ge)", "").strip()
    return raw, gloss, ge


def transfer_quantity(form: str, lemma: str) -> tuple[str, str]:
    """Carry the lemma's macrons onto the form along their shared prefix.

    Returns (form with macrons, status): 'exact' when every macron in the lemma lies within the
    shared prefix, 'partial' when the form diverges before a macron (e.g. cōm from cuman needs
    the table), 'none' when there is no lemma."""
    if not lemma:
        return form, "none"
    lem = lemma.split("/")[0].split("-")[0].lower()
    base_l = _strip_macrons(lem)
    f = form.lower()
    offset = 0
    if f.startswith("ge") and not base_l.startswith("ge"):
        offset = 2
    root = f[offset:]
    k = 0
    while k < min(len(root), len(base_l)) and root[k] == base_l[k]:
        k += 1
    lem_nfd = ud.normalize("NFD", lem)
    macron_at, idx = [], -1
    for ch in lem_nfd:
        if ch == MACRON:
            macron_at.append(idx)
        elif not ud.combining(ch):
            idx += 1
    out = list(f)
    for pos in macron_at:
        if pos < k:
            out[offset + pos] = out[offset + pos] + MACRON
    status = "exact" if all(p < k for p in macron_at) else "partial"
    return ud.normalize("NFC", "".join(out)), status


# ---------------------------------------------------------------- sounds
V_IPA = {"a": ("ɑ", "ɑː"), "æ": ("æ", "æː"), "e": ("e", "eː"), "i": ("i", "iː"),
         "o": ("o", "oː"), "u": ("u", "uː"), "y": ("y", "yː"),
         "ea": ("æɑ", "æːɑ"), "eo": ("eo", "eːo"), "ie": ("iy", "iːy"), "io": ("io", "iːo")}


def _is_front(seg: Seg | None) -> bool:
    return bool(seg and seg.vowel and seg.text[0] in FRONT and seg.text[0] != "y")


def _word_ipa(syls: list[Syl], root_start: int, boundaries: set[int] | None = None) -> list[str]:
    """IPA per syllable. root_start: index of the first syllable of the root (after any prefix)."""
    flat: list[tuple[int, Seg]] = []
    for n, s in enumerate(syls):
        for seg in s.onset + [s.nucleus] + s.coda:
            flat.append((n, seg))
    # index in `flat` where the root begins: sounds there count as word-initial
    root_k = next((k for k, (n, _) in enumerate(flat) if n == root_start), 0)
    root_k = min(root_k, next((k for k, (n, s) in enumerate(flat) if n == root_start and not s.vowel), root_k))
    first_root = [k for k, (n, _) in enumerate(flat) if n == root_start]
    if first_root:
        root_k = first_root[0]
    parts = [""] * len(syls)
    for k, (n, seg) in enumerate(flat):
        prev = flat[k - 1][1] if k > 0 else None
        nxt = flat[k + 1][1] if k + 1 < len(flat) else None
        initial = k == 0 or k == root_k or k in (boundaries or set())
        final = k == len(flat) - 1
        t = seg.text
        if seg.vowel:
            parts[n] += V_IPA[t][1 if seg.long else 0]
            continue
        voiced_env = (not initial and not final and prev is not None and nxt is not None
                      and (prev.vowel or prev.text in "lrmnw") and (nxt.vowel or nxt.text in "lrmnw")
                      and not (prev.text == t or nxt.text == t))
        if t == "c":
            if (initial and _is_front(nxt)) or (final and prev is not None and prev.vowel and prev.text in ("i",)):
                parts[n] += "tʃ"
            elif prev is not None and prev.vowel and prev.text in ("i", "e") and nxt is not None and nxt.vowel and nxt.text in ("e",) and not initial:
                parts[n] += "tʃ"
            else:
                parts[n] += "k"
        elif t == "sc":
            parts[n] += "ʃ"
        elif t == "cg":
            parts[n] += "dʒ"
        elif t == "g":
            if prev is not None and prev.text == "n":
                parts[n] += "ɡ"
            elif initial:
                parts[n] += "j" if _is_front(nxt) else "ɡ"
            elif prev is not None and prev.vowel and prev.text[-1] in "ieæ":
                parts[n] += "j"
            elif prev is not None and (prev.vowel or prev.text in "lr"):
                parts[n] += "ɣ"
            else:
                parts[n] += "ɡ"
        elif t == "n" and nxt is not None and nxt.text in ("g", "c", "k"):
            parts[n] += "ŋ"
        elif t == "h":
            if initial or (nxt is not None and nxt.vowel):
                parts[n] += "h"
            else:
                parts[n] += "ç" if (prev is not None and prev.vowel and prev.text[-1] in "ie") else "x"
        elif t == "f":
            parts[n] += "v" if voiced_env else "f"
        elif t == "s":
            parts[n] += "z" if voiced_env else "s"
        elif t == "ð":
            parts[n] += "ð" if voiced_env else "θ"
        elif t == "j":
            parts[n] += "j"
        else:
            parts[n] += {"r": "r", "w": "w"}.get(t, t)
    return parts


RESPELL = [("æːɑ", "ǣa"), ("æɑ", "æa"), ("eːo", "ēo"), ("iːy", "īe"), ("iːo", "īo"), ("ŋɡ", "ng"),
           ("ɑː", "aah"), ("æː", "aa"), ("eː", "ay"), ("iː", "ee"), ("oː", "oh"), ("uː", "oo"), ("yː", "üü"),
           ("eo", "eo"), ("iy", "ie"), ("io", "io"),
           ("ɑ", "ah"), ("æ", "a"), ("y", "ü"),
           ("tʃ", "ch"), ("dʒ", "j"), ("ʃ", "sh"), ("θ", "th"), ("ð", "dh"), ("ɣ", "gh"),
           ("ç", "kh"), ("x", "kh"), ("ŋ", "ng"), ("ɡ", "g"), ("j", "y")]
KEY = {
    "west-saxon": [
        ("ah / aah", "a as in father, short / long"),
        ("a / aa", "æ: a as in cat, short / held long"),
        ("e / ay", "e as in pet / long close e, no glide"),
        ("i / ee", "i as in pit / ee as in see"),
        ("o / oh", "o as in pot / oh without the glide"),
        ("u / oo", "u as in put / oo as in food"),
        ("ü / üü", "y: French u, German ü"),
        ("æa / ǣa, eo / ēo", "diphthongs ea and eo, short / long: a as in cat gliding to uh; e gliding to o, in one syllable"),
        ("ng", "the g is always sounded, as in finger, never as in singer"),
        ("ch, sh, j", "c before front vowels (cild = child), sc (scip = ship), cg (ecg = edge)"),
        ("y", "g before front vowels (gēar = year) and after them (dæg = dæy)"),
        ("gh", "g between back vowels: a soft, voiced h-like g"),
        ("kh", "h after vowels: as in Scottish loch or German ich"),
        ("th / dh", "þ, ð: as in thin / as in this, by position"),
        ("v, z", "f and s between voiced sounds: heofon = he-o-von"),
        ("CAPS", "stressed syllable: the root's first; ge- and verb prefixes are unstressed"),
    ],
}
SCHEME_LABELS = {"west-saxon": "Late West Saxon, around the year 1000"}


def _respell(ipa: str) -> str:
    out, i = [], 0
    while i < len(ipa):
        for a, b in RESPELL:
            if ipa.startswith(a, i):
                out.append(b); i += len(a); break
        else:
            out.append(ipa[i]); i += 1
    return "".join(out)


def resolve_quantity(word: str, table: dict | None, lemma: str | None) -> tuple[str, str]:
    key = ud.normalize("NFC", word.lower())
    if table and key in table:
        return ud.normalize("NFC", table[key]), "table"
    if lemma:
        form, status = transfer_quantity(word, lemma)
        return form, f"lemma-{status}"
    return word, "none"


def phonemize(word: str, scheme: str = "west-saxon", quantities: dict | None = None,
              pos: str | None = None, lemma: str | None = None,
              prefixes: dict | None = None, **_) -> dict:
    w = "".join(ch for ch in word if ch not in PUNCT)
    # an editor's hyphen marks a compound boundary: the sound after it is word-initial
    parts = w.split("-")
    w = "".join(parts)
    norm, qsrc = resolve_quantity(w, quantities, lemma)
    boundaries: set[int] = set()
    if len(parts) > 1:
        offset = 0
        for part in parts[:-1]:
            offset += len(_segments(part))
            boundaries.add(offset)
    prefix, rest = _split_prefix(norm, pos, lemma, prefixes)
    syls = _syllabify(_segments(norm))
    if not syls:
        return {"ipa": norm, "respell": norm, "syllables": 0, "qsrc": qsrc}
    root_start = len(_syllabify(_segments(prefix))) if prefix else 0
    stress = root_start if root_start < len(syls) else 0
    ipas = _word_ipa(syls, root_start, boundaries)
    spells = []
    for n, ip in enumerate(ipas):
        r = _respell(ip)
        spells.append(r.upper() if n == stress and len(syls) > 1 else r)
    ipa = ".".join(("ˈ" if n == stress and len(syls) > 1 else "") + ip for n, ip in enumerate(ipas))
    return {"ipa": ipa, "respell": "-".join(spells), "syllables": len(syls), "qsrc": qsrc}
