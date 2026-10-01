"""Japanese: historical kana reading -> morae -> romanized sound.

Each token carries its reading in historical kana (the spelling of Bashō's day): 蛙 is かはづ,
水 is みづ. Rules turn that spelling into sound for each scheme. Japanese verse counts morae
(on), not syllables, so the mora count is returned for the metre row.

Schemes
-------
edo-1686   Japanese as spoken in Edo in the 1680s, approximate. Word-medial は ひ ふ へ ほ are
           read wa i u e o (a change completed centuries earlier); づ and ぢ are read dzu and dji,
           following reconstructions that keep them distinct from ず and じ into the 1600s,
           though they were merging in Edo by Bashō's time. The vowel-only mora e (え, ゑ, and
           word-medial へ) is read ye, as Portuguese missionaries wrote it around 1600 (Rodrigues)
           and as Europeans still spelled the city itself, Yedo; when ye became plain e is not
           settled, so this is approximate. Medial -afu (よこたふ) is read ō, a long o counted as
           two morae: afu had become au, then an open long o, which had probably merged with ō
           in Edo by the 1680s.
modern     Modern Tokyo Japanese, standard Hepburn romanization.

Both schemes read a token written only は as the topic particle wa. A noun spelled は alone
(葉, leaf) would be misread; none occurs yet. Pitch accent is not marked in either scheme.

Schemes added in 0.2 for prose and for kanbun (Chinese-character text read in Japanese)
----------------------------------------------------------------------------------------
These four read a fuller historical spelling: small ゃ ゅ ょ for palatal syllables (きゃう), small
っ for a doubled consonant (もっぱら), small ゎ for kwa and gwa (くゎ), and ・ where two words or
characters meet, which stops the medial-h and long-vowel rules from reaching across the join
(こく・はふ). Long vowels are formed within a word: au and afu become an open long o, ou a closed
long o, eu a palatal yō, iu yū, uu ū. Hyphens divide syllables; a long vowel, a final n and the
first half of a doubled consonant each count as a further mora. All four are approximate, and
none marks pitch accent.

kakuichi-1371  Japanese as a biwa hōshi recited it in Kyoto in the later 14th century (Kakuichi
           fixed his text in 1371). h is a lip sound, fa fi fu fe fo; t and d keep their stop
           before i and u (ti, tu, di, du: the change to chi and tsu is usually dated to the 15th
           and 16th centuries); じ and ず stay apart from ぢ and づ; s and z before e are she and
           zhe; vowel-only e is ye and o (お, を) is wo; kwa and gwa are kept; an open long o (from
           au) stays apart from a closed one (from ou). The evidence is indirect (later Jesuit
           spellings projected back, kana usage, Chinese and Korean transcriptions).
keicho-1615  Japanese of Kyoto and the Tokugawa court around 1600 to 1620, as the Jesuit
           dictionary (Nippo jisho, 1603) and grammar (Rodrigues, 1604 to 1608) spell it: fa fi
           fu fe fo; chi and tsu; ぢ dji and づ dzu apart from じ zhi and ず zu; she and zhe; ye and
           wo; kwa and gwa; open aw (from au) apart from closed ō (from ou). Better attested than
           1371, still approximate, and the Jesuits recorded speech, not the reading of kanbun.
genroku-1703  Edo around 1700, on the edo-1686 conventions (ye, dji, dzu, h), with the long
           vowels of the fuller spelling: the open and closed long o had merged into ō; kwa had
           become ka in Edo speech (approximate).
hepburn    Modern Japanese, Hepburn romanization, reading the historical spelling the way it is
           read aloud today. A token may give `mod`, its reading in modern kana, where today's
           reading does not follow from the rules (たまふ is read tamau, not tamō).

Kanbun and kunten
-----------------
A section marked `kunten: true` is Chinese-character text read in Japanese (kundoku). Each token
is one character, or a word of two or more, in the order the text was written. Its `n` is the
reading a Japanese reader gave it, including the inflection and particles that the kunten add
beside it (okurigana); `kaeri` is the return mark (kaeriten) printed beside it: レ, 一 二 三,
上 中 下, 甲 乙. A token the reader passes over in silence (a placeholder character, okiji) has
`oki: true` and no reading. From the marks this module computes the order in which a reader
says the tokens, and gives each token a `script` field: its place in that order and its mark,
shown above the character. A line may carry `yomi`, the whole line written out as the reader
said it (yomikudashi); `line_checks` confirms that it follows the computed order and the
tokens' readings, `weft draft` copies it to the line's `reading` (shown as its own row, "Read
aloud"), and `line_metre` reports no metre for such a prose line. An edition
may name `kunten_in` (source files) and `work`, so that `line_checks` can confirm each mark
against the source as printed.
"""
from __future__ import annotations

