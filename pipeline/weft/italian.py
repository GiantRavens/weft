"""Italian sound layer (weft.italian): Florentine of the author's day, then standard modern Italian.

Scope. Two works use this module: Petrarch's Canzoniere, sonnet 1 (composed about 1350) and
Machiavelli's Il Principe, chapters 17 and 18 (written 1513). Both wrote a literary Florentine.

Scheme `florentine` (first, the default) is one reconstruction for both dates. The evidence does
not support a separate reconstruction for 1350 and 1513 in the features a per-word respelling can
show, so the two works share it and each dates it through `scheme_labels` in its manifest. The
reconstruction is approximate. What it assumes:

- Spelling is read as written. Latinizing spellings of the period (et, cognoscere, esperienzia,
  osservanzia) are pronounced from the letters, except `et`, which the lexicon reads as e, as
  Italian readers did. This is the weakest assumption: some of these spellings may be learned
  ornament rather than speech.
- Open and closed e and o (è ɛ / é e, ò ɔ / ó o) under stress come from the lexicon
  (pipeline/weft/data/it_lexicon.yaml). Each entry follows the Florentine-based standard as
  recorded in the DOP (Migliorini, Tagliavini, Fiorelli, Dizionario d'ortografia e di pronunzia),
  checked against the Latin source vowel (Latin short e and o give open vowels, long e and o and
  short i and u give closed ones). Modern Florentine keeps the medieval distribution in nearly all
  inherited words; learned words (bestia, obbligo) follow the DOP and are less certain for these
  dates. Unstressed e and o are closed.
- Stressed vowels in an open syllable that is not word-final are long; the IPA shows it.
- ʎ, ɲ, ʃ, ts and dz between vowels are long (geminate), as written double consonants are.
- s between vowels is voiceless [s] unless the lexicon marks it voiced (ŝ), as in Tuscan speech
  (casa, cosa with [s]; bisogno, uso with [z]). s before a voiced consonant is [z].
- The gorgia toscana (k t p between vowels softened to h θ ɸ, as in present-day Florence) is NOT
  applied. It is not securely attested in writing before the sixteenth century; whether
  Machiavelli's Florence had it is uncertain, and for Petrarch's day there is no positive
  evidence. The same holds for the softening of intervocalic c and g before e and i to ʃ and ʒ.
- Each word is phonemized alone. Syntactic doubling (raddoppiamento sintattico: a casa said
  [akˈkaːsa]) and elision across words are not modeled in the sound row; synalepha is modeled in
  the verse metre only.

Scheme `modern` is standard Italian today. It differs from `florentine` in one systematic feature
a per-word respelling can show: s between vowels is voiced [z] in every word, as in most of Italy
today (the DOP records this as the accepted modern variant). Stress and vowel quality are shared.

Lexicon marking (the lexicon value is a marked spelling, not IPA): à è é ì ò ó ù mark the stressed
vowel (è ò open, é ó closed); ï ü a vowel i or u that would otherwise be a glide; ŝ a voiced s;
ś an s that stays voiceless between vowels in both schemes (a word boundary inside, as in
trovandosi); ẑ a voiced z [dz]. An entry with no mark is unstressed (an article, a clitic, a
preposition). A word missing from the lexicon is stressed by rule (a written final accent, else
the next-to-last vowel), read with closed e and o, and reported as pron-not-in-lexicon.

Verse metre (`line_metre`, used by the sonnet): the Italian count of an endecasillabo, syllables
up to and including the one after the last accent, with synalepha across words, synaeresis of a
stressed i before a final vowel (mio, io, sia), and accents from the lexicon. The rhyme is compared
by spelling from the stressed vowel to the end of the line, as Italian poets rhymed (open and
closed vowels may rhyme). A token's `m` field in the edition overrides its metrical syllables.
"""
from __future__ import annotations

import re
import unicodedata
from pathlib import Path

import yaml

VERSION = "0.1"

