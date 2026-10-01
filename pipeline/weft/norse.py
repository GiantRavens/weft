"""Old Norse (normalized Old Icelandic) orthography -> IPA and respelling.

Normalized spelling marks vowel length with the acute (á é í ó ú ý) and with æ, so no
quantity table is needed. Stress is always on the first syllable.

Schemes
-------
old-norse         Reconstructed Old Icelandic of about 1200 (after E. V. Gordon, *An
                  Introduction to Old Norse*, and Haugen). Long vowels are pure and long;
                  ö is read as the open ǫ; v is w; f is v between voiced sounds; g is a
                  fricative (gh) after a vowel; hv is xw; hl, hr, hn are voiceless.
modern-icelandic  How Icelanders read the Edda today (approximate): á = ow, é = ye, ó = oh,
                  æ = eye, au = öy; ll = tl; nn after a long vowel = tn; hv = kv; a final r
                  after a consonant gains a vowel (frændr = frændur).
"""
from __future__ import annotations

import unicodedata as ud
from dataclasses import dataclass

VERSION = "0.1"
PUNCT = ",.;:!?()[]“”‘’\"—"
LONG = {"á": "a", "é": "e", "í": "i", "ó": "o", "ú": "u", "ý": "y", "æ": "æ", "œ": "œ"}
SHORT = set("aeiouyöøǫ")
DIPHTHONGS = ("au", "ei", "ey")


@dataclass
class Seg:
    text: str
    vowel: bool
    long: bool = False


def _segments(word: str) -> list[Seg]:
    w = ud.normalize("NFC", word.lower())
    segs: list[Seg] = []
    i = 0
    while i < len(w):
        c = w[i]
        pair = w[i:i + 2]
        if pair in DIPHTHONGS:
            segs.append(Seg(pair, True, True)); i += 2; continue
        if c in LONG:
            segs.append(Seg(c, True, True)); i += 1; continue
        if c in SHORT:
            segs.append(Seg(c, True, False)); i += 1; continue
        if c == "x":
            segs.append(Seg("k", False)); segs.append(Seg("s", False)); i += 1; continue
        if c == "z":
            segs.append(Seg("t", False)); segs.append(Seg("s", False)); i += 1; continue
        segs.append(Seg(c, False)); i += 1
    return segs


def _syllables(segs: list[Seg]) -> list[list[tuple[int, Seg]]]:
    """Group segments into syllables: each medial cluster gives its last consonant to the next."""
    vi = [i for i, s in enumerate(segs) if s.vowel]
    if not vi:
        return []
    bounds = [0]
    for n in range(len(vi) - 1):
        a, b = vi[n], vi[n + 1]
        cl = b - a - 1
        bounds.append(b if cl == 0 else b - 1)
    bounds.append(len(segs))
    return [[(k, segs[k]) for k in range(bounds[j], bounds[j + 1])] for j in range(len(vi))]


# ---------------------------------------------------------------- old-norse
ON_V = {"a": "a", "e": "e", "i": "i", "o": "o", "u": "u", "y": "y", "ö": "ɔ", "ø": "ø", "ǫ": "ɔ",
        "á": "aː", "é": "eː", "í": "iː", "ó": "oː", "ú": "uː", "ý": "yː", "æ": "ɛː", "œ": "øː",
        "au": "ɔu", "ei": "ei", "ey": "øy"}
MI_V = {"a": "a", "e": "ɛ", "i": "ɪ", "o": "ɔ", "u": "ʏ", "y": "ɪ", "ö": "œ", "ø": "œ", "ǫ": "œ",
        "á": "au", "é": "jɛ", "í": "i", "ó": "ou", "ú": "u", "ý": "i", "æ": "ai", "œ": "ai",
        "au": "øy", "ei": "ei", "ey": "ei"}


def _voiced(s: Seg | None) -> bool:
    return s is not None and (s.vowel or s.text in "lrmnvjðg")


