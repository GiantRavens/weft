"""Quenya and Sindarin, as J. R. R. Tolkien described their sounds: spelling -> syllables -> sound.

Weft uses this module for private works only. Tolkien's texts are in copyright (until 2043), so
no public work in texts/ is in either language; a reader builds Namárië or the hymn to Elbereth
from their own copy with `weft build <work> --private` (see private/README.md). The module itself
holds no text: it is a statement of pronunciation rules in Weft's own words, with single words as
examples, and the KEY tables say what each rule rests on.

Evidence. The one source is Tolkien, The Lord of the Rings, Appendix E, part I, "Pronunciation of
Words and Names" (1955; cited below as App. E), the author's own account of how the letters of his
transcription are to be read: the consonant table, the vowels and diphthongs, and the stress rule
with its twelve worked examples. This is the rare case where the author of a text wrote down its
pronunciation, so the scheme is not a reconstruction. What App. E leaves open is listed under
"Where it is thin" and in the KEY. Tolkien's own recordings (1952) are not used here: the
recording differs from the printed text in places, and it is a performance, not a rule.

Languages
---------
qya  Quenya ("High-elven"), the language of Namárië. Spelt by Tolkien "as much like Latin as
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
  l; ng = the ng of finger (ŋg), but at the end of a word the ng of sing (ŋ); ph = f; qu = kw;
  r = trilled, in every position; rh = voiceless r; s = always voiceless, as in so; th = the th of
  thin (θ); ty = the t of English tune (tʲ); ny = n with following y (nʲ); hy = the h of hew, huge
  (ç); hw = voiceless w (ʍ); v = v; w = w; y = the y of you in Quenya, a vowel in Sindarin; in
  Sindarin i before a vowel at the start of a word = y. Doubled consonants are long.
  Vowels (App. E, "Vowels"): a e i o u "approximately" as in father, were, machine, for, brute,
  short or long; an acute marks a long vowel; in Quenya long é and ó are "tenser and 'closer'"
  than the short ones, so they are written eː oː against short ɛ ɔ; in Sindarin long e a o keep
  the quality of the short ones. Sindarin y = French u (y), ŷ long. Final e is never silent.
  The groups er ir ur before a consonant or finally are air, eer, oor, not fern, fir, fur: the
  vowel keeps its value and the r is sounded.
  Diphthongs: Quenya ai oi ui au eu iu; Sindarin ae ai ei oe ui au; all falling (stressed on the
  first element), "the simple vowels run together". Every other pair of vowels is two syllables
  (ëa, ëo, oë are written with the diaeresis to show it).
  Stress (App. E, "Stress"): two syllables, the first. Longer words: the last but one if it holds
  a long vowel, a diphthong, or a vowel followed by two or more consonants; otherwise the third
  from the end. Tolkien's examples (stressed vowel in capitals, his notation): isIldur, Orome,
  erEssëa, fËanor, ancAlima, elentÁri, dEnethor, periAnnath, ecthElion, pelArgir, silIvren,
  andÚne. They are this module's regression tests. The digraphs that spell one sound (th dh ch
  ph, and Quenya qu ty ny hy hw) count as one consonant, as App. E says of Sindarin dh th ch and
  as the Tengwar write them. A hyphen inside a word (lisse-miruvóreva) joins two stress domains:
  each part is stressed by the rule for itself.

Where it is thin
----------------
- App. E gives letter values "approximately"; it does not give vowel qualities beyond the five
  English keywords, so the IPA here is broad.
- The quality of Sindarin ae and oe: "nothing in English closely corresponding"; App. E allows
  them to be pronounced as ai, oi, and the respelling does that while the IPA keeps them apart.
- Quenya th: App. E says the sound had become s in spoken Quenya "though still written with a
  different letter"; Tolkien's transcription writes s (Isil), so a written th in a Quenya text is
  read θ here and flagged in the KEY.
- Archaic Quenya hl, hr: "in the Third Age usually pronounced as l" (hl); hr is read as voiceless r.
- Length of a doubled consonant at the end of a word, and how long a long vowel is, are not
  described; the respelling doubles the letter and leaves it there.
- Secondary stress in long compounds is not described and not marked.

Edition token fields (texts or private/<work>/edition.yaml)
---------------------------------------------------------
t      the word as the source prints it, punctuation attached (Ai!); the punctuation moves to punct
ipa    {scheme: ipa} override for this occurrence (not needed so far)
"""
from __future__ import annotations

