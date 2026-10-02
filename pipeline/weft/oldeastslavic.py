"""Old East Slavic (the language of Rus', 11th-12th centuries): reading form -> sound.

Built for the entries for 6367-6370 (859-862) of the Tale of Bygone Years (Повѣсть временьныхъ
лѣтъ) in the Laurentian copy of 1377, as printed in Полное собрание русских летописей, vol. 1
(Leningrad, 1926). The chronicle was compiled in Kiev in the early 12th century; the Laurentian
manuscript was copied in Suzdalian Rus' about 260 years later and keeps much of the older spelling.

Edition token fields (texts/<work>/edition.yaml)
-----------------------------------------------
t      the word as printed: ѣ ъ ь ѧ ꙗ ѡ ѿ і оу kept. A letter written above the line is lowered
       into it in parentheses (пр(а)вды); an abbreviation mark (pokrytie) is replaced by the letter
       it stands for, also in parentheses (ни(х) for нихъ). Combining Cyrillic letters and the
       combining titlo and pokrytie are not used, because the page's web font is split into subsets
       and a base letter and its mark then come from different files, which shows as an empty box.
       For the same reason the titlo over letter numerals is not shown (҂ѕ·т·ѯ·з). Square brackets
       mark words the 1926 editor supplied from the other copies
num    true for a letter numeral: its reading is a number, so the spelling sensor skips it
n      the reading form, typed by hand: abbreviations and superscripts written out (ни҇ -> нихъ,
       лѣⷮ -> лѣто), ѡ as о, ѿ as отъ, оу as у, ѧ and ꙗ as я, і as и, and an acute accent on the
       stressed vowel. A letter numeral is given as its value in digits. Both schemes read n.
p      the punctuation that follows (the middle dot of the manuscript, :· at the end of an entry)

Schemes
-------
orv1100  Old East Slavic of about 1100, when the chronicle was first compiled; approximate.
         Evidence: the handbooks of Russian historical phonology (A. A. Shakhmatov; P. S. Kuznetsov;
         G. Y. Shevelov, A Prehistory of Slavic, 1964; A. M. Schenker, The Dawn of Slavic, 1995),
         which rest on the spelling of dated manuscripts and birchbark letters. Positions taken:
         - the jers ъ and ь are still pronounced, as very short vowels [ŭ] and [ĭ]. Their loss in
           weak position (word-final, and before a syllable with a full vowel) is dated to the
           12th century in East Slavic; at 1100 the weak ones were fading. This is the scheme's
           weakest point, and it treats every written jer alike.
         - ѣ is a close e [e], distinct from е, an open [ɛ]. Its value varied by region (in the
           Novgorod area it was close to i).
         - ѧ and ꙗ are the same sound as я: [a] after a soft consonant, [ja] at the start of a
           word or after a vowel. The nasal vowels had been lost before the earliest East Slavic
           manuscripts; ѧ is a spelling taken over from Church Slavonic.
         - ы is [ɨ]; оу and у are [u]; ѡ is [o]; г is a stop [ɡ] (a fricative [ɣ] is likely in the
           south, including Kiev, and is not shown); в is [v] (a [w] is also possible).
         - consonants before ь, я and ю are soft (palatalized, ʲ). Softening before е, ѣ and и is
           also assumed by the handbooks and is not marked.
         - syllables are open: every consonant goes with the vowel after it (the law of open
           syllables still held while the jers were sounded).
         - stress: the place of stress is not written in the manuscript. It is hand-entered in n
           from the stress of the same words in Russian and Ukrainian and from the accent
           paradigms of the handbooks; approximate.
ru       The text read aloud by a reader of Russian today, as it is read in a university class on
         the history of the language: ъ silent, ь marks a soft consonant, ѣ as е, the same stress
         as the first scheme, and modern Russian vowel reduction (unstressed о and а as [ɐ] or
         [ə], unstressed е and я as [ɪ] after a soft consonant), final devoicing and voicing
         assimilation. A convention of reading, not a reconstruction.
"""
from __future__ import annotations

import re
import unicodedata as ud

VERSION = "0.1"
SHOW_TRANSLIT = True
TRANSLIT_LABEL = "Reading form (abbreviations written out, stress marked)"

