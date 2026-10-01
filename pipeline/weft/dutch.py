"""Early modern Dutch (Linschoten, 1596): modern spelling -> syllables and stress -> sound.

The printed text keeps the spelling of 1596 (Eylandt, ghedeelt, cleyne, mylen). Each token gives,
by hand, the modern Dutch spelling of the same word form in n (eiland, gedeeld, kleine, mijlen);
the form itself is not modernized (ende stays ende, alleenelick becomes alleenelijk, not alleen).
The page shows n under the original as "Modern spelling". The sound of both schemes is computed
from n: the spelling reform of 1804 (Siegenbeek) and its successors fixed a phonemic spelling that
keeps the distinctions this module needs, among them ij against ei, so the 1596 spelling adds
little that n does not carry, and it is far less regular (y, ij and ii for one sound; gh and g; ck,
c and k). Syllable division and stress come from a hand-written lexicon,
`pipeline/weft/data/nl_lexicon.yaml`, keyed by n; letters are turned into sounds by the rules
below, one syllable at a time.

Schemes
-------
h1596    The Dutch of Holland (Amsterdam) around 1596, approximate. Evidence: the spelling of the
         period; the Twe-spraack vande Nederduitsche letterkunst (Amsterdam, 1584), the grammar of
         the chamber of rhetoric In Liefd Bloeyende, usually credited to Hendrick Laurensz.
         Spiegel; Pontus de Heuiter, Nederduitse orthographie (1581); and the historical grammars
         that weigh them (M. Schönfeld, Historische grammatica van het Nederlands, revised by A.
         van Loey, 1959; C. G. N. de Vooys, Geschiedenis van de Nederlandse taal, 1952). Features
         modelled:
         - ij (old long i) is a diphthong, written [ei] here: closer at the start than the modern
           [ɛi], and kept apart from ei (old ai), written [ɛi]. The Twe-spraack still keeps the
           two apart in spelling and treats them as different sounds. The diphthongization of
           long i and u had reached Holland from Brabant during the 16th century and was helped
           by the immigration from the southern Netherlands after 1585; whether a plain [iː] was
           still heard in Amsterdam in 1596 is the main uncertainty of this scheme.
         - ui (old long u) is a diphthong [øy], an early stage of the modern [œy].
         - ou and au are [ɔu]; the modern lowered [ʌu] is later.
         - g is a voiced fricative [ɣ], sch is [sx], ch is [x]. w is bilabial [w].
         - an e in an unstressed syllable is [ə], and the -en of plurals and infinitives keeps its
           n, as the grammarians write and rhyme it; the loss of this n in Holland speech is
           attested but its date and social spread are uncertain.
         - final obstruents are voiceless (landt, ghedeelt: the print often writes the t).
         - r is a tongue-tip trill.
         Not modelled: the distinction of sharp-long and soft-long ee and oo (from old long vowels
         against lengthened short ones), which the grammarians describe but which a per-word
         respelling cannot show reliably; the Holland pronunciation of initial z as s, which the
         print reflects in its wavering between seer and zeer.
modern   Standard Dutch of the Netherlands, the word said alone: ij and ei both [ɛi], ui [œy],
         ou [ʌu], w [ʋ], the final -n of -en dropped as in ordinary speech. g is written [ɣ]; most
         speakers in the Netherlands today devoice it toward [x].

Stress falls on the syllable the lexicon marks (ˈ). Native words stress the first syllable of
the root; the prefixes be-, ge-, ver-, ont- and er- are unstressed; French and Latin loans keep the
stress of their source on the last full syllable (passeert, curieus, different). The same stress
is used in both schemes; for some loans (communicatie, experientie) the stress of 1596 is
uncertain.

Edition token fields (texts/<work>/edition.yaml)
-----------------------------------------------
t      the word as printed, punctuation attached (landt,); the punctuation moves to punct
n      the modern spelling of the same form; clitic groups apart (van 't, dat er)
ocr    the OCR's reading of this token where it differs from the printed page (see line_checks)
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

LEAD_P = re.compile(r"^([(\[„“]+)")
TRAIL_P = re.compile(r"([,;:!?)\]”]+|(?<![0-9])\.)$")
ABBR = re.compile(r"^\w(\.\w)+\.$")          # n.o. keeps its points

_LEX: dict | None = None
_CTX: dict = {}

# monosyllables said without stress in running text (articles, clitics, prepositions,
# conjunctions); everything else of one syllable is stressed
UNSTRESSED = {"de", "het", "'t", "een", "en", "te", "ze", "er", "van", "in", "met", "bij", "om",
              "op", "tot", "als", "of", "die", "dat", "men", "al", "haar", "zij", "wij"}
FIXED = {   # function words whose reduced form is not what the letters give
    "'t": {"h1596": "ət", "modern": "ət"},
    "een": {"h1596": "ən", "modern": "ən"},
    "er": {"h1596": "ər", "modern": "ər"},
}


def lexicon() -> dict:
    global _LEX
    if _LEX is None:
        p = Path(__file__).parent / "data" / "nl_lexicon.yaml"
        _LEX = {ud.normalize("NFC", k): v for k, v in (yaml.safe_load(p.read_text(encoding="utf-8")) or {}).items()}
    return _LEX


def key(word: str) -> str:
    return ud.normalize("NFC", word.replace("’", "'")).lower()


# ---------------------------------------------------------------- spelling -> syllables
VOWEL_G = ["ieuw", "eeuw", "aai", "ooi", "oei", "ouw", "auw", "ieu", "aa", "ee", "oo", "uu", "ie",
           "oe", "eu", "ei", "ij", "ui", "ou", "au", "a", "e", "i", "o", "u", "y", "ë", "é", "ï"]
CONS_G = ["sch", "ch", "ng", "th", "ph", "qu", "dt", "b", "c", "d", "f", "g", "h", "j", "k", "l", "m",
          "n", "p", "r", "s", "t", "v", "w", "x", "z", "'"]
ONSETS2 = {"bl", "br", "dr", "dw", "fl", "fr", "gl", "gr", "kl", "kn", "kr", "kw", "pl", "pr", "sl",
           "sm", "sn", "sw", "tr", "tw", "vl", "vr", "wr", "zw", "schr"}


def graphemes(s: str) -> list[tuple[str, str]]:
    """Split a spelling into (grapheme, 'V' or 'C')."""
    out, i = [], 0
    while i < len(s):
        for g in VOWEL_G:
            if s.startswith(g, i):
                out.append((g, "V")); i += len(g); break
        else:
            for g in CONS_G:
                if s.startswith(g, i):
                    out.append((g, "C")); i += len(g); break
            else:
                out.append((s[i], "C")); i += 1
    return out


def syllabify_rule(word: str) -> list[str]:
    """Rule division, used only when the lexicon has no entry: one consonant goes to the next
    syllable; of a cluster, the longest permitted onset goes to the next syllable."""
    gs = graphemes(word)
    vidx = [k for k, (_, t) in enumerate(gs) if t == "V"]
    if len(vidx) < 2:
        return [word]
    cuts = []
    for a, b in zip(vidx, vidx[1:]):
        cl = [g for g, _ in gs[a + 1:b]]
        if not cl:
            cuts.append(b); continue
        take = 0 if cl[-1] == "ng" else 1
        for n in range(len(cl), 1, -1):
            if "".join(cl[-n:]) in ONSETS2:
                take = n; break
        cuts.append(b - take)
    sylls, start = [], 0
    for c in cuts:
        sylls.append("".join(g for g, _ in gs[start:c])); start = c
    sylls.append("".join(g for g, _ in gs[start:]))
    return sylls


def lex_entry(word: str) -> tuple[list[str], int | None, dict]:
    """(syllables, index of the stressed syllable or None, per-scheme IPA overrides)."""
    e = lexicon().get(key(word))
    over = {}
    if isinstance(e, dict):
        over = {k: v for k, v in e.items() if k in ("h1596", "modern")}
        e = e.get("syl")
    if isinstance(e, str):
        sylls = e.split(".")
        st = next((k for k, s in enumerate(sylls) if s.startswith("ˈ")), None)
        return [s.lstrip("ˈ") for s in sylls], st, over
    sylls = syllabify_rule(key(word))
    if len(sylls) == 1:
        return sylls, (None if key(word) in UNSTRESSED else 0), over
    return sylls, 0, over


# ---------------------------------------------------------------- syllable -> IPA
REDUCED_CODA = {"n", "l", "r", "ns", "nd", "nt", "s", "ls", "rs", "lt", "rt", "rd", "nst", "st", "ts", "t"}
FRONT = ("e", "i", "ij", "y", "ie", "ee", "ei", "ë", "é", "eu")


def nucleus(v: str, scheme: str, stressed: bool, open_: bool, coda: str, last: bool, poly: bool = True) -> str:
    old = scheme == "h1596"
    fixed = {"aa": "aː", "ee": "eː", "oo": "oː", "uu": "y", "ie": "i", "oe": "u", "eu": "øː",
             "ei": "ɛi", "ij": "ei" if old else "ɛi", "y": "ei" if old else "ɛi",
             "ui": "øy" if old else "œy", "ou": "ɔu" if old else "ʌu", "au": "ɔu" if old else "ʌu",
             "ouw": "ɔu" if old else "ʌu", "auw": "ɔu" if old else "ʌu", "eeuw": "eːu",
             "ieuw": "iu", "ieu": "iu", "aai": "aːi", "ooi": "oːi", "oei": "ui", "ï": "i"}
    if v in fixed:
        return fixed[v]
    if v == "a":
        return ("aː" if stressed else "a") if open_ else "ɑ"
    if v in ("e", "ë", "é"):
        if v == "é":
            stressed = True
        if open_:
            return "eː" if stressed else "ə"
        if stressed:
            return "ɛ"
        return "ə" if poly and coda in REDUCED_CODA else "ɛ"
    if v == "i":
        if open_:
            return "i"
        if not stressed and last and coda in ("g", "ch"):
            return "ə"
        return "ɪ"
    if v == "o":
        return ("oː" if stressed else "o") if open_ else "ɔ"
    if v == "u":
        return "y" if open_ else "ʏ"
    return v


def consonant(c: str, scheme: str, coda: bool, nxt: str) -> str:
    old = scheme == "h1596"
    if c == "c":
        c = "s" if nxt.startswith(FRONT) else "k"
    m = {"sch": "s" if coda else "sx", "ch": "x", "ng": "ŋ", "th": "t", "ph": "f", "qu": "kw",
         "dt": "t", "g": "x" if coda else "ɣ", "w": "w" if old else "ʋ", "x": "ks", "j": "j",
         "h": "h", "'": ""}
    out = m.get(c, c)
    if coda:
        out = {"b": "p", "d": "t", "v": "f", "z": "s"}.get(out, out)
    return out


def syllable_ipa(syl: str, scheme: str, stressed: bool, last: bool, poly: bool = True) -> str:
    gs = graphemes(syl)
    vi = next((k for k, (_, t) in enumerate(gs) if t == "V"), None)
    if vi is None:
        return "".join(consonant(g, scheme, True, "") for g, _ in gs)
    onset = gs[:vi]
    v = gs[vi][0]
    coda = gs[vi + 1:]
    coda_s = "".join(g for g, _ in coda)
    out = "".join(consonant(g, scheme, False, (onset[k + 1][0] if k + 1 < len(onset) else v))
                  for k, (g, _) in enumerate(onset))
    if not stressed and poly and v == "ij" and syl.startswith("lij"):
        out += "ə"                     # -lijk, -lijks, -lijke: reduced in both schemes
    else:
        out += nucleus(v, scheme, stressed, not coda, coda_s, last, poly)
    cod = ""
    for k, (g, _) in enumerate(coda):
        nx = coda[k + 1][0] if k + 1 < len(coda) else ""
        if g == "n" and nx in ("k", "c", "g", "ch"):
            cod += "ŋ"; continue
        cod += consonant(g, scheme, True, nx)
    # the -en of plurals and infinitives: n kept in 1596, dropped in modern speech
    if scheme == "modern" and last and not stressed and out.endswith("ə") and cod == "n":
        cod = ""
    return out + cod


def word_ipa(word: str, scheme: str) -> tuple[str, int, bool]:
    """(ipa, syllable count, from_lexicon)."""
    k = key(word)
    if k in FIXED:
        return FIXED[k][scheme], 1, True
    sylls, st, over = lex_entry(word)
    if over.get(scheme):
        ipa = over[scheme]
        return ipa, len(ipa.split(".")), True
    parts = []
    for i, s in enumerate(sylls):
        nxt = sylls[i + 1] if i + 1 < len(sylls) else ""
        ip = syllable_ipa(s, scheme, i == st, i == len(sylls) - 1, len(sylls) > 1)
        # a doubled consonant letter (hebben, matten) is one consonant: the vowel before it stays
        # short, and the sound is said once, at the start of the next syllable
        if nxt and s[-1:] == nxt[:1] and s[-1:] not in "aeiouyë":
            ip = ip[:-1] if not ip.endswith(("ŋ",)) else ip
        parts.append(("ˈ" if i == st and (len(sylls) > 1 or st is not None) else "") + ip)
    return ".".join(parts), len(sylls), k in lexicon()


# ---------------------------------------------------------------- IPA -> respelling
RESPELL = [("aːi", "aay"), ("oːi", "ohy"), ("eːu", "ayw"), ("ɛi", "ei"), ("ei", "ey"), ("øy", "öy"),
           ("œy", "öy"), ("ɔu", "ow"), ("ʌu", "ow"), ("ui", "ooy"), ("iu", "eew"), ("aː", "aa"),
           ("eː", "ay"), ("oː", "oh"), ("øː", "öö"), ("sx", "skh"), ("ɑ", "ah"), ("ɛ", "e"),
           ("ə", "uh"), ("ɪ", "i"), ("i", "ee"), ("ɔ", "o"), ("o", "oh"), ("u", "oo"), ("y", "ü"),
           ("ʏ", "ö"), ("x", "kh"), ("ɣ", "gh"), ("ŋ", "ng"), ("ʋ", "w"), ("j", "y"), ("ʃ", "sh")]


def respell_syl(s: str) -> str:
    out, i = "", 0
    while i < len(s):
        for a, b in RESPELL:
            if s.startswith(a, i):
                out += b; i += len(a); break
        else:
            out += s[i]; i += 1
    return out


def respell(ipa: str) -> str:
    words = []
    for w in ipa.split(" "):
        sy = []
        for s in w.split("."):
            r = respell_syl(s.lstrip("ˈ"))
            sy.append(r.upper() if s.startswith("ˈ") else r)
        words.append("-".join(sy))
    return " ".join(words)


# ---------------------------------------------------------------- language hooks
def token_fields(surface: str, et: dict, group: dict) -> tuple[dict, list[tuple[str, str]]]:
    """Split punctuation off the printed word, check every polysyllable against the lexicon, and
    hold the token's ipa override for phonemize, which draft calls next for this token."""
    global _CTX
    fields: dict = {}
    fails: list[tuple[str, str]] = []
    word = surface
    ml = LEAD_P.search(word)
    if ml:
        fields["lead"] = ml.group(1)
        word = word[ml.end():]
    if not ABBR.match(word):
        mt = TRAIL_P.search(word)
        if mt:
            fields["punct"] = mt.group(1)
            word = word[:mt.start()]
    if word != surface:
        fields["surface"] = word
    n = et.get("n")
    if not n:
        fails.append(("modern-spelling-missing", surface))
    else:
        for w in n.split():
            sylls, _, _ = lex_entry(w)
            if len(sylls) > 1 and key(w) not in lexicon() and not et.get("ipa"):
                fails.append(("syllables-by-rule", w))
    _CTX = {"n": n, "ipa": et.get("ipa") or {}}
    return fields, fails


