"""Old French and Franco-Italian prose: printed spelling -> normalized spelling -> sound.

Built for the Cipangu chapter of Marco Polo's book in the Franco-Italian F text (Paris, BnF fr. 1116,
as printed by the Société de Géographie, 1824). The language of that text is French written by
Italians: its grammar and most of its words are French, its spelling and some of its words are
Italian (qe for que, voz for vos, jens for genz, da for de, cum and con for 'with', coverto). Each
token therefore carries two spellings: t, the word as printed, and n, the same word in the spelling
of central French about 1300 (que, vos, genz), typed by hand. n normalizes letters only, never the
grammar; Italian words with no French counterpart keep their printed form.

Schemes
-------
fr1300   French of about 1300, read in the Paris norm; approximate. This is the language the book is
         written in, and the sound a French-trained reader would have given it. It is not the sound
         of the dictation itself: Marco Polo was Venetian and Rustichello Pisan, and how far their
         reading of this French differed from Paris speech is not recorded. The second scheme
         models that difference.
         Evidence: the standard histories of French sound change (for example Kristoffer Nyrop,
         Grammaire historique de la langue française, vol. 1, 1899; Mildred K. Pope, From Latin to
         Modern French, 1934), which rest on rhymes, spellings and the later grammarians. The scheme
         takes these positions:
         - stress on the last syllable that is not a final e (ə); CAPS in the respelling.
         - the final e (ə) is sounded, and elided before a vowel.
         - s before a consonant is silent, the vowel before it long (isle ˈiː.lə, nostre). Its loss
           is placed in the 12th and 13th centuries; the spelling kept the s for centuries after.
         - a written final consonant is sounded before a pause and before a vowel (final s then as
           z), and dropped before a consonant (s, t, p). The handbooks place the start of this
           pattern in later Old French; its extent by 1300 is the weakest point of the scheme.
         - oi is [wɛ] (the stage between [oj] and later [ɛ] or [wa]); ai and ei are [ɛ]; au and al
           before a consonant are [aw] (still a diphthong); ou is [u]; eu and ue are [ø]; u is [y].
         - ch is [tʃ] and j, g before e or i are [dʒ]. These affricates were simplifying to [ʃ] and
           [ʒ] in Paris during the 13th century; the scheme keeps them, the conservative choice. The
           dental affricate of c before e or i and of z had already become [s].
         - vowels before n or m are nasal, and the n or m is still sounded after them (grant
           ɡrãnt); i and u before n are not yet nasal.
         - r is trilled with the tongue tip.
it1300   The same text read by an Italian reader about 1300, letter by letter with Tuscan values; a
         hypothesis, offered because the book was written down by Italians and copied and read in
         Italy. Rules: every written letter is sounded, final consonants and final e included; c and
         g before e or i are [tʃ] and [dʒ], ch and gh are [k] and [ɡ], q and qu before e or i are
         [k], qu before a or o [kw], gn and ngn [ɲ], j [dʒ], z [ts] (initial z [dz]), s between
         vowels [z], h silent, y [i], ou [u]; vowels are oral, with no nasal vowels; doubled
         consonants are long. Stress stays on the French syllable (the last, or the one before a
         final e, es or the verb ending ent), because Franco-Italian verse follows the French
         syllable count and rhyme on the final stressed syllable. The evidence is the spelling of
         Franco-Italian manuscripts, which writes Italian letter values into French words; no
         grammarian of the period describes such a reading.

Edition token fields (texts/<work>/edition.yaml)
-----------------------------------------------
t      the word as printed, with punctuation attached (ysle,); the punctuation is split off
n      the normalized central-French spelling; the key into pipeline/weft/data/fro_lexicon.yaml
glue   no space follows (the elided d’ l’ qu’ s’)
ipa    {scheme: ipa} override for this occurrence

The edition may also carry `ocr_verify`: the printed source exists openly only as a scan with an
uncorrected OCR text, so `line_checks` checks each line against that OCR text after applying a
declared list of corrections, each one a reading of the scan (see the edition file).
"""
from __future__ import annotations

import re
import unicodedata as ud
from pathlib import Path

import yaml

VERSION = "0.1"
SHOW_TRANSLIT = True
TRANSLIT_LABEL = "Central French spelling"

_LEX: dict | None = None
_CTX: dict = {}
_OCR: dict = {}

LEAD_P = re.compile(r"^([(\[«“]+)")
TRAIL_P = re.compile(r"([,.;:!?)\]»”]+)$")
VOWELS = set("aeiouyɑɛɔøœəɥ")


