"""Akkadian: sign readings -> cuneiform, and a hand normalization -> sound.

An Akkadian text reaches us as cuneiform signs. Scholars publish it in two further forms:
a transliteration, which names each sign by one of its readings (ša-me-e), and a normalization,
which writes the word as it is thought to have been said (šamê). Weft keeps all three:

  t    the edition's transliteration, verbatim (here R. F. Harper, 1904, with his conventions:
       superscript ilu for the divine determinative, no homophone indices, capitals for signs
       read as Sumerian words)
  sg   the signs as read today, in Oracc conventions (indices, {d} and {ki} for determinatives,
       capitals for logograms). Hand-entered, because Harper's readings do not always identify
       the sign: his u may be the sign U, Ú or Ù. The cuneiform row is generated from sg.
  n    the normalized Old Babylonian form, hand-entered. It drives the sound.

The cuneiform comes from a value table built from the Oracc Sign List (CC0), `build_sign_table`.
A reading the table does not know is reported as `sign-unmapped`, never guessed. A sensor counts
Harper's signs against the modern reading and reports `sign-count-differs-from-harper` where the
two analyses of the same line disagree (a personal-name wedge Harper leaves out, a sign he reads
as two). Where Harper writes a whole word for a logogram (mâtim, dârî) the count is not compared.

Schemes
-------
ob-1750    Old Babylonian as it may have been spoken in Babylon around 1750 BC. Approximate
           throughout. Follows the view, argued by Streck and Kogan among others, that š was a
           plain s and the letters s, z, ṣ were affricates (ts, dz, ts'), and treats the
           "emphatic" ṭ, q, ṣ as ejectives. Both points are debated.
classroom  The conventional reading of Assyriology classes: š as sh, emphatics as plain t, s,
           and a back q. A reading convention, not a claim about ancient speech.

Vowel length is written in the normalization (ā, and â for a vowel from contraction). Stress is
not written in cuneiform; both schemes place it by the rule of the modern grammars (Huehnergard,
A Grammar of Akkadian, stress section): a final syllable with a contracted vowel or with a long
vowel before a consonant takes the stress; otherwise the last heavy syllable before the final
one; otherwise the first. The rule is a scholarly inference.
"""
from __future__ import annotations

import re
import unicodedata as ud
from pathlib import Path

VERSION = "0.1"
SCRIPT_LABEL = "Script (cuneiform)"
SCRIPT_WORD = "cuneiform"
SHOW_TRANSLIT = True
TRANSLIT_LABEL = "Normalization"          # the normalization (n) is shown under the transliteration

DATA = Path(__file__).parent / "data" / "akk_osl_values.tsv"
OSL_COMMIT = "193cadfb13bccae6f1f36a8e100ce5660b9e1605"

LAYERS = {
    "script": {"src": f"weft.akkadian {VERSION}: cuneiform generated from the hand sign reading "
                      f"via the Oracc Sign List (CC0), commit {OSL_COMMIT[:7]}"},
    "translit": {"src": "Weft edition: hand-entered Old Babylonian normalization"},
    "signs": {"src": "Weft edition: hand sign reading in Oracc conventions, checked against the stele"},
}

# ---------------------------------------------------------------- sign table
SUB = str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉")


def _key(value: str) -> str:
    """Lookup form of a sign reading: lower case, index digits as subscripts, h for ḫ, ʾ for aleph."""
    v = ud.normalize("NFC", value.strip()).lower().translate(SUB)
    return v.replace("ḫ", "h").replace("’", "ʾ").replace("'", "ʾ").rstrip("?")


def build_sign_table(osl: Path, out: Path, commit: str = OSL_COMMIT) -> int:
    """Oracc Sign List (osl.asl) -> value<TAB>sign name<TAB>cuneiform. Values listed under a
    sign's variant forms are skipped; a value claimed by two signs keeps the first."""
    import hashlib
    rows: dict[str, tuple[str, str]] = {}
    cun: dict[str, str] = {}
    vals: list[tuple[str, str]] = []
    name, inform = None, False
    for line in osl.read_text(encoding="utf-8").splitlines():
        parts = line.split(None, 1)
        tag = parts[0] if parts else ""
        arg = parts[1].strip() if len(parts) > 1 else ""
        if tag == "@sign":
            name, inform = arg, False
        elif tag.startswith("@form"):
            inform = True
        elif tag == "@end" and arg.startswith("form"):
            inform = False
        elif tag == "@end" and arg.startswith("sign"):
            name, inform = None, False
        elif tag == "@ucun" and name and not inform:
            cun[name] = arg
        elif tag == "@v" and name and not inform and arg:
            vals.append((_key(arg.split()[0]), name))
    for v, n in vals:
        if v not in rows and n in cun:
            rows[v] = (n, cun[n])
    sha = hashlib.sha256(osl.read_bytes()).hexdigest()
    head = ("# Sign values from the Oracc Sign List (osl.asl), CC0, https://github.com/oracc/osl\n"
            f"# commit {commit}, osl.asl sha256 {sha}\n"
            "# Built by weft.akkadian.build_sign_table. value<TAB>sign<TAB>cuneiform\n")
    out.write_text(head + "".join(f"{v}\t{n}\t{c}\n" for v, (n, c) in sorted(rows.items())), encoding="utf-8")
    return len(rows)


