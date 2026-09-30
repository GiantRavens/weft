"""Old Tamil: hand transliteration -> sound, Tamil script -> transliteration sensor, and kural metre.

Each token gives its transliteration (n) in ISO 15919, typed by hand from the Tamil script (t).
`tamil_to_iso` converts the script to the same transliteration so `weft draft` can check the two
against each other. Sound and metre are derived from the transliteration.

Schemes
-------
old-tamil  Old Tamil as the Tirukkural was most likely first recited, approximate. The date of the
           text is uncertain; estimates run from about the 4th to the 6th century AD, and some place
           it earlier. The rules follow the description of sounds in the Tolkāppiyam and the usual
           reconstructions of Old Tamil, and they are approximate. The six stops k c ṭ t p ṟ are
           voiceless at the start of a word and when doubled; after a nasal and between vowels
           they are voiced, as allophones the script does not write. c is a palatal stop. ṟ is a
           trilled r; doubled ṟṟ is an alveolar stop, and ṉṟ is alveolar nd. ḻ is the retroflex
           approximant. ḵ (āytam) is a weak fricative whose exact value is not known.
modern     Tamil as the Kural is commonly recited today. c is s (ch when doubled, j after a
           nasal); k between vowels is a soft gh; ṟṟ is tr and ṉṟ is ndr; a word-initial e or o
           takes a glide (ye, wo).

In both schemes a word-final u after a stop in a longer word is the shortened u
(kuṟṟiyalukaram), which the grammarians describe as half the length of a short vowel. Tamil has
no word stress that distinguishes meaning, so no syllable is written in capitals.

Metre
-----
A kural is a couplet in the kuṟaḷ veṇpā: four feet (cīr) in the first line and three in the
second. Each foot is made of metrical units (acai). A nēr is one syllable, short or long, with
any consonants that close it; a nirai is an open short syllable followed by a second syllable,
short or long. Feet are named by their units (tēmā = nēr nēr, puḷimā = nirai nēr, and so on).
A veṇpā admits only two-unit feet and three-unit feet ending in nēr (the -kāy feet); the last
foot is a single unit, or a unit plus a final shortened u (kācu, piṟappu). The link (taḷai)
between feet is fixed: after a -mā foot the next begins with nirai; after a -viḷam foot, or a
-kāy foot, it begins with nēr. Each printed word is one foot, as the edition divides them.
"""
from __future__ import annotations

import unicodedata as ud

VERSION = "0.1"

# ---------------------------------------------------------------- Tamil script -> ISO 15919
TA_VOWEL = {"அ": "a", "ஆ": "ā", "இ": "i", "ஈ": "ī", "உ": "u", "ஊ": "ū", "எ": "e", "ஏ": "ē",
            "ஐ": "ai", "ஒ": "o", "ஓ": "ō", "ஔ": "au"}
TA_SIGN = {"ா": "ā", "ி": "i", "ீ": "ī", "ு": "u", "ூ": "ū", "ெ": "e", "ே": "ē", "ை": "ai",
           "ொ": "o", "ோ": "ō", "ௌ": "au"}
TA_CONS = {"க": "k", "ங": "ṅ", "ச": "c", "ஞ": "ñ", "ட": "ṭ", "ண": "ṇ", "த": "t", "ந": "n",
           "ப": "p", "ம": "m", "ய": "y", "ர": "r", "ல": "l", "வ": "v", "ழ": "ḻ", "ள": "ḷ",
           "ற": "ṟ", "ன": "ṉ", "ஜ": "j", "ஷ": "ṣ", "ஸ": "s", "ஹ": "h"}
PULLI, AYTAM = "்", "ஃ"