def lexicon() -> dict:
    global _LEX
    if _LEX is None:
        p = Path(__file__).parent / "data" / "fro_lexicon.yaml"
        _LEX = {ud.normalize("NFC", k): v for k, v in (yaml.safe_load(p.read_text(encoding="utf-8")) or {}).items()}
    return _LEX


def key(word: str) -> str:
    return ud.normalize("NFC", word.replace("'", "’"))


def entry(word: str) -> dict | None:
    lx = lexicon()
    k = key(word)
    return lx.get(k) or lx.get(k.lower())


def base_ipa(word: str, scheme: str = "fr1300") -> str | None:
    e = entry(word)
    return e.get(scheme) if e else None


def _first(ipa: str | None) -> str:
    s = ud.normalize("NFD", (ipa or "").lstrip("ˈ"))
    return s[:1]


def begins_with_vowel(ipa: str | None) -> bool:
    return _first(ipa) in VOWELS


# ---------------------------------------------------------------- IPA -> respelling
NASAL = {"a": "ahⁿ", "ɛ": "ehⁿ", "e": "ehⁿ", "o": "ohⁿ", "ɔ": "ohⁿ"}
LONG = {"a": "aa", "e": "ayy", "ɛ": "ehh", "i": "eee", "o": "ohh", "ɔ": "ohh", "y": "üü", "u": "ooo"}
MULTI = [("tʃ", "ch"), ("dʒ", "j"), ("ts", "ts"), ("dz", "dz"), ("aw", "ow"), ("ɛj", "ay"), ("ej", "ay"),
         ("oj", "oy"), ("aj", "ai"), ("ɛw", "ehw"), ("ew", "ehw")]
PLAIN = {"a": "a", "e": "ay", "ɛ": "eh", "i": "ee", "o": "oh", "ɔ": "o", "u": "oo", "y": "ü", "ø": "ö",
         "ə": "uh", "ʃ": "sh", "ʒ": "zh", "ɲ": "ny", "ʎ": "ly", "j": "y", "w": "w", "ɥ": "ü", "ɡ": "g",
         "r": "r", "‿": "‿"}


def _respell_syl(s: str) -> str:
    out, i = [], 0
    while i < len(s):
        nxt = s[i + 1] if i + 1 < len(s) else ""
        if nxt == "̃":
            out.append(NASAL.get(s[i], s[i]))
            i += 2
            continue
        if nxt == "ː":
            out.append(LONG.get(s[i], s[i] * 2))
            i += 2
            continue
        hit = next(((a, b) for a, b in MULTI if s.startswith(a, i)), None)
        if hit:
            out.append(hit[1])
            i += len(hit[0])
            continue
        out.append(PLAIN.get(s[i], s[i]))
        i += 1
    return "".join(out)


def respell(ipa: str) -> str:
    """Syllables joined by hyphens; the stressed syllable (ˈ) in capitals."""
    s = ud.normalize("NFD", ipa)
    parts = []
    for syl in s.split("."):
        stressed = syl.startswith("ˈ")
        r = _respell_syl(syl.lstrip("ˈ"))
        parts.append(r.upper() if stressed else r)
    return ud.normalize("NFC", "-".join(parts))


# ---------------------------------------------------------------- Italian reading of the spelling
_IV = {"a": "a", "à": "a", "á": "a", "e": "e", "é": "e", "è": "e", "ê": "e", "i": "i", "ï": "i", "í": "i",
       "o": "o", "ó": "o", "ò": "o", "u": "u", "ú": "u", "y": "i"}
FRONTL = set("eéèêiïíy")
IT_FINAL_STRESS = {"avent"}          # Franco-Italian avent = French avint, a preterite stressed on the end


