"""Spanish sound layer (weft.spanish): Castilian of about 1492, then modern Castilian.

Scope. One work uses this module so far: Columbus's letter announcing the first voyage, in the
Spanish text printed at Barcelona in 1493. The printed spelling is kept in the edition (u for v,
fallé, nonbre, the Catalan-influenced spellings of the Barcelona compositor), and each token gives
its modern spelling by hand in `n`; the page shows it as "Modern spelling".

How the sound is made. Neither spelling is a safe guide to the sound of 1492 on its own: the print
is inconsistent (fallé and hallaron, i and y and e for the same conjunction, s for ss), and the
modern spelling has lost the distinctions that matter (s and ss, ç and z, x and j). So the 1492
form comes from a hand-written lexicon, `pipeline/weft/data/es_lexicon.yaml`, keyed by the modern
spelling. Each value is the word in a normalized spelling of the period, one letter per sound, in
the manner Nebrija recommends (Gramática de la lengua castellana, 1492, book 1, chapters 5-10;
Reglas de orthographía, 1517): ç and c before e/i, z, s, ss, x, j and g before e/i, h, v and b are
each read with one value, below. This module turns that spelling into IPA. An edition token may
override the lookup with `o` (the 1490s spelling for this occurrence: the conjunction printed e,
not y) or with `ipa` ({scheme: ipa}).

The modern form is computed from `n` by the rules of standard Castilian spelling, so a modern
reading needs no hand entry.

Schemes
-------
c1492    Castilian as an educated reader at the court of the Catholic Monarchs would have read the
         letter aloud in 1493, approximate. Evidence: Nebrija's Gramática (1492) and Reglas de
         orthographía (1517), which describe the letters as sounds; his Vocabulario
         español-latino (about 1495) for which words had aspirated h; and the modern synthesis in
         Rafael Lapesa, Historia de la lengua española, and Ralph Penny, A History of the Spanish
         Language, on the medieval sibilants. What the scheme assumes:
         - Six sibilants, three voiceless and three voiced: ç (and c before e, i) = [ts]; z =
           [dz]; ss, and s at the start or end of a word or next to a consonant = [s]; single s
           between vowels = [z]; x = [ʃ]; j, and g before e, i = [ʒ]. The s and z were apical
           (tongue tip raised, as in northern Spain today); the IPA writes plain s and z and the
           KEY says so. The devoicing and merger of these pairs began in the 16th century and is
           not applied. How far the [ts] and [dz] were already losing their stop element by 1492
           is uncertain; they are kept as affricates, the value Nebrija's descriptions support.
         - h from Latin f before a vowel (hallar, hermoso, hazer, hierro, hoja) is an aspiration
           [h]. Nebrija writes these words with h and treats h as a sound. The Barcelona print
           mostly keeps the older spelling f (fallé, fermosas, fazen, fierro, foia); that spelling
           was conservative by 1492, and a Castilian reader of the Toledo norm said [h]. Northern
           speakers (Old Castile) had already lost the aspiration, and a Portuguese or Italian
           reader would have said [f]. h from Latin h (hombres, haber, aunque) is silent. f
           before ue and r stays [f] (fue, frutos).
         - b and v are kept apart: b = [b], v (and u used as a consonant) = [β], a bilabial
           fricative. Medieval Castilian kept two phonemes in the middle of words (cabo with b,
           cavallo with v); at the start of words the distinction was weaker. The lexicon follows
           the spelling of the period for each word. The merger was under way and this point is
           uncertain.
         - ll = [ʎ], ñ = [ɲ], ch = [tʃ], y before a vowel = [ʝ], r tap and rr (and initial r)
           trill, as today.
         - Stress falls where it falls today in every word of the passage, by the same written
           rules. Learned words (illustríssimos, comemoración, concepción) are read with their
           letters.
         Columbus's own speech is NOT modelled. He was Genoese by birth, lived in Portugal for
         about a decade before coming to Castile, and his written Spanish shows Portuguese
         features (Ramón Menéndez Pidal, La lengua de Cristóbal Colón, 1940). The scheme models a
         Castilian reader of the printed text, not the writer.
modern   Standard Castilian of Spain today: c before e, i and z = [θ], j and g before e, i = [x],
         h silent, b and v both [b], ll = [ʝ] (yeísmo, the usual modern pronunciation). Broad
         transcription: the softening of b, d, g between vowels ([β ð ɣ]) is not shown.

Each word is phonemized alone. Synalepha and linking between words are not modelled. CAPS mark
the stressed syllable; clitics (articles, most prepositions, object pronouns, que) carry none.

Edition token fields (texts/<work>/edition.yaml)
-----------------------------------------------
t      the word as printed, punctuation attached (Señor:, ésta,); split off into punct
n      the modern spelling; lowercase except proper names. Two words for a contraction (della ->
       de ella), each phonemized
o      the 1490s spelling for this occurrence, overriding the lexicon (the conjunction e)
ipa    {scheme: ipa} override for this occurrence
"""
from __future__ import annotations