def tamil_to_iso(text: str) -> str:
    """ISO 15919 transliteration of Tamil script. Spaces are kept; other marks are dropped.
    An independent i or u written after a consonant's inherent a is set off with a colon (a:i),
    as ISO 15919 does, so it is not read as the diphthong ai or au."""
    out: list[str] = []
    pending_a = False                       # a consonant waiting for its vowel
    for c in ud.normalize("NFC", text):
        if c in TA_CONS:
            if pending_a:
                out.append("a")
            out.append(TA_CONS[c]); pending_a = True
        elif c in TA_SIGN:
            out.append(TA_SIGN[c]); pending_a = False
        elif c == PULLI:
            pending_a = False
        elif c in TA_VOWEL:
            if pending_a:
                out.append("a")
                pending_a = False
            v = TA_VOWEL[c]
            if out and out[-1].endswith("a") and v in ("i", "u"):
                v = ":" + v
            out.append(v)
        elif c == AYTAM:
            if pending_a:
                out.append("a"); pending_a = False
            out.append("ḵ")
        else:
            if pending_a:
                out.append("a"); pending_a = False
            if c.isspace():
                out.append(" ")
    if pending_a:
        out.append("a")
    return "".join(out)


# ---------------------------------------------------------------- transliteration -> segments
SHORT = {"a", "i", "u", "e", "o"}
LONG = {"ā", "ī", "ū", "ē", "ō", "ai", "au"}
VOWELS = SHORT | LONG
STOPS = {"k", "c", "ṭ", "t", "p", "ṟ"}          # vallinam
NASALS = {"ṅ", "ñ", "ṇ", "n", "m", "ṉ"}          # mellinam


def segments(word: str) -> list[dict]:
    """Phonological segments {s, kind: V|C} from ISO 15919 transliteration."""
    w = ud.normalize("NFC", word.lower())
    segs: list[dict] = []
    i = 0
    while i < len(w):
        c = w[i]
        nxt = w[i + 1] if i + 1 < len(w) else ""
        if c == ":":                         # a:i, set off from the diphthong
            i += 1; continue
        if c == "a" and nxt in ("i", "u"):
            segs.append({"s": c + nxt, "kind": "V"}); i += 2; continue
        if c in VOWELS:
            segs.append({"s": c, "kind": "V"}); i += 1; continue
        if c.isalpha():
            segs.append({"s": c, "kind": "C"})
        i += 1
    return segs


def syllables(segs: list[dict]) -> list[dict]:
    """Tamil syllables: the consonant just before a vowel begins its syllable, and consonants
    written with the pulli close the syllable before (cēr-n-tār: cērn.tār).
    Each syllable is {segs, v (its vowel), long, closed}."""
    vi = [k for k, s in enumerate(segs) if s["kind"] == "V"]
    if not vi:
        return [{"segs": segs, "v": "", "long": False, "closed": True}]
    bounds = [0]
    for a, b in zip(vi, vi[1:]):
        bounds.append(b - 1 if b - 1 > a else b)
    bounds.append(len(segs))
    out = []
    for j, v in enumerate(vi):
        part = segs[bounds[j]:bounds[j + 1]]
        out.append({"segs": part, "v": segs[v]["s"], "long": segs[v]["s"] in LONG,
                    "closed": part[-1]["kind"] == "C"})
    return out


def is_kurriyalukaram(sylls: list[dict]) -> bool:
    """Word-final short u after a stop, in a word longer than one short open syllable plus u
    (atu, pacu keep a full u; ulaku, māṭṭu, aritu have the shortened one)."""
    if len(sylls) < 2:
        return False
    last = sylls[-1]
    if last["v"] != "u" or last["closed"] or len(last["segs"]) < 2 or last["segs"][-2]["s"] not in STOPS:
        return False
    first = sylls[0]
    return not (len(sylls) == 2 and not first["long"] and not first["closed"])


# ---------------------------------------------------------------- sound
IPA_V = {"a": "a", "ā": "aː", "i": "i", "ī": "iː", "u": "u", "ū": "uː", "e": "e", "ē": "eː",
         "o": "o", "ō": "oː", "ai": "aj", "au": "aw"}
