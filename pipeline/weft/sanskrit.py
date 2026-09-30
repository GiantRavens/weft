"""Vedic Sanskrit: accented transliteration -> sound, Devanagari accent marks -> pitch, and metre.

Each token gives its recited form in IAST transliteration (n), with the Vedic pitch accent written
the scholarly way: an acute for the raised pitch (udātta, á), a grave for an independent falling
pitch (svarita, à). The Rigveda's own manuscripts mark the accent differently, with a stroke below
the syllable before a raised one and a stroke above the syllable after it. `decode_marks` reads those
strokes back into raised syllables, so the hand-entered accents can be checked against the source.

Schemes
-------
vedic    Vedic as recited around 1200 BC, approximate. Pitch accent as recorded in the text and
         described by the ancient phonetic treatises (prātiśākhyas). Short a is a close vowel, as
         Pāṇini states; e and o are long monophthongs; c and j are palatal stops; v is between v
         and w; ṛ is a syllable made of r alone; intervocalic ḍ is the lateral ḷ.
modern   Sanskrit as commonly read aloud in north India today: ṛ is ri, ś and ṣ are both sh, jñ is
         gy, visarga echoes the vowel before it. Pitch is not marked.

Syllables are counted across word boundaries for the metre, since the Vedic line is recited as one
continuous stream. A syllable is heavy (guru) when its vowel is long or a diphthong, or when two
or more consonants, an anusvāra or a visarga follow the vowel.
"""
from __future__ import annotations

import unicodedata as ud

VERSION = "0.1"

ACUTE, GRAVE = "́", "̀"
SHORT = {"a", "i", "u", "ṛ"}
LONG = {"ā", "ī", "ū", "ṝ", "e", "o", "ai", "au"}
VOWELS = SHORT | LONG
STOPS = set("kgcjṭḍtdpb") | {"ḷ"}
CODA = {"ṃ", "ḥ", "ṁ"}     # anusvāra, visarga, candrabindu (written ṁ, one letter, as the treebank does)

# ---------------------------------------------------------------- IAST parsing


def _graphemes(word: str) -> list[tuple[str, str]]:
    """(letter, accent) pairs; the accent ('' | 'U' | 'S') is lifted off vowels."""
    out: list[list[str]] = []
    for c in ud.normalize("NFD", word):
        if ud.combining(c) and out:
            if c == ACUTE and out[-1][0] == "s":
                out[-1][0] += c              # ś is s + acute in decomposed form: a letter, not an accent
            elif c == ACUTE:
                out[-1][1] = "U"
            elif c == GRAVE:
                out[-1][1] = "S"
            else:
                out[-1][0] += c
        else:
            out.append([c, ""])
    return [(ud.normalize("NFC", g).lower(), a) for g, a in out]


def segments(word: str) -> list[dict]:
    """Phonological segments: {s, kind: V|C|N (coda nasal/visarga), acc}."""
    gs = [g for g in _graphemes(word) if g[0] not in "'’-"]
    segs: list[dict] = []
    i = 0
    while i < len(gs):
        g, acc = gs[i]
        nxt = gs[i + 1][0] if i + 1 < len(gs) else ""
        if g == "a" and nxt in ("i", "u") and not gs[i + 1][1]:
            segs.append({"s": g + nxt, "kind": "V", "acc": acc}); i += 2; continue
        if g in VOWELS:
            segs.append({"s": g, "kind": "V", "acc": acc}); i += 1; continue
        if g in ("ṃ", "ḥ", "ṁ"):
            segs.append({"s": g, "kind": "N", "acc": ""}); i += 1; continue
        if (g in STOPS) and nxt == "h":
            segs.append({"s": g + "h", "kind": "C", "acc": ""}); i += 2; continue
        segs.append({"s": g, "kind": "C", "acc": ""}); i += 1
    return segs


def syllables(segs: list[dict]) -> list[dict]:
    """One consonant between vowels starts the next syllable (V.CV); a consonant
    cluster splits before its last consonant, as in the Greek and Latin schemes. Codas (ṃ ḥ ṁ)
    stay with their vowel.
    Each syllable gets {segs, acc, heavy}; heavy depends on what follows the vowel."""
    vi = [k for k, s in enumerate(segs) if s["kind"] == "V"]
    if not vi:
        return [{"segs": segs, "acc": "", "heavy": False}]
    bounds = [0]
    for a, b in zip(vi, vi[1:]):
        cons = [k for k in range(a + 1, b) if segs[k]["kind"] == "C"]
        bounds.append(b if not cons else cons[-1])
    bounds.append(len(segs))
    out = []
    for j, v in enumerate(vi):
        after = segs[v + 1:(vi[j + 1] if j + 1 < len(vi) else len(segs))]
        heavy = (segs[v]["s"] in LONG or len([x for x in after if x["kind"] in "CN"]) >= 2
                 or any(x["kind"] == "N" for x in after))
        out.append({"segs": segs[bounds[j]:bounds[j + 1]], "acc": segs[v]["acc"], "heavy": heavy})
    return out


