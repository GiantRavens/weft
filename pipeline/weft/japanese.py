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
"""
from __future__ import annotations

VERSION = "0.2"

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
}
SCHEME_LABELS = {"edo-1686": "Edo, 1686: as Bashō's contemporaries spoke (approximate)",
                 "modern": "Modern Japanese (Hepburn)"}


def phonemize(word: str, scheme: str = "edo-1686", quantities=None, **_) -> dict:
    """`word` is the token's historical kana reading."""
    ms = morae(word, scheme)
    shown = _contract(ms, word) if word != "は" else ms
    return {"ipa": ".".join(_ipa(m) for m in shown), "respell": "-".join(shown), "syllables": len(ms)}
