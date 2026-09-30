"""Classical Persian: hand transliteration -> sound, a check against the script, and rubāʿī metre.

Persian in Arabic script writes long vowels and leaves most short vowels out, so each token carries
a hand transliteration (n) with every vowel written. The transliteration uses the vowels of Early
New Persian, the language of Khayyam's lifetime: the "unknown" (majhul) vowels ē and ō are kept
apart from ī and ū (šēr 'lion', gōr 'wild ass', and the -ē of the indefinite and the conditional),
as grammarians and early manuscripts show and as Dari and Tajik still keep them. The modern Iranian
scheme is derived from the same spelling by the mergers that later happened.

Separators inside n (they carry no sound):
  -   prefix or suffix: mē-girift, ba-kamand, būdanī-hā
  +   compound: kōza+gar, yak+čand
  =   enclitic, unstressed: ezafe =i / =yi, personal endings =am =ēm, -ē, =ast, =rā
  '   a contracted conjunction: k'az (ki az), w'ān (u ān)

Schemes
-------
early    Early New Persian around 1100, as Khayyam's contemporaries in Khorasan likely spoke it.
         Approximate. Majhul ē and ō distinct from ī and ū; w is still [w] (xw- a rounded kh, as in
         xwad 'self'); the old diphthongs ay and aw; q and ġ distinct; d after a vowel in the same
         morpheme is the fricative ð, as early manuscripts write it with ذ (būð, bāð). Stress is
         placed by the modern rules, which is the least certain part of the reconstruction.
modern   Iranian Persian of Tehran today: ē merged with ī and ō with ū; short i and u lowered to e and
         o; a fronted to æ; ā backed to ɒ; w became v; q and ġ merged; ay and aw became ey and ow;
         final silent-h -a became -e; xwa- became xo-.

Stress (CAPS in the respelling): the last syllable of the word before any enclitic; a stressed
verbal prefix (mē-, mī-, bi-, na-, ma-, bar-) takes it instead.

Metre
-----
The rubāʿī is quantitative. A syllable is short (◡) when it ends in a short vowel; long (—) when
it ends in a long vowel or in a short vowel plus one consonant; overlong (—◡) when it ends in a
long vowel plus a consonant, or any vowel plus two consonants, except that ān, īn, ūn count as long.
The last syllable of a line counts as long. Following Elwell-Sutton (The Persian Metres, 1976) and
Farzaad's division of the line, every rubāʿī line fits one of two 13-position patterns, which
differ only in positions 6 and 7:

    5.1.13   — | — ◡ ◡ — | ◡ — ◡ — | — ◡ ◡ —
    3.3.13   — | — ◡ ◡ — | — ◡ ◡ — | — ◡ ◡ —

The final ◡ ◡ may be one long syllable (about half of all lines), and so, rarely, may the first.
Recognized licences, each used only when the plain reading does not fit: a word-final consonant
before a vowel either joins the next syllable (wasl) or not; the ezafe and the conjunction u may
count long; a long vowel before a vowel may count short. A line that fits no pattern is reported
as the failure class metre-not-rubai.
"""
from __future__ import annotations

import itertools
import re
import unicodedata as ud

VERSION = "0.1"

SHORT = set("aiu")
LONG = set("āīūēō")
VOWELS = SHORT | LONG
SEPS = "-+='"
STRESSED_PREFIX = {"mē", "mī", "bi", "bu", "na", "ma", "nē", "bar"}
MODERN_LEX = {"suxun": "suxan"}           # classical suxun, modern soxan

# ---------------------------------------------------------------- parsing


def morphs(word: str) -> list[tuple[str, str]]:
    """[(separator_before, text)], the first separator ''."""
    out, sep, cur = [], "", ""
    for c in ud.normalize("NFC", word.strip()):
        if c in SEPS:
            out.append((sep, cur)); sep, cur = c, ""
        else:
            cur += c
    out.append((sep, cur))
    return [(s, t) for s, t in out if t or s]