def _ipa(segs: list[Seg], scheme: str) -> list[str]:
    out: list[str] = []
    n = len(segs)
    for k, s in enumerate(segs):
        prev = segs[k - 1] if k else None
        nxt = segs[k + 1] if k + 1 < n else None
        nxt2 = segs[k + 2] if k + 2 < n else None
        t = s.text
        if s.vowel:
            out.append("ʏ" if t == "*" else (ON_V if scheme == "old-norse" else MI_V)[t])
            continue
        if t == "h" and nxt is not None and not nxt.vowel:
            if nxt.text == "v":
                out.append("x" if scheme == "old-norse" else "k"); continue
            out.append(""); continue                               # hl hr hn: devoice the next
        if prev is not None and prev.text == "h" and not s.vowel and k == 1:
            if t == "v":
                out.append("w" if scheme == "old-norse" else "v"); continue
            out.append({"l": "l̥", "r": "r̥", "n": "n̥"}.get(t, t)); continue
        if t == "þ":
            out.append("θ"); continue
        if t == "ð":
            out.append("ð"); continue
        if t == "v":
            out.append("w" if scheme == "old-norse" else "v"); continue
        if t == "f":
            if k == 0:
                out.append("f")
            elif scheme == "modern-icelandic" and nxt is not None and nxt.text in "ln":
                out.append("p")
            else:
                out.append("v" if _voiced(prev) and (nxt is None or _voiced(nxt)) else "f")
            continue
        if t == "g":
            if prev is not None and prev.text == "n":
                out.append("ɡ"); continue
            if nxt is not None and nxt.text == "g":
                out.append("ɡ" if scheme == "old-norse" else "k"); continue
            if prev is not None and prev.text == "g":
                out.append("ɡ" if scheme == "old-norse" else ""); continue
            if k == 0:
                out.append("ɡ"); continue
            out.append("ɣ" if prev is not None and prev.vowel else "ɡ"); continue
        if t == "n" and nxt is not None and nxt.text in ("g", "k"):
            out.append("ŋ"); continue
        if scheme == "modern-icelandic":
            if t == "l" and nxt is not None and nxt.text == "l":
                out.append("t"); continue                             # ll = tl
            if t == "n" and nxt is not None and nxt.text == "n" and prev is not None and prev.vowel and prev.long:
                out.append("t"); continue                             # long vowel + nn = tn
        if t == "j":
            out.append("j"); continue
        out.append(t)
    return out


