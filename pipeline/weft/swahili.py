"""Swahili of Zanzibar, as written down by Edward Steere (1870): spelling -> syllables -> sound.

The printed text keeps Steere's roman spelling of 1870 (hatta, assubui, bass, asikari, Muungu,
mgine, wangine, weye). Each token also gives, by hand, the modern standard Swahili form of the
same word in n (hata, asubuhi, basi, askari, Mungu, mwingine, wengine, wewe). n changes spelling
and the phonological shape of a word, never its grammar: concords (Sultani ya, where the modern
standard has Sultani wa), tense forms (naliwaambia, modern niliwaambia) and word choice (enenda
beside enda) are kept as the narrator said them. The page shows n under the original as "Modern
standard form".

Steere's spelling is close to phonemic, and he says how to read it: "the vowels are pronounced as
in Italian, the consonants as in English, and ... there is always an accent on the last syllable
but one" (Swahili Tales, 1870, preface, p. xiv). The Handbook gives the letter values in detail
(A Handbook of the Swahili Language as Spoken at Zanzibar, third edition, revised by A. C. Madan,
1884, pp. 8-15). Both schemes are computed by the same rules: the first from Steere's letters, the
second from n.

Schemes
-------
z1870    Zanzibar town Swahili about 1870, approximate: Steere's letters read by the values his
         Handbook gives them. Features modelled:
         - five vowels, a e i o u, each its own syllable ("the vowels are all pronounced
           distinctly, and do not form diphthongs"); e is open [ɛ] ("a in chair"), o open [ɔ]
           ("o in boy, more like au than the common English o").
         - a + e: "when a formative particle ending in -a is placed before a word beginning with
           e-, the two letters coalesce into a long e sound", usually but not always. Applied
           where a and e meet before a consonant (wakaenda [wa.ˈkeː.nda]).
         - m before any consonant except b or w is a syllable of its own and can carry the
           accent: mtu [ˈm.tu], mzee [m.ˈzɛ.ɛ], mmoja [m.ˈmɔ.dʒa]. n is a syllable before ch, f,
           h, k, m, n, p, s, t (Steere lists ch, f, h, m, n, s). Before b (m) and d, g, j, z (n)
           the nasal begins the next syllable (mbuyu, kunguru [ku.ˈŋgu.ɾu]). A word whose only
           vowel follows a nasal and a consonant takes the nasal as a syllable (nje [ˈn.dʒɛ]).
         - ny [ɲ], ng' [ŋ], ch [tʃ], sh [ʃ], j [dʒ], y [j], r a tap [ɾ]; the Arabic sounds th
           [θ], dh [ð], gh [ɣ], kh [x] (none occurs in this tale).
         - double consonants in Arabic loans are kept as Steere writes them (hatta [ˈhat.ta],
           assubui [as.su.ˈbu.i]); his Handbook notes "a strong tendency in all such cases to
           drop one of the consonants", so the long consonant is uncertain. A final consonant
           (bass) closes the syllable.
         - the accent on the last syllable but one, counting a syllabic nasal.
         Not modelled: the "explosive or aspirated" p, t, k that Steere hears where a nasal has
         been lost (plural pepo), which he says the refined speakers smooth down; implosive b,
         d, g, which later descriptions report and Steere does not mention; tone and intonation.
modern   Standard Swahili (Kiswahili sanifu), the word said alone, computed from n by the same
         rules without the a + e coalescence. Standard Swahili was fixed in the 1930s on the
         Zanzibar town dialect, so the two schemes differ mainly where the spelling of a word
         has changed (hatta/hata, assubui/asubuhi, Muungu/Mungu).

Edition token fields (texts/<work>/edition.yaml)
-----------------------------------------------
t      the word as printed in 1870, punctuation attached (kunguru,); the punctuation moves to punct
n      the modern standard form of the same word (see above)
ocr    the OCR's reading of this token where it differs from the printed page (see line_checks)
ipa    {scheme: ipa} override for this occurrence
"""
from __future__ import annotations

import re
from pathlib import Path