def segments(word: str, modern: bool = False) -> list[dict]:
    """Segments {s, V: bool, long, m (morph index), ez (ezafe vowel), last (morph-final)}."""
    segs: list[dict] = []
    for j, (sep, text) in enumerate(morphs(word)):
        if modern:
            text = MODERN_LEX.get(text, text)
        ez = sep == "=" and text in ("i", "yi")
        k = 0
        while k < len(text):
            c = text[k]
            if c == "x" and text[k + 1:k + 2] == "w" and text[k + 2:k + 3] in VOWELS:
                segs.append({"s": "xw", "V": False, "m": j}); k += 2; continue
            if c in VOWELS:
                segs.append({"s": c, "V": True, "long": c in LONG, "m": j, "ez": ez})
            else:
                segs.append({"s": c, "V": False, "m": j})
            k += 1
        if segs and segs[-1]["m"] == j:
            segs[-1]["last"] = True
            segs[-1]["mlen"] = len(text)
            segs[-1]["next_sep"] = None
    ms = morphs(word)
    for s in segs:
        if s.get("last") and s["m"] + 1 < len(ms):
            s["next_sep"] = ms[s["m"] + 1][0]
    return segs


def syllabify(segs: list[dict]) -> list[list[dict]]:
    """Persian has no onset clusters: one consonant between vowels starts the next syllable,
    a cluster splits before its last consonant."""
    vi = [k for k, s in enumerate(segs) if s["V"]]
    if not vi:
        return [segs]
    bounds = [0]
    for a, b in zip(vi, vi[1:]):
        cons = [k for k in range(a + 1, b)]
        bounds.append(b if not cons else cons[-1])
    bounds.append(len(segs))
    return [segs[bounds[j]:bounds[j + 1]] for j in range(len(vi))]


def stress_vowel(word: str) -> int | None:
    """Index (among the word's vowels) of the stressed vowel, or None."""
    ms = morphs(word)
    start = 0
    if len(ms) > 1 and ms[1][0] == "'":          # proclitic k' w': stress lies on the host
        start = 1
    host_end = next((j for j in range(start + 1, len(ms)) if ms[j][0] == "="), len(ms))
    if ms[start][0] == "=":
        return None                               # a bare enclitic (=rā) takes no stress
    counts = [sum(1 for c in t if c in VOWELS) for _, t in ms]
    before = sum(counts[:start])
    if ms[start][1] in STRESSED_PREFIX and start + 1 < len(ms) and ms[start + 1][0] == "-" and counts[start]:
        return before
    n_host = sum(counts[start:host_end])
    if not n_host:
        return None
    return before + n_host - 1


# ---------------------------------------------------------------- sound
EARLY_V = {"a": "a", "i": "i", "u": "u", "ā": "ɑː", "ī": "iː", "ū": "uː", "ē": "eː", "ō": "oː"}
MOD_V = {"a": "æ", "i": "e", "u": "o", "ā": "ɒ", "ī": "i", "ū": "u", "ē": "i", "ō": "u"}
CONS = {"b": "b", "p": "p", "t": "t", "ṭ": "t", "d": "d", "k": "k", "g": "ɡ", "q": "q", "ʾ": "ʔ",
        "ʿ": "ʔ", "f": "f", "s": "s", "ṣ": "s", "z": "z", "ẓ": "z", "ḍ": "z", "š": "ʃ", "ž": "ʒ",
        "x": "x", "xw": "xʷ", "ġ": "ɣ", "h": "h", "ḥ": "h", "č": "tʃ", "j": "dʒ", "m": "m", "n": "n",
        "l": "l", "r": "r", "w": "w", "y": "j", "ð": "ð"}
MOD_CONS = {"q": "ɢ", "ġ": "ɢ", "w": "v", "xw": "x", "r": "ɾ"}
RSP_EARLY_V = {"a": "a", "i": "i", "u": "u", "ā": "aa", "ī": "ee", "ū": "oo", "ē": "ê", "ō": "ô"}
RSP_MOD_V = {"æ": "a", "e": "e", "o": "o", "ɒ": "aa", "i": "ee", "u": "oo"}
RSP_CONS = {"š": "sh", "ž": "zh", "č": "ch", "x": "kh", "xw": "khw", "ġ": "gh", "ʾ": "'", "ʿ": "'",
            "ð": "dh", "ḥ": "h", "ṣ": "s", "ṭ": "t", "ẓ": "z", "ḍ": "z"}
RSP_MOD_CONS = {"q": "gh", "ġ": "gh", "w": "v", "xw": "kh"}