import re
from pathlib import Path

VERSION = "0.3"

KANA = {
    "あ": "a", "い": "i", "う": "u", "え": "e", "お": "o",
    "か": "ka", "き": "ki", "く": "ku", "け": "ke", "こ": "ko",
    "が": "ga", "ぎ": "gi", "ぐ": "gu", "げ": "ge", "ご": "go",
    "さ": "sa", "し": "shi", "す": "su", "せ": "se", "そ": "so",
    "ざ": "za", "じ": "ji", "ず": "zu", "ぜ": "ze", "ぞ": "zo",
    "た": "ta", "ち": "chi", "つ": "tsu", "て": "te", "と": "to",
    "だ": "da", "ぢ": "dji", "づ": "dzu", "で": "de", "ど": "do",
    "な": "na", "に": "ni", "ぬ": "nu", "ね": "ne", "の": "no",
    "は": "ha", "ひ": "hi", "ふ": "fu", "へ": "he", "ほ": "ho",
    "ば": "ba", "び": "bi", "ぶ": "bu", "べ": "be", "ぼ": "bo",
    "ぱ": "pa", "ぴ": "pi", "ぷ": "pu", "ぺ": "pe", "ぽ": "po",
    "ま": "ma", "み": "mi", "む": "mu", "め": "me", "も": "mo",
    "や": "ya", "ゆ": "yu", "よ": "yo",
    "ら": "ra", "り": "ri", "る": "ru", "れ": "re", "ろ": "ro",
    "わ": "wa", "ゐ": "i", "ゑ": "e", "を": "o", "ん": "n",
}
MEDIAL_H = {"は": "wa", "ひ": "i", "ふ": "u", "へ": "e", "ほ": "o"}   # ha-gyō tenko
MODERN = {"dzu": "zu", "dji": "ji"}
IPA = {"shi": "ɕi", "chi": "tɕi", "tsu": "tsɯ", "fu": "ɸɯ", "ji": "dʑi", "dji": "dʑi", "dzu": "dzɯ",
       "zu": "zɯ", "su": "sɯ", "ku": "kɯ", "gu": "ɡɯ", "nu": "nɯ", "mu": "mɯ", "ru": "ɾɯ", "yu": "jɯ",
       "bu": "bɯ", "pu": "pɯ", "u": "ɯ"}


EDO_YE = {"え", "ゑ"}                     # vowel-only e, read ye in the Edo scheme


def morae(kana: str, scheme: str) -> list[str]:
    if kana == "は":
        return ["wa"]                            # the topic particle, written は, said wa
    out = []
    for i, ch in enumerate(kana):
        if i > 0 and ch in MEDIAL_H:
            r = MEDIAL_H[ch]                     # かは -> kawa, not kaha
        else:
            r = KANA.get(ch, ch)
        if scheme == "edo-1686" and (ch in EDO_YE or (i > 0 and ch == "へ")):
            r = "ye"                             # こゑ -> koye, as in Yedo
        if scheme == "modern":
            r = MODERN.get(r, r)
        out.append(r)
    return out


def _contract(ms: list[str], kana: str) -> list[str]:
    """Medial -afu -> ō: よこたふ is yo-ko-tō. Display only; the mora count is taken before."""
    out = list(ms)
    for i in range(1, len(kana)):
        if kana[i] == "ふ" and out[i] == "u" and out[i - 1].endswith("a"):
            out[i - 1] = out[i - 1][:-1] + "ō"
            out[i] = ""
    return [m for m in out if m]


def _ipa(m: str) -> str:
    if m in IPA:
        return IPA[m]
    ipa = m.replace("ō", "oː").replace("r", "ɾ").replace("y", "j").replace("g", "ɡ")
    return ipa


# ---------------------------------------------------------------------------------------------
# The fuller reader (schemes kakuichi-1371, keicho-1615, genroku-1703, hepburn)

NEW_SCHEMES = ("kakuichi-1371", "keicho-1615", "genroku-1703", "hepburn")
_OLD = {"kakuichi-1371": 1371, "keicho-1615": 1615, "genroku-1703": 1703, "hepburn": 2000}

