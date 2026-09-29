"""Classical Chinese: one character, one syllable. Readings come from the Unicode Han Database.

Schemes
-------
tang       Tang-dynasty reading (8th century), from Unihan kTang, which follows Hugh M. Stimson,
           *T'ang Poetic Vocabulary* (1976). This is how Li Bai's generation read the characters.
           Stimson's notation is kept as the respelling; the key explains it. Tones: no mark =
           level (平), caron = rising (上), grave = departing (去), final -p -t -k = entering (入).
mandarin   Modern Standard Mandarin (pinyin), from Unihan kMandarin.
cantonese  Cantonese (Jyutping), from Unihan kCantonese. Cantonese keeps the Tang final -p -t -k
           and the -m that Mandarin lost, so old rhymes often still rhyme in it.

The reading table is built from the Unihan files by `load_readings`; a character with no reading
of its own borrows one from a glyph variant (kZVariant, then kSemanticVariant) and says so.
"""
from __future__ import annotations

import re
from pathlib import Path

VERSION = "0.1"
FIELDS = ("kTang", "kMandarin", "kCantonese", "kDefinition")
SCHEME_FIELD = {"tang": "kTang", "mandarin": "kMandarin", "cantonese": "kCantonese"}


def load_readings(readings: Path, variants: Path, chars: set[str]) -> dict[str, dict]:
    """{char: {kTang, kMandarin, kCantonese, kDefinition, via?}} for the characters needed."""
    want = {f"U+{ord(c):04X}": c for c in chars}
    var: dict[str, list[str]] = {}
    for line in variants.read_text(encoding="utf-8").splitlines():
        if line.startswith("#") or not line.strip():
            continue
        cp, field, val = line.split("\t", 2)
        if cp in want and field in ("kZVariant", "kSemanticVariant"):
            var.setdefault(want[cp], [])
            var[want[cp]] += [chr(int(v.split("<")[0][2:], 16)) for v in val.split()]
    need = set(want) | {f"U+{ord(v):04X}" for vs in var.values() for v in vs}
    table: dict[str, dict] = {}
    for line in readings.read_text(encoding="utf-8").splitlines():
        if line.startswith("#") or not line.strip():
            continue
        cp, field, val = line.split("\t", 2)
        if cp in need and field in FIELDS:
            table.setdefault(chr(int(cp[2:], 16)), {})[field] = val
    out: dict[str, dict] = {}
    for c in chars:
        rec = dict(table.get(c, {}))
        for f in FIELDS:
            if f not in rec:
                for v in var.get(c, []):
                    if f in table.get(v, {}):
                        rec[f] = table[v][f]
                        rec.setdefault("via", {})[f] = v
                        break
        out[c] = rec
    return out


def tang_tone(reading: str) -> str:
    """'level' | 'rising' | 'departing' | 'entering' for one Stimson syllable."""
    r = reading.lstrip("*")
    if re.search(r"[ptk]$", r):
        return "entering"
    if "̌" in r or any(ch in r for ch in "ǎěǐǒǔ"):
        return "rising"
    if "̀" in r or any(ch in r for ch in "àèìòù"):
        return "departing"
    import unicodedata as ud
    d = ud.normalize("NFD", r)
    if "̌" in d:
        return "rising"
    if "̀" in d:
        return "departing"
    return "level"


def tang_final(reading: str) -> str:
    """The rhyme part of a Stimson syllable: strip the initial consonants and any medial i/u glide."""
    import unicodedata as ud
    r = ud.normalize("NFD", reading.lstrip("*"))
    r = "".join(c for c in r if not ud.combining(c))
    m = re.match(r"^[^aeiouyɑæəɛɨ]*", r)
    rest = r[m.end():]
    rest = re.sub(r"^[iu](?=[aeouɑæəɛɨ])", "", rest)
    return rest


KEY = {
    "tang": [
        ("ɑ, æ, ə, ɛ", "ɑ as in father, æ as in cat, ə as in about, ɛ as in pet"),
        ("h after a consonant", "a breathy, voiced initial (dh, zh, jr...): the old voiced series"),
        ("ng-", "ng can begin a syllable: 月 ngiuæt"),
        ("jr, shr", "retroflex sounds, tongue curled back"),
        ("no tone mark", "level tone (平)"),
        ("ǎ (caron)", "rising tone (上)"),
        ("à (grave)", "departing tone (去)"),
        ("-p, -t, -k", "entering tone (入): a short syllable cut off by a stop"),
    ],
    "mandarin": [("pinyin", "standard pinyin; tone marks: ā level, á rising, ǎ dipping, à falling")],
    "cantonese": [("Jyutping", "number = tone 1-6; Cantonese keeps final -p -t -k and -m")],
}
SCHEME_LABELS = {
    "tang": "Tang: as Li Bai's generation read it, 8th century (Stimson, via Unicode)",
    "mandarin": "Modern Mandarin",
    "cantonese": "Cantonese, which keeps many Tang sounds",
}


def phonemize(word: str, scheme: str = "tang", quantities: dict | None = None, **_) -> dict:
    """quantities: the reading table from load_readings. First listed reading wins."""
    rec = (quantities or {}).get(word, {})
    val = rec.get(SCHEME_FIELD[scheme], "")
    first = val.split()[0].lstrip("*") if val else "?"
    out = {"ipa": first, "respell": first, "syllables": 1}
    if scheme == "tang" and val:
        out["tone"] = tang_tone(first)
        out["final"] = tang_final(first)
    if "via" in rec and SCHEME_FIELD[scheme] in rec["via"]:
        out["via"] = rec["via"][SCHEME_FIELD[scheme]]
    return out