import re
import unicodedata as ud
from pathlib import Path

import yaml

VERSION = "0.1"
SHOW_TRANSLIT = True
TRANSLIT_LABEL = "Modern spelling"

_LEX: dict | None = None
_CTX: dict = {}

LEAD_P = re.compile(r"^([(¿¡«“]+)")
TRAIL_P = re.compile(r"([,.;:!?)»”]+)$")
STRONG = set("aeo")
WEAK = set("iu")
ACUTE = {"á": "a", "é": "e", "í": "i", "ó": "o", "ú": "u"}
# unstressed words: articles, the common prepositions and conjunctions, object pronouns,
# possessives before a noun, the relatives que and the proclitic San
CLITICS = {"el", "la", "lo", "los", "las", "un", "a", "al", "de", "del", "en", "con", "por", "sin",
           "para", "pa", "que", "y", "e", "i", "o", "ni", "me", "te", "se", "nos", "os", "vos", "le",
           "les", "mi", "tu", "su", "sus", "mis", "tus", "san", "sant"}


def lexicon() -> dict:
    global _LEX
    if _LEX is None:
        p = Path(__file__).parent / "data" / "es_lexicon.yaml"
        _LEX = {ud.normalize("NFC", k): v for k, v in (yaml.safe_load(p.read_text(encoding="utf-8")) or {}).items()}
    return _LEX


def key(word: str) -> str:
    return ud.normalize("NFC", word).lower()


# ---------------------------------------------------------------- spelling -> segments
def _segments(word: str, scheme: str) -> list[list]:
    """Spelling -> list of [phoneme, kind, written_accent]; kind is 'V' (vowel) or 'C'."""
    w = ud.normalize("NFC", word.lower())
    old = scheme == "c1492"
    out: list[list] = []
    i = 0
    n = len(w)

    def at(k):
        return w[k] if 0 <= k < n else ""

    def vowel_letter(ch):
        return bool(ch) and ch in "aeiouáéíóúü"

    while i < n:
        c, nx = w[i], at(i + 1)
        if c in ACUTE:
            out.append([ACUTE[c], "V", True]); i += 1; continue
        if c in "aeiou":
            out.append([c, "V", False]); i += 1; continue
        if c == "ü":
            out.append(["u", "V", False]); i += 1; continue
        if c == "y":
            # y before a vowel is a consonant; otherwise the vowel i (rey, muy, y)
            if vowel_letter(nx):
                out.append(["ʝ", "C", False])
            else:
                out.append(["i", "V", False])
            i += 1; continue
        if c == "c":
            if nx == "h":
                out.append(["tʃ", "C", False]); i += 2; continue
            if nx in "eéiíy" and nx:
                out.append(["ts" if old else "θ", "C", False]); i += 1; continue
            out.append(["k", "C", False]); i += 1; continue
        if c == "ç":
            out.append(["ts", "C", False]); i += 1; continue
        if c == "z":
            out.append(["dz" if old else "θ", "C", False]); i += 1; continue
        if c == "q":
            # qu before e, i: k (u silent); before a, o: kw (quando, qual in the old spelling)
            if nx == "u" and at(i + 2) in ("e", "i", "é", "í"):
                out.append(["k", "C", False]); i += 2; continue
            out.append(["k", "C", False]); i += 1; continue
        if c == "g":
            if nx == "u" and at(i + 2) in ("e", "i", "é", "í"):
                out.append(["g", "C", False]); i += 2; continue
            if nx in ("e", "i", "é", "í"):
                out.append(["ʒ" if old else "x", "C", False]); i += 1; continue
            out.append(["g", "C", False]); i += 1; continue
        if c == "j":
            out.append(["ʒ" if old else "x", "C", False]); i += 1; continue
        if c == "x":
            if old:
                out.append(["ʃ", "C", False])
            else:
                out.append(["k", "C", False]); out.append(["s", "C", False])
            i += 1; continue
        if c == "h":
            if old:
                out.append(["h", "C", False])
            i += 1; continue
        if c == "l" and nx == "l":
            out.append(["ʎ" if old else "ʝ", "C", False]); i += 2; continue
        if c == "r":
            if nx == "r":
                out.append(["r", "C", False]); i += 2; continue
            prev = at(i - 1)
            out.append(["r" if i == 0 or prev in ("l", "n", "s") else "ɾ", "C", False]); i += 1; continue
        if c == "s":
            if old:
                if nx == "s":
                    out.append(["s", "C", False]); i += 2; continue
                voiced = vowel_letter(at(i - 1)) and vowel_letter(nx)
                out.append(["z" if voiced else "s", "C", False]); i += 1; continue
            out.append(["s", "C", False]); i += 1; continue
        if c == "v":
            out.append(["β" if old else "b", "C", False]); i += 1; continue
        if c == "ñ":
            out.append(["ɲ", "C", False]); i += 1; continue
        if c in "bdfklmnptw":
            out.append([c, "C", False]); i += 1; continue
        if c in "-’'":
            i += 1; continue
        out.append([c, "C", False]); i += 1
    return out