# each kana as (onset, vowel); historical kana keep their own onset (ゐ ゑ を are w-)
_UNITS = {}
for _k, _r in KANA.items():
    if _k == "ん":
        continue
    _UNITS[_k] = (_r[:-1], _r[-1])
_UNITS.update({"し": ("s", "i"), "ち": ("t", "i"), "つ": ("t", "u"), "ふ": ("h", "u"), "じ": ("z", "i"),
               "ぢ": ("d", "i"), "づ": ("d", "u"), "ゐ": ("w", "i"), "ゑ": ("w", "e"), "を": ("w", "o")})
_SMALL_Y = {"ゃ": "a", "ゅ": "u", "ょ": "o"}
_SMALL = set(_SMALL_Y) | {"ゎ", "っ"}
_SEP = "・"
_HOLD = "'"                      # no long vowel across this point: もち'ふ is mochiu, not mochū
KANA_OK = set(KANA) | _SMALL | {_SEP, _HOLD, "ー"}


def _parse(kana: str) -> list[dict]:
    """Historical kana -> units {c: onset, v: vowel, start: begins a word} plus Q (っ) and N (ん)."""
    units: list[dict] = []
    start = True
    hold = False
    for ch in kana:
        if ch == _SEP:
            start = True
            continue
        if ch == _HOLD:
            hold = True
            continue
        if ch in _SMALL_Y and units and units[-1].get("v"):
            u = units[-1]
            base = {"s": "s", "z": "z", "t": "t", "d": "d"}.get(u["c"], u["c"])
            u["c"], u["v"] = base + "y", _SMALL_Y[ch]          # き + ゃ -> kya
            continue
        if ch == "ゎ" and units and units[-1].get("v") == "u":
            units[-1]["c"], units[-1]["v"] = units[-1]["c"] + "w", "a"   # く + ゎ -> kwa
            continue
        if ch == "っ":
            units.append({"q": True, "start": start}); start = False
            continue
        if ch == "ん":
            units.append({"n": True, "start": start}); start = False
            continue
        c, v = _UNITS.get(ch, ("?", ""))
        if c == "h" and not start and units and not units[-1].get("q") and not units[-1].get("n"):
            c = "w"                                      # medial h: かは kawa, はふ hau
        units.append({"c": c, "v": v, "start": start, "hold": hold})
        start = hold = False
    return units


def _lengthen(units: list[dict], year: int, modern_kana: bool = False) -> list[dict]:
    """Form long vowels within a word: au/afu open ō, ou closed ō, eu yō, iu yū, uu ū. In modern
    kana (a token's `mod`) only ou and uu are long vowels: au and iu are written as said."""
    out: list[dict] = []
    for u in units:
        prev = out[-1] if out else None
        glide_u = u.get("c") in ("", "w") and u.get("v") == "u" and not u.get("start") and not u.get("hold")
        glide_o = u.get("c") in ("", "w") and u.get("v") == "o" and not u.get("start") and not u.get("hold")
        if modern_kana and prev and prev.get("v") in ("a", "i", "e"):
            glide_u = glide_o = False
        if prev and prev.get("v") and not prev.get("long") and glide_u:
            pv = prev["v"]
            if pv == "a":
                prev["v"], prev["long"] = "o", ("open" if year < 1650 else "close")
            elif pv == "o":
                prev["long"] = "close"
            elif pv == "e":
                prev["c"] = _palatal(prev["c"]); prev["v"], prev["long"] = "o", "close"
            elif pv == "i":
                prev["c"] = _palatal(prev["c"]); prev["v"], prev["long"] = "u", "close"
            elif pv == "u":
                prev["long"] = "close"
            continue
        if prev and prev.get("v") == "o" and not prev.get("long") and glide_o:
            prev["long"] = "close"                       # おほ, とを: oo -> ō
            continue
        out.append(dict(u))
    return out


def _palatal(c: str) -> str:
    if c in ("", "w"):
        return "y"
    return c if c.endswith("y") else c + "y"