ACUTE = "́"
VOWELS = "аеиоуыъьѣяю"
FRONT = "еиьѣяю"
CONS = {"б": "b", "в": "v", "г": "ɡ", "д": "d", "ж": "ʒ", "з": "z", "й": "j", "к": "k", "л": "l", "м": "m",
        "н": "n", "п": "p", "р": "r", "с": "s", "т": "t", "ф": "f", "х": "x", "ц": "ts", "ч": "tʃ",
        "ш": "ʃ", "щ": "ʃtʃ"}
V1100 = {"а": "a", "е": "ɛ", "и": "i", "о": "o", "у": "u", "ы": "ɨ", "ъ": "ŭ", "ь": "ĭ", "ѣ": "e",
         "я": "a", "ю": "u"}
# respelling for English readers: IPA segment -> letters
R1100 = {"a": "ah", "ɛ": "eh", "i": "ee", "o": "oh", "u": "oo", "ɨ": "ih", "ŭ": "ŭ", "ĭ": "ĭ", "e": "ay",
         "b": "b", "v": "v", "ɡ": "g", "d": "d", "ʒ": "zh", "z": "z", "j": "y", "k": "k", "l": "l",
         "m": "m", "n": "n", "p": "p", "r": "r", "s": "s", "t": "t", "f": "f", "x": "kh", "ts": "ts",
         "tʃ": "ch", "ʃ": "sh", "ʃtʃ": "shch", "ʲ": "y"}
RRU = {"a": "ah", "e": "eh", "ɛ": "eh", "i": "ee", "o": "oh", "u": "oo", "ɨ": "ih", "ɐ": "uh", "ə": "uh",
       "ɪ": "i", "b": "b", "v": "v", "ɡ": "g", "d": "d", "ʐ": "zh", "z": "z", "j": "y", "k": "k",
       "l": "l", "m": "m", "n": "n", "p": "p", "r": "r", "s": "s", "t": "t", "f": "f", "x": "kh",
       "ts": "ts", "tɕ": "ch", "ʂ": "sh", "ɕː": "shsh", "ʲ": "y"}
VOICED = {"b": "p", "v": "f", "ɡ": "k", "d": "t", "z": "s", "ʐ": "ʂ"}
UNVOICED = {v: k for k, v in VOICED.items()}


def reading_letters(n: str) -> list[tuple[str, bool]]:
    """The reading form as (letter, stressed) pairs, lower case."""
    s = ud.normalize("NFD", n.lower())
    out: list[tuple[str, bool]] = []
    for ch in s:
        if ch == ACUTE and out:
            out[-1] = (out[-1][0], True)
        elif ch == "̆" and out and out[-1][0] == "и":      # й decomposes to и + breve
            out[-1] = ("й", False)
        elif ch == "̈" and out and out[-1][0] == "е":      # ё (not expected) read as е
            continue
        elif ud.category(ch).startswith("L"):
            out.append((ud.normalize("NFC", ch), False))
    return out


def _segments_1100(letters):
    """Old East Slavic c. 1100: list of syllables, each a list of IPA segments, and the stressed index."""
    sylls, cur, stress = [], [], None
    prev_vowel = True
    for k, (ch, st) in enumerate(letters):
        if ch in "яю":
            cur.append("j" if prev_vowel else "ʲ")
            cur.append(V1100[ch])
        elif ch == "е" and prev_vowel:          # initial and post-vocalic е had a glide, as in Russian
            cur += ["j", V1100[ch]]
        elif ch in V1100:
            if ch == "ь" and cur and cur[-1] not in ("ʲ",) and cur[-1] not in V1100.values():
                cur.append("ʲ")
            cur.append(V1100[ch])
        elif ch in CONS:
            cur.append(CONS[ch])
            prev_vowel = False
            continue
        else:
            continue
        prev_vowel = True
        if st:
            stress = len(sylls)
        sylls.append(cur)
        cur = []
    if cur:                       # consonants after the last vowel (rare: a word written without a final jer)
        if sylls:
            sylls[-1].extend(cur)
        else:
            sylls.append(cur)
    return sylls, stress


def _ipa(sylls, stress) -> str:
    parts = []
    for i, s in enumerate(sylls):
        parts.append(("ˈ" if i == stress and len(sylls) > 1 else "") + "".join(s))
    return ".".join(parts)


def _respell(sylls, stress, table) -> str:
    out = []
    for i, s in enumerate(sylls):
        r = ""
        for k, seg in enumerate(s):
            r += table.get(seg, seg)
        r = r.replace("yy", "y")
        out.append(r.upper() if i == stress and len(sylls) > 1 else r)
    return "-".join(out)