# ---------------------------------------------------------------- sound
IPA_V = {"a": "ɐ", "ā": "aː", "i": "i", "ī": "iː", "u": "u", "ū": "uː", "ṛ": "r̩", "ṝ": "r̩ː",
         "e": "eː", "o": "oː", "ai": "aːi", "au": "aːu"}
IPA_C = {"k": "k", "kh": "kʰ", "g": "ɡ", "gh": "ɡʱ", "ṅ": "ŋ", "c": "c", "ch": "cʰ", "j": "ɟ",
         "jh": "ɟʱ", "ñ": "ɲ", "ṭ": "ʈ", "ṭh": "ʈʰ", "ḍ": "ɖ", "ḍh": "ɖʱ", "ṇ": "ɳ", "t": "t",
         "th": "tʰ", "d": "d", "dh": "dʱ", "n": "n", "p": "p", "ph": "pʰ", "b": "b", "bh": "bʱ",
         "m": "m", "y": "j", "r": "ɾ", "l": "l", "v": "ʋ", "ś": "ɕ", "ṣ": "ʂ", "s": "s", "h": "ɦ",
         "ḷ": "ɭ", "ḷh": "ɭʱ", "ṃ": "ⁿ", "ḥ": "h", "ṁ": "ⁿ"}
RSP_V = {"a": "uh", "ā": "aa", "i": "i", "ī": "ee", "u": "u", "ū": "oo", "ṛ": "r", "ṝ": "rr",
         "e": "ay", "o": "oh", "ai": "aai", "au": "aau"}
RSP_C = {"kh": "kʰ", "gh": "gʰ", "c": "ch", "ch": "chʰ", "jh": "jʰ", "ñ": "ny", "ṅ": "ng",
         "ṭh": "ṭʰ", "ḍh": "ḍʰ", "th": "tʰ", "dh": "dʰ", "ph": "pʰ", "bh": "bʰ", "ś": "sh",
         "ṣ": "ṣh", "ḷh": "ḷʰ", "ṃ": "ṃ", "ḥ": "h", "ṁ": "ṃ"}
MOD_V = {"a": "ə", "ṛ": "rɪ", "ṝ": "riː", "ai": "əi", "au": "əu"}
MOD_C = {"c": "tʃ", "ch": "tʃʰ", "j": "dʒ", "jh": "dʒʱ", "ś": "ʃ", "ṣ": "ʃ", "ḷ": "ɭ", "ṁ": "ⁿ", "ṃ": "m"}
MOD_RSP_V = {"a": "uh", "ṛ": "ri", "ṝ": "ree"}
MOD_RSP_C = {"ṣ": "sh", "ṃ": "m", "ṁ": "n"}


def _ipa_seg(s: dict, scheme: str) -> str:
    if scheme == "modern":
        if s["kind"] == "V":
            return MOD_V.get(s["s"], IPA_V[s["s"]])
        return MOD_C.get(s["s"], IPA_C.get(s["s"], s["s"]))
    return (IPA_V if s["kind"] == "V" else IPA_C).get(s["s"], s["s"])


def _rsp_seg(s: dict, scheme: str) -> str:
    if scheme == "modern":
        if s["kind"] == "V":
            return MOD_RSP_V.get(s["s"], RSP_V[s["s"]])
        return MOD_RSP_C.get(s["s"], RSP_C.get(s["s"], s["s"]))
    return (RSP_V if s["kind"] == "V" else RSP_C).get(s["s"], s["s"])


def _jna(segs: list[dict]) -> list[dict]:
    """Modern north Indian reading of jñ as gy."""
    out = []
    for k, s in enumerate(segs):
        if s["s"] == "j" and k + 1 < len(segs) and segs[k + 1]["s"] == "ñ":
            out.append({**s, "s": "g"}); continue
        if s["s"] == "ñ" and k > 0 and segs[k - 1]["s"] == "j":
            out.append({**s, "s": "y"}); continue
        out.append(s)
    return out