# onset spellings and IPA by period: (respelling, IPA)
def _onset(c: str, v: str, year: int, first: bool) -> tuple[str, str]:
    early, mid = year < 1500, year < 1650             # 1371; 1615 and 1371
    if c == "":
        if v == "e" and year < 1900:
            return "y", "j"                              # え: ye
        if v == "o" and mid and first:
            return "w", "w"                              # お: wo (Jesuit vo)
        return "", ""
    if c == "w":
        if v == "a":
            return "w", "w"
        if v == "o":
            return ("w", "w") if mid else ("", "")
        if v == "e":
            return ("y", "j") if year < 1900 else ("", "")
        return "", ""                                    # ゐ and medial ひ, ふ: i, u
    if c in ("s", "sy"):
        if c == "sy" or v == "i" or (v == "e" and mid):
            return "sh", ("ʃ" if mid else "ɕ")
        return "s", "s"
    if c in ("z", "zy"):
        if c == "zy" or v == "i" or (v == "e" and mid):
            return ("zh", "ʒ") if mid else ("j", "dʑ")
        return "z", "z"
    if c in ("t", "ty"):
        if early:
            return ("ty", "tʲ") if c == "ty" else ("t", "t")
        if c == "ty" or v == "i":
            return "ch", ("tʃ" if mid else "tɕ")
        if v == "u":
            return "ts", "ts"
        return "t", "t"
    if c in ("d", "dy"):
        if early:
            return ("dy", "dʲ") if c == "dy" else ("d", "d")
        if c == "dy" or v == "i":
            return ("dj", "dʒ" if mid else "dʑ") if year < 1900 else ("j", "dʑ")
        if v == "u":
            return ("dz", "dz") if year < 1900 else ("z", "z")
        return "d", "d"
    if c in ("h", "hy"):
        if mid:
            return ("fy", "ɸj") if c == "hy" else ("f", "ɸ")
        if c == "hy":
            return "hy", "ç"
        return {"i": ("h", "ç"), "u": ("f", "ɸ")}.get(v, ("h", "h"))
    if c in ("kw", "gw"):
        if mid:
            return c, ("kʷ" if c == "kw" else "ɡʷ")
        return c[0], ("k" if c == "kw" else "ɡ")
    if c.endswith("y"):
        b = c[:-1]
        return c, {"r": "ɾ", "g": "ɡ"}.get(b, b) + "j"
    return c, {"r": "ɾ", "g": "ɡ", "y": "j"}.get(c, c)


def _vowel(u: dict, year: int, after_y: bool) -> tuple[str, str]:
    v, lg = u["v"], u.get("long")
    if not lg:
        if v == "u":
            return "u", ("u" if year < 1650 else "ɯ")
        return v, v
    if v == "o" and lg == "open":
        return "aw", "ɔː"
    if v == "u":
        return "ū", ("uː" if year < 1650 else "ɯː")
    return {"o": "ō", "e": "ē", "a": "ā", "i": "ī"}[v], v + "ː"


def _render(kana: str, scheme: str, modern_kana: bool = False) -> dict:
    year = _OLD[scheme]
    units = _lengthen(_parse(kana), year, modern_kana)
    syl_r: list[str] = []
    syl_i: list[str] = []
    gem = None
    for k, u in enumerate(units):
        if u.get("n"):
            if syl_r:
                syl_r[-1] += "n"; syl_i[-1] += "ɴ"
            else:
                syl_r.append("n"); syl_i.append("ɴ")
            continue
        if u.get("q"):
            gem = True
            continue
        o_r, o_i = _onset(u["c"], u["v"], year, u["start"] or k == 0)
        if u["c"] == "?":
            o_r, o_i = "?", "?"
        if u["c"] == "kw" and u["v"] != "a":
            o_r, o_i = "k", "k"
        v_r, v_i = _vowel(u, year, u["c"].endswith("y"))
        if gem and syl_r and o_r:
            syl_r[-1] += {"ch": "t", "sh": "s", "ts": "t"}.get(o_r, o_r[0])
            syl_i[-1] += o_i[0]
        gem = None
        syl_r.append(o_r + v_r)
        syl_i.append(o_i + v_i)
    return {"ipa": ".".join(syl_i), "respell": "-".join(syl_r)}


def mora_count(kana: str) -> int:
    return sum(1 for ch in kana if ch not in _SMALL_Y and ch not in ("ゎ", _SEP, _HOLD))


_PICK: tuple = (None, {})         # the token being drafted: (reading, its edition fields)


def _new_phonemize(word: str, scheme: str) -> dict:
    pick = _PICK[1] if _PICK[0] == word else {}
    if pick.get("oki") or not word or not any(ch in KANA_OK for ch in word):
        return {"ipa": "", "respell": "(silent)", "syllables": 0}
    if word == "は":
        return {"ipa": "wa", "respell": "wa", "syllables": 1}
    if scheme == "hepburn" and pick.get("mod"):
        r = _render(pick["mod"], scheme, modern_kana=True)   # today's reading, where the rules miss it
    else:
        r = _render(word, scheme)
    return {**r, "syllables": mora_count(word)}