RSP_V = {"a": "a", "ā": "aa", "i": "i", "ī": "ee", "u": "u", "ū": "oo", "e": "e", "ē": "ay",
         "o": "o", "ō": "oh", "ai": "ai", "au": "ow"}
IPA_C = {"ṅ": "ŋ", "ñ": "ɲ", "ṇ": "ɳ", "n": "n̪", "m": "m", "ṉ": "n", "y": "j", "r": "ɾ",
         "l": "l", "v": "ʋ", "ḻ": "ɻ", "ḷ": "ɭ", "j": "dʒ", "ṣ": "ʂ", "s": "s", "h": "h"}
RSP_C = {"ṅ": "ng", "ñ": "ny", "ṇ": "ṇ", "n": "n", "m": "m", "ṉ": "n", "y": "y", "r": "r",
         "l": "l", "v": "v", "ḻ": "zh", "ḷ": "ḷ", "j": "j", "ṣ": "ṣh", "s": "s", "h": "h"}
# stops: (voiceless, voiced) in IPA and respelling
STOP_OLD = {"k": ("k", "ɡ", "k", "g"), "c": ("c", "ɟ", "ch", "j"), "ṭ": ("ʈ", "ɖ", "ṭ", "ḍ"),
            "t": ("t̪", "d̪", "t", "d"), "p": ("p", "b", "p", "b")}


def _stop(segs: list[dict], k: int, scheme: str) -> tuple[str, str]:
    """IPA and respelling of the stop at segs[k], by position."""
    s = segs[k]["s"]
    prev = segs[k - 1] if k > 0 else None
    nxt = segs[k + 1] if k + 1 < len(segs) else None
    doubled = (prev and prev["s"] == s) or (nxt and nxt["s"] == s)
    after_nasal = prev is not None and prev["s"] in NASALS
    between = prev is not None and prev["kind"] == "V" and nxt is not None and nxt["kind"] == "V"
    voiced = (after_nasal or between) and not doubled
    if s == "ṟ":
        if scheme == "modern":
            if doubled:
                return ("t", "t") if nxt and nxt["s"] == "ṟ" else ("r", "r")
            return ("dr", "dr") if after_nasal else ("r", "ṟ")
        if doubled:
            return "t", "ṯ"
        return ("d", "d") if after_nasal else ("r", "ṟ")
    if scheme == "modern":
        if s == "c":
            if doubled:
                return ("t", "t") if nxt and nxt["s"] == "c" else ("tʃ", "ch")
            return ("dʒ", "j") if after_nasal else ("s", "s")
        if s == "k" and between:
            return "ɣ", "gh"
    vl_i, vd_i, vl_r, vd_r = STOP_OLD[s]
    return (vd_i, vd_r) if voiced else (vl_i, vl_r)


def phonemize(word: str, scheme: str = "old-tamil", quantities=None, **_) -> dict:
    segs = segments(word)
    sylls = syllables(segs)
    kurr = is_kurriyalukaram(sylls)
    # map each segment to (ipa, respelling)
    rend: list[tuple[str, str]] = []
    for k, s in enumerate(segs):
        if s["kind"] == "V":
            i, r = IPA_V[s["s"]], RSP_V[s["s"]]
            if kurr and k == len(segs) - 1:
                i, r = "ɯ", "ŭ"
            if scheme == "modern" and k == 0 and s["s"] in ("e", "ē", "o", "ō"):
                glide = ("j", "y") if s["s"] in ("e", "ē") else ("w", "w")
                i, r = glide[0] + i, glide[1] + r
            rend.append((i, r))
        elif s["s"] in STOPS:
            rend.append(_stop(segs, k, scheme))
        elif s["s"] == "ḵ":
            rend.append(("h", "h") if scheme == "modern" else ("x", "kh"))
        else:
            rend.append((IPA_C.get(s["s"], s["s"]), RSP_C.get(s["s"], s["s"])))
    ipa, rsp, k = [], [], 0
    for sy in sylls:
        n = len(sy["segs"])
        ipa.append("".join(x[0] for x in rend[k:k + n]))
        rsp.append("".join(x[1] for x in rend[k:k + n]))
        k += n
    return {"ipa": ud.normalize("NFC", ".".join(ipa)), "respell": "-".join(rsp), "syllables": len(sylls)}


