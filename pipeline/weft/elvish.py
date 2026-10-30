"""Quenya and Sindarin, as J. R. R. Tolkien described their sounds: spelling -> syllables -> sound.

Weft uses this module for private works only. Tolkien's texts are in copyright (until 2043), so
no public work in texts/ is in either language; a reader builds Namárië or the hymn to Elbereth
from their own copy with `weft build <work> --private` (see private/README.md). The module itself
holds no text: it is a statement of pronunciation rules in Weft's own words, with single words as
examples, and the KEY tables say what each rule rests on.

Evidence. Two sources, both Tolkien's own.
- The Lord of the Rings, Appendix E, part I, "Pronunciation of Words and Names" (1955; cited below
  as App. E): the consonant table, the vowels and diphthongs, and the stress rule with its twelve
  worked examples.
- The Road Goes Ever On (1967; cited as RGEO, pages of the 3rd edition, HarperCollins 2002),
  "Notes and Translations", pp. 66-72. Tolkien wrote these notes because App. E gave the
  pronunciation "not perhaps with great clarity" (p. 71). For Quenya (pp. 66, 68-69) they add: the
  main stress is high in tone; the first syllable keeps some stress in longer words; the last
  syllable of a word ending in two short syllables after the main stress takes a light stress; and
  they print Namárië with every major stress (acute) and minor stress (grave) marked. For Sindarin
  (p. 71): the short vowels as in sick, bed, hot, foot, with a as in ah, never cat; ae close to the
  vowel of high and ui as in pursuing; the "long diphthongs" ae oe au ui with their first vowel
  "somewhat prolonged"; ng at the start of a word the sound of sing.
This is the rare case where the author of a text wrote down its pronunciation, so the scheme is not
a reconstruction. Where RGEO is more specific than App. E, RGEO is followed, as Tolkien intended.
What both leave open is listed under "Where it is thin" and in the KEY. Tolkien's own recordings
(1952) are not used here: the recording differs from the printed text in places, and it is a
performance, not a rule.

Languages
---------
qya  Quenya ("High-elven"), the language of Namárië. Spelled by Tolkien "as much like Latin as
     its sounds allowed" (App. E): c is always k, qu is kw, y is a consonant, final e is always
     sounded (often written ë), diphthongs ai au eu iu oi ui.
sjn  Sindarin ("Grey-elven"), the language of the hymn A Elbereth Gilthoniel: y is a vowel (French
     u), dh th ch are single consonants, f at the end of a word is v, ng final is the sound of
     sing, diphthongs ae ai ei oe ui au, a circumflex marks a long vowel in a stressed monosyllable.

Scheme (one, both languages)
----------------------------
tolkien  "As Tolkien described it (Appendix E, 1955)". The rules, in Weft's words:
  Consonants (App. E, "Consonants"): c = k always; ch = the sound of German or Welsh bach (x);
  dh = the th of these (ð); f = f, but v at the end of a word; g = the g of give; h = h, and in
  Quenya ht = cht as in German acht, after e and i the sound of German ich (ç); l = l; lh = voiceless
  l; ng = the ng of finger (ŋg), but at the end of a word the ng of sing (ŋ), and in Sindarin at
  the start of a word too (RGEO p. 71); ph = f; qu = kw;
  r = trilled, in every position; rh = voiceless r; s = always voiceless, as in so; th = the th of
  thin (θ); ty = the t of English tune (tʲ); ny = n with following y (nʲ); hy = the h of hew, huge
  (ç); hw = voiceless w (ʍ); v = v; w = w; y = the y of you in Quenya, a vowel in Sindarin; in
  Sindarin i before a vowel at the start of a word = y. Doubled consonants are long.
  Vowels (App. E, "Vowels"): a e i o u "approximately" as in father, were, machine, for, brute,
  short or long; an acute marks a long vowel; in Quenya long é and ó are "tenser and 'closer'"
  than the short ones, so they are written eː oː against short ɛ ɔ; in Sindarin long e a o keep
  the quality of the short ones. Sindarin y = French u (y), ŷ long. Final e is never silent.
  RGEO (p. 71) adds for Sindarin: short vowels as in sick, bed, hot, foot; short a "not ... as in
  cat, but ... as in ah", so both vowels of aglar are the same; short o rounder than in English.
  The groups er ir ur before a consonant or finally are air, eer, oor, not fern, fir, fur: the
  vowel keeps its value and the r is sounded.
  Diphthongs: Quenya ai oi ui au eu iu; Sindarin ae ai ei oe ui au; all falling (stressed on the
  first element), "the simple vowels run together". Every other pair of vowels is two syllables
  (ëa, ëo, oë are written with the diaeresis to show it).
  Stress (App. E, "Stress"; RGEO pp. 68-69, 71): two syllables, the first. Longer words: the last but one if it holds
  a long vowel, a diphthong, or a vowel followed by two or more consonants; otherwise the third
  from the end. Tolkien's examples (stressed vowel in capitals, his notation): isIldur, Orome,
  erEssëa, fËanor, ancAlima, elentÁri, dEnethor, periAnnath, ecthElion, pelArgir, silIvren,
  andÚne. They are this module's regression tests. The digraphs that spell one sound (th dh ch
  ph, and Quenya qu ty ny hy hw) count as one consonant, as App. E says of Sindarin dh th ch and
  as the Tengwar write them. A hyphen inside a word (lisse-miruvóreva) joins two stress domains:
  each part is stressed by the rule for itself.
  Secondary stress, Quenya only (RGEO pp. 68-69), written ˌ in the IPA and not capitalized: the
  first syllable, when the main stress falls two or more syllables later ("though lower in tone,
  often equal in force": óromárdi, Càlacíryo), or falls on the next syllable and the first is long
  (Àndúne, ōmáryo; a short one is unstressed: avániër); and the last syllable of a word that ends
  in two short syllables after the main stress (súrinèn, tellumàr), "a light stress that could be
  used metrically". RGEO's marked text of Namárië is the regression test for both. RGEO says
  nothing of secondary stress in Sindarin, so none is marked there.

Where it is thin
----------------
- App. E gives letter values "approximately"; it does not give vowel qualities beyond the five
  English keywords, so the IPA here is broad.
- The quality of Sindarin oe: App. E finds "nothing in English closely corresponding" and allows
  oi. For ae, RGEO (p. 71) settles it as "very similar to the E. [ai] diphthong in high"; the IPA
  keeps the spelling (aˑe̯) and the respelling reads ai. The prolonged first vowel of the long
  diphthongs is written half-long (ˑ); RGEO says only "somewhat prolonged".
- Sindarin short vowels: RGEO gives English keywords (sick, bed, hot, foot) and says only that they
  "may be rendered" so; the IPA stays broad (i ɛ ɔ u) rather than reading the lax English vowels
  in as Sindarin ones.
- Quenya th: App. E says the sound had become s in spoken Quenya "though still written with a
  different letter"; Tolkien's transcription writes s (Isil), so a written th in a Quenya text is
  read θ here and flagged in the KEY.
- Archaic Quenya hl, hr: "in the Third Age usually pronounced as l" (hl); hr is read as voiceless r.
- Length of a doubled consonant at the end of a word, and how long a long vowel is, are not
  described; the respelling doubles the letter and leaves it there.
- Secondary stress in hyphenated compounds: RGEO marks the parts unevenly (aíre-tári-lírinèn with
  three major stresses, ùndu-láve with the first part minor); each part here takes its own main
  stress. Sindarin secondary stress is not described and not marked.

Edition token fields (texts or private/<work>/edition.yaml)
---------------------------------------------------------
t      the word as the source prints it, punctuation attached (Ai!); the punctuation moves to punct
ipa    {scheme: ipa} override for this occurrence (not needed so far)
"""
from __future__ import annotations

