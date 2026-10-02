"""Middle Mongolian of the Secret History, as the Ming court wrote it in Chinese characters.

The Secret History of the Mongols survives only in an early Ming transcription made for teaching
Mongolian: each Mongolian word is spelled out syllable by syllable in Chinese characters, a
Chinese word gloss (旁譯, pangyi) stands beside each word, and a short Chinese summary (總譯,
zongyi) follows each section. The Uyghur-script original is lost. Weft's text is the edition of
Shiratori Kurakichi, Onyaku Mōbun Genchō hishi (Tōyō Bunko, 1943), as transcribed on Japanese
Wikisource. Shiratori reprints the Ye Dehui edition of 1908 column for column and adds a
romanization of his own under each word.

The Ming spelling devices
-------------------------
Chinese of the 14th century had no syllable-final l, r, s or q and no uvular stops, so the
transcribers added small marks (Shiratori's preface, 凡例, sets them out):
  中  written at the left shoulder of an h- character: the uvular q or γ (中合 qa, against 合 ha)
  舌  written at the left shoulder of an l- character: r, not l (舌列 re, against 列 le)
  small 勒 木 思 惕 黑 克 卜, set beside the line: a consonant with no vowel, l m s d γ g b
On the page the surface row gives the characters without the shoulder marks and with the small
characters at full size, which is how most plain-text editions print them. The marked form, with
each shoulder mark in angle brackets before its character (〈舌〉列) and each small character in
angle brackets after its syllable (列〈克〉), is kept as `printed` and shown in the word panel.

Token fields (edition.yaml)
---------------------------
  t    the characters as Shiratori prints them, without the shoulder marks, his hyphens and the
       variation selectors of the wiki text; checked verbatim against the pinned source by
       `weft draft` (verify_in, verify_strip)
  pr   the same with the marks (convention above); checked against the source by a sensor here
  pz   the Ming word gloss (旁譯) as Shiratori prints it. His parentheses mark what he added or
       corrected: he normalized 名 'name' to 人名, 婦人名, 兒名 and so on (凡例)
  sh   Shiratori's romanization, verbatim (he writes ž for j, j for y, γ̇ and ġ for the hiatus)
  n    optional: Weft's romanization where the conversion rule below gets it wrong

Romanization (the transliteration row, "Middle Mongolian")
----------------------------------------------------------
Weft converts Shiratori's romanization by rule into the conventions of current English-language
work (the general practice of Igor de Rachewiltz's index and translation; no text of his is
copied): ž > j, j > y, ṅ > ng, γ̇ and ġ > ' (a hiatus where an older consonant was lost), an
initial γ > q, Shiratori's (n) after the genitive dropped, name parts joined by a space and
suffixes by a hyphen, lower case except in names. Where the rule is wrong for a word, `n` in the
edition overrides it, and the token's provenance says so with Shiratori's form beside it. Two
sensors test the result against the Ming spelling: the shoulder marks (every 舌 is an r, every
r has a 舌; every 中 is a q or γ before a vowel other than i) and vowel harmony (a word has back
vowels a o u or front vowels e ö ü, not both; i goes with either).

Scheme
------
mm-1250  Middle Mongolian of the mid-13th century, reconstructed and approximate. Vowels a e i o
         u ö ü, with ö and ü front rounded as in German. Stops and affricates are taken to
         contrast in aspiration rather than voicing: the transcribers wrote t, č, k, q with
         aspirated Chinese initials (塔 ta, 察 ča) and d, j, g, b with unaspirated ones (荅 da,
         札 ja), which Shiratori's preface also notes; modern Mongolian has the same contrast.
         q is uvular, γ a voiced uvular fricative, h a plain h (from older p-, lost later).
         Two vowels in hiatus (') are said as two syllables; by the 14th century many had
         probably merged into one long vowel, and the scheme does not decide where. Stress is
         put on the first syllable, as in the usual account of Mongolian; it is not attested
         for the 13th century. There is no second scheme: a modern Khalkha reading would mean
         substituting modern words, not reading these.
"""
from __future__ import annotations

