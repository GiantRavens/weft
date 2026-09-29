"""Runic inscriptions: transliteration -> runes, and normalized form -> sound.

Two alphabets, rendered with the Unicode Runic block:
  elder     the 24-rune elder futhark (about 150-750), used for Proto-Norse
  younger   the 16-rune younger futhark in its short-twig forms (from about 750), used for
            Old Norse; Rök and many Swedish stones use short-twig runes

The runes are generated from the transliteration letter by letter, so the script row is a
generated layer like the sound row. The younger futhark has 16 runes for about 30 sounds
(one rune spells *stonta* for *standa*), so pronunciation is derived from each word's
scholarly normalization, never from the runes.

Scheme
------
as-carved   Each inscription in the language of its own date: Proto-Norse for the elder
            futhark inscriptions (about 400), Old East Norse for Rök (about 800). The token's
            `dialect` selects the rules: pn or oen.
"""
from __future__ import annotations

import unicodedata as ud

VERSION = "0.1"

ELDER = {"f": "ᚠ", "u": "ᚢ", "þ": "ᚦ", "a": "ᚨ", "r": "ᚱ", "k": "ᚲ", "g": "ᚷ", "w": "ᚹ",
         "h": "ᚺ", "n": "ᚾ", "i": "ᛁ", "j": "ᛃ", "ï": "ᛇ", "p": "ᛈ", "z": "ᛉ", "s": "ᛊ",
         "t": "ᛏ", "b": "ᛒ", "e": "ᛖ", "m": "ᛗ", "l": "ᛚ", "ŋ": "ᛜ", "d": "ᛞ", "o": "ᛟ"}
YOUNGER_SHORT = {"f": "ᚠ", "u": "ᚢ", "þ": "ᚦ", "o": "ᚬ", "r": "ᚱ", "k": "ᚴ", "h": "ᚽ",
                 "n": "ᚿ", "i": "ᛁ", "a": "ᛆ", "s": "ᛌ", "t": "ᛐ", "b": "ᛓ", "m": "ᛙ",
                 "l": "ᛚ", "R": "ᛧ"}
ALPHABETS = {"elder": ELDER, "younger-short-twig": YOUNGER_SHORT}

# reconstructed Proto-Germanic rune names and meanings, in futhark order
RUNE_NAMES = {"f": ("*fehu", "cattle, wealth"), "u": ("*ūruz", "aurochs"), "þ": ("*þurisaz", "giant"),
              "a": ("*ansuz", "god"), "r": ("*raidō", "ride"), "k": ("*kaunan", "ulcer, or torch"),
              "g": ("*gebō", "gift"), "w": ("*wunjō", "joy"), "h": ("*hagalaz", "hail"),
              "n": ("*naudiz", "need"), "i": ("*īsaz", "ice"), "j": ("*jēran", "year, harvest"),
              "p": ("*perþō", "meaning unknown"), "ï": ("*īhwaz", "yew"), "z": ("*algiz", "elk, or protection"),
              "s": ("*sōwilō", "sun"), "t": ("*tīwaz", "the god Tyr"), "b": ("*berkanan", "birch"),
              "e": ("*ehwaz", "horse"), "m": ("*mannaz", "man"), "l": ("*laguz", "water"),
              "ŋ": ("*ingwaz", "the god Ing"), "d": ("*dagaz", "day"), "o": ("*ōþalan", "inherited land")}


def to_runes(transliteration: str, alphabet: str) -> tuple[str, list[str]]:
    """Runes for a transliterated word, and any letters the alphabet cannot write."""
    table = ALPHABETS[alphabet]
    out, missing = [], []
    for ch in transliteration:
        key = ch if ch in table else ch.lower()
        if key in table:
            out.append(table[key])
        elif ch not in "-’'":
            missing.append(ch)
    return "".join(out), missing


# ---------------------------------------------------------------- sound
VOWELS = set("aeiouyæøǫ")
LONG_MARKS = {"̄", "́"}        # macron or acute on a normalized vowel = long
DIPH = {"pn": ("ai", "au", "eu"), "oen": ("æi", "au", "øy", "ai")}


def _segments(word: str, dialect: str) -> list[tuple[str, bool, bool]]:
    """(text, is_vowel, is_long). Keeps ʀ (Old Norse R) distinct from r."""
    w = ud.normalize("NFD", word.replace("R", "ʀ"))
    chars: list[list] = []
    for c in w:
        if c in LONG_MARKS and chars:
            chars[-1][1] = True
        elif not ud.combining(c):
            chars.append([c.lower() if c != "ʀ" else c, False])
    segs: list[tuple[str, bool, bool]] = []
    i = 0
    while i < len(chars):
        c, lg = chars[i]
        pair = c + (chars[i + 1][0] if i + 1 < len(chars) else "")
        if pair in DIPH[dialect]:
            segs.append((pair, True, True)); i += 2; continue
        segs.append((c, c in VOWELS, lg)); i += 1
    return segs