import re
import unicodedata as ud

VERSION = "0.3"
SHOW_TRANSLIT = False
LAYERS = {"script": {"src": f"weft.elvish {VERSION}: Tengwar generated from the spelling; Quenya by the classical mode "
                             "as Tolkien wrote Namárië (RGEO p. 65), Sindarin by App. E's general use (Weft's transcription); "
                             "font Alcarin Tengwar (SIL OFL 1.1)"}}
SCRIPT_LABEL = "Script (Tengwar)"
SCRIPT_WORD = "Tengwar"

LEAD_P = re.compile(r"^([(\[“«‹\"'‘]+)")
TRAIL_P = re.compile(r"([,.;:!?)\]”»›\"'’]+)$")

LONG = {"á": "a", "é": "e", "í": "i", "ó": "o", "ú": "u", "ý": "y", "â": "a", "ê": "e", "î": "i", "ô": "o", "û": "u", "ŷ": "y",
        "à": "a", "è": "e", "ì": "i", "ò": "o", "ù": "u"}   # grave: a printing variant of the acute (untùpa, LotR 1954)
SHORT_VOWELS = set("aeiou")
SJN_LONG_DIPH = {"ae", "oe", "au", "ui"}     # RGEO p. 71, the Sindarin "long diphthongs"
DIPHTHONGS = {"qya": {"ai", "oi", "ui", "au", "eu", "iu"}, "sjn": {"ae", "ai", "ei", "oe", "ui", "au"}}