import re
import unicodedata as ud
from pathlib import Path

VERSION = "0.1"
SCRIPT_LABEL = "Ming gloss (旁譯)"
SCRIPT_WORD = "Ming gloss (旁譯)"
SHOW_TRANSLIT = True
TRANSLIT_LABEL = "Middle Mongolian"
REPO = Path(__file__).resolve().parents[2]

LAYERS = {
    "script": {"src": "the Ming word gloss (旁譯) as printed by Shiratori (1943), verbatim"},
    "translit": {"src": f"weft.mongolian {VERSION}: Shiratori's romanization converted by rule, hand-corrected where marked"},
    "printed": {"src": "the transcription with the Ming shoulder marks and small characters, from Shiratori (1943)"},
}

VS = re.compile("[︀-️]")
BACK, FRONT = set("aou"), set("eöü")
NAME_GLOSS = re.compile(r"(人|女|兒|地|山|水|河|馬|部落|\))名|姓氏|^\(人\)")


# ---------------------------------------------------------------- romanization
def from_shiratori(sh: str, pz: str = "") -> str:
    """Shiratori's romanization -> Weft's (de Rachewiltz-style) by the documented rule."""
    s = sh.strip().strip('".,:;')
    s = s.replace("(n)", "").replace("(", "").replace(")", "")
    s = ud.normalize("NFC", s).replace("γ̇", "'").replace("ġ", "'").replace("ṅ", "ng")
    s = s.replace("j", "y").replace("ž", "j").replace("Ž", "J")
    # a name: the Ming gloss says whose name (人名, 婦人名, 地名, 山名, (兒)名 ...) or gives a clan name
    named = bool(NAME_GLOSS.search(pz))
    parts = s.split("-")
    out = ""
    for k, p in enumerate(parts):
        if p[:1] in ("γ", "Γ"):
            p = ("Q" if p[0] == "Γ" else "q") + p[1:]
        cap = named and (k == 0 or p[:1].isupper())
        p = (p[:1].upper() + p[1:]) if cap else p.lower()
        if k == 0:
            out = p
        else:
            out += (" " if cap else "-") + p
    return out


def _markers_check(pr: str, n: str) -> list[tuple[str, str]]:
    """The Ming shoulder marks against the romanization: 舌 is r, 中 is q/γ (not before i)."""
    fails = []
    letters = n.lower().replace("'", "")
    r_marks, r_count = pr.count("〈舌〉"), letters.count("r")
    if r_marks != r_count:
        fails.append(("marker-r-mismatch", f"{pr} {n}: 舌 {r_marks}, r {r_count}"))
    q_marks = pr.count("〈中〉")
    q_count = len(re.findall(r"[qγ](?=[aeouöü])", letters))
    if q_marks != q_count:
        fails.append(("marker-q-mismatch", f"{pr} {n}: 中 {q_marks}, q/γ {q_count}"))
    return fails


def _harmony_check(n: str) -> list[tuple[str, str]]:
    fails = []
    for w in n.lower().split():
        vs = set(w)
        if vs & BACK and vs & FRONT:
            fails.append(("vowel-harmony", n))
    return fails


# ---------------------------------------------------------------- source sensor
_SRC: dict[str, list[tuple[str, str, str, str]]] = {}