ONSETS = {"pɾ", "bɾ", "tɾ", "dɾ", "kɾ", "gɾ", "fɾ", "βɾ", "pl", "bl", "kl", "gl", "fl", "βl"}


def _syllabify(segs: list[list]) -> tuple[list[list[str]], int | None]:
    """Glides, nuclei, consonant division. Returns syllables (lists of phonemes) and the index of
    the syllable holding a written accent, if any."""
    # glides: an unaccented weak vowel next to another vowel; of two weak vowels the first glides
    k = len(segs)
    for j, (p, kind, acc) in enumerate(segs):
        if kind != "V" or acc or p not in WEAK:
            continue
        prev = segs[j - 1] if j > 0 else None
        nxt = segs[j + 1] if j + 1 < k else None
        nv = nxt and nxt[1] == "V"
        pv = prev and prev[1] == "V" and prev[0] != "_"
        if nv and (nxt[0] in STRONG or (nxt[0] in WEAK)):
            segs[j] = [{"i": "j", "u": "w"}[p], "G", False]
        elif pv and (prev[0] in STRONG):
            segs[j] = [{"i": "j", "u": "w"}[p], "G", False]
    # nuclei: each vowel; a strong vowel after another strong vowel starts a new syllable
    nuclei = [j for j, s in enumerate(segs) if s[1] == "V"]
    if not nuclei:
        return [[s[0] for s in segs]], None
    bounds = []          # start index of each syllable
    for a, b in zip(nuclei, nuclei[1:]):
        between = list(range(a + 1, b))
        cons = [j for j in between if segs[j][1] == "C"]
        if not cons:
            # hiatus (two vowels) or vowel-glide-vowel: the glide opens the next syllable
            gl = [j for j in between if segs[j][1] == "G"]
            bounds.append(gl[0] if gl else b)
            continue
        # a glide right after the first vowel closes its syllable (aunque, reina); one right
        # before the second opens it (tierra). The consonants divide before the last one, or
        # before an obstruent + liquid onset (pobladas, contradicho)
        if len(cons) == 1:
            start = cons[0]
        else:
            last2 = segs[cons[-2]][0] + segs[cons[-1]][0]
            start = cons[-2] if (last2 in ONSETS and cons[-1] == cons[-2] + 1) else cons[-1]
        bounds.append(start)
    sylls, idx = [], 0
    for bnd in bounds + [len(segs)]:
        sylls.append(list(range(idx, bnd)))
        idx = bnd
    acc_syll = None
    for si, sy in enumerate(sylls):
        if any(segs[j][2] for j in sy):
            acc_syll = si
    return [[segs[j][0] for j in sy] for sy in sylls], acc_syll


def _stress(word: str, sylls: list, acc: int | None) -> int | None:
    if acc is not None:
        return acc
    w = key(word).strip("-’'")
    if w in CLITICS:
        return None
    if len(sylls) == 1:
        return 0
    last = w[-1:]
    return len(sylls) - 2 if last in "aeiouns" else len(sylls) - 1


def word_ipa(word: str, scheme: str) -> tuple[str, int]:
    segs = _segments(word, scheme)
    sylls, acc = _syllabify(segs)
    st = _stress(word, sylls, acc)
    parts = []
    for si, sy in enumerate(sylls):
        s = "".join(sy)
        if si == st:
            parts.append("ˈ" + s)
        else:
            parts.append(("." if parts else "") + s)
    ipa = "".join(parts)
    return ipa, len(sylls)


