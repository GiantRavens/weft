"""Middle French (Montaigne, 1580s): modern spelling -> lexicon -> sound, with liaison and elision.

The printed text keeps the spelling of its edition (icy, vn liure, moy-mesme). Each token gives its
modern spelling by hand in n (ici, un livre, moi-même); the page shows it under the original as
"Modern spelling". The old spelling is not a guide to sound in 1580 either: the s of estre and the
c of subiect were already silent, and u and v, i and j are one letter each. So the sound does not
come from rules over either spelling. It comes from a hand-written lexicon,
`pipeline/weft/data/fr_lexicon.yaml`, keyed by the modern spelling, with one IPA form per scheme
and the latent final consonant each word sounds in liaison. This module adds what depends on the
next word: liaison and the elision of a final e caduc.

Schemes
-------
m1580    French as an educated reader would have said it about 1580, approximate. The model is the
         Paris norm the grammarians describe; Montaigne himself was from Périgord, spoke Gascon-
         influenced French, and says in the Essais that his speech had a provincial accent, so his
         own reading differed in ways this scheme does not try to recover.
         Evidence: the grammarians and spelling reformers of the 16th century, chiefly Louis
         Meigret (Traité touchant le commun usage de l'escriture françoise, 1542; Le tretté de la
         grammere françoeze, 1550), Jacques Peletier du Mans (Dialogue de l'ortografe e
         prononciation françoese, 1550), Pierre de la Ramée (Gramere, 1562 and 1572), Théodore de
         Bèze (De Francicae linguae recta pronuntiatione, 1584) and Henri Estienne (Deux dialogues
         du nouveau langage françois italianizé, 1578), as collected and weighed by Charles Thurot,
         De la prononciation française depuis le commencement du XVIe siècle (1881-1883). The main
         features modelled:
         - final consonants are silent before a consonant and before a pause, and sounded before a
           vowel when no pause intervenes (liaison). Final r after i (loisir, mourir), final l,
           f and the c of donc are sounded everywhere. Palsgrave (1530) still reports final
           consonants sounded before a pause; by the 1580s that use was receding, and the scheme
           follows the later grammarians. The r of infinitives in -er is treated as silent except
           in liaison; the grammarians disagree on this point.
         - s before a consonant is silent (estre, nostre, aprester); where it closed a stressed
           syllable, the vowel is long (tost, toː; moy-mesme, mɛː).
         - oi is [wɛ] (foy, moy, loix, connoissance). The 16th century had three competing values,
           [we], [wɛ] and [ɛ]; [ɛ] was spreading in the imperfect and conditional and in some
           words at court, and was mocked by Estienne. [wɛ] is a middle choice.
         - the nasal vowels; un is [ỹ], not yet lowered to [œ̃]. A vowel before n or m and a
           following vowel is still nasal (bonne, bɔ̃.nə); the denasalization came in the 17th
           century.
         - the e caduc (ə) at the end of a word is written where the grammarians still count it,
           before a consonant and at a pause; it is elided before a vowel. How strongly it was
           sounded in speech, as opposed to verse, is not certain.
         - r is a tongue-tip trill; the uvular r came later. h in hors is sounded (h aspiré).
         - ai before gn in Montaigne is a spelling of the palatal n, so the name is [mɔ̃.ta.ɲə], as
           in Champaigne for Champagne; the modern [mɔ̃.tɛɲ] follows the spelling.
         - il and ils are [i] before a consonant, as the grammarians report for ordinary speech.
         Vowel length is marked only where the loss of s or of a final e left a long vowel.
modern   Standard modern French, the word said alone, with the liaisons that today's careful
         reading makes (those the edition marks z: true).
fr1885   French as an educated Parisian reader of the 1880s would have read a formal text aloud,
         used for the General Act of the Berlin Conference (1885). French of 1885 is close to
         modern standard French: the spelling had been fixed since the Academy's dictionary of 1835
         and is the modern one, and most sounds are the modern ones. Evidence is direct, not
         reconstructed from rhymes or spelling: Paul Passy, Les sons du français (1887) and the
         phonetic transcriptions of Le Maître phonétique (from 1886), and Émile Littré's
         Dictionnaire de la langue française (1863-1872), which gives a pronunciation for each word.
         What the scheme shows differently from modern:
         - vowel length. Passy hears a long vowel in a final syllable closed by r, z, zh or v
           (commerce no, affaires yes: a.fɛːʁ) and in many words with a circumflex (même, mɛːm).
           Length was then partly distinctive (maître, mettre); it is now an automatic effect of
           position, and the modern scheme does not mark it.
         - a back a, [ɑ], in words where Littré marks it with a circumflex in his respelling (pas,
           pâ; the plural droits, droî). Paris speech has since largely merged it with front a.
           These forms are written word by word in the lexicon (fr1885), each from Littré.
         - more liaisons. Formal reading of the period sounded final consonants before a vowel in
           places today's reading leaves silent (the edition marks these zf); liaisons marked z
           are made in both schemes.
         - a few words where Littré gives a silent final consonant now often sounded (but, bu).
         The r is the uvular r, which Passy reports as the usual Paris r in the 1880s, with the
         tongue-tip r still used in the provinces and on the stage. The conference met in Berlin
         and its delegates were not French; the scheme models the Paris norm of the language they
         wrote in, not any delegate's own accent. Where the lexicon has no fr1885 form the word is
         taken from its modern form with the length rule applied.

French has no word stress that distinguishes meaning: the last full syllable of a phrase is
lengthened. No syllable is written in capitals.

Edition token fields (texts/<work>/edition.yaml)
-----------------------------------------------
t      the word as printed, with any punctuation attached to it (foy,); the punctuation is split
       off into the token's punct
n      the modern spelling (lowercase except proper names); the lexicon key. A work printed in
       modern spelling (the Berlin Act) gives n only where the print differs (Etat, État); the
       lexicon key is then the printed word, lowercased, without its punctuation
p      punctuation set off by a space in the print (French " :")
glue   no space follows (the elided c', l', qu')
z      modern liaison: the final consonant is sounded before the next word in the modern scheme
nz     no liaison in m1580 for this word, where the general rule would make one
zf     liaison in fr1885 only: made in formal reading of the 1880s, not in the modern scheme
ipa    {scheme: ipa} override for this occurrence
"""
from __future__ import annotations