# consonant digraphs, longest first; each is one consonant for stress
DIGRAPHS = {"qya": ["qu", "ty", "ny", "hy", "hw", "hl", "hr", "th", "ph", "ch", "ng", "dh"],
            "sjn": ["th", "dh", "ch", "ph", "lh", "rh", "ng", "hw"]}

# IPA values (App. E); ng and f and h are resolved in context below
IPA = {"c": "k", "k": "k", "qu": "kʷ", "ty": "tʲ", "ny": "nʲ", "hy": "ç", "hw": "ʍ", "hl": "l", "hr": "r̥", "lh": "l̥", "rh": "r̥",
       "th": "θ", "dh": "ð", "ph": "f", "ch": "x", "ng": "ŋg", "g": "g", "d": "d", "b": "b", "t": "t", "p": "p", "m": "m", "n": "n",
       "l": "l", "r": "r", "s": "s", "v": "v", "w": "w", "y": "j", "f": "f", "h": "h", "j": "j"}

# respelling for an English reader (the scheme's KEY explains each)
RESP = {"k": "k", "kʷ": "kw", "tʲ": "ty", "nʲ": "ny", "ç": "hy", "ʍ": "hw", "l": "l", "r̥": "rh", "l̥": "lh", "r": "r",
        "θ": "th", "ð": "dh", "f": "f", "x": "kh", "g": "g", "d": "d", "b": "b", "t": "t", "p": "p", "m": "m", "n": "n",
        "s": "s", "v": "v", "w": "w", "j": "y", "h": "h", "ŋ": "ng", "ŋg": "ng", "gʷ": "gw"}
# vowels: (short respell, long respell); Quenya close long é ó get their own symbols
RESP_V = {"a": ("a", "aa"), "e": ("e", "ay"), "i": ("i", "ee"), "o": ("o", "oh"), "u": ("u", "oo"), "y": ("ü", "üü")}
RESP_D = {"ai": "ai", "oi": "oy", "ui": "ui", "au": "ow", "eu": "eu", "iu": "iu", "ae": "ai", "ei": "ay", "oe": "oy"}


def _letters(word: str) -> str:
    """Lower-case letters only, diaeresis dropped (it marks a separately sounded vowel, which the
    syllable rule already gives), hyphen kept as a boundary."""
    w = ud.normalize("NFC", word.lower())
    w = w.replace("ë", "e").replace("ä", "a").replace("ö", "o").replace("ü", "u").replace("ï", "i")
    return "".join(ch for ch in w if ch.isalpha() or ch == "-")


def _segments(w: str, lang: str) -> list[tuple[str, str]]:
    """Letters -> [(kind, unit)], kind V for a vowel (with length as a trailing ':') or diphthong,
    C for a consonant; the digraphs are one unit."""
    out: list[tuple[str, str]] = []
    i = 0
    dig = DIGRAPHS[lang]
    while i < len(w):
        ch = w[i]
        if ch in LONG or ch in SHORT_VOWELS or (lang == "sjn" and ch == "y"):
            base, longv = (LONG[ch], True) if ch in LONG else (ch, False)
            # Sindarin initial i before a vowel is the consonant y
            nxt = w[i + 1] if i + 1 < len(w) else ""
            if lang == "sjn" and ch == "i" and i == 0 and nxt and (nxt in SHORT_VOWELS or nxt in LONG):
                out.append(("C", "j")); i += 1; continue
            if not longv and nxt and (nxt in SHORT_VOWELS or (lang == "sjn" and nxt == "y")) and base + nxt in DIPHTHONGS[lang]:
                out.append(("V", base + nxt)); i += 2; continue
            out.append(("V", base + (":" if longv else ""))); i += 1; continue
        if lang == "qya" and ch == "y":
            out.append(("C", "j")); i += 1; continue
        two = w[i:i + 2]
        if two in dig:
            out.append(("C", IPA[two])); i += 2; continue
        if ch == "-":
            out.append(("-", "-")); i += 1; continue
        out.append(("C", IPA.get(ch, ch))); i += 1
    return out


def _syllabify(segs: list[tuple[str, str]]) -> list[dict]:
    """Onset-nucleus-coda syllables. One consonant between vowels begins the next syllable; of two
    or more, the first closes the syllable before (that is what App. E counts as heavy); a long
    (doubled) consonant counts as two."""
    sylls: list[dict] = []
    cur: dict = {"onset": [], "nuc": None, "coda": []}
    pending: list[str] = []
    for kind, u in segs:
        if kind == "V":
            if cur["nuc"] is None:
                cur["onset"] = pending
            else:
                # split the cluster: all but the last consonant close the previous syllable; a long
                # (doubled) consonant closes one syllable and opens the next, so it counts as two
                if len(pending) == 1 and pending[0].endswith("ː"):
                    pending = [pending[0][:-1], pending[0][:-1]]
                cur["coda"] = pending[:-1]
                sylls.append(cur)
                cur = {"onset": pending[-1:], "nuc": None, "coda": []}
            pending = []
            cur["nuc"] = u
        else:
            pending.append(u)
    if cur["nuc"] is None:          # no vowel at all (an abbreviation)
        cur["onset"] = pending
        pending = []
    cur["coda"] = pending
    sylls.append(cur)
    return sylls


