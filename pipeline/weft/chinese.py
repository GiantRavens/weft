"""Classical Chinese: one character, one syllable. Readings come from the Unicode Han Database,
and for Old Chinese from the Baxter-Sagart reconstruction as published in Wiktionary.

Schemes
-------
old-chinese  Old Chinese, approximate: the Baxter-Sagart (2014) reconstruction, version 1.1, taken
           per character from Wiktionary's data modules (CC BY-SA 4.0) into
           data/lzh_oc_bs.yaml, each character pinned to a Wiktionary revision. It models the
           language of roughly 1000 to 200 BC, the period of the Laozi and the Shijing. It is a
           reconstruction from rhymes, graphic series and later dialects, not an attested sound:
           square brackets in the scholarly form mark an uncertain segment, parentheses an
           uncertain presence. Old Chinese had no tones in this model; final *-ʔ and *-s became
           the later rising and departing tones. A character missing from the Baxter-Sagart list
           falls back to Zhengzhang Shangfang (2003) and says so in its provenance.
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

import yaml

VERSION = "0.1"
FIELDS = ("kTang", "kMandarin", "kCantonese", "kDefinition")
SCHEME_FIELD = {"tang": "kTang", "mandarin": "kMandarin", "cantonese": "kCantonese"}


def load_readings(readings: Path, variants: Path, chars: set[str]) -> dict[str, dict]:
    """{char: {kTang, kMandarin, kCantonese, kDefinition, via?}} for the characters needed."""
    global _PICK
    _PICK = None                 # a new draft starts with no reading choice pending
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
    "old-chinese": [
        ("", "Old Chinese as reconstructed by Baxter and Sagart (2014), approximate. The respelling is a reading aid; the details panel shows their notation (*, brackets and all)."),
        ("", "No capitals: in this model Old Chinese had no tones, and a word's stress fell on its main (last) syllable."),
        ("ə, ə-", "ə as in about. A leading ə- is a light half-syllable before the main one (kə-lˤuʔ for 道); where its consonant is unknown only ə- is written."),
        ("ˤ", "after a consonant: the throat narrowed (pharyngealized), which darkens the vowel after it. These syllables became the plain, non-palatal type of later Chinese."),
        ("ʔ", "a catch in the throat, as in uh-oh. At the end of a word it later became the rising tone."),
        ("final s", "a suffix -s, later the departing tone: 故 kˤas"),
        ("kh, th, ph, tsh", "k, t, p, ts with a puff of breath, as in English kit"),
        ("q, ɢ", "k and g made further back, against the soft palate's end (uvular)"),
        ("hl", "a voiceless l, breathed rather than voiced"),
        ("ng", "can begin a word: ŋa[n] 言 is ngan"),
        ("kw, ɢw", "k or ɢ with rounded lips"),
        ("ː", "only in words taken from Zhengzhang Shangfang's system where the Baxter-Sagart list has no reading (較, 校): his long vowel, which corresponds to their ˤ"),
    ],
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
    "old-chinese": "Old Chinese: as the text may have sounded when first written down (Baxter-Sagart 2014, via Wiktionary; approximate)",
    "tang": "Tang: as Li Bai's generation read it, 8th century (Stimson, via Unicode)",
    "mandarin": "Modern Mandarin",
    "cantonese": "Cantonese, which keeps many Tang sounds",
}


# ---------------------------------------------------------------------------------------------
# Old Chinese (Baxter-Sagart 2014 via Wiktionary)

OC_DATA = Path(__file__).parent / "data" / "lzh_oc_bs.yaml"
_OC: dict | None = None
# The reading chosen for the token being drafted. An edition token may name which of a
# character's readings applies ({t: 惡, oc: 1, tang: 1, mandarin: è}); draft calls token_fields
# before it phonemizes that token, so the choice is held here for the calls that follow.
# load_readings clears it at the start of every draft. Works without an edition file (Li Bai)
# never set it, so their readings are the first listed, as before.
_PICK: tuple[str, dict] | None = None


def oc_table() -> dict:
    global _OC
    if _OC is None:
        _OC = yaml.safe_load(OC_DATA.read_text(encoding="utf-8")) or {}
    return _OC


def oc_form(raw: str) -> str:
    """The reconstruction itself, without Wiktionary's trailing remark: '*sreŋ (or *s.reŋ ?)' -> '*sreŋ'.
    Wiktionary writes a voiceless sonorant with a space after the ring ('*l̥ ˤi[n]'); rejoin it."""
    s = re.sub("([\u0325\u030a]) ", "\\1", raw.strip())
    s = s.split(" ")[0]
    return s if s.startswith("*") else "*" + s


def oc_respell(form: str) -> tuple[str, int]:
    """A reading aid from a Baxter-Sagart form: '*[kə.l]ˤuʔ' -> 'kə-lˤuʔ'. Returns (respelling, syllables).
    Uncertain segments in square brackets are read; optional ones in parentheses are left out.
    A loose preinitial (C. or Cə.) is a light half-syllable, written with ə and a hyphen; an
    unidentified consonant (C) is not written."""
    s = form.lstrip("*")
    s = re.sub(r"\([^)]*\)", "", s)
    s = s.replace("[", "").replace("]", "").replace("<", "").replace(">", "")
    s = s.replace("ə.", "ə·").replace("ə-", "ə·")
    s = re.sub(r"([^aeiouəɨA·])\.", r"\1ə·", s)
    s = s.replace("-", "").replace(".", "")
    s = s.replace("C", "").replace("A", "a").replace("N", "n")
    for voiceless, out in (("l\u0325", "hl"), ("n\u0325", "hn"), ("m\u0325", "hm"), ("ŋ\u030a", "hng")):
        s = s.replace(voiceless, out)
    s = s.replace("ʰ", "h").replace("ʷ", "w").replace("ŋ", "ng").replace("ɡ", "g")
    return s.replace("·", "-"), s.count("·") + 1


def oc_rime(form: str) -> str:
    """The rhyming part of a Baxter-Sagart form: main vowel and coda, without *-ʔ and *-s, which do
    not block a rhyme in this model. '*[k]ˤew(k)-s' -> 'ew'; '*[ɢ]ˤoj-s' -> 'oj'."""
    s = re.sub(r"\([^)]*\)", "", form.lstrip("*"))
    s = s.replace("[", "").replace("]", "").replace("<", "").replace(">", "").replace("ː", "")
    s = re.sub(r"-s$", "", s).replace("-", "").replace(".", "")
    s = re.sub(r"ʔ$", "", s)
    m = re.search(r"[aeiouəɨA][^aeiouəɨA]*$", s)        # the main syllable's vowel and coda
    return (m.group(0) if m else s).replace("A", "a")


def oc_reading(char: str, index: int = 1) -> dict | None:
    """One reading of a character, 1-based, with its source: {oc, en?, system, src}."""
    ent = oc_table().get(char)
    if not ent or not 1 <= index <= len(ent["readings"]):
        return None
    r = ent["readings"][index - 1]
    return {**r, "oc": oc_form(r["oc"]), "system": ent["system"], "src": ent["src"]}


def token_fields(surface: str, edition_token: dict, group: dict) -> tuple[dict, list]:
    """Language hook: hold the token's reading choice for phonemize, and check it against the data."""
    global _PICK
    pick = {k: edition_token[k] for k in ("oc", "tang", "mandarin") if k in edition_token}
    _PICK = (surface, pick)
    fields, fails = {}, []
    ent = oc_table().get(surface)
    if not ent:
        fails.append(("oc-reading-missing", surface))
        return fields, fails
    k = pick.get("oc", 1)
    if not 1 <= k <= len(ent["readings"]):
        fails.append(("oc-reading-index", f"{surface} oc={k}"))
    if ent["system"] == "ZS":
        fields["prov"] = {"sound": f"Old Chinese: Zhengzhang Shangfang (2003), {ent['src']['page']} "
                                   f"(oldid {ent['src']['oldid']}); the Baxter-Sagart list has no reading for {surface}"}
        fails.append(("oc-from-zhengzhang", surface))
    if "mandarin" in pick:
        # a chosen Mandarin reading must be one the Baxter-Sagart list gives for this character
        attested = {r.get("pinyin") for r in ent["readings"]}
        if pick["mandarin"] not in attested:
            fails.append(("mandarin-reading-unattested", f"{surface} {pick['mandarin']}"))
    return fields, fails