VERSION = "0.1"
SHOW_TRANSLIT = True
TRANSLIT_LABEL = "Modern standard form"

LEAD_P = re.compile(r"^([(\[“‘\"]+)")
TRAIL_P = re.compile(r"([,;:!?.—)\]”’\"]+)$")

VOWELS = {"a": ("a", "a"), "e": ("ɛ", "e"), "i": ("i", "ee"), "o": ("ɔ", "o"), "u": ("u", "oo"),
          "Ē": ("eː", "ay")}                           # Ē: a + e coalesced (z1870 only)
# consonant graphemes, longest first: (ipa, respelling)
CONS = [("ng'", "ŋ", "ng'"), ("ch", "tʃ", "ch"), ("sh", "ʃ", "sh"), ("ny", "ɲ", "ny"),
        ("th", "θ", "th"), ("dh", "ð", "dh"), ("gh", "ɣ", "gh"), ("kh", "x", "kh"),
        ("b", "b", "b"), ("d", "d", "d"), ("f", "f", "f"), ("g", "g", "g"), ("h", "h", "h"),
        ("j", "dʒ", "j"), ("k", "k", "k"), ("l", "l", "l"), ("m", "m", "m"), ("n", "n", "n"),
        ("p", "p", "p"), ("r", "ɾ", "r"), ("s", "s", "s"), ("t", "t", "t"), ("v", "v", "v"),
        ("w", "w", "w"), ("y", "j", "y"), ("z", "z", "z")]
GLIDES = {"w", "y"}
NASAL_ONSET = {"m": {"b", "v", "w"}, "n": {"d", "g", "j", "z"}}   # nasal + these begins a syllable
# monosyllables said without stress in running speech: the associative -a, na, kwa
UNSTRESSED = {"ya", "wa", "za", "la", "cha", "vya", "pa", "kwa", "mwa", "na"}
# letters Steere's alphabet uses (Handbook pp. 8-11): no c without h, no q, no x
STEERE_LETTERS = set("abcdefghijklmnoprstuvwyz'")

_CTX: dict = {}


def units(word: str) -> list[tuple[str, str]]:
    """'kunguru' -> [('C','k'),('V','u'),('C','n'),('C','g'),...]; Ē stays a vowel."""
    out, i = [], 0
    while i < len(word):
        ch = word[i]
        if ch in VOWELS:
            out.append(("V", ch)); i += 1; continue
        for g, _, _ in CONS:
            if word.startswith(g, i):
                out.append(("C", g)); i += len(g); break
        else:
            i += 1                                     # apostrophe or stray mark: skip
    return out


def syllables(word: str) -> list[list[tuple[str, str]]]:
    """Open syllables; a syllabic nasal is a syllable of its own; a consonant that cannot begin
    the next syllable (geminate, final consonant, Arabic cluster) closes the one before."""
    us = units(word)
    nvow = sum(1 for k, _ in us if k == "V")
    sylls: list[list] = []
    cur: list = []
    for i, (k, g) in enumerate(us):
        nxt = us[i + 1] if i + 1 < len(us) else None
        if k == "C" and g in ("m", "n") and nxt and nxt[0] == "C":
            prenasal = nxt[1] in NASAL_ONSET[g] and not (i == 0 and nvow == 1 and nxt[1] != "w")
            if not prenasal:                           # syllabic m / n
                if cur:
                    _close(sylls, cur)
                sylls.append([("N", g)]); cur = []
                continue
        cur.append((k, g))
        if k == "V":
            _close(sylls, cur); cur = []
    if cur:                                            # final consonant(s): coda of the last syllable
        cur = [u for k_, u in enumerate(cur) if k_ == 0 or u != cur[k_ - 1]]   # bass: one s at the end
        if sylls:
            sylls[-1].extend(cur)
        else:
            sylls.append(cur)
    return sylls