LEXICON_PATH = Path(__file__).parent / "data" / "it_lexicon.yaml"
_LEX: dict | None = None


def lexicon() -> dict:
    global _LEX
    if _LEX is None:
        _LEX = yaml.safe_load(LEXICON_PATH.read_text(encoding="utf-8")) or {}
    return _LEX


PUNCT_TRAIL = re.compile(r"([,.;:!?»”)]+)$")
PUNCT_LEAD = re.compile(r"^([«“(]+)")
STRESS_MARKS = {"à": "a", "è": "ɛ", "é": "e", "ì": "i", "í": "i", "ò": "ɔ", "ó": "o", "ù": "u", "ú": "u"}
VOWELS = set("aeiou") | set(STRESS_MARKS) | {"ï", "ü"}
FRONT = set("eiéèìí")
STOPS = set("pbtdkgfv")
LIQUIDS = set("rl")
VOICED_C = set("bdglmnrv")
LONG_INTERVOCALIC = {"ʎ", "ɲ", "ʃ", "ts", "dz"}


def key(word: str) -> str:
    """Lexicon key: lower case, typographic apostrophe as ', punctuation removed."""
    w = word.replace("’", "'").replace("‘", "'").lower()
    w = PUNCT_LEAD.sub("", PUNCT_TRAIL.sub("", w))
    return unicodedata.normalize("NFC", w)


def marked_form(word: str, table: dict | None = None) -> tuple[str, bool]:
    """(marked spelling, known). The lexicon wins; a word typed with marks is taken as marked."""
    table = lexicon() if table is None else table
    k = key(word)
    if k in table:
        return str(table[k]), True
    if any(c in "èéìíòóùúŝẑïüś" for c in k):     # an explicit reading (edition `n`) is already marked
        return k, True
    return k, False