def _segments_ru(letters):
    """Modern Russian reading: segments with vowel reduction, devoicing and assimilation."""
    segs: list[list] = []        # [ipa, kind, stressed]  kind: V or C
    prev_vowel = True
    nvow = sum(1 for ch, _ in letters if ch in "аеиоуыѣяю")
    stressed_idx = next((i for i, (ch, st) in enumerate([l for l in letters if l[0] in "аеиоуыѣяю"]) if st), None)
    vi = -1
    for k, (ch, st) in enumerate(letters):
        if ch in "ъ":
            prev_vowel = False if segs and segs[-1][1] == "C" else prev_vowel
            continue
        if ch == "ь":
            if segs and segs[-1][1] == "C" and segs[-1][0] not in ("ʐ", "ʂ", "ts", "tɕ", "ɕː"):
                segs[-1][0] += "ʲ"
            if k + 1 < len(letters) and letters[k + 1][0] in "еиѣяю":
                segs.append(["j", "C", False])      # the separating soft sign: братья, людье
            prev_vowel = False
            continue
        if ch in "аеиоуыѣяю":
            vi += 1
            soft_v = ch in "еиѣяю"
            if soft_v and segs and segs[-1][1] == "C" and not segs[-1][0].endswith("ʲ") \
                    and segs[-1][0] not in ("ʐ", "ʂ", "ts", "tɕ", "ɕː", "j"):
                segs[-1][0] += "ʲ"
            if ch in "еѣяю" and (prev_vowel or not segs):
                segs.append(["j", "C", False])
            base = {"а": "a", "е": "e", "ѣ": "e", "и": "i", "о": "o", "у": "u", "ы": "ɨ", "я": "a", "ю": "u"}[ch]
            after_soft = len(segs) > 0 and (segs[-1][0].endswith("ʲ") or segs[-1][0] in ("j", "tɕ", "ɕː"))
            after_hard_sib = len(segs) > 0 and segs[-1][0] in ("ʐ", "ʂ", "ts")
            if base == "i" and after_hard_sib:
                base = "ɨ"
            if base == "e" and not after_soft:
                base = "ɛ"
            stressed = vi == stressed_idx
            if not stressed and nvow > 1:
                last = not any(c in "аеиоуыѣяю" for c, _ in letters[k + 1:])
                if base in ("a", "o"):
                    if after_soft and not (last and ch in "ая"):
                        base = "ɪ"
                    else:
                        pretonic = stressed_idx is not None and vi == stressed_idx - 1
                        base = "ɐ" if ((pretonic or vi == 0) and not (after_soft and last)) else "ə"
                elif base in ("e", "ɛ"):
                    base = "ɪ" if after_soft else "ɨ" if after_hard_sib else "ɪ"
            segs.append([base, "V", stressed])
            prev_vowel = True
            continue
        if ch in CONS:
            ipa = {"ж": "ʐ", "ш": "ʂ", "ч": "tɕ", "щ": "ɕː"}.get(ch, CONS[ch])
            if ch == "с" and segs and segs[-1][0].rstrip("ʲ") == "t" and k + 1 < len(letters) and letters[k + 1][0] == "я":
                segs[-1][0] = "ts"                  # -тся, -ться of the reflexive verb: one ts
                continue
            segs.append([ipa, "C", False])
            prev_vowel = False
    # final devoicing, then regressive voicing assimilation among obstruents (в does not trigger it)
    for i in range(len(segs) - 1, -1, -1):
        if segs[i][1] != "C":
            continue
        base = segs[i][0].rstrip("ʲ")
        soft = segs[i][0].endswith("ʲ")
        nxt = next((s for s in segs[i + 1:]), None)
        if nxt is None:
            if base in VOICED:
                segs[i][0] = VOICED[base] + ("ʲ" if soft else "")
        elif nxt[1] == "C":
            nb = nxt[0].rstrip("ʲ")
            if nb in UNVOICED and base in VOICED:
                segs[i][0] = VOICED[base] + ("ʲ" if soft else "")
            elif nb in VOICED and nb != "v" and base in UNVOICED:
                segs[i][0] = UNVOICED[base] + ("ʲ" if soft else "")
    # syllables: split a cluster before its last consonant, except stop + liquid
    vidx = [i for i, s in enumerate(segs) if s[1] == "V"]
    if not vidx:
        return [[s[0] for s in segs]], None
    bounds = [0]
    for a, b in zip(vidx, vidx[1:]):
        cl = list(range(a + 1, b))
        if len(cl) <= 1:
            bounds.append(a + 1)
        else:
            last2 = [segs[j][0].rstrip("ʲ") for j in cl[-2:]]
            if last2[0] in ("p", "b", "t", "d", "k", "ɡ", "f", "v") and last2[1] in ("r", "l"):
                bounds.append(cl[-2])
            else:
                bounds.append(cl[-1])
    bounds.append(len(segs))
    sylls, stress = [], None
    for k in range(len(bounds) - 1):
        chunk = segs[bounds[k]:bounds[k + 1]]
        if any(s[2] for s in chunk):
            stress = k
        sylls.append([s[0] for s in chunk])
    return sylls, stress