def _mark_long_consonants(segs: list[tuple[str, str]]) -> list[tuple[str, str]]:
    """tt ll ss nn -> one long consonant (counted as two for stress, written doubled in respelling)."""
    out: list[tuple[str, str]] = []
    for kind, u in segs:
        if kind == "C" and out and out[-1] == ("C", u) and len(u) == 1:
            out[-1] = ("C", u + "ː")
        else:
            out.append((kind, u))
    return out


def _stress(sylls: list[dict]) -> int:
    """Index of the stressed syllable by App. E's rule."""
    n = len(sylls)
    if n <= 2:
        return 0
    pen = sylls[-2]
    # a syllable closed by one consonant whose next syllable has none: the vowel is followed by one
    # consonant only; two or more consonants (coda + following onset) make it heavy
    nxt_onset = len(sylls[-1]["onset"])
    nuc = pen["nuc"] or ""
    if ":" in nuc or len(nuc) == 2:
        return n - 2
    cons = len(pen["coda"]) + nxt_onset
    return n - 2 if cons >= 2 else n - 3


def _heavy(s: dict, nxt: dict | None) -> bool:
    """A long syllable (RGEO p. 68 n.): a long vowel, a diphthong, or a vowel before two consonants."""
    nuc = s["nuc"] or ""
    return ":" in nuc or len(nuc) == 2 or len(s["coda"]) + (len(nxt["onset"]) if nxt else 0) >= 2


def _secondary(sylls: list[dict], st: int, lang: str) -> set[int]:
    """Quenya secondary stresses (RGEO pp. 68-69): the first syllable when the main stress is two or
    more later, or next and the first is long; the last when two short syllables follow the main."""
    n = len(sylls)
    if lang != "qya" or st < 0:
        return set()
    out: set[int] = set()
    if st >= 2 or (st == 1 and _heavy(sylls[0], sylls[1])):
        out.add(0)
    last = sylls[-1]["nuc"] or ""
    if st <= n - 3 and ":" not in last and len(last) == 1:
        out.add(n - 1)
    return out


def _ipa_syll(s: dict, lang: str, stressed: bool, secondary: bool = False) -> str:
    nuc = s["nuc"] or ""
    longv = ":" in nuc
    base = nuc.replace(":", "")
    if len(base) == 2:                       # diphthong
        v = {"ae": "ae̯", "oe": "oe̯"}.get(base, base[0] + base[1] + "̯")
        if lang == "sjn" and base in SJN_LONG_DIPH:     # RGEO p. 71: first vowel "somewhat prolonged"
            v = v[0] + "ˑ" + v[1:]
    elif lang == "qya":
        v = {"e": "eː" if longv else "ɛ", "o": "oː" if longv else "ɔ"}.get(base, base + ("ː" if longv else ""))
    else:
        v = {"e": "ɛ", "o": "ɔ"}.get(base, base) + ("ː" if longv else "")
    return ("ˈ" if stressed else "ˌ" if secondary else "") + "".join(_ipa_c(c, "onset") for c in s["onset"]) + v + "".join(_ipa_c(c, "coda") for c in s["coda"])


def _ipa_c(c: str, where: str) -> str:
    if c == "ŋg":
        return "ŋ" if where == "coda" else "ŋg"
    return c


def _resp_syll(s: dict, lang: str, stressed: bool) -> str:
    nuc = s["nuc"] or ""
    longv = ":" in nuc
    base = nuc.replace(":", "")
    if len(base) == 2:
        v = RESP_D[base]
    else:
        v = RESP_V[base][1 if longv else 0]
        if lang == "sjn" and longv and base in "eo":      # Sindarin long e, o keep the short quality: just longer
            v = {"e": "ehh", "o": "ohh"}[base]
    cons = lambda cs: "".join((RESP[c[:-1]] * 2 if c.endswith("ː") else RESP.get(c, c)) for c in cs)
    out = (cons(s["onset"]) + v + cons(s["coda"])).replace("ngg", "ng")   # ŋg in one coda: Angband
    return out.upper() if stressed else out