def _early(segs: list[dict]) -> list[tuple[str, str]]:
    """(ipa, respell) per segment for the early scheme."""
    out = []
    for k, s in enumerate(segs):
        if s["V"]:
            nxt = segs[k + 1] if k + 1 < len(segs) else None
            after = segs[k + 2] if k + 2 < len(segs) else None
            diph = s["s"] == "a" and nxt and nxt["s"] in ("y", "w") and not (after and after["V"])
            if diph:
                out.append(("a", "a" + ("i" if nxt["s"] == "y" else "u")))
            else:
                out.append((EARLY_V[s["s"]], RSP_EARLY_V[s["s"]]))
            continue
        c = s["s"]
        prev = segs[k - 1] if k else None
        if c == "d" and prev and prev["V"] and prev["m"] == s["m"]:
            c = "ð"                              # postvocalic d, the dhāl of early manuscripts
        if c in ("y", "w") and prev and prev["V"] and prev["s"] == "a" and not (k + 1 < len(segs) and segs[k + 1]["V"]):
            out.append((CONS[c], ""))            # second half of a diphthong: spelled with its vowel
            continue
        out.append((CONS.get(c, c), RSP_CONS.get(c, c)))
    return out


def _modern(segs: list[dict]) -> list[tuple[str, str]]:
    out = []
    for k, s in enumerate(segs):
        nxt = segs[k + 1] if k + 1 < len(segs) else None
        after = segs[k + 2] if k + 2 < len(segs) else None
        prev = segs[k - 1] if k else None
        if s["V"]:
            v = MOD_V[s["s"]]
            if s["s"] == "i" and nxt and nxt["s"] == "y":
                v = "i"                          # miyān, šahriyār: i before y stays i
            if s["s"] == "a" and nxt and nxt["s"] in ("y", "w") and not (after and after["V"]):
                v = "e" if nxt["s"] == "y" else "o"   # ay > ey, aw > ow
            if s["s"] == "a" and prev and prev["s"] == "xw":
                v = "o"                          # xwad > xod, xwardan > xordan
            if s["s"] == "a" and s.get("last") and s.get("mlen", 0) >= 3 and s.get("next_sep") != "-":
                v = "e"                          # silent-h ending: kōza > kuze
            if s["s"] == "a" and s.get("last") and s.get("mlen") == 2 and s.get("next_sep") == "-" and prev and prev["s"] == "b":
                v = "e"                          # preposition ba- > be-
            out.append((v, RSP_MOD_V[v]))
            continue
        c = s["s"]
        if c == "w" and prev and prev["V"] and prev["s"] == "a" and not (nxt and nxt["V"]):
            out.append(("w", "w")); continue     # the w of ow
        if c == "y" and prev and prev["V"] and prev["s"] == "a" and not (nxt and nxt["V"]):
            out.append(("j", "y")); continue
        out.append((MOD_CONS.get(c, CONS.get(c, c)), RSP_MOD_CONS.get(c, RSP_CONS.get(c, c))))
    return out


def phonemize(word: str, scheme: str = "early", quantities=None, **_) -> dict:
    modern = scheme == "modern"
    segs = segments(word, modern=modern)
    per = _modern(segs) if modern else _early(segs)
    idx = {id(s): k for k, s in enumerate(segs)}
    sylls = syllabify(segs)
    st = stress_vowel(word)
    ipa, rsp = [], []
    for j, sy in enumerate(sylls):
        i = "".join(per[idx[id(s)]][0] for s in sy)
        r = "".join(per[idx[id(s)]][1] for s in sy)
        if st is not None and j == st and len(sylls) > 1:
            i, r = "ˈ" + i, r.upper()
        ipa.append(i); rsp.append(r)
    return {"ipa": ".".join(ipa).replace(".ˈ", "ˈ"), "respell": "-".join(rsp), "syllables": len(sylls)}


# ---------------------------------------------------------------- script check
DIACRITICS = re.compile("[ً-ٰٟ‌‍ـ]")
FOLD = str.maketrans({"آ": "ا", "أ": "ا", "إ": "ا", "ك": "ک", "ي": "ی", "ى": "ی", "ئ": "ی", "ؤ": "و",
                      "ة": "ه", "ۀ": "ه"})
LETTER = {"b": "ب", "p": "پ", "t": "[تط]", "ṭ": "ط", "s": "[سثص]", "ṣ": "ص", "j": "ج", "č": "چ",
          "ḥ": "ح", "x": "خ", "d": "د", "r": "ر", "z": "[زذضظ]", "ẓ": "ظ", "ḍ": "ض", "ž": "ژ",
          "š": "ش", "ʿ": "ع", "ġ": "غ", "f": "ف", "q": "ق", "k": "ک", "g": "[گک]", "l": "ل",
          "m": "م", "n": "ن", "w": "و", "h": "[هح]", "y": "ی", "ʾ": "[ءای]?"}