# ---------------------------------------------------------------- metre (kuṟaḷ veṇpā)
NER, NIRAI = "nēr", "nirai"
FOOT2 = {(NER, NER): "tēmā", (NIRAI, NER): "puḷimā", (NIRAI, NIRAI): "karuviḷam", (NER, NIRAI): "kūviḷam"}
FINAL = {(NER,): "nāḷ", (NIRAI,): "malar", (NER, "bu"): "kācu", (NIRAI, "bu"): "piṟappu"}


def acai(sylls: list[dict]) -> list[str]:
    """Metrical units of one foot, left to right: an open short syllable takes the next syllable
    with it (nirai); anything else stands alone (nēr)."""
    out, i = [], 0
    while i < len(sylls):
        sy = sylls[i]
        if not sy["long"] and not sy["closed"] and i + 1 < len(sylls):
            out.append(NIRAI); i += 2
        else:
            out.append(NER); i += 1
    return out


def foot(word: str, final: bool = False) -> tuple[list[str], str]:
    """(units, name) for one foot. In the last foot of the couplet a final shortened u after a
    single unit is counted as the -bu of kācu or piṟappu."""
    sylls = syllables(segments(word))
    if final and is_kurriyalukaram(sylls):
        head = acai(sylls[:-1])
        if len(head) == 1:
            units = head + ["bu"]
            return units, FINAL[tuple(units)]
    units = acai(sylls)
    t = tuple(units)
    if final and t in FINAL:
        return units, FINAL[t]
    if len(t) == 2:
        return units, FOOT2[t]
    if len(t) == 3:
        base = FOOT2[t[:2]].replace("mā", "māṅ").replace("viḷam", "viḷaṅ")
        return units, base + ("kāy" if t[2] == NER else "kaṉi")
    return units, f"{len(t)}-unit foot"


def _link_ok(prev_units: list[str], prev_name: str, next_first: str) -> bool:
    """Veṇṭaḷai: after a -mā foot the next begins with nirai; after -viḷam or -kāy, with nēr."""
    if prev_name.endswith("kāy"):
        return next_first == NER
    if len(prev_units) == 2:
        return next_first == (NIRAI if prev_units[-1] == NER else NER)
    return False


def _where(etoks: list[dict], edition: dict) -> tuple[int, list | None]:
    """(line index within its kural, the kural's other line's tokens or None)."""
    for g in edition.get("sections") or []:
        lines = [ln for ln in g["lines"] if not isinstance(ln, str)]
        for k, ln in enumerate(lines):
            if ln["tokens"] is etoks:
                return k, (lines[0]["tokens"] if k == 1 else None)
    return 0, None


def line_metre(etoks: list[dict], edition: dict):
    """Metre string (foot name and units per foot, | between feet) and failure classes."""
    fails: list[tuple[str, str]] = []
    k, prev_line = _where(etoks, edition)
    last_line = k == 1
    words = [t["n"] for t in etoks]
    feet = [foot(w, final=last_line and j == len(words) - 1) for j, w in enumerate(words)]
    want = 3 if last_line else 4
    if len(feet) != want:
        fails.append(("kural-foot-count", f"{len(feet)} feet, the kuṟaḷ veṇpā wants {want}"))
    for j, (units, name) in enumerate(feet):
        is_last = last_line and j == len(feet) - 1
        if is_last:
            if name not in FINAL.values():
                fails.append(("venpa-final-foot", f"{words[j]}: {name}"))
        elif not (len(units) == 2 or name.endswith("kāy")):
            fails.append(("venpa-foot-type", f"{words[j]}: {name}"))
    # links between feet, including from the end of line 1 into line 2
    chain = list(zip(words, feet))
    if prev_line is not None:
        pw = prev_line[-1]["n"]
        chain = [(pw, foot(pw))] + chain
    for (w1, (u1, n1)), (w2, (u2, _)) in zip(chain, chain[1:]):
        if not _link_ok(u1, n1, u2[0]):
            fails.append(("venpa-talai", f"{w1} ({n1}) then {w2} ({u2[0]})"))
    # one span per foot (the page splits on |); the dot keeps the feet apart when the row is read
    text = "|".join(("· " if j else "") + f"{name} ({' '.join(units)})" for j, (units, name) in enumerate(feet))
    return text, fails