# ---------------------------------------------------------------- spelling to phonemes
def _phonemes(m: str, scheme: str) -> list[dict]:
    """Marked spelling -> list of {p: phoneme, v: is-vowel, s: stressed, g: glide}."""
    w = m.replace("'", "")
    out: list[dict] = []
    i, n = 0, len(w)

    def vowel_at(k):
        return k < n and w[k] in VOWELS

    def add(p, **kw):
        out.append({"p": p, "v": False, "s": False, **kw})

    while i < n:
        c = w[i]
        nxt = w[i + 1] if i + 1 < n else ""
        nxt2 = w[i + 2] if i + 2 < n else ""
        if c in VOWELS:
            if c in STRESS_MARKS:
                out.append({"p": STRESS_MARKS[c], "v": True, "s": True})
            elif c in "ïü":
                out.append({"p": "i" if c == "ï" else "u", "v": True, "s": False})
            else:
                out.append({"p": c, "v": True, "s": False, "plain": True})
            i += 1
            continue
        if c == "h":
            i += 1; continue
        # c, g, sc before front vowels; a plain i after them before a vowel is only a spelling
        if c == "s" and nxt == "c" and nxt2 in FRONT:
            add("ʃ"); i += 2
            if w[i] == "i" and vowel_at(i + 1):
                i += 1
            continue
        if c == "c" and nxt == "c" and nxt2 in FRONT:
            add("t"); add("tʃ"); i += 2
            if w[i] == "i" and vowel_at(i + 1):
                i += 1
            continue
        if c == "g" and nxt == "g" and nxt2 in FRONT:
            add("d"); add("dʒ"); i += 2
            if w[i] == "i" and vowel_at(i + 1):
                i += 1
            continue
        if c in "cg" and nxt in FRONT:
            add("tʃ" if c == "c" else "dʒ"); i += 1
            if w[i] == "i" and vowel_at(i + 1):
                i += 1
            continue
        if c in "cg" and nxt == "h":
            add("k" if c == "c" else "g"); i += 2; continue
        if c == "g" and nxt == "l" and nxt2 == "i":
            add("ʎ"); i += 2
            if vowel_at(i + 1):
                i += 1                      # gli + vowel: the i only spells ʎ
            continue
        if c == "g" and nxt == "n":
            add("ɲ"); i += 2; continue
        if c == "c" and nxt == "q":
            add("k"); i += 1; continue      # cqu: k + kw
        if c == "q" and nxt == "u":
            add("k"); add("w", g=True); i += 2; continue
        if c == "g" and nxt == "u" and vowel_at(i + 2) and w[i + 2] not in "ù":
            add("g"); add("w", g=True); i += 2; continue
        if c == "c":
            add("k"); i += 1; continue
        if c == "x":
            add("k"); add("s"); i += 1; continue
        if c == "j":
            add("j", g=True); i += 1; continue
        if c in "zẑ":
            add("dz" if c == "ẑ" else "ts"); i += 1; continue
        if c in "sŝś":
            add("z" if c == "ŝ" else "s", fixed=(c == "ś")); i += 1; continue
        add(c); i += 1

    # glides: a plain i or u next to a vowel, unstressed, is j or w
    for k, ph in enumerate(out):
        if ph["v"] and ph.get("plain") and ph["p"] in "iu":
            before = out[k - 1] if k else None
            after = out[k + 1] if k + 1 < len(out) else None
            if (after and after["v"]) or (before and before["v"] and not (after and after["v"])):
                ph.update(p="j" if ph["p"] == "i" else "w", v=False, g=True)
    # doubled letters: two identical consonants in a row stay, written as one long consonant
    # inherent length: ʎ ɲ ʃ ts dz between vowels (or vowel and glide) are long
    res: list[dict] = []
    for k, ph in enumerate(out):
        prev = res[-1] if res else None
        nxt_ph = out[k + 1] if k + 1 < len(out) else None
        if ph["p"] in LONG_INTERVOCALIC and prev and (prev["v"] or prev.get("g")) and nxt_ph and (nxt_ph["v"] or nxt_ph.get("g")):
            if not (prev["p"] in ("t", "d") and ph["p"] in ("ts", "dz")):
                if ph["p"] in ("ts", "dz"):
                    res.append({"p": ph["p"][0], "v": False, "s": False})
                else:
                    res.append(dict(ph))
        # zz written double: t + ts, d + dz
        if prev and prev["p"] in ("ts", "dz") and ph["p"] == prev["p"]:
            res[-1] = {"p": prev["p"][0], "v": False, "s": False}
        res.append(ph)
    # s voicing
    for k, ph in enumerate(res):
        if ph["p"] != "s" or ph.get("fixed"):
            continue
        prev = res[k - 1] if k else None
        nxt_ph = res[k + 1] if k + 1 < len(res) else None
        if nxt_ph and not nxt_ph["v"] and nxt_ph["p"] in VOICED_C and not nxt_ph.get("g"):
            ph["p"] = "z"
        elif scheme == "modern" and prev and nxt_ph and (prev["v"] or prev.get("g")) and nxt_ph["v"]:
            ph["p"] = "z"
    # n before a velar is ŋ
    for k, ph in enumerate(res[:-1]):
        if ph["p"] == "n" and res[k + 1]["p"] in ("k", "g"):
            ph["p"] = "ŋ"
    return res


def _syllables(ph: list[dict]) -> list[list[dict]]:
    """Split before the last consonant of a cluster; stop + liquid and glides go to the onset."""
    nuclei = [k for k, p in enumerate(ph) if p["v"]]
    if not nuclei:
        return [ph] if ph else []
    syls, start = [], 0
    for a, b in zip(nuclei, nuclei[1:]):
        between = list(range(a + 1, b))
        onset_from = b
        # glides immediately before the next vowel belong to its onset
        while between and ph[between[-1]].get("g") and onset_from - 1 == between[-1]:
            onset_from = between.pop()
        cons = between
        if len(cons) >= 2 and ph[cons[-2]]["p"] in STOPS and ph[cons[-1]]["p"] in LIQUIDS:
            onset_from = cons[-2]
        elif cons:
            onset_from = cons[-1]
        syls.append(ph[start:onset_from])
        start = onset_from
    syls.append(ph[start:])
    return syls