# ---------------------------------------------------------------- IPA -> respelling
RESPELL = [("tʃ", "ch"), ("ts", "ts"), ("dz", "dz"), ("ʃ", "sh"), ("ʒ", "zh"), ("ʎ", "ly"),
           ("ɲ", "ny"), ("ʝ", "y"), ("β", "v"), ("θ", "th"), ("x", "kh"), ("ɾ", "r"), ("r", "rr"),
           ("j", "y"), ("w", "w"), ("a", "ah"), ("e", "eh"), ("i", "ee"), ("o", "oh"), ("u", "oo"),
           ("ɡ", "g")]


def _respell_syll(s: str) -> str:
    out, i = "", 0
    while i < len(s):
        for a, b in RESPELL:
            if s.startswith(a, i):
                out += b
                i += len(a)
                break
        else:
            out += s[i]
            i += 1
    return out


def respell(ipa: str) -> str:
    words = []
    for w in ipa.split(" "):
        sylls = re.split(r"(?=ˈ)|\.", w)
        parts = []
        for sy in sylls:
            if not sy:
                continue
            if sy.startswith("ˈ"):
                parts.append(_respell_syll(sy[1:]).upper())
            else:
                parts.append(_respell_syll(sy))
        words.append("-".join(parts))
    return " ".join(words)


# ---------------------------------------------------------------- the 1490s spelling
def old_spelling(n: str) -> str | None:
    """The lexicon's 1490s spelling for a modern form (one or more words)."""
    v = lexicon().get(key(n))
    if isinstance(v, dict):
        v = v.get("c1492")
    return v


def sibilants(spelling: str) -> list[str]:
    """The sibilant letters of a spelling, read with their 1490s values: ts dz s z ʃ. Used to
    compare the print with the lexicon; j, g and i (which the print uses for j) are left out
    because the print's i does not tell vowel from consonant."""
    w = re.sub(r"[^a-zçñ]", "", ud.normalize("NFD", spelling.lower()).replace("̧", "ç"))
    w = ud.normalize("NFC", w)
    out, i = [], 0
    vow = set("aeiouy")
    while i < len(w):
        c = w[i]
        nx = w[i + 1] if i + 1 < len(w) else ""
        if c == "ç" or (c == "c" and nx in "eiy" and nx):
            out.append("ts")
        elif c == "z":
            out.append("dz")
        elif c == "x":
            out.append("ʃ")
        elif c == "s":
            if nx == "s":
                out.append("s"); i += 2; continue
            prev = w[i - 1] if i else ""
            out.append("z" if prev in vow and nx in vow and prev and nx else "s")
        i += 1
    return out


def phon_ipa(n: str, scheme: str, override: str | None = None) -> tuple[str, int]:
    if scheme == "c1492":
        sp = override or old_spelling(n)
        if not sp:
            return "?", 0
    else:
        sp = n
    ipas, total = [], 0
    for part in sp.split():
        ip, k = word_ipa(part, scheme)
        ipas.append(ip)
        total += k
    return " ".join(ipas), total


# ---------------------------------------------------------------- hooks
def token_fields(surface: str, et: dict, group: dict) -> tuple[dict, list[tuple[str, str]]]:
    """Split punctuation off the printed word, check the lexicon, and compare the sibilant letters
    of the print with the 1490s spelling the lexicon gives (a sensor: a difference is either a
    printing habit, such as s for ss, or a lexicon error)."""
    global _CTX
    fields: dict = {}
    fails: list[tuple[str, str]] = []
    word = surface
    ml = LEAD_P.search(word)
    if ml:
        fields["lead"] = ml.group(1)
        word = word[ml.end():]
    mt = TRAIL_P.search(word)
    if mt:
        fields["punct"] = mt.group(1)
        word = word[:mt.start()]
    if word != surface:
        fields["surface"] = word
    n = et.get("n")
    _CTX = {"n": n, "o": et.get("o"), "ipa": et.get("ipa") or {}}
    if not n:
        fails.append(("modern-spelling-missing", surface))
        return fields, fails
    old = et.get("o") or old_spelling(n)
    if not old and not (et.get("ipa") or {}).get("c1492"):
        fails.append(("lexicon-missing", n))
        return fields, fails
    if old:
        printed = word.replace("[", "").replace("]", "")
        if sibilants(printed) != sibilants(old.replace(" ", "")):
            fails.append(("print-sibilant-differs", f"{printed} / {old}"))
    return fields, fails