def word_sound(word: str, lang: str) -> tuple[str, str, int]:
    """One word (no hyphen) -> (ipa, respell, syllable count)."""
    w = _letters(word)
    if not w:
        return "—", "—", 0
    segs = _mark_long_consonants(_segments(w, lang))
    # ng at the end of a word is the simple nasal; f at the end of a word is v (App. E)
    if segs and segs[-1] == ("C", "ŋg"):
        segs[-1] = ("C", "ŋ")
    if segs and segs[-1] == ("C", "f"):
        segs[-1] = ("C", "v")
    # Sindarin ng at the start of a word is also the ng of sing (RGEO p. 71: nguruthos)
    if lang == "sjn" and segs and segs[0] == ("C", "ŋg"):
        segs[0] = ("C", "ŋ")
    # inside a word ng is the ng of finger: two sounds, n closing one syllable and g opening the next
    segs = [x for k, s in enumerate(segs)
            for x in ([("C", "ŋ"), ("C", "g")] if s == ("C", "ŋg") and k > 0 else [s])]
    if lang == "qya":                    # Quenya ngw: the gw is one rounded consonant, like qu
        for k in range(len(segs) - 1, 0, -1):
            if segs[k - 1] == ("C", "g") and segs[k] == ("C", "w"):
                segs[k - 1:k + 1] = [("C", "gʷ")]
    # Quenya ht: cht; after e or i the h is the sound of ich
    for k in range(len(segs) - 1):
        if lang == "qya" and segs[k] == ("C", "h") and segs[k + 1] == ("C", "t"):
            prev = segs[k - 1][1] if k else ""
            segs[k] = ("C", "ç" if prev.startswith(("e", "i")) else "x")
    sylls = _syllabify(segs)
    st = _stress(sylls) if len(sylls) > 1 else -1          # a monosyllable is not capitalized
    sec = _secondary(sylls, st, lang)
    ipa = ".".join(_ipa_syll(s, lang, k == st, k in sec) for k, s in enumerate(sylls))
    resp = "-".join(_resp_syll(s, lang, k == st) for k, s in enumerate(sylls))
    return ipa, resp, len(sylls)


# ---------------------------------------------------------------- Tengwar
# A script row in the Tengwar, code points in the Free Tengwar / ConScript arrangement that the bundled
# font (Alcarin Tengwar, SIL OFL 1.1) follows. Quenya is written in the classical mode as App. E sets it
# out and as Tolkien wrote Namárië in Tengwar (RGEO 3rd ed. p. 65; Björkman's "DTS 20"): the vowel sign
# sits over the consonant before it, or over a short carrier when no consonant precedes; a long vowel
# takes the long carrier, except long é, which Tolkien wrote there as a doubled accent (yéni); a diphthong ending in i is yanta, one ending in u is úre, with the first
# vowel's sign above it; r is rómen before a vowel and óre elsewhere; ss is esse; s takes its turned form
# (silme nuquerna) under a vowel sign; y after a consonant is two dots below it, and anna carries those
# dots where no consonant does; a doubled consonant is one letter with a bar below. The row for Namárië
# is tested word by word against Tolkien's page. Sindarin has no Tengwar by Tolkien for these texts;
# its row follows App. E's general use (the vowel sign over the consonant that follows it) and is Weft's
# transcription, labelled so.

TNG = {"t": "\ue000", "p": "\ue001", "c": "\ue002", "k": "\ue002", "qu": "\ue003", "nd": "\ue004", "mb": "\ue005",
       "ng": "\ue006", "ngw": "\ue007", "th": "\ue008", "f": "\ue009", "ch": "\ue00a", "hw": "\ue00b", "nt": "\ue00c",
       "mp": "\ue00d", "nc": "\ue00e", "nk": "\ue00e", "nqu": "\ue00f", "n": "\ue010", "m": "\ue011", "nw": "\ue013",
       "r_": "\ue014", "v": "\ue015", "y": "\ue016", "w": "\ue017", "r": "\ue020", "rd": "\ue021", "l": "\ue022",
       "ld": "\ue023", "s": "\ue024", "ss": "\ue026", "h": "\ue028", "b": "\ue005", "d": "\ue004", "g": "\ue006",
       "dh": "\ue004", "x": "\ue002"}
