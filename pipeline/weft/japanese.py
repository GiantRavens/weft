"""Japanese: historical kana reading -> morae -> romanized sound.

Each token carries its reading in historical kana (the spelling of Bashō's day): 蛙 is かはづ,
水 is みづ. Rules turn that spelling into sound for each scheme. Japanese verse counts morae
(on), not syllables, so the mora count is returned for the metre row.

Schemes
-------
edo-1686   Japanese as spoken in Edo in the 1680s, approximate. Word-medial は ひ ふ へ ほ are
           read wa i u e o (a change completed centuries earlier); づ and ぢ are read dzu and dji,
           following reconstructions that keep them distinct from ず and じ into the 1600s,
           though they were merging in Edo by Bashō's time.
modern     Modern Tokyo Japanese, standard Hepburn romanization.

Pitch accent is not marked in either scheme.
"""
from __future__ import annotations

VERSION = "0.1"

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


def morae(kana: str, scheme: str) -> list[str]:
    out = []
    for i, ch in enumerate(kana):
        if i > 0 and ch in MEDIAL_H:
            r = MEDIAL_H[ch]                     # かは -> kawa, not kaha
        else:
            r = KANA.get(ch, ch)
        if scheme == "modern":
            r = MODERN.get(r, r)
        out.append(r)
    return out


def _ipa(m: str) -> str:
    if m in IPA:
        return IPA[m]
    ipa = m.replace("r", "ɾ").replace("y", "j").replace("g", "ɡ")
    return ipa


KEY = {
    "edo-1686": [
        ("", "Each hyphen divides a mora (on), the unit Japanese verse counts: furu-ike is fu-ru-i-ke, four morae."),
        ("dzu", "づ, as in the old spelling かはづ and みづ; possibly still distinct from zu in the 1680s, approximate"),
        ("wa", "は inside a word: かはづ is kawadzu, not kahadzu"),
        ("u", "unrounded, lips spread"),
        ("r", "a light tap, between r and l"),
        ("", "Pitch accent is not marked."),
    ],
    "modern": [
        ("", "Standard Hepburn romanization of modern Tokyo Japanese; hyphens divide morae."),
        ("zu", "づ and ず are now the same sound"),
        ("", "Pitch accent is not marked."),
    ],
}
SCHEME_LABELS = {"edo-1686": "Edo, 1686: as Bashō's contemporaries spoke (approximate)",
                 "modern": "Modern Japanese (Hepburn)"}


def phonemize(word: str, scheme: str = "edo-1686", quantities=None, **_) -> dict:
    """`word` is the token's historical kana reading."""
    ms = morae(word, scheme)
    return {"ipa": ".".join(_ipa(m) for m in ms), "respell": "-".join(ms), "syllables": len(ms)}