_TABLE: dict[str, tuple[str, str]] | None = None


def signs_table() -> dict[str, tuple[str, str]]:
    global _TABLE
    if _TABLE is None:
        _TABLE = {}
        for line in DATA.read_text(encoding="utf-8").splitlines():
            if line and not line.startswith("#"):
                v, n, c = line.split("\t")
                _TABLE[v] = (n, c)
    return _TABLE


def split_signs(reading: str) -> list[str]:
    """'{d}a-nun-na-ki' -> ['d', 'a', 'nun', 'na', 'ki']; 'KA₂.DINGIR.RA{ki}' -> ['KA₂', 'DINGIR', 'RA', 'ki'].
    Determinatives in braces are signs too. Spaces separate words of a phrase."""
    out = []
    for word in reading.split():
        for piece in re.split(r"(\{[^}]+\})", word):
            if piece.startswith("{"):
                out.append(piece[1:-1])
            else:
                out += [p for p in re.split(r"[-.]", piece) if p]
    return out


def to_cuneiform(reading: str) -> tuple[str, list[str]]:
    """Cuneiform for a sign reading, and the readings the sign list does not know."""
    table = signs_table()
    out, missing = [], []
    for s in split_signs(reading):
        hit = table.get(_key(s))
        if hit:
            out.append(hit[1])
        else:
            missing.append(s)
    return "".join(out), missing


# ---------------------------------------------------------------- Harper's transliteration
SUPER = {"ilu": "ⁱˡᵘ", "alu": "ᵃˡᵘ"}
SYLL = re.compile(r"^[bdgḫhklmnpqḳrsṣštṭwyz]?[aeiu][bdgḫhklmnpqḳrsṣštṭwyz]?$")


def harper_sign_count(t: str, det: str | None) -> int | None:
    """Number of signs Harper's transliteration names, or None when he writes a logogram as a
    whole word (mâtim, dârî, Marduk), whose sign count his reading does not show."""
    body = t[len(det):] if det else t
    n = 1 if det else 0
    for part in re.split(r"[-.+]", body):
        p = re.sub(r"[()]", "", part)
        if p in ("’", "'"):
            n += 1
        elif p.isupper():
            n += 1
        elif SYLL.match(p.lower()):
            n += 1
        else:
            return None
    return n


def token_fields(surface: str, et: dict, group: dict) -> tuple[dict, list[tuple[str, str]]]:
    fields: dict = {}
    fails: list[tuple[str, str]] = []
    det = et.get("det")
    if det:
        # Harper prints the determinative raised, as the tablet's unpronounced sign
        fields["surface"] = SUPER.get(det, det) + surface[len(det):]
    sg = et.get("sg")
    if not sg:
        fails.append(("sign-reading-missing", surface))
        return fields, fails
    fields["signs"] = sg
    cun, missing = to_cuneiform(sg)
    fields["script"] = cun
    for s in missing:
        fails.append(("sign-unmapped", f"{s} in {sg}"))
    h = harper_sign_count(surface, det)
    k = len(split_signs(sg))
    if h is not None and h != k:
        fails.append(("sign-count-differs-from-harper", f"{surface}: Harper {h}, reading {sg} {k}"))
    return fields, fails


# ---------------------------------------------------------------- sound
SHORT = set("aeiu")
LONG = set("āēīū")
CONTRACTED = set("âêîû")
BASE = {"ā": "a", "ē": "e", "ī": "i", "ū": "u", "â": "a", "ê": "e", "î": "i", "û": "u"}
CONS = set("bdgḫklmnpqrsṣštṭwyzʾ")

IPA_C = {
    "ob-1750": {"b": "b", "d": "d", "g": "ɡ", "ḫ": "x", "k": "k", "l": "l", "m": "m", "n": "n",
                "p": "p", "q": "kʼ", "r": "r", "s": "ts", "ṣ": "tsʼ", "š": "s", "t": "t",
                "ṭ": "tʼ", "w": "w", "y": "j", "z": "dz", "ʾ": "ʔ"},
    "classroom": {"b": "b", "d": "d", "g": "ɡ", "ḫ": "x", "k": "k", "l": "l", "m": "m", "n": "n",
                  "p": "p", "q": "q", "r": "r", "s": "s", "ṣ": "sˤ", "š": "ʃ", "t": "t",
                  "ṭ": "tˤ", "w": "w", "y": "j", "z": "z", "ʾ": "ʔ"},
}
RSP_C = {
    "ob-1750": {"ḫ": "kh", "q": "k'", "s": "ts", "ṣ": "ts'", "š": "s", "ṭ": "t'", "z": "dz", "ʾ": "ʔ"},
    "classroom": {"ḫ": "kh", "ṣ": "s", "š": "sh", "ṭ": "t", "ʾ": "ʔ"},
}
RSP_V = {"a": "a", "e": "e", "i": "i", "u": "u", "ā": "aa", "ē": "ay", "ī": "ee", "ū": "oo",
         "â": "aa", "ê": "ay", "î": "ee", "û": "oo"}