LONG_LETTER = {"ā": "ا", "ī": "ی", "ē": "ی", "ū": "و", "ō": "و"}


def fold(surface: str) -> str:
    return DIACRITICS.sub("", ud.normalize("NFC", surface)).translate(FOLD)


def skeleton(word: str) -> str:
    """A regex of the Arabic-script letters the transliteration implies."""
    if word == "u":
        return "و"
    ms = morphs(word)
    out: list[str] = []
    prev_char = ""
    for j, (sep, text) in enumerate(ms):
        if sep == "=" and text in ("i", "yi"):
            continue                             # the ezafe is not written (a kasra at most)
        for k, c in enumerate(text):
            first, final = k == 0, k == len(text) - 1
            if c in VOWELS:
                if first and (j == 0 or sep in "-+"):
                    out.append("ا" + (LONG_LETTER[c] if c in "īēūō" else ""))
                elif first and sep == "=" and prev_char in VOWELS:
                    out.append("ا" + (LONG_LETTER[c] if c in "īēūō" else ""))
                elif c in LONG:
                    out.append(LONG_LETTER[c])
                elif final and c == "a" and len(text) >= 3:
                    out.append("ه")              # silent h: kōza, būda
                elif final and c == "i" and j == len(ms) - 1 or (final and c == "i" and ms[j + 1][0] == "+"):
                    out.append("ه?")             # ki, či (zi is written without it)
                elif final and c == "u" and (j == len(ms) - 1 or ms[j + 1][0] == "+"):
                    out.append("و")              # tu, ču
                elif c == "i" and text[k + 1:k + 2] == "y":
                    out.append("ی?")             # miyān, šahriyār
            else:
                if c == prev_char and c not in VOWELS:
                    continue                     # a doubled consonant is written once
                out.append(LETTER.get(c, re.escape(c)))
            prev_char = c
    return "".join(out)


def token_fields(surface: str, et: dict, group: dict):
    """Sensor: the hand transliteration must spell the printed word's letters."""
    fails = []
    if et.get("n") and not re.fullmatch(skeleton(et["n"]), fold(surface)):
        fails.append(("translit-script-mismatch", f"{surface} vs {et['n']} ({skeleton(et['n'])})"))
    return {}, fails


# ---------------------------------------------------------------- metre
FEET = {
    "5.1.13": ["—", "—◡◡—", "◡—◡—", "—◡◡—"],
    "3.3.13": ["—", "—◡◡—", "—◡◡—", "—◡◡—"],
}


def templates() -> list[tuple[str, list[str], int]]:
    """(name, feet, rarity) for every admitted shape. Rarity orders ties: plain first."""
    out = []
    for name, feet in FEET.items():
        for f2, f3, f4 in itertools.product([0, 1], [0, 1], [0, 1]):
            if f3 and name != "3.3.13":
                continue
            ft = list(feet)
            if f2:
                ft[1] = "———"
            if f3:
                ft[2] = "———"
            if f4:
                ft[3] = "———"
            out.append((name, ft, f2 + 3 * f3))
    return out


TEMPLATES = templates()


def _stream_options(words: list[str], links: tuple[bool, ...]):
    """Syllables of the line for one choice of joins, each with its admissible weights
    (default first) and whether using the second one is a licence."""
    stream: list[dict] = []
    junction = 0
    for w_i, w in enumerate(words):
        segs = [dict(s, w=w_i, conj=(w == "u")) for s in segments(w)]
        if not segs:
            continue
        if stream and segs[0]["V"] and not stream[-1]["V"]:
            if not links[junction]:
                stream.append({"s": "ʔ", "V": False, "m": -1, "w": w_i})   # no wasl: a glottal onset
            junction += 1
        stream.extend(segs)
    sylls = syllabify(stream)
    opts = []
    for j, sy in enumerate(sylls):
        v = next(s for s in sy if s["V"])
        coda = [s for s in sy[sy.index(v) + 1:]]
        if j == len(sylls) - 1:
            opts.append(["×"]); continue
        c = len(coda)
        if v["long"]:
            base = "—" if c == 0 or [s["s"] for s in coda] == ["n"] else "—◡"
        else:
            base = "◡" if c == 0 else ("—" if c == 1 else "—◡")
        choice = [base]
        nxt = sylls[j + 1]
        next_starts_vowel = nxt[0]["V"] or (nxt[0]["s"] == "y" and nxt[1:2] and nxt[1]["V"] and nxt[1].get("ez"))
        if c == 0 and not v["long"] and (v.get("ez") or v.get("conj")):
            choice.append("—")                  # ezafe or u lengthened
        elif c == 0 and v["long"] and next_starts_vowel and (nxt[0]["w"] != v["w"] or nxt[0]["s"] == "y"):
            choice.append("◡")                  # long vowel shortened before a vowel
        opts.append(choice)
    return opts