# ---------------------------------------------------------------------------------------------
# Kunten: return marks -> reading order

_FAMILY = [("一", "二", "三", "四"), ("上", "中", "下"), ("甲", "乙", "丙", "丁")]


def _rank(mark: str) -> tuple[int, int] | None:
    for f, fam in enumerate(_FAMILY):
        for r, ch in enumerate(fam):
            if ch in mark:
                return f, r
    return None


def reading_order(marks: list[str | None]) -> tuple[list[int], list[str]]:
    """Indexes in the order a reader says them, from the kaeriten. レ: read this after the next
    character. 二 after 一, 三 after 二; 中 and 下 after 上 (下 after 中 where there is one); 乙 after
    甲. A mark such as 一レ is both: read after the next character, then release 二."""
    return _strip(_order(marks, [False] * len(marks)))


def _strip(r):
    seq, problems = r
    return [i for i, part in seq if part == "main"], problems


def _order(marks: list[str | None], saidoku: list[bool]) -> tuple[list[tuple[int, str]], list[str]]:
    """As reading_order, as (index, part) pairs: a re-read character (saidoku moji, such as 將
    read まさに ... す) is said once where it stands ("first") and again where its mark sends it
    ("main")."""
    out: list[tuple[int, str]] = []
    problems: list[str] = []
    stack: list[int] = []
    fams_present = [{_rank(m)[1] for m in marks if m and _rank(m) and _rank(m)[0] == f} for f in range(len(_FAMILY))]

    def triggered(j: int, i: int) -> bool:
        mj, mi = marks[j] or "", marks[i] or ""
        if "レ" in mj:
            return i == j + 1
        rj, ri = _rank(mj), _rank(mi)
        if not rj or not ri or rj[0] != ri[0]:
            return False
        # the release comes from the next lower rank that this line actually uses
        lower = [r for r in fams_present[rj[0]] if r < rj[1]]
        return bool(lower) and ri[1] == max(lower)

    def read(i: int):
        out.append((i, "main"))
        while stack and triggered(stack[-1], i):
            read(stack.pop())

    for i, m in enumerate(marks):
        m = m or ""
        if saidoku[i]:
            out.append((i, "first"))
        defers = "レ" in m or (_rank(m) is not None and _rank(m)[1] > 0)
        if defers:
            stack.append(i)
        else:
            read(i)
    if stack:
        problems.append("unresolved " + " ".join(str(j + 1) for j in stack))
        out.extend((j, "main") for j in reversed(stack))
    return out, problems


def _line_order(toks: list[dict]) -> tuple[list[tuple[int, str]], list[str]]:
    """The order for a line of edition tokens; a token's `kaeri_read` (the mark a reader needs
    where the print has another) wins over `kaeri` (the mark as printed)."""
    return _order([t.get("kaeri_read") or t.get("kaeri") for t in toks], [bool(t.get("saidoku")) for t in toks])


def _find_line(group: dict, et: dict) -> dict | None:
    for ln in group.get("lines") or []:
        if isinstance(ln, dict) and any(t is et for t in ln.get("tokens", [])):
            return ln
    return None


def _find_line_in_edition(edition: dict, etoks: list[dict]) -> dict | None:
    for g in (edition.get("sections") or edition.get("inscriptions") or []):
        for ln in g.get("lines") or []:
            if isinstance(ln, dict) and ln.get("tokens") is etoks:
                return ln
    return None


def token_fields(surface: str, et: dict, group: dict) -> tuple[dict, list[tuple[str, str]]]:
    """Language hook. Holds the token's reading options for phonemize; in a kunten section, adds
    `script`: the token's place in the reading order and its return mark."""
    global _PICK
    reading = et.get("n") or surface
    _PICK = (reading, {k: et[k] for k in ("oki", "mod") if k in et})
    fields: dict = {}
    fails: list[tuple[str, str]] = []
    if et.get("n"):
        bad = [ch for ch in et["n"] if ch not in KANA_OK]
        if bad:
            fails.append(("reading-not-kana", f"{surface} {et['n']}"))
    if group.get("kunten"):
        if et.get("oki") and et.get("n"):
            fails.append(("okiji-has-reading", surface))
        if not et.get("oki") and not et.get("n"):
            fails.append(("reading-missing", surface))
        if et.get("saidoku") and not (et.get("n") or "").startswith(et["saidoku"] + _SEP):
            fails.append(("saidoku-reading", f"{surface} {et.get('n')}"))
        ln = _find_line(group, et)
        if ln is not None:
            toks = ln["tokens"]
            seq, problems = _line_order(toks)
            idx = next(k for k, t in enumerate(toks) if t is et)
            places = [str(k + 1) for k, (i, _) in enumerate(seq) if i == idx]
            mark = et.get("kaeri_read") or et.get("kaeri") or ""
            fields["script"] = "·".join(places) + mark + ("*" if et.get("kaeri_read") else "")
            if et.get("kaeri_read"):
                fails.append(("kaeriten-emended", f"{surface}: printed {et.get('kaeri') or 'no mark'}, read {et['kaeri_read']}"))
            if problems and idx == 0:
                fails.append(("kaeriten-unresolved", f"{''.join(t['t'] for t in toks)}: {problems[0]}"))
    return fields, fails