def _ipa(segs: list[tuple[str, bool, bool]], dialect: str) -> list[str]:
    out = []
    n = len(segs)
    for k, (t, v, lg) in enumerate(segs):
        prev = segs[k - 1] if k else None
        nxt = segs[k + 1] if k + 1 < n else None
        if v:
            # diphthongs written plainly (ai, not ai̯): the non-syllabic mark breaks common web fonts
            base = {"ǫ": "ɔ"}.get(t, t)
            out.append(base + ("ː" if lg and len(t) == 1 else ""))
            continue
        between = prev is not None and prev[1] and (nxt is None or nxt[1] or nxt[0] in "lrjwʀ")
        after_nasal = prev is not None and prev[0] in "nml"
        if t == "þ":
            out.append("θ")
        elif t == "ð":
            out.append("ð")
        elif t == "g":
            out.append("ɡ" if (k == 0 or after_nasal) else "ɣ")
        elif t == "d":
            out.append("d" if (k == 0 or after_nasal) else "ð")
        elif t == "b":
            out.append("b" if (k == 0 or after_nasal) else "β")
        elif t == "f":
            out.append("v" if (dialect == "oen" and between) else "f")
        elif t == "v":
            out.append("w")
        elif t == "z":
            out.append("z")
        elif t == "ʀ":
            out.append("ʀ")
        elif t == "h" and nxt is not None and not nxt[1]:
            out.append("h")
        else:
            out.append(t)
    return out


RESPELL = [("ai", "ai"), ("au", "ow"), ("eu", "e-oo"), ("æi", "a-ee"), ("øy", "öy"),
           ("aː", "aa"), ("eː", "ay"), ("iː", "ee"), ("oː", "oh"), ("uː", "oo"),
           ("æ", "a"), ("ɔ", "aw"), ("y", "ü"), ("θ", "th"), ("ð", "dh"), ("ɣ", "gh"),
           ("β", "bh"), ("ɡ", "g"), ("j", "y"), ("ŋ", "ng")]
KEY = {
    "as-carved": [
        ("", "Each inscription in the language of its own date: Proto-Norse around 400, Old East Norse around 800. Runes do not mark vowel length; long vowels follow the scholarly normalization."),
        ("th / dh", "þ as in thin; ð as in this"),
        ("gh, bh", "g and b between vowels: soft, breathy versions of g and b"),
        ("z", "the Proto-Norse z, a buzzing sound that later became r"),
        ("ʀ", "Old Norse R, the same sound some centuries on: between z and r"),
        ("w", "v and w are both w"),
        ("ai, ow", "diphthongs: ai as in aisle, au as in cow"),
        ("CAPS", "stress: always the first syllable of the word"),
    ],
}
SCHEME_LABELS = {"as-carved": "As carved: Proto-Norse around 400, Old East Norse around 800"}


def _respell(ipa: str) -> str:
    out, i = [], 0
    while i < len(ipa):
        for a, b in RESPELL:
            if ipa.startswith(a, i):
                out.append(b); i += len(a); break
        else:
            out.append(ipa[i]); i += 1
    return "".join(out)


def phonemize(word: str, scheme: str = "as-carved", quantities=None, dialect: str = "pn", **_) -> dict:
    segs = _segments(word, dialect)
    vi = [k for k, s in enumerate(segs) if s[1]]
    ipas_seg = _ipa(segs, dialect)
    if not vi:
        ipa = "".join(ipas_seg)
        return {"ipa": ipa, "respell": _respell(ipa), "syllables": 0}
    bounds = [0]
    for n in range(len(vi) - 1):
        a, b = vi[n], vi[n + 1]
        bounds.append(b if b - a == 1 else b - 1)
    bounds.append(len(segs))
    sylls = ["".join(ipas_seg[k] for k in range(bounds[j], bounds[j + 1])) for j in range(len(vi))]
    spells = [_respell(s) for s in sylls]
    if len(spells) > 1:
        spells[0] = spells[0].upper().replace("Ʀ", "ʀ")
    ipa = ".".join(("ˈ" if j == 0 and len(sylls) > 1 else "") + s for j, s in enumerate(sylls))
    return {"ipa": ipa, "respell": "-".join(spells), "syllables": len(sylls)}