def scan(words: list[str]) -> tuple[str | None, str | None, int]:
    """Best match: (metre string, pattern name, licences used)."""
    n_junctions = 0
    for a, b in zip(words, words[1:]):
        sa, sb = segments(a), segments(b)
        if sa and sb and sb[0]["V"] and not sa[-1]["V"]:
            n_junctions += 1
    best = None
    for links in itertools.product([True, False], repeat=n_junctions):
        cost_links = sum(1 for x in links if not x)
        opts = _stream_options(words, links)
        for pick in itertools.product(*[range(len(o)) for o in opts]):
            cost = cost_links + sum(1 for p in pick if p)
            if best and cost > best[0]:
                continue
            weights = "".join(opts[k][p] for k, p in enumerate(pick))
            for name, feet, rarity in TEMPLATES:
                t = "".join(feet)
                if len(t) == len(weights) and t[:-1] == weights[:-1]:
                    shown = "|".join(feet)
                    shown = shown[:-1] + "×"
                    key = (cost, rarity)
                    if not best or key < best[:2]:
                        best = (cost, rarity, shown, name)
    if not best:
        return None, None, 0
    return best[2], best[3], best[0]


def line_metre(etoks: list[dict], edition: dict):
    words = [et.get("m") or et["n"] for et in etoks]
    shown, name, cost = scan(words)
    if not shown:
        return None, [("metre-not-rubai", " ".join(words))]
    return f"{shown} · {name}", []


LAYERS = {
    "translit": {"src": "Weft edition: hand transliteration in Early New Persian vowels, checked against the script"},
    "metre": {"src": f"weft.persian {VERSION}: syllable quantity from the transliteration, matched to the two rubāʿī patterns"},
}
SHOW_TRANSLIT = True

KEY = {
    "early": [
        ("", "Persian as Khayyam's contemporaries in Khorasan likely spoke it, around 1100. The vowels follow the grammarians, early manuscripts and the conservative eastern varieties (Dari, Tajik). The details are approximate, and the stress is placed by the modern rules."),
        ("CAPS", "the stressed syllable"),
        ("a, i, u", "short vowels: a as in father but short, i as in bit, u as in put"),
        ("aa, ee, oo", "long ā, ī, ū, held longer: father, machine, rule"),
        ("ê, ô", "the long 'unknown' (majhul) vowels ē and ō, as in café and go without a glide. Later Iranian Persian merged them with ee and oo"),
        ("ai, au", "the old diphthongs ay and aw: aisle, house"),
        ("dh", "d after a vowel, a soft th as in this"),
        ("kh", "as in Scottish loch; khw is a rounded kh, the xw of xwad 'self'"),
        ("gh, q", "gh a throaty g (French r); q a k made far back in the throat"),
        ("w", "as in English wet"),
        ("'", "a catch in the throat"),
    ],
    "modern": [
        ("", "Iranian Persian of Tehran today, as the quatrains are read aloud in Iran."),
        ("CAPS", "the stressed syllable"),
        ("a", "æ, as in cat"),
        ("aa", "ā, a back a, between father and law"),
        ("e, o", "short e as in bet, o as in go without a glide"),
        ("ee, oo", "as in machine, rule; length is no longer kept apart in speech"),
        ("ey, ow", "as in they, low"),
        ("kh", "as in Scottish loch"),
        ("gh", "q and ġ merged: a g made far back in the throat"),
        ("v", "the old w"),
    ],
}
SCHEME_LABELS = {
    "early": "Early New Persian: as spoken around 1100 (approximate)",
    "modern": "Modern Iranian Persian",
}