def _it_phones(w: str) -> list[list]:
    """Letters -> [phone, kind, flags]; kind 'V' vowel, 'C' consonant."""
    out: list[list] = []
    i = 0
    while i < len(w):
        c = w[i]
        nx = w[i + 1] if i + 1 < len(w) else ""
        prev_v = bool(out) and out[-1][1] == "V"
        if w.startswith("ngn", i):
            out.append(["ɲ", "C", ""]); i += 3; continue
        if w.startswith("gn", i):
            out.append(["ɲ", "C", ""]); i += 2; continue
        if w.startswith("ch", i):
            out.append(["k", "C", ""]); i += 2; continue
        if w.startswith("gh", i):
            out.append(["ɡ", "C", ""]); i += 2; continue
        if w.startswith("qu", i):
            after = w[i + 2] if i + 2 < len(w) else ""
            out.append(["k", "C", ""])
            if after and after not in FRONTL:
                out.append(["w", "C", "glide"])
            i += 2; continue
        if c in "cg":
            if nx in FRONTL:
                out.append(["tʃ" if c == "c" else "dʒ", "C", "pal"])
                # Italian spelling: i after a palatal c or g and before a vowel only marks the palatal
                if nx == "i" and i + 2 < len(w) and w[i + 2] in _IV:
                    i += 1
            else:
                out.append(["k" if c == "c" else "ɡ", "C", ""])
            i += 1; continue
        if c == "ç":
            out.append(["ts", "C", ""]); i += 1; continue
        if c == "q":
            out.append(["k", "C", ""]); i += 1; continue
        if c == "j":
            out.append(["dʒ", "C", ""]); i += 1; continue
        if c == "h":
            i += 1; continue
        if c == "x":
            out.append(["k", "C", ""]); out.append(["s", "C", ""]); i += 1; continue
        if c == "z":
            out.append(["dz" if i == 0 else "ts", "C", ""]); i += 1; continue
        if c == "s":
            if prev_v and nx in _IV and nx != "s":
                out.append(["z", "C", ""])
            else:
                out.append(["s", "C", ""])
            i += 1; continue
        if c == "i" and prev_v and (w.startswith("gn", i + 1) or w.startswith("ngn", i + 1)):
            i += 1; continue                     # ei before gn spells the palatal n (seingnor)
        if w.startswith("ou", i):
            out.append(["u", "V", ""]); i += 2; continue
        if c in _IV:
            flags = ("hiatus" if c == "ï" else "") + (" acute" if c == "é" else "")
            out.append([_IV[c], "V", flags]); i += 1; continue
        if c.isalpha():
            out.append([c if c != "g" else "ɡ", "C", ""])
        i += 1
    return out


def _it_glides(ph: list[list]) -> list[list]:
    """i or u before a vowel becomes a glide (onset); i or u after a vowel closes the syllable."""
    out = [p[:] for p in ph]
    n = len(out)
    for k, p in enumerate(out):
        if p[1] != "V" or "hiatus" in p[2]:
            continue
        nxt = out[k + 1] if k + 1 < n else None
        prv = out[k - 1] if k > 0 else None
        if p[0] in "iu" and nxt and nxt[1] == "V" and "hiatus" not in nxt[2]:
            rest = "".join(q[0] for q in out[k + 1:])
            # final -ie, -ies after a consonant (envie, seignorie): two syllables, unless the e is
            # accented (sachiés)
            final_hiatus = (p[0] == "i" and rest in ("e", "es") and "acute" not in nxt[2]
                            and prv is not None and prv[1] == "C")
            if not final_hiatus:
                p[0], p[1], p[2] = ("j" if p[0] == "i" else "w"), "C", "glide"
                continue
        if p[0] in "iu" and prv and prv[1] == "V" and prv[0] not in "iu" and "hiatus" not in p[2]:
            p[0], p[1], p[2] = ("j" if p[0] == "i" else "w"), "OFF", "glide"
    return out


def it_ipa(printed: str) -> str:
    w = ud.normalize("NFC", printed).lower().replace("’", "").replace("'", "")
    ph = _it_glides(_it_phones(w))
    # syllables: each vowel is a nucleus; an offglide stays with its vowel; consonants between
    # nuclei: one goes to the next syllable, stop or f plus r or l go together, otherwise split
    nuclei = [k for k, p in enumerate(ph) if p[1] == "V"]
    if not nuclei:
        return "".join(p[0] for p in ph)
    bounds = []
    for a, b in zip(nuclei, nuclei[1:]):
        k = a + 1
        while k < b and ph[k][1] == "OFF":
            k += 1
        cons = list(range(k, b))
        if not cons:
            bounds.append(b)
        elif len(cons) == 1:
            bounds.append(cons[0])
        else:
            # a consonant plus a glide (kj, dj) and a stop or f plus r or l begin the next syllable
            together = (ph[cons[-1]][2] == "glide"
                        or (ph[cons[-1]][0] in "rl" and ph[cons[-2]][0] in "pbtdkɡfv"))
            bounds.append(cons[-2] if together else cons[-1])
    syls, start = [], 0
    for b in bounds + [len(ph)]:
        seg = ph[start:b]
        closed = bool(seg) and seg[-1][1] in ("C", "OFF") and seg[-1][2] != "glide"
        # Tuscan e is open in a closed syllable, close in an open one
        syls.append("".join(("ɛ" if closed and q[0] == "e" and q[1] == "V" else q[0]) for q in seg))
        start = b
    nsyl = len(syls)
    if nsyl == 1:
        return syls[0]
    last_v = ph[nuclei[-1]]
    tail = "".join(p[0] for p in ph[nuclei[-1]:])
    stress = nsyl - 1
    if w in IT_FINAL_STRESS or "acute" in last_v[2]:
        stress = nsyl - 1
    elif tail in ("e", "es", "o") or (tail == "ent" and nsyl >= 2):
        stress = nsyl - 2
    syls[stress] = "ˈ" + syls[stress]
    return ".".join(syls)