def line_metre(etoks: list[dict], edition: dict):
    """Language hook. A kunten line shows its yomikudashi in the line row, in place of a mora
    count (the count of a prose sentence is not a metre). Other lines keep the default."""
    ln = _find_line_in_edition(edition, etoks)
    if ln and ln.get("yomi"):
        return False, []      # a prose kunten line: no metre; its reading is the line's `reading`
    return None, []


_PUNCT = re.compile(r"[\s、。，．・「」『』（）()]")
_SRC_CACHE: dict[str, str] = {}


def _norm_wikitext(raw: str) -> str:
    """Wikisource page text with its markup removed except the kaeriten templates."""
    s = re.sub(r"<!--.*?-->|<[^>]+>", "", raw, flags=re.S)
    s = re.sub(r"\{\{(?:small|resize\|[^|}]*)\|([^{}]*)\}\}", r"\1", s)
    s = re.sub(r"\{\{r\|([^|{}]*)\|[^{}]*\}\}", r"\1", s)
    s = re.sub(r"\{\{(?:left|indent)/[se][^{}]*\}\}", "", s)
    return "".join(s.split())


def _clean(r: str) -> str:
    return r.replace(_SEP, "").replace(_HOLD, "")


def _yomi_fits(parts: list[tuple[str, str]], yomi: str) -> bool:
    """Does the written-out reading follow the tokens in reading order? Each token appears either
    as its characters (kana may stand between them) plus some okurigana (a tail of its reading),
    or as its whole reading in kana. parts: (surface, reading) in reading order."""
    y = _PUNCT.sub("", yomi)
    pats = {s: re.compile("[ぁ-ゖ]*".join(re.escape(c) for c in s)) for s, _ in parts}
    from functools import lru_cache

    @lru_cache(maxsize=None)
    def go(ti: int, yi: int) -> bool:
        if ti == len(parts):
            return yi == len(y)
        s, r = parts[ti]
        if r and y.startswith(r, yi) and go(ti + 1, yi + len(r)):
            return True
        m = pats[s].match(y, yi)
        if m:
            j = m.end()
            for k in range(len(r), -1, -1):
                tail = r[len(r) - k:] if k else ""
                if y.startswith(tail, j) and go(ti + 1, j + len(tail)):
                    return True
        return False

    return go(0, 0)


def _yomi_parts(etoks: list[dict]) -> list[tuple[str, str]]:
    seq, _ = _line_order(etoks)
    parts = []
    for i, part in seq:
        t = etoks[i]
        if t.get("oki"):
            continue
        n = t.get("n") or ""
        if t.get("saidoku"):
            n = t["saidoku"] if part == "first" else n.split(_SEP, 1)[1]
        parts.append((t["t"], _clean(n)))
    return parts


def _marked(etoks: list[dict]) -> str:
    out = ""
    for t in etoks:
        s, k = t["t"], t.get("kaeri")
        if not k:
            out += s
            continue
        at = t.get("kaeri_at", len(s))
        out += s[:at] + "{{" + k + "}}" + s[at:]
    return out


_OCR_KEEP = re.compile(r"[\u3041-\u309f\u3400-\u9fff\uf900-\ufaff々〆]")


def _ocr_text(p: Path) -> str:
    """The text of a page of NDL's OCR (National Diet Library, next digital library JSON): the
    blocks in order, with punctuation and katakana dropped (the OCR reads small return marks as
    katakana ニ and レ)."""
    import json
    d = json.loads(p.read_text(encoding="utf-8"))
    pages = d["list"] if "list" in d else [d]
    out = []
    for pg in pages:
        seen = set()
        for b in json.loads(pg.get("coordjson") or "[]"):
            key = (b.get("contenttext"), b.get("xmin"), b.get("ymin"))
            if key in seen:
                continue
            seen.add(key)
            out.append(b.get("contenttext") or "")
    return "".join(ch for ch in "".join(out) if _OCR_KEEP.match(ch))