def _parse_source(rel: str) -> list[tuple[str, str, str, str]]:
    """Every word of the pinned source, in order: (t, pr, pz, sh)."""
    if rel in _SRC:
        return _SRC[rel]
    hits = sorted((REPO / "texts").glob(f"*/{rel}")) + sorted((REPO / "private").glob(f"*/{rel}"))
    if not hits:
        _SRC[rel] = []
        return []
    txt = hits[0].read_text(encoding="utf-8")
    txt = re.sub(r"\{\{ϴ\|入力者注=(?:[^{}]|\{\{[^{}]*\}\})*\}\}", "", txt)
    out = []
    for m in re.finditer(r"\{\{ϕ\|((?:[^{}|]|\{\{ϕ\|[LR]=.\}\})+)\|([^{}|]*)\|([^{}|]*)\}\}", txt):
        raw, pz, sh = m.groups()
        pr = re.sub(r"\{\{ϕ\|L=(.)\}\}", r"〈\1〉", raw)
        pr = re.sub(r"\{\{ϕ\|R=(.)\}\}", r"〈\1〉", pr)
        pr = VS.sub("", pr).replace("-", "")
        t = re.sub(r"〈[中舌]〉", "", pr).replace("〈", "").replace("〉", "")
        out.append((t, pr, VS.sub("", pz), sh))
    _SRC[rel] = out
    return out


def line_checks(text: str, etoks: list[dict], edition: dict) -> list[tuple[str, str]]:
    """The marked form, the Ming gloss and Shiratori's romanization must stand in the source
    as one run of words, in order, exactly as the edition carries them."""
    src = _parse_source(edition.get("verify_in", ""))
    if not src:
        return [("source-unparsed", edition.get("verify_in", "?"))]
    want = [(et["t"], et.get("pr", et["t"]), et.get("pz", ""), et.get("sh", "")) for et in etoks]
    k = len(want)
    for i in range(len(src) - k + 1):
        if src[i:i + k] == want:
            return []
    # locate the first word that disagrees, for the sample
    for i in range(len(src) - k + 1):
        if src[i][0] == want[0][0] and all(src[i + j][0] == want[j][0] for j in range(k)):
            bad = next(j for j in range(k) if src[i + j] != want[j])
            return [("marks-gloss-not-in-source", f"{want[bad]} vs {src[i + bad]}")]
    return [("marks-gloss-not-in-source", text)]


def token_fields(surface: str, et: dict, group: dict) -> tuple[dict, list[tuple[str, str]]]:
    fields: dict = {}
    fails: list[tuple[str, str]] = []
    if et.get("pz"):
        fields["script"] = et["pz"]
    pr = et.get("pr", surface)
    if pr != surface:
        fields["printed"] = pr
    sh = et.get("sh", "")
    rule = from_shiratori(sh, et.get("pz", "")) if sh else ""
    n = et.get("n") or rule
    if not n:
        fails.append(("romanization-missing", surface))
        return fields, fails
    fields["norm"] = n
    fields["shiratori"] = sh
    how = ("Weft romanization by rule from Shiratori (1943), who reads " if n == rule
           else "Weft romanization, hand-corrected; Shiratori (1943) reads ")
    fields["prov"] = {"sound": f"weft.mongolian {VERSION} from the romanization. {how}{sh.strip(chr(34) + '.,:;')}",
                      "translit": "rule" if n == rule else "hand"}
    fails += _markers_check(pr, n)
    fails += _harmony_check(n)
    return fields, fails


def line_metre(etoks, edition):
    return False, []          # prose: no metre


# ---------------------------------------------------------------- sound
VOWELS = set("aeiouöü")
IPA_V = {"a": "a", "e": "e", "i": "i", "o": "o", "u": "u", "ö": "ø", "ü": "y"}
IPA_C = {"b": "p", "d": "t", "t": "tʰ", "g": "k", "k": "kʰ", "q": "qʰ", "γ": "ʁ", "h": "h",
         "č": "tʃʰ", "j": "tʃ", "š": "ʃ", "s": "s", "m": "m", "n": "n", "ŋ": "ŋ", "l": "l",
         "r": "r", "y": "j", "w": "w", "p": "pʰ"}
RSP_C = {"γ": "gh", "č": "ch", "š": "sh", "ŋ": "ng"}


def _segments(word: str) -> list[str]:
    w = ud.normalize("NFC", word.lower()).replace("-", "")
    w = w.replace("ng", "ŋ")
    return [c for c in w if c in VOWELS or c in IPA_C or c == "'"]