def phonemize(word: str, scheme: str = "h1596", quantities=None, **_) -> dict:
    """`word` is the token's modern spelling (n); a clitic group (van 't) is said word by word."""
    ov = (_CTX.get("ipa") or {}).get(scheme) if _CTX.get("n") == word else None
    if ov:
        return {"ipa": ov, "respell": respell(ov), "syllables": len(re.split(r"[. ]", ov))}
    parts, n = [], 0
    for w in word.split():
        ipa, k, _ = word_ipa(w, scheme)
        parts.append(ipa); n += k
    ipa = " ".join(parts)
    return {"ipa": ipa, "respell": respell(ipa), "syllables": n}


# ---------------------------------------------------------------- OCR sensor
_OCR: dict[str, str] = {}
_W = re.compile(r"<span class=['\"]ocrx_word['\"][^>]*title=['\"]bbox (\d+) (\d+) (\d+) (\d+)[^'\"]*['\"][^>]*>(.*?)</span>", re.S)
_PAGE = re.compile(r"<div class=['\"]ocr_page['\"] id=['\"]([^'\"]+)['\"]")


def ocr_body(path: Path, pages: dict) -> str:
    """The words inside each page's body column, in reading order, line-end hyphens rejoined,
    without spaces."""
    import html
    h = path.read_text(encoding="utf-8")
    starts = [(m.start(), m.group(1)) for m in _PAGE.finditer(h)]
    out = []
    for k, (pos, pid) in enumerate(starts):
        if pid not in pages:
            continue
        x0, y0, x1, y1 = pages[pid]
        seg = h[pos:starts[k + 1][0] if k + 1 < len(starts) else len(h)]
        for line in re.split(r"(?=<span class=['\"]ocr_line)", seg)[1:]:
            ws = [html.unescape(re.sub(r"<[^>]+>", "", t)).strip()
                  for a, b, _, _, t in _W.findall(line) if x0 <= int(a) < x1 and y0 <= int(b) < y1]
            ws = [w for w in ws if w]
            if not ws:
                continue
            if ws[-1].endswith("-"):
                ws[-1] = ws[-1][:-1]
            out.append("".join(ws))
    return re.sub(r"\s+", "", "".join(out))