import re
import unicodedata as ud

VERSION = "0.1"
SHOW_TRANSLIT = False

LEAD_P = re.compile(r"^([(\[“«‹\"'‘]+)")
TRAIL_P = re.compile(r"([,.;:!?)\]”»›\"'’]+)$")

LONG = {"á": "a", "é": "e", "í": "i", "ó": "o", "ú": "u", "ý": "y", "â": "a", "ê": "e", "î": "i", "ô": "o", "û": "u", "ŷ": "y",
        "à": "a", "è": "e", "ì": "i", "ò": "o", "ù": "u"}   # grave: a printing variant of the acute (untùpa, LotR 1954)
SHORT_VOWELS = set("aeiou")
DIPHTHONGS = {"qya": {"ai", "oi", "ui", "au", "eu", "iu"}, "sjn": {"ae", "ai", "ei", "oe", "ui", "au"}}

# consonant digraphs, longest first; each is one consonant for stress
DIGRAPHS = {"qya": ["qu", "ty", "ny", "hy", "hw", "hl", "hr", "th", "ph", "ch", "ng", "dh"],
            "sjn": ["th", "dh", "ch", "ph", "lh", "rh", "ng", "hw"]}

# IPA values (App. E); ng and f and h are resolved in context below
IPA = {"c": "k", "k": "k", "qu": "kʷ", "ty": "tʲ", "ny": "nʲ", "hy": "ç", "hw": "ʍ", "hl": "l", "hr": "r̥", "lh": "l̥", "rh": "r̥",
       "th": "θ", "dh": "ð", "ph": "f", "ch": "x", "g": "g", "d": "d", "b": "b", "t": "t", "p": "p", "m": "m", "n": "n",
       "l": "l", "r": "r", "s": "s", "v": "v", "w": "w", "y": "j", "f": "f", "h": "h", "j": "j"}

# respelling for an English reader (the scheme's KEY explains each)
RESP = {"k": "k", "kʷ": "kw", "tʲ": "ty", "nʲ": "ny", "ç": "hy", "ʍ": "hw", "l": "l", "r̥": "rh", "l̥": "lh", "r": "r",
        "θ": "th", "ð": "dh", "f": "f", "x": "kh", "g": "g", "d": "d", "b": "b", "t": "t", "p": "p", "m": "m", "n": "n",
        "s": "s", "v": "v", "w": "w", "j": "y", "h": "h", "ŋ": "ng", "ŋg": "ng"}
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


def _ipa_syll(s: dict, lang: str, stressed: bool) -> str:
    nuc = s["nuc"] or ""
    longv = ":" in nuc
    base = nuc.replace(":", "")
    if len(base) == 2:                       # diphthong
        v = {"ae": "ae̯", "oe": "oe̯"}.get(base, base[0] + base[1] + "̯")
    elif lang == "qya":
        v = {"e": "eː" if longv else "ɛ", "o": "oː" if longv else "ɔ"}.get(base, base + ("ː" if longv else ""))
    else:
        v = {"e": "ɛ", "o": "ɔ"}.get(base, base) + ("ː" if longv else "")
    return ("ˈ" if stressed else "") + "".join(_ipa_c(c, "onset") for c in s["onset"]) + v + "".join(_ipa_c(c, "coda") for c in s["coda"])


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
    out = cons(s["onset"]) + v + cons(s["coda"])
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
    # Quenya ht: cht; after e or i the h is the sound of ich
    for k in range(len(segs) - 1):
        if lang == "qya" and segs[k] == ("C", "h") and segs[k + 1] == ("C", "t"):
            prev = segs[k - 1][1] if k else ""
            segs[k] = ("C", "ç" if prev.startswith(("e", "i")) else "x")
    sylls = _syllabify(segs)
    st = _stress(sylls) if len(sylls) > 1 else -1          # a monosyllable is not capitalized
    ipa = ".".join(_ipa_syll(s, lang, k == st) for k, s in enumerate(sylls))
    resp = "-".join(_resp_syll(s, lang, k == st) for k, s in enumerate(sylls))
    return ipa, resp, len(sylls)