def _syllables(segs: list[str]) -> list[list[str]]:
    """(C)V(V)(C): a single consonant goes with the following vowel; a hiatus mark splits two
    vowels into two syllables; two written vowels with no mark between them are a diphthong."""
    sylls: list[list[str]] = []
    cur: list[str] = []
    k = 0
    while k < len(segs):
        s = segs[k]
        if s == "'":
            if cur:
                sylls.append(cur)
            cur = []
        elif s in VOWELS:
            if any(x in VOWELS for x in cur):
                if cur[-1] in VOWELS and s in "iu" and cur[-1] != s:
                    cur.append(s + "̯")        # diphthong glide, marked below
                else:
                    sylls.append(cur)
                    cur = [s]
            else:
                cur.append(s)
        else:
            nxt = segs[k + 1] if k + 1 < len(segs) else None
            if any(x[0] in VOWELS for x in cur) and nxt is not None and nxt in VOWELS:
                sylls.append(cur)
                cur = [s]
            else:
                cur.append(s)
        k += 1
    if cur:
        if sylls and not any(x[0] in VOWELS for x in cur):
            sylls[-1].extend(cur)
        else:
            sylls.append(cur)
    return sylls


def _word(word: str) -> tuple[str, str, int]:
    sylls = _syllables(_segments(word))
    ipa, rsp = [], []
    for k, sy in enumerate(sylls):
        i, r = "", ""
        for s in sy:
            if s.endswith("̯"):              # glide: spacing j / w, not the combining mark
                i += "j" if s[0] == "i" else "w"
                r += "y" if s[0] == "i" else "w"
            elif s in VOWELS:
                i += IPA_V[s]
                r += s
            else:
                i += IPA_C[s]
                r += RSP_C.get(s, s)
        if k == 0 and len(sylls) > 1:
            i, r = "ˈ" + i, r.upper()
        ipa.append(i)
        rsp.append(r)
    return ".".join(ipa), "-".join(rsp), len(sylls)


def phonemize(word: str, scheme: str = "mm-1250", quantities=None, **_) -> dict:
    parts = [_word(w) for w in word.split() if _segments(w)]
    if not parts:
        return {"ipa": "?", "respell": "?", "syllables": 0}
    return {"ipa": " ".join(p[0] for p in parts), "respell": " ".join(p[1] for p in parts),
            "syllables": sum(p[2] for p in parts)}


KEY = {
    "mm-1250": [
        ("", "Middle Mongolian as it may have sounded in the mid-13th century, when the Secret History was composed. This is a reconstruction and approximate throughout. It rests on the Ming transcription itself (which Chinese characters were chosen for which sounds), on the Uyghur-script spelling of later Mongolian, and on comparison with modern Mongolian. The pronunciation is derived from the romanization row, not from the Chinese characters read aloud."),
        ("CAPS", "the first syllable, taken as stressed, as in the usual account of Mongolian. Stress is not attested for this period"),
        ("a, e, i, o, u", "a as in father, e as in bet, i as in machine but short, o as in law but short, u as in put"),
        ("ö, ü", "front rounded vowels, as in German schön and für"),
        ("ay, ey, oy, uy, üy", "diphthongs, one syllable: written ai, ei, oi, ui, üi"),
        ("hyphen between two vowels", "a hiatus (written ' in the romanization) where an older consonant had been lost: ja-a-tu. Many such pairs had probably become one long vowel by the 14th century"),
        ("t, ch, k, q", "with a puff of breath, as English t, ch, k at the start of a word"),
        ("d, j, g, b", "without the puff of breath, closer to the d, j, g, b of English than to t, ch, k, p"),
        ("q", "a k made further back, at the soft palate's end (the uvula), with breath"),
        ("gh", "the letter γ: a voiced sound made at the uvula, like a soft French r"),
        ("h", "a plain h, at the start of words such as huja'ur; modern Mongolian has lost it"),
        ("ng", "as in sing, also before g: teng-ge-ri"),
        ("r", "a tapped or trilled r"),
    ],
}
SCHEME_LABELS = {"mm-1250": "Middle Mongolian, mid-13th century (approximate)"}