import re
import unicodedata as ud
from pathlib import Path

import yaml

VERSION = "0.2"
SHOW_TRANSLIT = True
TRANSLIT_LABEL = "Modern spelling"

_LEX: dict | None = None
_CTX: dict = {}            # the current token's context, set by token_fields for phonemize

LEAD_P = re.compile(r"^([(\[«“]+)")
TRAIL_P = re.compile(r"([,.;:!?)\]»”]+)$")
VOWELS = set("aeiouyɑɛɔøœəɥ")
ELIDED = re.compile(r"^[^\W\d_]+[’']$")       # a word beginning with one of these takes liaison and elision


def lexicon() -> dict:
    global _LEX
    if _LEX is None:
        p = Path(__file__).parent / "data" / "fr_lexicon.yaml"
        _LEX = {ud.normalize("NFC", k): v for k, v in (yaml.safe_load(p.read_text(encoding="utf-8")) or {}).items()}
    return _LEX


def key(word: str) -> str:
    return ud.normalize("NFC", word.replace("'", "’")).lower()


LENGTHENING = ("ʁ", "z", "ʒ", "v", "vʁ")   # a final syllable closed by these lengthens its vowel
ORAL = "aɑeɛiouyøœə"


def lengthen_1885(ipa: str) -> str:
    """fr1885 from a modern form: the vowel of a final syllable closed by r, z, zh, v (or vr) is long,
    as Passy (1887) marks it. Other period forms (pas, pɑ) are written in the lexicon."""
    if "ː" in ipa:
        return ipa
    head, _, last = ipa.rpartition(".")
    for c in sorted(LENGTHENING, key=len, reverse=True):
        if last.endswith(c) and len(last) > len(c) and last[-len(c) - 1] in ORAL and last[-len(c) - 1] != "ə":
            last = last[:-len(c)] + "ː" + c
            break
    return (head + "." if head else "") + last


def base_ipa(word: str, scheme: str) -> str | None:
    e = lexicon().get(key(word))
    if not e:
        return None
    if scheme == "fr1885" and "fr1885" not in e and e.get("modern"):
        return lengthen_1885(e["modern"])
    return e.get(scheme)


def bare(word: str) -> str:
    """The printed word without leading or trailing punctuation."""
    word = LEAD_P.sub("", word or "")
    return TRAIL_P.sub("", word)


def begins_with_vowel(ipa: str | None) -> bool:
    return bool(ipa) and ipa[0] in VOWELS


# ---------------------------------------------------------------- IPA -> respelling
NASAL = {"ɑ": "ahⁿ", "a": "ahⁿ", "ɛ": "ehⁿ", "e": "ehⁿ", "ɔ": "ohⁿ", "o": "ohⁿ", "œ": "öⁿ", "y": "üⁿ"}
LONG = {"a": "aa", "ɑ": "aa", "e": "ayy", "ɛ": "ehh", "o": "ohh", "ɔ": "ohh", "y": "üü", "i": "eee", "u": "ooo",
        "ø": "öö", "œ": "öö"}