# ---------------------------------------------------------------- context
def _flat(group: dict) -> list[dict]:
    return [t for ln in group.get("lines", []) if not isinstance(ln, str) for t in ln["tokens"]]


def _strip(word: str) -> tuple[str, str | None, str | None]:
    lead = trail = None
    ml = LEAD_P.search(word)
    if ml:
        lead, word = ml.group(1), word[ml.end():]
    mt = TRAIL_P.search(word)
    if mt:
        trail, word = mt.group(1), word[:mt.start()]
    return word, lead, trail


def token_fields(surface: str, et: dict, group: dict) -> tuple[dict, list[tuple[str, str]]]:
    """Split punctuation off the printed word, check the lexicon, and hold the token's context
    (next word, pause, printed form) for phonemize, which draft calls next for this token."""
    global _CTX
    fields: dict = {}
    fails: list[tuple[str, str]] = []
    word, lead, trail = _strip(surface)
    if lead:
        fields["lead"] = lead
    if trail:
        fields["punct"] = trail
    if word != surface:
        fields["surface"] = word
    n = et.get("n")
    if not n:
        fails.append(("normalized-spelling-missing", surface))
    elif entry(n) is None and not et.get("ipa"):
        fails.append(("lexicon-missing", n))
    toks = _flat(group)
    k = next((i for i, t in enumerate(toks) if t is et), None)
    nxt = toks[k + 1] if k is not None and k + 1 < len(toks) else None
    pause = bool(trail) or nxt is None or bool(nxt and LEAD_P.search(nxt["t"]))
    _CTX = {"n": n, "next": (nxt or {}).get("n"), "pause": pause, "printed": word,
            "ipa": et.get("ipa") or {}, "glue": bool(et.get("glue"))}
    return fields, fails


def in_context(word: str, scheme: str) -> str:
    ctx = _CTX if _CTX.get("n") == word else {}
    over = (ctx.get("ipa") or {}).get(scheme)
    if over:
        return over
    if scheme == "it1300":
        return it_ipa(ctx.get("printed") or word)
    ipa = base_ipa(word, scheme)
    if ipa is None:
        return "?"
    if not ctx or ctx.get("pause") or ctx.get("glue"):
        return ipa
    nxt = base_ipa(ctx.get("next") or "", scheme)
    if nxt is None:
        return ipa
    if begins_with_vowel(nxt):
        if ipa.endswith("ə") and "." in ipa:
            head, last = ipa[:-1].rsplit(".", 1)
            return head + last + "‿"
        if ipa.endswith("ə"):
            return ipa[:-1] + "‿"
        if ipa.endswith("s"):
            return ipa[:-1] + "z‿"
        if not ipa[-1] in VOWELS and ipa[-1] not in "̃ː":
            return ipa + "‿"
        return ipa
    # before a consonant: a final s, t or p falls silent
    if ipa[-1] in "stp" and len(ipa) > 1:
        return ipa[:-1]
    return ipa


def syllables(ipa: str) -> int:
    if ipa in ("?", ""):
        return 0
    parts = [p for p in ipa.replace("‿", "").split(".")
             if any(ch in VOWELS for ch in ud.normalize("NFD", p))]
    return len(parts)


def phonemize(word: str, scheme: str = "fr1300", quantities=None, **_) -> dict:
    """`word` is the token's normalized spelling (n); the Italian reading uses the printed form."""
    ipa = in_context(word, scheme)
    return {"ipa": ipa, "respell": respell(ipa) if ipa != "?" else "?", "syllables": syllables(ipa)}


# ---------------------------------------------------------------- sensors
def _norm_text(s: str) -> str:
    s = ud.normalize("NFC", s).replace("’", "'")
    s = " ".join(s.split())
    return re.sub(r"\s+([,.;:?!])", r"\1", s)