def phonemize(word: str, scheme: str = "vedic", quantities=None, **_) -> dict:
    segs = segments(word)
    if scheme == "modern":
        segs = _jna(segs)
    sylls = syllables(segs)
    ipa, rsp = [], []
    for sy in sylls:
        i = "".join(_ipa_seg(s, scheme) for s in sy["segs"])
        r = "".join(_rsp_seg(s, scheme) for s in sy["segs"])
        if scheme == "modern" and sy["segs"] and sy["segs"][-1]["s"] == "ḥ":
            # recitation echoes the vowel after a final visarga: namaḥ -> namaha
            v = next((s for s in reversed(sy["segs"]) if s["kind"] == "V"), None)
            if v:
                ipa.append(i[:-1]); rsp.append(r[:-1])
                i, r = "h" + _ipa_seg(v, scheme), "h" + _rsp_seg(v, scheme)
        if scheme == "vedic" and sy["acc"]:
            # raised pitch: acute on the vowel in IPA, capitals in the respelling; an independent
            # svarita (falling) takes a circumflex in IPA
            mark = "́" if sy["acc"] == "U" else "̂"
            vpos = next((k for k, s in enumerate(sy["segs"]) if s["kind"] == "V"), None)
            pre = "".join(_ipa_seg(s, scheme) for s in sy["segs"][:vpos])
            v = _ipa_seg(sy["segs"][vpos], scheme)
            i = pre + v[0] + mark + v[1:] + "".join(_ipa_seg(s, scheme) for s in sy["segs"][vpos + 1:])
            r = r.upper()
        ipa.append(i)
        rsp.append(r)
    return {"ipa": ud.normalize("NFC", ".".join(ipa)), "respell": "-".join(rsp), "syllables": len(sylls)}


# ---------------------------------------------------------------- metre
def line_weights(words: list[str]) -> list[bool]:
    """Heavy (True) or light for each syllable of a line recited as one stream."""
    stream = [s for w in words for s in segments(w)]
    return [sy["heavy"] for sy in syllables(stream)]


def metre(words: list[str], pada_starts: list[int]) -> tuple[str, list[int]]:
    """Weft metre string with | between pādas, and the syllable count of each pāda.
    pada_starts: indexes into `words` where a new pāda begins (after the first)."""
    counts = [phonemize(w)["syllables"] for w in words]
    cuts = [sum(counts[:k]) for k in pada_starts]
    weights = line_weights(words)
    out, sizes, prev = [], [], 0
    for c in cuts + [len(weights)]:
        part = weights[prev:c]
        sizes.append(len(part))
        s = "".join("—" if h else "◡" for h in part)
        if c == len(weights) and s:
            s = s[:-1] + "×"           # the last syllable of the line is free (anceps)
        out.append(s)
        prev = c
    return "|".join(out), sizes


# ---------------------------------------------------------------- Devanagari
DV_VOWEL = {"अ": "a", "आ": "ā", "इ": "i", "ई": "ī", "उ": "u", "ऊ": "ū", "ऋ": "ṛ", "ॠ": "ṝ",
            "ए": "e", "ऐ": "ai", "ओ": "o", "औ": "au"}
DV_MATRA = {"ा": "ā", "ि": "i", "ी": "ī", "ु": "u", "ू": "ū", "ृ": "ṛ", "ॄ": "ṝ", "े": "e",
            "ै": "ai", "ो": "o", "ौ": "au"}
DV_CONS = {"क": "k", "ख": "kh", "ग": "g", "घ": "gh", "ङ": "ṅ", "च": "c", "छ": "ch", "ज": "j",
           "झ": "jh", "ञ": "ñ", "ट": "ṭ", "ठ": "ṭh", "ड": "ḍ", "ढ": "ḍh", "ण": "ṇ", "त": "t",
           "थ": "th", "द": "d", "ध": "dh", "न": "n", "प": "p", "फ": "ph", "ब": "b", "भ": "bh",
           "म": "m", "य": "y", "र": "r", "ल": "l", "व": "v", "श": "ś", "ष": "ṣ", "स": "s",
           "ह": "h", "ळ": "ḷ"}
DV_SIGN = {"ं": "ṃ", "ः": "ḥ", "ँ": "ṁ", "ऽ": "'"}
VIRAMA, UDATTA_STROKE, ANUDATTA_STROKE = "्", "॑", "॒"