def _ocr_disagreements(line: str, ocr: str) -> list[str]:
    """Runs of the line's characters that the OCR text does not have in that order."""
    import difflib
    sm = difflib.SequenceMatcher(None, line, ocr, autojunk=False)
    covered = [False] * len(line)
    for a, b, size in sm.get_matching_blocks():
        if size >= 2 or (size == 1 and len(line) == 1):
            for k in range(a, a + size):
                covered[k] = True
    runs, cur = [], ""
    for ch, ok in zip(line, covered):
        if ok:
            if cur:
                runs.append(cur)
            cur = ""
        else:
            cur += ch
    if cur:
        runs.append(cur)
    return runs


def _resolve(edition: dict, rel: str) -> Path | None:
    repo = Path(__file__).resolve().parents[2]
    for base in (repo / "texts" / edition["work"], repo / "private" / edition["work"]):
        if (base / rel).exists():
            return base / rel
    return None


def line_checks(text: str, etoks: list[dict], edition: dict) -> list[tuple[str, str]]:
    """Language hook, kunten lines only: (1) the yomikudashi follows the reading order and the
    tokens' readings; (2) each return mark stands where the printed source has it. For an edition
    transcribed from a scan (ocr_in: the library's OCR of those pages), (3) every run of the
    line's characters is in the OCR text; where it is not, the scan decides and the run is
    reported (ocr-disagrees) so that each difference is checked by eye."""
    fails: list[tuple[str, str]] = []
    ln = _find_line_in_edition(edition, etoks)
    if ln is None:
        return fails
    if ln.get("yomi") and not _yomi_fits(_yomi_parts(etoks), ln["yomi"]):
        fails.append(("yomi-mismatch", ln["yomi"]))
    if edition.get("kunten_in") and edition.get("work"):
        repo = Path(__file__).resolve().parents[2]
        joined = ""
        for rel in edition["kunten_in"]:
            for base in (repo / "texts" / edition["work"], repo / "private" / edition["work"]):
                p = base / rel
                if p.exists():
                    key = str(p)
                    if key not in _SRC_CACHE:
                        _SRC_CACHE[key] = _norm_wikitext(p.read_text(encoding="utf-8"))
                    joined += _SRC_CACHE[key]
                    break
        marked = _marked(etoks)
        if joined and marked not in joined:
            fails.append(("kaeriten-not-in-source", marked))
    if edition.get("ocr_in") and edition.get("work"):
        key = "ocr:" + "|".join(edition["ocr_in"])
        if key not in _SRC_CACHE:
            _SRC_CACHE[key] = "".join(_ocr_text(p) for p in (_resolve(edition, r) for r in edition["ocr_in"]) if p)
        line = "".join(ch for t in etoks for ch in t["t"] if _OCR_KEEP.match(ch))
        for run in _ocr_disagreements(line, _SRC_CACHE[key]):
            fails.append(("ocr-disagrees", f"{run} ({line})"))
    return fails