def phonemize(word: str, scheme: str = "c1492", quantities=None, **_) -> dict:
    """`word` is the token's modern spelling (n)."""
    ctx = _CTX if _CTX.get("n") == word else {}
    ov = (ctx.get("ipa") or {}).get(scheme)
    if ov:
        ipa = ov
        syl = len([p for p in re.split(r"[.ˈ ]", ov) if p])
    else:
        ipa, syl = phon_ipa(word, scheme, ctx.get("o") if scheme == "c1492" else None)
    return {"ipa": ipa, "respell": respell(ipa) if ipa != "?" else "?", "syllables": syl}


def line_checks(text: str, etoks: list[dict], edition: dict) -> list[tuple[str, str]]:
    """Sensor: stress should fall on the same syllable (counted from the end of the word) in both
    schemes; the scheme assumes no stress shift since 1492, so a difference is a lexicon error."""
    out = []
    for t in etoks:
        n = t.get("n")
        if not n or t.get("ipa"):
            continue
        a, _ = phon_ipa(n, "c1492", t.get("o"))
        b, _ = phon_ipa(n, "modern")
        if a == "?":
            continue

        def pos(ipa):
            res = []
            for w in ipa.split(" "):
                sy = [s for s in re.split(r"(?=ˈ)|\.", w) if s]
                res.append(next((len(sy) - k for k, s in enumerate(sy) if s.startswith("ˈ")), 0))
            return res
        pa, pb = pos(a), pos(b)
        if len(pa) != len(pb):
            # a contraction (della, desta) is one word in 1492 and two today: compare the last
            pa, pb = pa[-1:], pb[-1:]
        if pa != pb:
            out.append(("stress-differs-between-schemes", f"{t['t']} {a} / {b}"))
    return out


KEY = {
    "c1492": [
        ("", "Castilian of about 1492, as Nebrija describes the letters; approximate. A Castilian reader of the printed letter is modelled, not Columbus's own Genoese and Portuguese-coloured Spanish."),
        ("", "Hyphens divide syllables; CAPS mark the stressed syllable. Articles, most prepositions and object pronouns are unstressed."),
        ("ah eh ee oh oo", "the five vowels, as in father, bet, machine, note, rule, but short and pure"),
        ("ts", "ç, and c before e or i (plazer is plah-DZEHR, concepción kohn-tsehp-TSYOHN): t and s together, as in cats"),
        ("dz", "z (plazer, altezas, hazen): d and z together, as in adze"),
        ("s z", "s and z with the tip of the tongue raised toward the gums (apical), a sound between s and sh, as in northern Spain today. Single s between vowels is voiced z (cosa, KOH-zah); ss is voiceless (assí)"),
        ("sh", "x (not in this passage), as in ship"),
        ("zh", "j, and g before e or i (gente, mugeres, Juana): the s of measure"),
        ("h", "aspirated, as in English hat, in words with h from Latin f (hallar, hermoso, hazer, hierro, hoja), which the print still writes with f (fallé, fermosas, fazen). Silent where the h comes from Latin h (hombres, haber)"),
        ("v", "v, and u used as a consonant (uandera, marauilla): made with both lips, not lip and teeth; distinct from b in most words in 1492, though the two were merging"),
        ("ly", "ll (llaman, della): the lli of million said as one sound"),
        ("ny", "ñ (señor): the ny of canyon"),
        ("y", "y before a vowel (yo, aya): as in yes, with more friction"),
        ("r rr", "r is a single tap of the tongue, as in American butter; rr, and r at the start of a word, is trilled"),
    ],
    "modern": [
        ("", "Standard Castilian of Spain today. Hyphens divide syllables; CAPS mark the stressed syllable. Broad transcription."),
        ("ah eh ee oh oo", "the five vowels, short and pure"),
        ("th", "c before e or i, and z: as in thin (distinción, the usage of central and northern Spain)"),
        ("kh", "j, and g before e or i: as ch in Scottish loch"),
        ("y", "y and ll (yeísmo, the usual modern pronunciation): as in yes, with more friction"),
        ("ny", "ñ: the ny of canyon"),
        ("r rr", "r is a single tap; rr, and r at the start of a word, is trilled"),
        ("", "h is silent; b and v are the same sound (softened between vowels, not shown)"),
    ],
}
SCHEME_LABELS = {"c1492": "Castilian about 1492: Nebrija's day (approximate)",
                 "modern": "Modern Castilian"}