def _split_soft(sylls):
    """Break 'tʲ' style segments into base + ʲ for the respelling table."""
    out = []
    for s in sylls:
        t = []
        for seg in s:
            if seg.endswith("ʲ") and len(seg) > 1:
                t += [seg[:-1], "ʲ"]
            else:
                t.append(seg)
        out.append(t)
    return out


def phonemize(word: str, scheme: str = "orv1100", quantities=None, **_) -> dict:
    w = word.strip("[]·:")
    if re.fullmatch(r"\d+", w):              # a letter numeral, given in n as its value
        return {"ipa": "—", "respell": f"({w})", "syllables": 0}
    letters = reading_letters(w)
    if not letters:
        return {"ipa": "—", "respell": "—", "syllables": 0}
    if scheme == "ru":
        if w.lower().replace(ACUTE, "") == "его":    # read with v, as in Russian
            return {"ipa": "jɪ.ˈvo", "respell": "yi-VOH", "syllables": 2}
        sylls, stress = _segments_ru(letters)
        return {"ipa": _ipa(sylls, stress), "respell": _respell(_split_soft(sylls), stress, RRU),
                "syllables": len(sylls)}
    sylls, stress = _segments_1100(letters)
    return {"ipa": _ipa(sylls, stress), "respell": _respell(sylls, stress, R1100), "syllables": len(sylls)}


# ---------------------------------------------------------------- sensors
# letter forms folded together (the OCR reads ѧ, ꙗ and я as а or д, ѡ as ш or о) before comparing an edition word with its reading form, or an
# edition line with the OCR of its printed source
FOLD = str.maketrans({"ѧ": "а", "ꙗ": "а", "я": "а", "ѡ": "о", "і": "и", "ї": "и", "ѳ": "ф", "ѕ": "з", "ѵ": "и", "ꙋ": "у"})


def letters_of(s: str, inline_superscripts: bool = True) -> str:
    """Lower-case Cyrillic letters only: letters in parentheses (raised in the print) and combining
    superscript letters kept in the line, or dropped; titla, accents, brackets, punctuation and
    digits removed; ѿ read as от,
    оу as у; then the letter-form fold."""
    # a letter in parentheses is written above the line in the print (or stands for an abbreviation mark)
    s = re.sub(r"\(([^)]*)\)", (lambda m: m.group(1)) if inline_superscripts else "", s)
    out = []
    for ch in ud.normalize("NFD", s.lower()):
        name = ud.name(ch, "")
        if name.startswith("COMBINING CYRILLIC LETTER"):
            if inline_superscripts:
                base = name.replace("COMBINING CYRILLIC LETTER ", "CYRILLIC SMALL LETTER ")
                try:
                    out.append(ud.lookup(base).lower())
                except KeyError:
                    pass
            continue
        if ch == "̆" and out and out[-1] == "и":
            continue                                   # й -> и
        if ud.category(ch).startswith("L") and ("CYRILLIC" in name):
            out.append(ch)
    s2 = ud.normalize("NFC", "".join(out)).replace("ѿ", "от").replace("оу", "у")
    return s2.translate(FOLD)


def _subseq(a: str, b: str) -> bool:
    it = iter(b)
    return all(c in it for c in a)


_OCR: dict = {}
_REPORTED: set = set()