IPA_V = {"a": "a", "e": "e", "ɛ": "ɛ", "i": "i", "o": "o", "ɔ": "ɔ", "u": "u"}
RESPELL = {"a": "a", "e": "ay", "ɛ": "e", "i": "ee", "o": "oh", "ɔ": "aw", "u": "oo",
           "j": "y", "w": "w", "tʃ": "ch", "dʒ": "j", "ʃ": "sh", "ɲ": "ny", "ʎ": "ly",
           "ts": "ts", "dz": "dz", "ŋ": "n", "k": "k", "g": "g"}
DIPH = {("ɔ", "j"): "oy", ("o", "j"): "oy", ("e", "j"): "ay", ("ɛ", "j"): "ey", ("a", "j"): "ai",
        ("u", "j"): "ooy", ("a", "w"): "ow", ("e", "w"): "ew", ("ɛ", "w"): "ew"}
CODA_HALF = {"ʎ": "l", "ɲ": "n", "ʃ": "sh", "tʃ": "t", "dʒ": "d"}


def _render(syls: list[list[dict]]) -> tuple[str, str, int | None]:
    stress = next((k for k, s in enumerate(syls) if any(p["s"] for p in s)), None)
    nsyl = len(syls)
    ipa_parts, resp_parts = [], []
    for k, s in enumerate(syls):
        ipa, rs = "", ""
        nuc = next((j for j, p in enumerate(s) if p["v"]), None)
        long_v = k == stress and k < nsyl - 1 and nuc is not None and nuc == len(s) - 1
        ipa = "".join(p["p"] + ("ː" if p["v"] and long_v else "") for p in s)
        for j, p in enumerate(s):
            if p["v"] and j + 1 < len(s) and (p["p"], s[j + 1]["p"]) in DIPH and j + 1 == len(s) - 1:
                rs += DIPH[(p["p"], s[j + 1]["p"])]
                break
            # first half of a long ʎ ɲ ʃ (or of cc, gg) closes the syllable
            if j == len(s) - 1 and not p["v"] and k + 1 < nsyl and syls[k + 1] and p["p"] in CODA_HALF:
                rs += CODA_HALF[p["p"]]
            else:
                rs += RESPELL.get(p["p"], p["p"])
        ipa_parts.append(("ˈ" if k == stress else "") + ipa)
        resp_parts.append(rs.upper() if k == stress else rs)
    return ".".join(ipa_parts), "-".join(resp_parts), stress


def _fallback(k: str) -> str:
    """No lexicon entry: stress a written final accent, else the next-to-last vowel."""
    if any(c in STRESS_MARKS for c in k):
        return k
    vs = [j for j, c in enumerate(k) if c in "aeiou"]
    # i or u before another vowel is a glide, not a stress-bearing vowel
    vs = [j for j in vs if not (k[j] in "iu" and j + 1 < len(k) and k[j + 1] in "aeiou")]
    if len(vs) < 2:
        return k
    j = vs[-2]
    acc = {"a": "à", "e": "é", "i": "ì", "o": "ó", "u": "ù"}[k[j]]
    return k[:j] + acc + k[j + 1:]


def analyse(word: str, scheme: str = "florentine", table: dict | None = None) -> dict:
    m, known = marked_form(word, table)
    if not known:
        m = _fallback(m)
    ph = _phonemes(m, scheme)
    syls = _syllables(ph)
    return {"marked": m, "known": known, "syls": syls}


def phonemize(word: str, scheme: str = "florentine", quantities=None, **_) -> dict:
    a = analyse(word, scheme, quantities or None)
    if not a["syls"]:
        return {"ipa": "", "respell": "", "syllables": 0}
    ipa, resp, _ = _render(a["syls"])
    return {"ipa": ipa, "respell": resp, "syllables": sum(1 for s in a["syls"] if any(p["v"] for p in s)),
            "known": a["known"]}