def _close(sylls: list, cur: list) -> None:
    """cur ends in a vowel. Keep the longest legal onset ([N]C[w|y]); earlier consonants are coda."""
    cons = [u for u in cur if u[0] == "C"]
    keep = 0
    j = len(cons)
    if j:
        keep = 1
        if j >= 2 and cons[-1][1] in GLIDES:
            keep = 2
        if j > keep and cons[-keep - 1][1] in ("m", "n") and cons[-keep][1] in NASAL_ONSET[cons[-keep - 1][1]]:
            keep += 1
    coda = cons[:j - keep]
    if coda and sylls and sylls[-1][-1][0] != "N":
        sylls[-1].extend(coda)
        cur = cur[len(coda):]
    sylls.append(list(cur))


def _seg(u: tuple[str, str], nxt: str | None) -> tuple[str, str]:
    k, g = u
    if k == "V":
        return VOWELS[g]
    if k == "N":
        return (g, g)
    if g == "n" and nxt == "g":
        return ("ŋ", "n")
    for gg, ipa, rs in CONS:
        if gg == g:
            return (ipa, rs)
    return (g, g)


def word_sound(word: str, scheme: str) -> tuple[str, str, int]:
    w = word.lower().replace("’", "'")
    if scheme == "z1870":
        w = re.sub(r"ae(?=[^aeiou'])", "Ē", w)
    sy = syllables(w)
    n = len(sy)
    stress = n - 2 if n >= 2 else (0 if w not in UNSTRESSED else None)
    ipas, rss = [], []
    for k, s in enumerate(sy):
        ip, rs = "", ""
        for j, u in enumerate(s):
            nxt = s[j + 1][1] if j + 1 < len(s) else None
            a, b = _seg(u, nxt)
            ip += a; rs += b
        ipas.append(("ˈ" if k == stress and n > 1 else "") + ip)
        rss.append(rs.upper() if k == stress else rs)
    return ".".join(ipas), "-".join(rss), n


def respell_ipa(ipa: str) -> str:
    """Respelling for an ipa override: syllables by '.', stress by ˈ."""
    back = {"a": "a", "ɛ": "e", "i": "ee", "ɔ": "o", "u": "oo", "eː": "ay", "tʃ": "ch", "ʃ": "sh",
            "ɲ": "ny", "ŋg": "ng", "ŋ": "ng'", "dʒ": "j", "j": "y", "ɾ": "r", "θ": "th", "ð": "dh",
            "ɣ": "gh", "x": "kh"}
    out = []
    for word in ipa.split():
        parts = []
        for syl in word.split("."):
            st = syl.startswith("ˈ")
            syl = syl.lstrip("ˈ")
            r = syl
            for k in sorted(back, key=len, reverse=True):
                r = r.replace(k, "\x00" + back[k] + "\x01")
            r = r.replace("\x00", "").replace("\x01", "")
            parts.append(r.upper() if st else r)
        out.append("-".join(parts))
    return " ".join(out)


# ---------------------------------------------------------------- language hooks
def token_fields(surface: str, et: dict, group: dict) -> tuple[dict, list[tuple[str, str]]]:
    """Split punctuation off the printed word, check its letters against Steere's alphabet, and
    hold the printed form and any ipa override for phonemize, which draft calls next."""
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
    low = word.lower()
    if set(low) - STEERE_LETTERS or re.search(r"c(?!h)", low):
        fails.append(("letter-outside-steere-alphabet", word))
    n = et.get("n")
    if not n:
        fails.append(("modern-form-missing", surface))
    _CTX = {"t": word, "n": n, "ipa": et.get("ipa") or {}}
    return fields, fails


def phonemize(word: str, scheme: str = "z1870", quantities=None, **_) -> dict:
    """`word` is the token's modern form (n). The 1870 scheme reads the printed form instead,
    which token_fields has just stored for this token."""
    mine = _CTX.get("n") == word
    ov = (_CTX.get("ipa") or {}).get(scheme) if mine else None
    if ov:
        return {"ipa": ov, "respell": respell_ipa(ov), "syllables": len(re.split(r"[. ]", ov))}
    src = _CTX["t"] if (scheme == "z1870" and mine and _CTX.get("t")) else word
    ipas, rss, n = [], [], 0
    for w in src.split():
        ipa, rs, k = word_sound(w, scheme)
        ipas.append(ipa); rss.append(rs); n += k
    return {"ipa": " ".join(ipas), "respell": " ".join(rss), "syllables": n}