def devanagari(text: str) -> tuple[str, list[str]]:
    """Unaccented IAST for a Devanagari string, and the accent stroke on each syllable
    ('A' stroke below, 'S' stroke above, '' none), in order. Spaces and dandas are dropped."""
    out: list[str] = []
    marks: list[str] = []
    pending_a = False                      # a consonant waiting for its vowel
    for c in text:
        if c in DV_CONS:
            if pending_a:
                out.append("a"); marks.append("")
            out.append(DV_CONS[c]); pending_a = True
        elif c in DV_MATRA:
            out.append(DV_MATRA[c]); marks.append(""); pending_a = False
        elif c == VIRAMA:
            pending_a = False
        elif c in DV_VOWEL:
            if pending_a:
                out.append("a"); marks.append("")
            out.append(DV_VOWEL[c]); marks.append(""); pending_a = False
        elif c in (UDATTA_STROKE, ANUDATTA_STROKE):
            if pending_a:
                out.append("a"); marks.append(""); pending_a = False
            if marks:
                marks[-1] = "S" if c == UDATTA_STROKE else "A"
        elif c in DV_SIGN:
            if pending_a:
                out.append("a"); marks.append(""); pending_a = False
            out.append(DV_SIGN[c])
        else:                              # space, danda, digit
            if pending_a:
                out.append("a"); marks.append(""); pending_a = False
    if pending_a:
        out.append("a"); marks.append("")
    return "".join(out), marks


def decode_marks(marks: list[str]) -> list[str]:
    """Rigvedic notation -> accent per syllable: U raised (udātta), S falling (svarita),
    A low (anudātta), P unmarked low after a fall (pracaya). An unmarked syllable is raised
    unless a fall came before it. Each printed half-verse is its own domain."""
    out: list[str] = []
    for m in marks:
        prev = out[-1] if out else None
        if m == "A":
            out.append("A")
        elif m == "S":
            out.append("S")
        else:
            out.append("P" if prev in ("S", "P") else "U")
    return out


def accents_from_words(words: list[str]) -> list[str]:
    """U / S (independent) / '' per syllable, from the acute and grave written in the IAST."""
    return [sy["acc"] for w in words for sy in syllables(segments(w))]


def strip_accents(s: str) -> str:
    """Remove the pitch accents, keeping ś (whose decomposed form also carries an acute)."""
    out = []
    for c in ud.normalize("NFD", s):
        if c in (ACUTE, GRAVE) and not (c == ACUTE and out and out[-1] == "s"):
            continue
        out.append(c)
    return ud.normalize("NFC", "".join(out))


KEY = {
    "vedic": [
        ("", "The Rigveda was passed down orally with its pitch accent, and the ancient phonetic treatises describe how it was voiced. This scheme follows them; the exact sounds of about 1200 BC are approximate."),
        ("CAPS", "raised pitch (udātta), not stress. The syllable after it glides down (svarita); the rest are low"),
        ("uh", "short a: a close vowel, as in but"),
        ("u", "short u, as in put"),
        ("aa, ee, oo", "long vowels, held about twice as long"),
        ("ay, oh", "e and o: long single vowels, as in they and go, without a glide"),
        ("r", "a syllable made of r alone: the ṛ of ṛtvíjam"),
        ("ṭ ḍ ṇ ṣ ḷ", "retroflex: the tongue tip curled back against the roof of the mouth"),
        ("ḷ", "the Rigveda's l-like sound for ḍ between vowels: īḷe"),
        ("kʰ, gʰ, tʰ, bʰ", "aspirated: a puff of breath after the consonant. tʰ is t + h, never the th of thin"),
        ("ch, j", "palatal stops, the tongue flat against the hard palate"),
        ("sh", "ś, the palatal sh; ṣh is the retroflex one"),
        ("v", "between v and w"),
        ("ṃ", "anusvāra: the vowel before it is nasalized"),
    ],
    "modern": [
        ("", "Sanskrit as commonly read aloud in north India today. The Vedic pitch accent is kept in traditional chanting but not marked here."),
        ("uh", "short a, as in about"),
        ("ri", "ṛ is said ri"),
        ("sh", "ś and ṣ are both sh"),
        ("gy", "jñ is said gy: yajña is yug-yuh"),
        ("-ha, -hi", "a final visarga echoes the vowel before it: namaḥ is na-ma-ha"),
    ],
}
SCHEME_LABELS = {
    "vedic": "Vedic: as recited around 1200 BC, with the pitch accent (approximate)",
    "modern": "Modern Indian reading of Sanskrit",
}