RESPELL = {
    "old-norse": [("ɔu", "ou"), ("øy", "öy"), ("aː", "aa"), ("eː", "ay"), ("iː", "ee"), ("oː", "oh"),
                  ("uː", "oo"), ("yː", "üü"), ("ɛː", "ê"), ("øː", "öö"), ("ɔ", "aw"), ("ø", "ö"),
                  ("y", "ü"), ("θ", "th"), ("ð", "dh"), ("ɣ", "gh"), ("x", "kh"), ("r̥", "hr"),
                  ("l̥", "hl"), ("n̥", "hn"), ("ŋ", "ng"), ("ɡ", "g"), ("j", "y")],
    "modern-icelandic": [("jɛ", "ye"), ("øy", "öy"), ("au", "ow"), ("ou", "oh"), ("ai", "ai"),
                         ("ei", "ay"), ("ɛ", "e"), ("ɪ", "i"), ("ɔ", "o"), ("ʏ", "ü"), ("œ", "ö"),
                         ("i", "ee"), ("u", "oo"), ("θ", "th"), ("ð", "dh"), ("ɣ", "gh"),
                         ("r̥", "hr"), ("l̥", "hl"), ("n̥", "hn"), ("ŋ", "ng"), ("ɡ", "g"), ("j", "y")],
}
KEY = {
    "old-norse": [
        ("a / aa", "a as in father, short / long (á)"),
        ("e / ay", "e as in pet / long close e (é), no glide"),
        ("i / ee", "i as in pit / ee as in see (í)"),
        ("o / oh", "o as in pot / oh without the glide (ó)"),
        ("u / oo", "u as in put / oo as in food (ú)"),
        ("ü / üü", "y and ý: French u"),
        ("aw", "ö (the old ǫ): short o as in awe"),
        ("ê", "æ: long open e, as in air"),
        ("ou, ay-ee, öy", "diphthongs au, ei, ey"),
        ("th / dh", "þ as in thin / ð as in this"),
        ("gh", "g after a vowel: a voiced, breathy g"),
        ("w", "v is w: veit = wayt"),
        ("hr, hl, hn, khw", "hr, hl, hn are breathy, voiceless r, l, n; hv is a breathy khw"),
        ("CAPS", "stress: always the first syllable"),
    ],
    "modern-icelandic": [
        ("ow, ye, oh, ai", "á, é, ó, æ: modern Icelandic diphthongs (ai as in aisle)"),
        ("öy / ay", "au / ei and ey"),
        ("ü", "u: rounded, between put and French u"),
        ("tl", "ll: allar = atlar"),
        ("tn", "nn after a long vowel: einn = aytn"),
        ("kv", "hv: hvar = kvar"),
        ("-ür", "final r after a consonant gains a vowel: frændr = frændur"),
        ("CAPS", "stress: always the first syllable"),
    ],
}
SCHEME_LABELS = {
    "old-norse": "Old Norse: reconstructed Old Icelandic, around 1200",
    "modern-icelandic": "Modern Icelandic: how the Edda is read aloud in Iceland today",
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


def phonemize(word: str, scheme: str = "old-norse", quantities=None, **_) -> dict:
    w = "".join(ch for ch in word if ch not in PUNCT)
    host_, _, clitic_ = w.strip("-").partition("-")
    if clitic_ and any(ch.isalpha() for ch in host_) and any(ch.isalpha() for ch in clitic_):
        # a hyphenated enclitic (er-a, kann-at, ákk-a): the host keeps the stress, the enclitic
        # follows as its own unstressed syllable(s)
        host, _, clitic = w.strip("-").partition("-")
        h, c = phonemize(host, scheme), phonemize(clitic, scheme)
        hs = h["respell"].upper() if h["syllables"] == 1 else h["respell"]
        hi = h["ipa"] if h["ipa"].startswith("ˈ") else "ˈ" + h["ipa"]
        if not c["syllables"]:          # a bare consonant (skyli-t) closes the host's last syllable
            return {"ipa": h["ipa"] + c["ipa"], "respell": h["respell"] + c["respell"].lower(), "syllables": h["syllables"]}
        return {"ipa": f"{hi}.{c['ipa'].lstrip('ˈ')}", "respell": f"{hs}-{c['respell'].lower()}",
                "syllables": h["syllables"] + c["syllables"]}
    segs = _segments(w)
    if (scheme == "modern-icelandic" and len(segs) >= 2 and segs[-1].text == "r"
            and not segs[-2].vowel and segs[-2].text != "r"):
        # modern Icelandic reads a final r after a consonant with a vowel: frændr = frændur
        segs.insert(len(segs) - 1, Seg("*", True, False))
    syls = _syllables(segs)
    if not syls:
        return {"ipa": w, "respell": w, "syllables": 0}
    seg_ipa = _ipa(segs, scheme)
    ipas = ["".join(seg_ipa[k] for k, _ in syl) for syl in syls]
    spells = [_respell(ip, scheme) for ip in ipas]
    if len(spells) > 1:
        spells[0] = spells[0].upper()
    ipa = ".".join(("ˈ" if n == 0 and len(ipas) > 1 else "") + ip for n, ip in enumerate(ipas))
    return {"ipa": ipa, "respell": "-".join(spells), "syllables": len(ipas)}