# ---------------------------------------------------------------- OCR sensor
_OCR: dict[str, str] = {}


def ocr_text(path: Path) -> str:
    """The archive.org plain-text OCR with words broken at a line end rejoined and all
    whitespace removed, so the comparison ignores line breaks and the OCR's spacing."""
    raw = path.read_text(encoding="utf-8")
    raw = re.sub(r"-\s*\n\s*", "", raw)
    return re.sub(r"\s+", "", raw)


def line_checks(text: str, etoks: list[dict], edition: dict) -> list[tuple[str, str]]:
    """Sensor: the line, with each token's declared OCR reading in place of the printed word,
    must occur in the OCR of the 1870 scan (edition-not-in-ocr otherwise). The edition is
    transcribed from the scan and checked verbatim against Wikisource by verify_in; this second
    check ties it to the scan's own OCR, and every place the OCR misreads the page is declared."""
    oc = edition.get("ocr_check")
    if not oc:
        return []
    from .paths import work_dir
    p = work_dir(Path(__file__).resolve().parents[2], edition["work"]) / oc["file"]
    if str(p) not in _OCR:
        if not p.exists():
            return [("ocr-source-missing", oc["file"])]
        _OCR[str(p)] = ocr_text(p)
    want = re.sub(r"\s+", "", "".join((t.get("ocr") or t["t"]) + (t.get("p") or "") for t in etoks))
    if want not in _OCR[str(p)]:
        return [("edition-not-in-ocr", " ".join(t["t"] for t in etoks[:4]) + " ...")]
    return []


KEY = {
    "z1870": [
        ("", "Zanzibar town Swahili about 1870, approximate: Steere's letters read by the values his Handbook gives them (vowels as in Italian, consonants as in English)."),
        ("CAPS", "the accented syllable, always the last but one; hyphens divide syllables. Small words (ya, wa, na, kwa) are unaccented"),
        ("a e o", "a as in father; e as in bet; o as in for (open, \"more like au\" in Steere's words)"),
        ("ee oo", "i and u: the vowels of see and too, short. Every vowel is its own syllable"),
        ("ay", "a and e run together into one long e (wakaenda: wa-KAY-nda), as Steere says is usual after a prefix ending in -a"),
        ("m- n-", "a nasal that is a syllable by itself, before another consonant: mtu M-too, mzee m-ZE-e, nje N-je"),
        ("mb nd ng nj nz", "a nasal and a consonant together at the start of a syllable: kunguru koo-NGOO-roo, with ng as in finger"),
        ("ng'", "ng as in singer, with no g after it"),
        ("ny", "ny as in canyon"),
        ("j", "j as in joy"),
        ("y", "y as in yes"),
        ("r", "a light tap of the tongue, as in Spanish pero"),
        ("tt ss", "double consonants in Arabic loanwords (hatta, assubui), kept as Steere writes them; he notes they were often reduced to one"),
    ],
    "modern": [
        ("", "Standard Swahili today, each word said alone, from the modern standard form shown under the text."),
        ("CAPS", "the accented syllable, the last but one; hyphens divide syllables. Small words (ya, wa, na, kwa) are unaccented"),
        ("a e o", "a as in father; e as in bet; o as in for"),
        ("ee oo", "i and u: the vowels of see and too, short. Every vowel is its own syllable"),
        ("m- n-", "a nasal that is a syllable by itself, before another consonant: mtu M-too, mzee m-ZE-e"),
        ("mb nd ng nj nz", "a nasal and a consonant together at the start of a syllable; ng as in finger"),
        ("ng'", "ng as in singer, with no g after it"),
        ("ny", "ny as in canyon"),
        ("j", "j as in joy; many speakers make it with the tongue flat against the palate"),
        ("y", "y as in yes"),
        ("r", "a light tap of the tongue, as in Spanish pero"),
    ],
}
SCHEME_LABELS = {"z1870": "Zanzibar Swahili about 1870: Steere's day (approximate)",
                 "modern": "Modern Standard Swahili"}