def _segments(word: str) -> list[str]:
    w = ud.normalize("NFC", word).lower().replace("'", "ʾ").replace("’", "ʾ")
    return [c for c in w if c in SHORT | LONG | CONTRACTED | CONS]


def _syllables(segs: list[str]) -> list[list[str]]:
    """One consonant before a vowel opens its syllable; other consonants close the syllable before."""
    vi = [k for k, s in enumerate(segs) if s not in CONS]
    if not vi:
        return [segs] if segs else []
    bounds = [0]
    for a, b in zip(vi, vi[1:]):
        bounds.append(b if b - a == 1 else b - 1)
    bounds.append(len(segs))
    return [segs[bounds[j]:bounds[j + 1]] for j in range(len(vi))]


def _stress(sylls: list[list[str]]) -> int | None:
    if len(sylls) < 2:
        return None
    def nucleus(sy):
        return next(s for s in sy if s not in CONS)
    def heavy(sy):
        v = nucleus(sy)
        return v in LONG or v in CONTRACTED or sy[-1] in CONS
    last = sylls[-1]
    v = nucleus(last)
    if v in CONTRACTED or (v in LONG and last[-1] in CONS):
        return len(sylls) - 1
    for k in range(len(sylls) - 2, -1, -1):
        if heavy(sylls[k]):
            return k
    return 0


def _word(word: str, scheme: str) -> tuple[str, str, int]:
    sylls = _syllables(_segments(word))
    st = _stress(sylls)
    ipa, rsp = [], []
    for k, sy in enumerate(sylls):
        i = "".join(IPA_C[scheme][s] if s in CONS else BASE.get(s, s) + ("ː" if s in LONG | CONTRACTED else "")
                     for s in sy)
        r = "".join(RSP_C[scheme].get(s, s) if s in CONS else RSP_V[s] for s in sy)
        if k == st:
            i, r = "ˈ" + i, r.upper()
        ipa.append(i)
        rsp.append(r)
    return ".".join(ipa), "-".join(rsp), len(sylls)


def phonemize(word: str, scheme: str = "ob-1750", quantities=None, **_) -> dict:
    """A normalized form, one word or a short phrase (mārim rēštîm), in the given scheme."""
    parts = [_word(w, scheme) for w in word.split()]
    return {"ipa": " ".join(p[0] for p in parts), "respell": " ".join(p[1] for p in parts),
            "syllables": sum(p[2] for p in parts)}


KEY = {
    "ob-1750": [
        ("", "Old Babylonian as it may have sounded in Babylon around 1750 BC. This is a reconstruction and approximate throughout. It rests on how the script spells words, on words borrowed into and out of Akkadian, and on comparison with other Semitic languages. Where scholars disagree, as on the sibilants, the page follows one view and names it."),
        ("CAPS", "the stressed syllable. Cuneiform does not mark stress; the position follows the rule of the modern grammars, which is inferred"),
        ("aa, ay, ee, oo", "long vowels, held about twice as long: ā ē ī ū, and â ê î û, long vowels formed when two vowels merged"),
        ("a, e, i, u", "short vowels: a as in father but short, e as in bet, i as in bit, u as in put"),
        ("s", "the letter š. On the view followed here, Old Babylonian š was a plain s"),
        ("ts, dz", "the letters s and z on the same view: the ts of cats and the ds of beds"),
        ("t', k', ts'", "the emphatic consonants ṭ, q, ṣ, taken here as ejectives: said with the throat closed and a popping release. Their exact sound is not known"),
        ("kh", "ḫ, a rasping sound as in Scottish loch"),
        ("ʔ", "the glottal stop, the catch in uh-oh"),
        ("doubled letters", "a doubled consonant is held longer: dan-num"),
    ],
    "classroom": [
        ("", "The reading taught in Assyriology classes today, which follows the normalization letter by letter. It is a convention for reading aloud, not a claim about ancient speech."),
        ("CAPS", "stress, placed by the modern grammars' rule"),
        ("sh", "the letter š"),
        ("s, t", "the emphatic ṣ and ṭ, usually said as plain s and t; some teachers give them the throaty quality of the Arabic emphatics"),
        ("q", "a k made further back in the mouth"),
        ("kh", "ḫ, as in Scottish loch"),
        ("ʔ", "the glottal stop, the catch in uh-oh"),
        ("aa, ay, ee, oo", "long vowels, held about twice as long"),
        ("doubled letters", "a doubled consonant is held longer"),
    ],
}
SCHEME_LABELS = {
    "ob-1750": "Old Babylonian, around 1750 BC (approximate)",
    "classroom": "Assyriological classroom reading",
}


if __name__ == "__main__":
    # python -m weft.akkadian build-signs <osl.asl>: rebuild data/akk_osl_values.tsv
    import sys
    if len(sys.argv) >= 3 and sys.argv[1] == "build-signs":
        print(build_sign_table(Path(sys.argv[2]), DATA), "values")
    else:
        for w in sys.argv[1:]:
            for s in KEY:
                print(w, s, phonemize(w, s))