# ---------------------------------------------------------------- sensors
def line_checks(text: str, etoks: list[dict], edition: dict):
    """The hand transliteration must spell the printed Tamil script, word by word."""
    fails = []
    for t in etoks:
        got = tamil_to_iso(t["t"]).replace(" ", "")
        said = ud.normalize("NFC", t["n"]).replace(" ", "")
        if got != said:
            fails.append(("translit-mismatch", f"{t['t']}: script gives {got}, typed {said}"))
    return fails


LAYERS = {
    "translit": {"src": "Weft edition: hand-typed ISO 15919 transliteration, checked against the Tamil script"},
    "metre": {"src": f"weft.tamil {VERSION}: feet (cīr) and units (acai) from the transliteration, kuṟaḷ veṇpā rules"},
}
SHOW_TRANSLIT = True

KEY = {
    "old-tamil": [
        ("", "Old Tamil as the Kural was most likely first recited. The date of the text is uncertain (estimates run from about the 4th to the 6th century AD), and the sounds follow the old grammar Tolkāppiyam and modern reconstructions, so the reading is approximate."),
        ("no capitals", "Tamil stress does not change meaning; a light stress falls on the first syllable"),
        ("aa, ee, oo", "long vowels, held about twice as long"),
        ("ay, oh", "long e and o, single vowels as in they and go, without a glide"),
        ("ai, ow", "the diphthongs ai (as in aisle) and au (as in how)"),
        ("ŭ", "the shortened u at the end of a word after a stop, half the length of a short vowel"),
        ("t, d, n", "dental: the tongue against the upper teeth"),
        ("ṭ ḍ ṇ ḷ", "retroflex: the tongue tip curled back against the roof of the mouth"),
        ("zh", "ḻ, the retroflex approximant: the tongue curled back as for ṭ, without touching; no buzz"),
        ("g, j, ḍ, d, b", "k, c, ṭ, t, p between vowels or after a nasal: voiced, though the script writes one letter for both"),
        ("ch, j", "c: a palatal stop, the tongue flat against the hard palate"),
        ("ṟ", "a trilled r; ṯ is the doubled ṟṟ, an alveolar t (tongue on the gum ridge, as in English t)"),
        ("kh", "ḵ, the āytam: a weak fricative whose exact value is not known"),
    ],
    "modern": [
        ("", "Tamil as the Kural is commonly recited today."),
        ("no capitals", "Tamil stress does not change meaning; a light stress falls on the first syllable"),
        ("aa, ee, oo, ay, oh", "long vowels"),
        ("ŭ", "the shortened final u, said with the lips spread"),
        ("gh", "k between vowels: a soft g, the back of the tongue not quite closing"),
        ("s", "c is said s; doubled cc is ch, and c after a nasal is j"),
        ("t-r, ndr", "doubled ṟṟ is said tr, and ṉṟ ndr"),
        ("ye, wo", "a word-initial e or o takes a glide"),
        ("zh", "ḻ, the retroflex approximant"),
        ("ṭ ḍ ṇ ḷ", "retroflex consonants"),
    ],
}
SCHEME_LABELS = {
    "old-tamil": "Old Tamil: as the Kural was likely first recited (approximate)",
    "modern": "Modern Tamil recitation",
}