def line_checks(text: str, edition_tokens: list[dict], edition: dict) -> list[tuple[str, str]]:
    """Language hook: a line the edition marks as rhyming (rhyme: A) must end in the same Old
    Chinese rime as every other line of its section with that mark."""
    fails = []
    for g in edition.get("sections") or []:
        lines = [ln for ln in g["lines"] if isinstance(ln, dict)]
        me = next((ln for ln in lines if ln["tokens"] is edition_tokens), None)
        if me is None or not me.get("rhyme"):
            continue
        def rime(ln):
            last = ln["tokens"][-1]
            r = oc_reading(last["t"], last.get("oc", 1))
            return oc_rime(r["oc"]) if r and r["system"] == "BS" else None
        mine = rime(me)
        for other in lines:
            if other is not me and other.get("rhyme") == me["rhyme"] and rime(other) != mine:
                fails.append(("rhyme-not-supported", f"{me['tokens'][-1]['t']} *-{mine} vs "
                                                     f"{other['tokens'][-1]['t']} *-{rime(other)}"))
    return fails


def phonemize(word: str, scheme: str = "tang", quantities: dict | None = None, **_) -> dict:
    """quantities: the reading table from load_readings. First listed reading wins, unless the
    edition token being drafted chose another (see _PICK)."""
    pick = _PICK[1] if _PICK and _PICK[0] == word else {}
    if scheme == "old-chinese":
        r = oc_reading(word, pick.get("oc", 1))
        if not r:
            return {"ipa": "?", "respell": "?", "syllables": 1}
        respell, n = oc_respell(r["oc"])
        return {"ipa": r["oc"], "respell": respell, "syllables": n}
    rec = (quantities or {}).get(word, {})
    val = rec.get(SCHEME_FIELD[scheme], "")
    readings = [v.lstrip("*") for v in val.split()]
    first = readings[0] if readings else "?"
    if scheme == "tang" and readings and 1 <= pick.get("tang", 1) <= len(readings):
        first = readings[pick.get("tang", 1) - 1]
    if scheme == "mandarin" and pick.get("mandarin"):
        first = pick["mandarin"]
    out = {"ipa": first, "respell": first, "syllables": 1}
    if scheme == "tang" and val:
        out["tone"] = tang_tone(first)
        out["final"] = tang_final(first)
    if "via" in rec and SCHEME_FIELD[scheme] in rec["via"]:
        out["via"] = rec["via"][SCHEME_FIELD[scheme]]
    return out