NUQUERNA = {"\ue024": "\ue025", "\ue026": "\ue027"}
TEHTA = {"a": "\ue040", "e": "\ue046", "i": "\ue044", "o": "\ue04a", "u": "\ue04c", "y": "\ue042"}   # Sindarin y: two dots, a later convention
SHORT_CARRIER, LONG_CARRIER, YANTA, URE = "\ue02e", "\ue02c", "\ue02a", "\ue02b"
Y_BELOW, BAR_BELOW, DOUBLE_ACUTE = "\ue043", "\ue051", "\ue048"
CARRIERS = (SHORT_CARRIER, LONG_CARRIER, YANTA, URE)
TNG_PUNCT = {",": "\ue060", ";": "\ue061", ":": "\ue061", ".": "\ue061", "!": "\ue065", "?": "\ue066"}
QYA_CLUSTERS = ["nqu", "ngw", "qu", "nd", "mb", "mp", "nt", "nc", "nk", "ng", "nw", "ss", "ld", "rd", "th", "hw", "ch", "hy"]
SJN_CLUSTERS = ["nd", "mb", "ng", "ss", "th", "dh", "ch", "ph", "hw", "lh", "rh"]
# Sindarin in App. E's general use: the fourth series (quessetéma) for k, g, ch; the third grade for dh, v;
# a bar above a stop for a nasal before it (nd, mb, ng); nwalme for ng as in sing (start or end of a word)
NASAL_ABOVE = "\ue050"
SJN_TNG = {"c": ("\ue003", ""), "k": ("\ue003", ""), "g": ("\ue007", ""), "ch": ("\ue00b", ""), "dh": ("\ue00c", ""),
           "v": ("\ue00d", ""), "b": ("\ue005", ""), "d": ("\ue004", ""), "nd": ("\ue004", NASAL_ABOVE),
           "mb": ("\ue005", NASAL_ABOVE), "ng": ("\ue007", NASAL_ABOVE), "th": ("\ue008", ""), "ss": ("\ue026", ""),
           "hw": ("\ue00b", "")}


def _tng_units(w: str, lang: str) -> list[tuple]:
    """Letters -> [("C", tengwa, below) | ("V", vowel, long) | ("D", first, glide)]."""
    out: list[tuple] = []
    cl = QYA_CLUSTERS if lang == "qya" else SJN_CLUSTERS
    i = 0
    while i < len(w):
        ch = w[i]
        if ch in LONG or ch in SHORT_VOWELS or (lang == "sjn" and ch == "y"):
            base, longv = (LONG[ch], True) if ch in LONG else (ch, False)
            nxt = w[i + 1] if i + 1 < len(w) else ""
            if not longv and nxt and base + nxt in DIPHTHONGS[lang] and nxt in "iu":
                out.append(("D", base, nxt)); i += 2; continue
            if lang == "sjn" and base + nxt in DIPHTHONGS["sjn"]:          # ae, oe: two signs
                out.append(("V", base, False)); i += 1; continue
            out.append(("V", base, longv)); i += 1; continue
        two = next((c for c in cl if w.startswith(c, i)), None)
        if lang == "sjn" and (two or ch) in SJN_TNG:
            key = two or ch
            g, above = SJN_TNG[key]
            if key == "ng" and (i == 0 or i + 2 == len(w)):
                g, above = "\ue013", ""                               # nwalme: ng as in sing
            if key == "v" or (key == "f" and i + 1 == len(w)):
                pass
            out.append(("C", g, "", above)); i += len(key); continue
        if lang == "sjn" and ch == "f" and i + 1 == len(w):           # final f is v
            out.append(("C", SJN_TNG["v"][0], "")); i += 1; continue
        if two == "hy":
            out.append(("C", TNG["h"], Y_BELOW)); i += 2; continue
        if two in ("ph",):
            out.append(("C", TNG["f"], "")); i += 2; continue
        if two in ("lh", "rh"):                                       # Sindarin voiceless l, r: halla before
            out.append(("C", "\ue02d", "")); out.append(("C", TNG[two[0]], "")); i += 2; continue
        if two == "nw" and i > 0:                                      # nwalme only for initial nw
            two = None
        if two:
            out.append(("C", TNG[two], "")); i += len(two); continue
        if ch == "y" and lang == "qya":
            prev = out[-1] if out else None
            if prev and prev[0] == "C" and not prev[2]:
                out[-1] = ("C", prev[1], Y_BELOW)                      # ty, ny, ry, ly: dots below
            else:
                out.append(("C", TNG["y"], Y_BELOW))                   # anna carries the dots
            i += 1; continue
        if ch == "w" and lang == "qya" and i == 0:
            out.append(("C", TNG["v"], "")); i += 1; continue
        if i + 1 < len(w) and w[i + 1] == ch and ch in TNG:             # doubled consonant: bar below
            out.append(("C", TNG[ch], BAR_BELOW)); i += 2; continue
        if ch in TNG:
            out.append(("C", TNG[ch], "")); i += 1; continue
        i += 1                                                         # anything else is not written
    return out