KEY = {
    "edo-1686": [
        ("", "Each hyphen divides a mora (on), the unit Japanese verse counts: furu-ike is fu-ru-i-ke, four morae."),
        ("dzu", "づ, as in the old spelling かはづ and みづ; possibly still distinct from zu in the 1680s, approximate"),
        ("wa", "は inside a word: かはづ is kawadzu, not kahadzu; は written alone is the particle wa"),
        ("ye", "え and ゑ, as in こゑ, koye, voice; written ye by Europeans around 1600 (Yedo); when it became plain e is not settled, approximate"),
        ("ō", "long o, two morae: よこたふ, once yokotafu, is yo-ko-tō; approximate"),
        ("h", "probably h by the 1680s; around 1600 は was still written fa, a sound made with the lips (approximate)"),
        ("u", "unrounded, lips spread"),
        ("r", "a light tap, between r and l"),
        ("", "Pitch accent is not marked."),
    ],
    "modern": [
        ("", "Standard Hepburn romanization of modern Tokyo Japanese; hyphens divide morae."),
        ("zu", "づ and ず are now the same sound"),
        ("ō", "long o, two morae: よこたふ is read yo-ko-tō"),
        ("", "Pitch accent is not marked."),
    ],
    "kakuichi-1371": [
        ("", "Hyphens divide syllables. A long vowel, a final n and a doubled consonant each add a mora. Reconstructed from indirect evidence; approximate throughout."),
        ("f", "は ひ ふ へ ほ at the start of a word: a breathy f made with the lips only, not the teeth"),
        ("ti, tu", "ち and つ before the change to chi and tsu (usually dated to the 15th and 16th centuries)"),
        ("di, du", "ぢ and づ, still distinct from じ (zhi) and ず (zu)"),
        ("zh", "as s in measure: じ is zhi, ぜ is zhe"),
        ("she", "せ; the s before e and i was probably sh"),
        ("ye", "え, ゑ and a medial へ"),
        ("wo", "お and を, and a medial ほ"),
        ("kw, gw", "くゎ and ぐゎ in Chinese loanwords, later ka and ga"),
        ("aw", "the open long o, from au or afu, as in law; apart from closed ō, from ou"),
        ("ō, ū", "long vowels, two morae each"),
        ("r", "a light tap, between r and l"),
        ("", "Silent marks a character the reader passes over (okiji). Pitch accent is not marked."),
    ],
    "keicho-1615": [
        ("", "Hyphens divide syllables. A long vowel, a final n and a doubled consonant each add a mora. Spellings follow the Jesuit records of c. 1600 to 1608; approximate."),
        ("f", "は ひ ふ へ ほ at the start of a word: a breathy f made with the lips only (the Jesuits wrote fa, fi, fu, fe, fo)"),
        ("dji, dzu", "ぢ and づ, still distinct from じ (zhi) and ず (zu)"),
        ("zh", "as s in measure: じ is zhi, ぜ is zhe"),
        ("she", "せ (the Jesuits wrote xe)"),
        ("ye", "え, ゑ and a medial へ (Jesuit ye)"),
        ("wo", "お and を at the start of a word, and a medial ほ (Jesuit vo)"),
        ("kw, gw", "くゎ and ぐゎ in Chinese loanwords, later ka and ga"),
        ("aw", "the open long o, from au or afu, as in law (Jesuit ŏ); apart from closed ō, from ou (Jesuit ô)"),
        ("ō, ū", "long vowels, two morae each"),
        ("r", "a light tap, between r and l"),
        ("", "Voiced stops may have had a slight nasal onset (Rodrigues); not marked. Silent marks a character the reader passes over (okiji). Pitch accent is not marked."),
    ],
    "genroku-1703": [
        ("", "Hyphens divide syllables. A long vowel, a final n and a doubled consonant each add a mora. Edo around 1700, approximate."),
        ("dji, dzu", "ぢ and づ, possibly still distinct from ji and zu; they were merging in Edo by 1700"),
        ("ye", "え, ゑ and a medial へ; when it became plain e is not settled"),
        ("ō", "long o, two morae: the open and closed long o had merged"),
        ("f", "ふ: made with the lips only, as today"),
        ("u", "unrounded, lips spread"),
        ("r", "a light tap, between r and l"),
        ("", "Silent marks a character the reader passes over (okiji). Pitch accent is not marked."),
    ],
    "hepburn": [
        ("", "Hepburn romanization of the reading as it is said aloud today; hyphens divide syllables."),
        ("ō, ū", "long vowels, two morae each: はふ is read hō, いふ yū"),
        ("zu, ji", "づ and ず, ぢ and じ are now the same sounds"),
        ("", "Silent marks a character the reader passes over (okiji). Pitch accent is not marked."),
    ],
}
SCHEME_LABELS = {"edo-1686": "Edo, 1686: as Bashō's contemporaries spoke (approximate)",
                 "modern": "Modern Japanese (Hepburn)",
                 "kakuichi-1371": "Kyoto, late 14th century: as the biwa reciters spoke (approximate)",
                 "keicho-1615": "Kyoto and Fushimi, c. 1615: as the Jesuits recorded it (approximate)",
                 "genroku-1703": "Edo, c. 1700 (approximate)",
                 "hepburn": "Modern Japanese reading (Hepburn)"}
SCRIPT_LABEL = "Reading order (kunten)"
SCRIPT_WORD = "reading order"


def phonemize(word: str, scheme: str = "edo-1686", quantities=None, **_) -> dict:
    """`word` is the token's historical kana reading."""
    if scheme in NEW_SCHEMES:
        return _new_phonemize(word, scheme)
    ms = morae(word, scheme)
    shown = _contract(ms, word) if word != "は" else ms
    return {"ipa": ".".join(_ipa(m) for m in shown), "respell": "-".join(shown), "syllables": len(ms)}