# ---------------------------------------------------------------- language hooks
def token_fields(surface: str, et: dict, group: dict):
    """The edition keeps punctuation in `t` so each line reproduces its source; here it moves to
    `punct` (and `lead`), and the lexicon sensor runs."""
    fields, fails = {}, []
    core = surface
    mt = PUNCT_TRAIL.search(core)
    if mt:
        fields["punct"] = mt.group(1)
        core = core[:mt.start()]
    ml = PUNCT_LEAD.search(core)
    if ml:
        fields["lead"] = ml.group(1)
        core = core[ml.end():]
    if core != surface:
        fields["surface"] = core
    if not et.get("n") and key(core) not in lexicon():
        fails.append(("pron-not-in-lexicon", core))
    return fields, fails


def _metrical(et: dict) -> tuple[list[dict], bool, bool]:
    """Metrical syllables of one token: [{stress}], starts with a vowel, ends with a vowel."""
    word = et.get("n") or et["t"]
    if et.get("m"):
        # explicit scansion: syllables separated by '.', the accented one in CAPS or marked
        parts = et["m"].split(".")
        syl = [{"s": p != p.lower() or any(c in STRESS_MARKS for c in p)} for p in parts]
        low = et["m"].lower()
        return syl, low[:1] in "aeiouàèéìòóù", low[-1:] in "aeiouàèéìòóù"
    a = analyse(word)
    syls = [s for s in a["syls"] if any(p["v"] for p in s)]
    ph = [p for s in a["syls"] for p in s]
    if not syls:
        return [], False, False
    out = [{"s": any(p["s"] for p in s)} for s in syls]
    # synaeresis: a stressed i before a final unstressed vowel (mio, io, sia, ond'io) is one syllable
    if len(syls) >= 2:
        last, prev = syls[-1], syls[-2]
        if (len(last) == 1 and last[0]["v"] and not last[0]["s"]
                and prev[-1]["v"] and prev[-1]["s"] and prev[-1]["p"] == "i"):
            out = out[:-1]
    ends_v = ph[-1]["v"]
    return out, bool(ph[0]["v"]), ends_v


def _rhyme(et: dict) -> str:
    """Spelling from the stressed vowel to the end of the line's last word, marks removed."""
    m, known = marked_form(et.get("n") or et["t"])
    if not known:
        m = _fallback(m)
    m = m.replace("'", "")
    j = max((k for k, c in enumerate(m) if c in STRESS_MARKS), default=None)
    if j is None:
        return m
    tail = m[j:]
    plain = "".join({"à": "a", "è": "e", "é": "e", "ì": "i", "í": "i", "ò": "o", "ó": "o", "ù": "u", "ú": "u",
                     "ŝ": "s", "ś": "s", "ẑ": "z", "ï": "i", "ü": "u"}.get(c, c) for c in tail)
    return plain


def scan(etoks: list[dict]) -> tuple[int, list[int]]:
    """Positions (1-based) and accented positions, with synalepha across words."""
    pos, accents = 0, []
    prev_ends_v = False
    for et in etoks:
        syl, starts_v, ends_v = _metrical(et)
        if not syl:                          # 'l, 'n: no vowel, leans on the syllable before
            prev_ends_v = False
            continue
        for k, s in enumerate(syl):
            if k == 0 and starts_v and prev_ends_v and pos:
                if s["s"] and pos not in accents:
                    accents.append(pos)       # synalepha: the vowels share one position
                continue
            pos += 1
            if s["s"]:
                accents.append(pos)
        prev_ends_v = ends_v
    return pos, sorted(accents)