def _r_forms(units: list[tuple]) -> list[tuple]:
    """rómen before a vowel, óre before a consonant and at the end of a word."""
    out = []
    for k, u in enumerate(units):
        if u[0] == "C" and u[1] == TNG["r"]:
            nxt = units[k + 1] if k + 1 < len(units) else None
            if not nxt or nxt[0] == "C":
                u = ("C", TNG["r_"], u[2])
        out.append(u)
    return out


def tengwar(word: str, lang: str) -> str:
    """One word (hyphens and apostrophes allowed) in Tengwar, by the mode of its language."""
    parts = [p for p in re.split(r"[-'’]", word) if p]
    return " ".join(_tengwar_one(p, lang) for p in parts) if len(parts) > 1 else _tengwar_one(word, lang)


def _tengwar_one(word: str, lang: str) -> str:
    w = _letters(word).replace("-", "")
    units = _r_forms(_tng_units(w, lang))
    glyphs: list[list[str]] = []         # each: [tengwa, below, above]
    def put_on(g: list[str], tehta: str):
        g[0] = NUQUERNA.get(g[0], g[0]); g[2] = tehta
    if lang == "qya":                     # the vowel sign over the consonant before it
        for u in units:
            if u[0] == "C":
                glyphs.append([u[1], u[2], ""])
            elif u[0] == "D":
                glyphs.append([YANTA if u[2] == "i" else URE, "", TEHTA[u[1]]])
            elif u[2] and u[1] == "e" and glyphs and glyphs[-1][2] == "" and glyphs[-1][0] not in CARRIERS:
                put_on(glyphs[-1], DOUBLE_ACUTE)   # long é: the accent doubled (yéni, RGEO p. 65)
            elif u[2]:                    # other long vowels: the long carrier
                glyphs.append([LONG_CARRIER, "", TEHTA[u[1]]])
            elif glyphs and glyphs[-1][2] == "" and glyphs[-1][0] not in CARRIERS:
                put_on(glyphs[-1], TEHTA[u[1]])
            else:
                glyphs.append([SHORT_CARRIER, "", TEHTA[u[1]]])
    else:                                 # Sindarin, general use: the vowel sign over the consonant after it
        pending = None
        for u in units:
            if u[0] == "C":
                g = [u[1], u[2], u[3] if len(u) > 3 else ""]
                if pending is not None:
                    put_on(g, (g[2] + pending) if g[2] else pending); pending = None
                glyphs.append(g)
            else:
                if pending is not None:
                    glyphs.append([SHORT_CARRIER, "", pending])
                if u[0] == "D":
                    glyphs.append([YANTA if u[2] == "i" else URE, "", TEHTA[u[1]]]); pending = None
                elif u[2]:
                    glyphs.append([LONG_CARRIER, "", TEHTA[u[1]]]); pending = None
                else:
                    pending = TEHTA[u[1]]
        if pending is not None:
            glyphs.append([SHORT_CARRIER, "", pending])
    return "".join(a + b + c for a, b, c in glyphs)




def token_fields(surface: str, et: dict, group: dict) -> tuple[dict, list[tuple[str, str]]]:
    """Split punctuation off the printed word and hold any ipa override for phonemize."""
    fields: dict = {}
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
    # the Tengwar row; an edition token may give Tolkien's own spelling where it departs from the mode
    # (tengwar: code points as written), as caita does on RGEO p. 65
    tng = et.get("tengwar") or tengwar(word, _LANG.get("lang", "qya"))
    fields["script"] = tng + "".join(TNG_PUNCT.get(c, "") for c in fields.get("punct", ""))
    return fields, []


def _printed_word(surface: str) -> str:
    """The printed word without its leading and trailing punctuation."""
    ml = LEAD_P.search(surface)
    w = surface[ml.end():] if ml else surface
    mt = TRAIL_P.search(w)
    return w[:mt.start()] if mt else w


WANTS_TOKEN = True        # draft passes the edition token and its printed surface: the ipa override (pin 201)


def phonemize(word: str, scheme: str = "tolkien", quantities=None, lang: str = "qya", etok: dict | None = None,
              surface: str | None = None, **_) -> dict:
    """A word (hyphenated compounds allowed) in the one scheme. `lang` is qya or sjn; draft passes
    the manifest's language through LANG below."""
    lang = _LANG.get("lang", lang)
    ov = (etok.get("ipa") or {}).get(scheme) if etok is not None and _printed_word(surface or "") == word else None
    if ov:
        return {"ipa": ov, "respell": ov, "syllables": len(ov.split("."))}
    # a hyphen joins two stress domains; so does an apostrophe of elision (di'nguruthos), and the
    # word after it keeps its own initial sound (ng = [ŋ], RGEO p. 71)
    parts = [p for p in re.split(r"[-'’]", word) if p]
    ipas, rss, n = [], [], 0
    for p in parts:
        ipa, rs, k = word_sound(p, lang)
        ipas.append(ipa); rss.append(rs); n += k
    return {"ipa": "-".join(ipas), "respell": "-".join(rss), "syllables": n}