PLAIN = {"a": "a", "ɑ": "ah", "e": "ay", "ɛ": "eh", "i": "ee", "o": "oh", "ɔ": "o", "u": "oo", "y": "ü",
         "ø": "ö", "œ": "ö", "ə": "uh", "ʃ": "sh", "ʒ": "zh", "ɲ": "ny", "ʎ": "ly", "j": "y", "w": "w",
         "ɥ": "ü", "r": "r", "ʁ": "r", "ɡ": "g", ".": "-", "‿": "‿"}
PRECOMPOSED = {"ỹ": "ỹ"}


def respell(ipa: str) -> str:
    s = ud.normalize("NFD", ipa)
    for k, v in PRECOMPOSED.items():
        s = s.replace(ud.normalize("NFD", k), v)
    out, i = [], 0
    while i < len(s):
        c = s[i]
        nxt = s[i + 1] if i + 1 < len(s) else ""
        if nxt == "̃":
            out.append(NASAL.get(c, c))
            i += 2
            continue
        if nxt == "ː":
            out.append(LONG.get(c, c + c))
            i += 2
            continue
        out.append(PLAIN.get(c, c))
        i += 1
    return "".join(out)


# ---------------------------------------------------------------- context
def _flat(group: dict) -> list[dict]:
    return [t for ln in group.get("lines", []) if not isinstance(ln, str) for t in ln["tokens"]]


def token_fields(surface: str, et: dict, group: dict) -> tuple[dict, list[tuple[str, str]]]:
    """Split punctuation off the printed word, check the lexicon, and hold the token's context
    (next word, pause, liaison marks) for phonemize, which draft calls next for this token."""
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
    # the lexicon key: the modern spelling, or the printed word when the print is modern
    n = et.get("n") or word
    if key(n) not in lexicon() and not et.get("ipa"):
        fails.append(("lexicon-missing", n))
    toks = _flat(group)
    k = next((i for i, t in enumerate(toks) if t is et), None)
    nxt = toks[k + 1] if k is not None and k + 1 < len(toks) else None
    pause = bool(mt) or bool(et.get("p")) or nxt is None or bool(nxt and LEAD_P.search(nxt["t"]))
    _CTX = {"n": n, "next": (nxt or {}).get("n") or (bare(nxt["t"]) if nxt else None), "pause": pause,
            "z": bool(et.get("z")), "zf": bool(et.get("zf")),
            "nz": bool(et.get("nz")), "ipa": et.get("ipa") or {}, "glue": bool(et.get("glue"))}
    for mark in ("z", "zf"):
        if et.get(mark):
            lz = (lexicon().get(key(n or "")) or {}).get("lz")
            if not lz:
                fails.append(("liaison-no-consonant", n or surface))
            elif pause or not begins_with_vowel(base_ipa(_CTX["next"] or "", "modern")):
                fails.append(("liaison-not-before-vowel", f"{n} {_CTX['next']}"))
    return fields, fails


def in_context(word: str, scheme: str) -> str:
    """The word's IPA in this scheme, with liaison and elision applied from the held context."""
    ctx = _CTX if _CTX.get("n") == word else {}
    ipa = (ctx.get("ipa") or {}).get(scheme) or base_ipa(word, scheme)
    if ipa is None:
        return "?"
    if not ctx or ctx.get("pause") or ctx.get("glue"):
        return ipa
    nxt = base_ipa(ctx.get("next") or "", scheme)
    if not begins_with_vowel(nxt):
        return ipa
    lz = (lexicon().get(key(word)) or {}).get("lz")
    if scheme == "m1580":
        if ipa.endswith("ə") and not lz:
            # e caduc elided before a vowel; its consonant closes the syllable before
            stem = ipa[:-1]
            if "." in stem:
                head, last = stem.rsplit(".", 1)
                stem = head + last
            return stem + "‿"
        if lz and not ctx.get("nz"):
            return ipa + lz + "‿"
        return ipa
    if lz and (ctx.get("z") or (scheme == "fr1885" and ctx.get("zf"))):
        return ipa + lz + "‿"
    return ipa


def syllables(ipa: str) -> int:
    if ipa in ("?", ""):
        return 0
    # an elided form (c’, l’) is a consonant alone and carries no syllable of its own
    parts = [p for p in ipa.replace("‿", "").split(".") if any(ch in VOWELS for ch in ud.normalize("NFD", p))]
    return len(parts)