def _ocr_region(spec: dict) -> tuple[str | None, list[str]]:
    """The OCR text between the start and end markers, with line-end hyphens joined, page headers
    stripped and the declared corrections applied (whole words). Returns the text and any
    correction that matched nothing (a sensor: the OCR changed, or the correction is wrong)."""
    path = Path(__file__).resolve().parents[2] / spec["file"]
    if str(path) in _OCR:
        return _OCR[str(path)]
    if not path.exists():
        _OCR[str(path)] = (None, [])
        return _OCR[str(path)]
    raw = ud.normalize("NFC", path.read_text(encoding="utf-8"))
    a = raw.find(spec["start"])
    b = raw.find(spec["end"], a + 1) if a >= 0 else -1
    reg = raw[a:b] if a >= 0 and b > a else ""
    for pat in spec.get("strip") or []:
        reg = re.sub(pat, "\n", reg)
    reg = re.sub(r"-\s*\n\s*", "", reg)
    reg = _norm_text(reg)
    unused = []
    for c in spec.get("corrections") or []:
        pat = r"(?<![\w'])" + re.escape(_norm_text(c["ocr"])) + r"(?![\w])"
        reg, k = re.subn(pat, _norm_text(c["print"]).replace("\\", "\\\\"), reg)
        if k == 0:
            unused.append(c["ocr"])
    _OCR[str(path)] = (reg, unused)
    return _OCR[str(path)]


_REPORTED: set = set()


def line_checks(text: str, etoks: list[dict], edition: dict) -> list[tuple[str, str]]:
    """Sensors: elisions are glued; and, where the edition declares ocr_verify, the line appears
    verbatim in the corrected OCR text of its printed source."""
    out = []
    for t in etoks:
        el = t["t"].endswith(("’", "'"))
        if el and not t.get("glue"):
            out.append(("elision-not-glued", t["t"]))
        if t.get("glue") and not el:
            out.append(("glue-without-elision", t["t"]))
    spec = edition.get("ocr_verify")
    if spec:
        reg, unused = _ocr_region(spec)
        if reg is None:
            if "missing" not in _REPORTED:
                _REPORTED.add("missing")
                out.append(("ocr-source-missing", spec["file"]))
        else:
            for u in unused:
                if u not in _REPORTED:
                    _REPORTED.add(u)
                    out.append(("ocr-correction-unused", u))
            if _norm_text(text) not in reg:
                out.append(("edition-not-in-source", _norm_text(text)[:40]))
    return out


KEY = {
    "fr1300": [
        ("", "French of about 1300 in the Paris norm, as a French-trained reader would have said this text; approximate. The book was dictated and written down by Italians, whose own reading is modelled in the second scheme."),
        ("", "Hyphens divide syllables; CAPS mark the stressed syllable of a word of two or more syllables, the last one that is not a final uh."),
        ("uh", "the final e (ə), still sounded; dropped before a vowel"),
        ("‿", "linked to the next word: a final consonant sounded before a vowel (s then as z), or a final uh dropped before one"),
        ("", "a final s, t or p is silent before a word beginning with a consonant, and sounded at a pause"),
        ("ahⁿn ohⁿn ehⁿn", "nasal vowels, with the n or m still sounded after them"),
        ("weh", "oi, as in voirement (vweh-ruh-MAHⁿNT) and avoit"),
        ("ow", "au and al before a consonant: a diphthong, as in cow (autre, chevaus)"),
        ("ch j", "the affricates of church and judge: ch in chastiaus, j and g in je, genz"),
        ("ü", "French u: say ee with rounded lips"),
        ("ö", "eu and ue (deus, truevent): say ay with rounded lips"),
        ("aa ayy ehh eee ohh", "long vowels, left where an s before a consonant fell silent (isle, EEE-luh; nostre)"),
        ("ly ny", "the palatal l of merveille and the palatal n of seignor"),
        ("r", "a trilled r with the tip of the tongue"),
    ],
    "it1300": [
        ("", "The printed spelling read by an Italian reader about 1300, every letter with its Tuscan value; a hypothesis, approximate. Stress stays on the French syllable."),
        ("", "Hyphens divide syllables; CAPS mark the stressed syllable."),
        ("", "every written letter is sounded: final consonants, final e (as ay), and doubled consonants as long ones; there are no nasal vowels"),
        ("ch j", "c and g before e or i (Cypungu, CHEE-; jens, JENS); j is always j"),
        ("k", "ch and q (ch'à, qe): as in Italian che"),
        ("ts dz", "z: ts inside and at the end of a word (voz, VOTS), dz at the start (Zaiton)"),
        ("ny", "gn and ngn (seingnor), as in canyon"),
        ("ay ee oh oo", "the vowels e, i, o, u; y is ee; ou is oo"),
    ],
}
SCHEME_LABELS = {"fr1300": "French about 1300 (approximate)",
                 "it1300": "Read by an Italian about 1300 (hypothesis)"}