def _ocr_region(spec: dict) -> tuple[str | None, list[str]]:
    """The OCR text between the start and end markers, corrected by the declared list (whole
    words, applied to the raw OCR), then reduced to letters with the fold above. Returns the
    letters and any correction that matched nothing (the OCR changed, or the correction is wrong)."""
    from pathlib import Path
    path = Path(__file__).resolve().parents[2] / spec["file"]
    key = str(path)
    if key in _OCR:
        return _OCR[key]
    if not path.exists():
        _OCR[key] = (None, [])
        return _OCR[key]
    raw = ud.normalize("NFC", path.read_text(encoding="utf-8"))
    a = raw.find(spec["start"])
    b = raw.find(spec["end"], a + 1) if a >= 0 else -1
    reg = raw[a:b] if a >= 0 and b > a else ""
    for pat in spec.get("strip") or []:
        reg = re.sub(pat, " ", reg)
    unused = []
    for c in spec.get("corrections") or []:
        pat = r"(?<!\w)" + re.escape(ud.normalize("NFC", c["ocr"])) + r"(?!\w)"
        reg, k = re.subn(pat, lambda _m: c["print"], reg)
        if k == 0:
            unused.append(c["ocr"])
    _OCR[key] = (letters_of(reg, inline_superscripts=False), unused)
    return _OCR[key]


def line_checks(text: str, etoks: list[dict], edition: dict) -> list[tuple[str, str]]:
    """Sensors. (1) every reading form n spells its printed word: the printed letters, with
    superscripts brought into the line, appear in order in n; (2) where the edition declares
    ocr_verify, the line's letters (superscript letters, which the OCR drops or garbles, left out)
    appear verbatim in the corrected OCR of the printed source."""
    out = []
    for t in etoks:
        if not t.get("n"):
            out.append(("reading-missing", t["t"]))
            continue
        if t.get("num") or re.fullmatch(r"\d+", t["n"]):
            continue                      # a letter numeral: its reading is a number word, not its letters
        if not _subseq(letters_of(t["t"]), letters_of(t["n"])):
            out.append(("reading-not-spelling", f"{t['t']} / {t['n']}"))
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
            mine = letters_of(" ".join(t["t"] for t in etoks), inline_superscripts=False)
            if mine not in reg:
                out.append(("edition-not-in-source", mine[:40]))
    return out


KEY = {
    "orv1100": [
        ("", "Old East Slavic of about 1100, when the chronicle was compiled in Kiev; approximate. Read from the reading form (abbreviations written out). The manuscript does not mark stress; the stress shown is hand-entered from Russian and Ukrainian and the handbooks."),
        ("", "Hyphens divide syllables; CAPS mark the stressed syllable. Syllables are open: every consonant goes with the vowel after it."),
        ("ŭ ĭ", "the jers ъ and ь: very short vowels, a quick uh and a quick ih. The weak ones, at the end of a word and before a syllable with a full vowel, were fading at this date and were lost during the 12th century"),
        ("ay", "ѣ (yat): a close e, as in say without the glide; distinct from е"),
        ("eh", "е: an open e, as in bed"),
        ("ih", "ы: an i said with the tongue drawn back, as in Russian ты"),
        ("y", "after a consonant: the consonant is soft (palatalized) before я, ю and ь: Варязи, vah-RYAH-zee. ѧ and ꙗ are written for the same sound as я; the nasal vowels were long gone"),
        ("kh", "х, as in Scottish loch"),
        ("zh sh ch ts", "ж, ш, ч, ц"),
        ("g", "г as a stop; in the south, Kiev included, a fricative (as in Ukrainian) is likely"),
        ("(6367)", "a date written in letter numerals (҂ѕ҃ = 6000, т = 300, ѯ = 60, з = 7); the number word read aloud is not reconstructed"),
    ],
    "ru": [
        ("", "The text as a reader of Russian reads it aloud today, in a class on the history of the language: a convention, not a reconstruction. Same stress as the first scheme."),
        ("", "Hyphens divide syllables; CAPS mark the stressed syllable."),
        ("", "ъ is silent; ь softens the consonant before it; ѣ is read as е"),
        ("uh", "unstressed о and а, reduced (as in Russian вода, vuh-DAH)"),
        ("i", "unstressed е and я after a soft consonant, reduced to a short i"),
        ("y", "after a consonant: the consonant is soft (palatalized)"),
        ("ih", "ы, an i with the tongue drawn back"),
        ("kh zh sh ch ts shsh", "х, ж, ш, ч, ц, щ"),
    ],
}
SCHEME_LABELS = {"orv1100": "Old East Slavic about 1100 (approximate)",
                 "ru": "Read as Russian today (a convention)"}