_CTX: dict = {}


def token_fields(surface: str, et: dict, group: dict) -> tuple[dict, list[tuple[str, str]]]:
    """Split punctuation off the printed word and hold any ipa override for phonemize."""
    global _CTX
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
    _CTX = {"t": word, "ipa": et.get("ipa") or {}}
    return fields, []


def phonemize(word: str, scheme: str = "tolkien", quantities=None, lang: str = "qya", **_) -> dict:
    """A word (hyphenated compounds allowed) in the one scheme. `lang` is qya or sjn; draft passes
    the manifest's language through LANG below."""
    lang = _LANG.get("lang", lang)
    ov = (_CTX.get("ipa") or {}).get(scheme) if _CTX.get("t") == word else None
    if ov:
        return {"ipa": ov, "respell": ov, "syllables": len(ov.split("."))}
    parts = [p for p in word.split("-") if p]
    ipas, rss, n = [], [], 0
    for p in parts:
        ipa, rs, k = word_sound(p, lang)
        ipas.append(ipa); rss.append(rs); n += k
    return {"ipa": "-".join(ipas), "respell": "-".join(rss), "syllables": n}


_LANG: dict = {}


def set_language(code: str) -> None:
    """draft calls this with the manifest's language (qya or sjn) before phonemizing a work."""
    _LANG["lang"] = code


SCHEME_LABELS = {"tolkien": "As Tolkien described it: Appendix E (1955)"}

_COMMON_KEY = [
    ("CAPS", "the stressed syllable, by Tolkien's rule: the first of two; in longer words the last but one when it has a long vowel, a diphthong or two consonants after its vowel, else the third from the end. Monosyllables are left in lower case. Hyphens divide syllables"),
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
        ("", "The sounds as Tolkien set them out in Appendix E to The Lord of the Rings (1955). This is the author's own guide, not a reconstruction; where it says 'approximately', so does Weft."),
        *_COMMON_KEY,
        ("aa, ay, ee, oh, oo", "long vowels (acute accent): in Quenya long é and ó are closer than the short ones, so ay and oh; in Sindarin they are the same vowel held longer (ehh, ohh)"),
        ("ai, oy, ui, ow, eu, iu", "Quenya diphthongs ai oi ui au eu iu, one syllable, falling: rye, boy, ruin, loud; eu and iu as e and i run into u"),
        ("ai, ay, oy, ui, ow", "Sindarin diphthongs ae ai, ei, oe, ui, au: ae and oe 'may be pronounced as ai, oi' (App. E), and the respelling does"),
        ("ü", "Sindarin y: French u, as in lune"),
        ("kw", "Quenya qu"),
        ("ty, ny, hy", "Quenya t and n with a following y (the t of tune), and the h of hew, huge"),
        ("hw", "voiceless w, as in a northern English white"),
        ("lh, rh", "voiceless l and r (Sindarin; archaic Quenya hl is read l)"),
        ("y", "the consonant of you (Quenya); in Sindarin, i before a vowel at the start of a word"),
        ("ng", "the ng of finger inside a word; of sing at the end of a word"),
        ("e at the end", "always sounded, never silent (often written ë)"),
        ("e-a, e-o, o-e", "two vowels in two syllables; only the diphthongs above are one"),
    ],
}