def phonemize(word: str, scheme: str = "m1580", quantities=None, **_) -> dict:
    """`word` is the token's modern spelling (n), or the printed word when the edition gives no n."""
    ipa = in_context(bare(word), scheme)
    return {"ipa": ipa, "respell": respell(ipa) if ipa != "?" else "?", "syllables": syllables(ipa)}


def line_checks(text: str, etoks: list[dict], edition: dict) -> list[tuple[str, str]]:
    """Sensors: an elided token (ending in an apostrophe) must be glued to the next word, and a
    glued token must be an elision."""
    out = []
    for t in etoks:
        # an elision is letters and an apostrophe (c’, qu’); 2°30’ (minutes of arc) is not one
        el = bool(ELIDED.match(t["t"]))
        if el and not t.get("glue"):
            out.append(("elision-not-glued", t["t"]))
        if t.get("glue") and not el:
            out.append(("glue-without-elision", t["t"]))
    return out


KEY = {
    "m1580": [
        ("", "French of about 1580, as the grammarians of the period describe the Paris norm; approximate. Montaigne's own Gascon-coloured accent is not modelled."),
        ("", "Hyphens divide syllables. French has no distinctive word stress; the last full syllable of a phrase is lengthened, so no capitals are used."),
        ("uh", "the e caduc (ə), still counted at the end of a word before a consonant or a pause; dropped before a vowel"),
        ("‿", "linked to the next word: a final consonant sounded in liaison (est‿icy), or an e caduc elided before a vowel"),
        ("ahⁿ ehⁿ ohⁿ üⁿ", "nasal vowels: the vowel said through the nose, no n sound after it. üⁿ (un) is ü through the nose"),
        ("weh", "oi, as in foy (fweh) and moy (mweh): the value most grammarians of the 1580s give; [we] and [ɛ] were also heard"),
        ("ü", "French u: say ee with rounded lips"),
        ("ö", "the vowel of peu and of fleur: say ay with rounded lips"),
        ("ayy ehh ohh aa üü", "long vowels: the length left where an s fell silent (tost, toh) or a final e was lost (privée)"),
        ("r", "a trilled r with the tip of the tongue"),
        ("zh", "the s of measure"),
        ("ny", "the palatal n of canyon, in Montaigne (mohⁿ-ta-nyuh)"),
        ("h", "sounded, in hors"),
    ],
    "modern": [
        ("", "Standard modern French. Hyphens divide syllables; no capitals, since French has no distinctive word stress."),
        ("uh", "the e caduc (ə), kept in je, de, que, ne, ce, me, se and inside words where careful reading keeps it"),
        ("‿", "liaison: the final consonant is sounded and runs into the next word"),
        ("ahⁿ ehⁿ ohⁿ öⁿ", "nasal vowels: the vowel said through the nose, no n sound after it"),
        ("ü", "French u: say ee with rounded lips"),
        ("ö", "the vowel of peu and of fleur"),
        ("r", "the uvular r, at the back of the throat"),
        ("zh", "the s of measure"),
        ("ny", "the gn of Montaigne, as in canyon"),
    ],
    "fr1885": [
        ("", "French as an educated Parisian would have read a formal text in the 1880s, after Passy (1887) and Littré. It is close to modern French; the differences shown are vowel length, a back a in some words, and more liaisons."),
        ("", "Hyphens divide syllables; no capitals, since French has no distinctive word stress. The word is shown as said alone; inside a phrase the long vowels were shorter."),
        ("aa ehh ohh eee ooo üü öö", "long vowels: in a final syllable closed by r, z, zh or v (sur, süür; fleuves, flööv), and in some words with a circumflex (même, mehhm)"),
        ("ah", "a back a, as in father, in words where Littré gives it (pas, pah; droits, drwah)"),
        ("uh", "the e caduc (ə), kept in de, le, que, ne, ce, se and where careful reading keeps it inside a word"),
        ("‿", "liaison: the final consonant is sounded and runs into the next word, including liaisons formal reading made then and seldom makes now (marked in the edition)"),
        ("ahⁿ ehⁿ ohⁿ öⁿ", "nasal vowels: the vowel said through the nose, no n sound after it; öⁿ (un) was kept apart from ehⁿ (in)"),
        ("ü", "French u: say ee with rounded lips"),
        ("ö", "the vowel of peu and of fleur: say ay with rounded lips"),
        ("r", "the uvular r, at the back of the throat, which Passy reports as the usual Paris r of the 1880s"),
        ("zh", "the s of measure"),
        ("ny", "the gn of signataires, as in canyon"),
    ],
}
SCHEME_LABELS = {"m1580": "French about 1580: Montaigne's day (approximate)",
                 "modern": "Modern French",
                 "fr1885": "French of the 1880s: formal Paris reading"}