def line_metre(etoks: list[dict], edition: dict):
    spec = edition.get("metre") or {}
    if spec.get("name") != "endecasillabo":
        return None, []
    fails = []
    count, accents = scan(etoks)
    last = accents[-1] if accents else 0
    if last != 10:
        fails.append(("metre-not-endecasillabo", f"last accent on {last}, {count} positions"))
    # a minore: main accents 4-8-10 (or 4-7-10); a maiore: 6-10. With both 4 and 6 accented and
    # no 8th, the 6th is taken as the main one. Which accents a reader stresses is a judgment.
    kind = ("a minore" if 4 in accents and (8 in accents or 7 in accents or 6 not in accents)
            else "a maiore" if 6 in accents else None)
    if not kind:
        fails.append(("metre-no-accent-4-or-6", "-".join(map(str, accents))))
    # rhyme: find this line in the edition, then compare it with the lines its letter pairs it with
    scheme = (spec.get("rhyme") or "").replace(" ", "")
    letter = ""
    for g in edition.get("sections") or []:
        token_lines = [ln for ln in g["lines"] if not isinstance(ln, str)]
        for idx, ln in enumerate(token_lines):
            if ln["tokens"] is etoks and idx < len(scheme):
                letter = scheme[idx]
                mine = _rhyme(etoks[-1])
                for jdx, other in enumerate(token_lines):
                    if jdx >= len(scheme) or jdx == idx:
                        continue
                    theirs = _rhyme(other["tokens"][-1])
                    if (scheme[jdx] == letter) != (theirs == mine):
                        fails.append(("rhyme-mismatch", f"-{mine} ({letter}) vs line {jdx + 1} -{theirs} ({scheme[jdx]})"))
                        break
    s = f"{count} syllables · accents {'-'.join(map(str, accents))}" + (f" · {kind}" if kind else "")
    if letter:
        s += f" · rhyme {letter} (-{_rhyme(etoks[-1])})"
    return s, fails


LAYERS = {
    "metre": {"src": f"weft.italian {VERSION}: verse only; syllables with synalepha, accents from the lexicon, rhyme by spelling"},
}
SHOW_TRANSLIT = False

KEY = {
    "florentine": [
        ("", "Florentine as the author and his first readers likely spoke it. Reconstructed from the "
             "spelling, the Latin source vowels and the Tuscan tradition recorded in modern dictionaries. "
             "Approximate: the details below are judgments, and the page says which."),
        ("CAPS", "the stressed syllable"),
        ("a", "as in father"),
        ("ay / e", "closed e (as in they, without the glide) / open e, as in pet"),
        ("oh / aw", "closed o (as in go, without the glide) / open o, as in law but shorter"),
        ("ee, oo", "i as in machine, u as in rule"),
        ("ai, oy, ow", "the falling diphthongs ai, oi, au: aisle, boy, cow"),
        ("y, w", "i and u before a vowel: yes, wet (piango = PYAN-goh, uomo = WAW-moh)"),
        ("ch, j, sh", "c and g before e and i (church, judge); sc before e and i (ship)"),
        ("ly, ny", "gli and gn, as in million and canyon; between vowels they are long"),
        ("ts, dz", "z: as in bits or adds; between vowels long"),
        ("doubled letters", "long consonants (fatto = FAT-toh): hold the consonant across the hyphen"),
        ("r", "a tapped or trilled r"),
        ("s", "s between vowels is voiceless here (cose = KAW-say), as in Tuscany"),
        ("not shown", "the gorgia toscana (k t p softened between vowels) is left out: it is not securely "
                      "attested this early. Doubling across words (a casa = ak-KA-sa) is not shown either"),
    ],
    "modern": [
        ("", "Standard Italian as it is taught and broadcast today."),
        ("CAPS", "the stressed syllable"),
        ("ay / e, oh / aw", "closed and open e and o, as in the Florentine scheme; many speakers today "
                            "outside Tuscany distribute them differently"),
        ("ee, oo, y, w", "i, u, and their glides before a vowel"),
        ("ch, j, sh, ly, ny, ts, dz", "as in the Florentine scheme"),
        ("z", "s between vowels is voiced (cose = KAW-zay), as in most of Italy today"),
    ],
}
SCHEME_LABELS = {
    "florentine": "Florentine of the author's day (approximate)",
    "modern": "Standard modern Italian",
}