_LANG: dict = {}


def set_language(code: str) -> None:
    """draft calls this with the manifest's language (qya or sjn) before phonemizing a work."""
    _LANG["lang"] = code


SCHEME_LABELS = {"tolkien": "As Tolkien described it: Appendix E (1955) and The Road Goes Ever On (1967)"}

_COMMON_KEY = [
    ("CAPS", "the stressed syllable, by Tolkien's rule: the first of two; in longer words the last but one when it has a long vowel, a diphthong or two consonants after its vowel, else the third from the end. Monosyllables are left in lower case. Hyphens divide syllables. In Quenya the main stress was high in tone (RGEO, 1967)"),
    ("ˌ (IPA)", "Quenya secondary stress (RGEO, 1967): the first syllable of a longer word keeps some stress, and the last syllable of a word ending in two short syllables after the main stress takes a light one, used in verse. Not capitalized in the respelling"),
    ("a, e, i, o, u", "short vowels, 'approximately' as in father, were, machine, for, brute (App. E)"),
    ("r", "trilled, in every position, including before a consonant and at the end of a word (part is not English part)"),
    ("er, ir, ur", "the vowel keeps its value and the r is trilled: air, eer, oor, not fern, fir, fur"),
    ("th", "as in thin"),
    ("dh", "as in these"),
    ("kh", "the ch of German or Welsh bach (written ch)"),
    ("k", "written c (and k in names from other tongues): always k, even before e and i"),
    ("g", "always as in give"),
    ("s", "always voiceless, as in so"),
    ("f", "f; at the end of a word the letter f is the sound v (written v elsewhere)"),
    ("tt, ll, nn, ss", "a long consonant, held"),
]
KEY = {
    "tolkien": [
        ("", "The sounds as Tolkien set them out in Appendix E to The Lord of the Rings (1955), with the notes he added in The Road Goes Ever On (1967) because Appendix E gave them 'not perhaps with great clarity'. This is the author's own guide, not a reconstruction; where it says 'approximately', so does Weft."),
        *_COMMON_KEY,
        ("aa, ay, ee, oh, oo", "long vowels (acute accent): in Quenya long é and ó are closer than the short ones, so ay and oh; in Sindarin they are the same vowel held longer (ehh, ohh)"),
        ("ai, oy, ui, ow, eu, iu", "Quenya diphthongs ai oi ui au eu iu, one syllable, falling: rye, boy, ruin, loud; eu and iu as e and i run into u"),
        ("ai, ay, oy, ui, ow", "Sindarin diphthongs ae ai, ei, oe, ui, au: ae 'very similar to' the vowel of high, ui as in pursuing but one syllable (RGEO); oe may be read oi (App. E). In ae, oe, au, ui the first vowel is 'somewhat prolonged', so in verse they can fill two beats (Fanuilos)"),
        ("a, e, i, o, u (Sindarin)", "short vowels as in ah (never cat), bed, sick, hot (rounder than English), foot (RGEO)"),
        ("ü", "Sindarin y: French u, as in lune"),
        ("kw", "Quenya qu"),
        ("ty, ny, hy", "Quenya t and n with a following y (the t of tune), and the h of hew, huge"),
        ("hw", "voiceless w, as in a northern English white"),
        ("lh, rh", "voiceless l and r (Sindarin; archaic Quenya hl is read l)"),
        ("y", "the consonant of you (Quenya); in Sindarin, i before a vowel at the start of a word"),
        ("ng", "the ng of finger inside a word; of sing at the end of a word, and in Sindarin at the start too (nguruthos)"),
        ("e at the end", "always sounded, never silent (often written ë)"),
        ("e-a, e-o, o-e", "two vowels in two syllables; only the diphthongs above are one"),
        ("|  ||  |||", "after a word in the sound row of Namárië: a pause in the chant as Tolkien marked it in his own copy (The Road Goes Ever On, p. 76), 'in ascending order of time-length and tone-fall'"),
        ("Tengwar (Quenya)", "the row above the text, in the classical mode as Tolkien wrote Namárië in Tengwar (The Road Goes Ever On, p. 65): each vowel sign over the consonant before it, a short carrier where none precedes, the long carrier for a long vowel (long é a doubled accent), yanta and úre for the second part of a diphthong. Generated by Weft from the spelling"),
        ("Tengwar (Sindarin)", "Weft's transcription in the general use of Appendix E (each vowel sign over the consonant after it); Tolkien left no Tengwar of these Sindarin texts"),
    ],
}