def line_checks(text: str, etoks: list[dict], edition: dict) -> list[tuple[str, str]]:
    """Sensor: the line, with each token's declared OCR reading in place of the printed word,
    must occur in the OCR of the page's body column (edition-not-in-source otherwise)."""
    oc = edition.get("ocr_check")
    if not oc:
        return []
    from .paths import work_dir
    p = work_dir(Path(__file__).resolve().parents[2], edition["work"]) / oc["file"]
    if str(p) not in _OCR:
        if not p.exists():
            return [("ocr-source-missing", oc["file"])]
        _OCR[str(p)] = ocr_body(p, oc["pages"])
    want = "".join((t.get("ocr") or t["t"]) + (t.get("p") or "") for t in etoks)
    want = re.sub(r"\s+", "", want)
    if want not in _OCR[str(p)]:
        return [("edition-not-in-source", " ".join(t["t"] for t in etoks[:4]) + " ...")]
    return []


KEY = {
    "h1596": [
        ("", "Dutch of Holland (Amsterdam) around 1596, approximate: reconstructed from the spelling of the period and the grammarians of the Twe-spraack (1584)."),
        ("CAPS", "the stressed syllable; hyphens divide syllables. Small words (de, het, van, die) are unstressed"),
        ("uh", "the reduced vowel of unstressed syllables (ə), as in the a of about"),
        ("ey", "ij (old long i), a diphthong starting near the vowel of say: closer than today's ei, and kept apart from it"),
        ("ei", "ei and ey (cleyne, Eylandt): e as in bet gliding to ee"),
        ("öy", "ui (huysen): a rounded e gliding to a rounded ee"),
        ("ow", "ou, au (hout, cout): o as in hot gliding to oo"),
        ("aa ay oh öö", "long vowels: a as in father, ay as in say without a glide, oh as in so without a glide, öö a long rounded ay"),
        ("ah", "short a, as in father but short"),
        ("ö ü", "ü: say ee with rounded lips; ö (short u, as in dus): a short rounded vowel"),
        ("gh", "g: a voiced fricative made at the back of the mouth, as in Spanish lago"),
        ("kh", "ch: the ch of Scottish loch"),
        ("skh", "sch at the start of a word: s followed by kh"),
        ("w", "w made with both lips, as in English"),
        ("r", "a trilled r with the tip of the tongue"),
        ("-uhn", "the -en of plurals and infinitives, with its n"),
    ],
    "modern": [
        ("", "Standard Dutch of the Netherlands today, each word said alone."),
        ("CAPS", "the stressed syllable; hyphens divide syllables. Small words (de, het, van, die) are unstressed"),
        ("uh", "the reduced vowel of unstressed syllables (ə); the final n of -en is dropped, as in ordinary speech"),
        ("ei", "ij and ei, one sound: e as in bet gliding to ee"),
        ("öy", "ui: a rounded open e gliding to a rounded ee"),
        ("ow", "ou, au: a vowel near the u of cut gliding to oo"),
        ("aa ay oh öö", "long vowels; ay and oh glide slightly in today's speech"),
        ("ah", "short a, as in father but short"),
        ("ö ü", "ü: say ee with rounded lips; ö: a short rounded vowel"),
        ("gh", "g: a fricative at the back of the mouth; most speakers in the Netherlands now say it voiceless, like kh"),
        ("kh", "ch: the ch of Scottish loch"),
        ("skh", "sch at the start of a word: s followed by kh"),
        ("w", "w made with the lower lip against the upper teeth, softer than English v"),
    ],
}
SCHEME_LABELS = {"h1596": "Holland Dutch about 1596: Linschoten's day (approximate)",
                 "modern": "Modern Standard Dutch"}
