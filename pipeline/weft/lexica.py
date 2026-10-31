"""Headword lists for sensors: does a lemma name a word the dictionary knows?

LSJ (Liddell, Scott and Jones, A Greek-English Lexicon, 9th ed., 1940) in the Perseus Digital Library's TEI
edition (CC BY-SA 3.0, github.com/PerseusDL/lexica), pinned by commit and by each file's sha256. The files
(27, about 280 MB) are fetched once by `weft lexica` into ~/.cache/weft/lsj/ and never committed (hard
rule 4); only the set of headwords derived from them is kept beside them.

Matching is by bare letters: the entry's Beta Code key and the treebank's Unicode lemma are both reduced to
lower-case letters, without breathings, accents, quantity marks, hyphens or homograph numbers. That is
coarse on purpose. The sensor's class is a lemma that is not a Greek word at all (GLAUx's ταραχθαίνω,
κροκύφω, στερείκνυμι), which bare letters catch; accent conventions, which they would not, differ between
LSJ and the treebanks and are not this sensor's concern.
"""
from __future__ import annotations

import hashlib
import re
import unicodedata as ud
import urllib.request
from pathlib import Path

LSJ_COMMIT = "1c34cdf756c63cf37db61bd366d733431dbd7aa0"
LSJ_URL = "https://raw.githubusercontent.com/PerseusDL/lexica/{commit}/CTS_XML_TEI/perseus/pdllex/grc/lsj/grc.lsj.perseus-eng{n}.xml"
LSJ_SHA256 = {
    1: "96c89b299bd3a81ee8707bd7092e42878d172b3f301da0adfa41d8d09dfbfde9",
    2: "e711d36e733f6c199afb84819e86ea0f607b92cbaea4ee8a915e77ebc4662ced",
    3: "2853d7882df86225df5824e63b579f1ac84f72a89f2ae75961a77a443b4958fa",
    4: "dbe9a65694887bac4e99c41155e48926ab4b840157ce955479642925bdfc029b",
    5: "ea63fc316565059bc05c338f369f72b1366dc464e3b3d761e1f9ad447416eb3f",
    6: "ce0111eb40d9b9d720e59e0d6caaa97b3386ff72f46b195d7a238756d1348479",
    7: "5340dd231acf6bc79d134e57def4c459c71ed9afbcd0ef3ad4457ebcab164c17",
    8: "94ea07a228bb7a25f1d2cf93fe0f3fa4b72e6b17553fca069ad06ae5bb78f518",
    9: "7f274c8dce5f6837c55f3f3db5c8e86c84c70c42631bb07b761b196d5c0d4f86",
    10: "51e496289761bab5fb0c4346eded476f12266ce203a30ed2d0fb7500193a9a81",
    11: "aefc985475f565798afc59ead25d6afa7175dfbc2ab858ef26cc0f3742b84809",
    12: "6f58010f38711cdcd2812ec9baaedc6d51f2cc39adb24ae9941371c0f2cc2543",
    13: "983c54dbb094763cb2b92a130656fdd73454b9e85bcfbd121c578c7f4795d58c",
    14: "8190b1823958783f4820fa7dbeef590cb7f46a50f366473d3008778dfd260c3c",
    15: "a5f8cc41fe8a05ad3dc45e105e647f20cadebd46ca5250256fe79913746eedb0",
    16: "492ce0d174267544388f4938324a4137f21a8d7ae86e5d28dec5beaf1a496b7e",
    17: "4c02d9b465e684d4d83286c80049492e7c5e81250e3ed8e6b1ca1d3fb21a6dc5",
    18: "72f346e95bf9cb334d119103ff1cab89e39b0bb2fae1364de51428ac8655f727",
    19: "867386bbb250dc127d73ba105a92fd3a2115a94702ec3c1ffdea575c77bdca57",
    20: "b39478b6c607db3750ab71e5c4dc4ff40b688cac3d966f4afe62d5ec281e142b",
    21: "21e5b7e46964192e520c90a177b2dc5c7893e524afce356ccbf9054d43d03189",
    22: "953b6c398e460cd633be2fefc144e17399a3a9f111d3388d032023227380149b",
    23: "36ad46cab32dc131619a902d959893a407f1fcfc743c7e129ea9aee6fbde6597",
    24: "6d3d8c83110b0a3b94c97cf2f9ddf8ced87a6d740a312de2b8a21a3b224677c7",
    25: "5ba38f1e6f5886af6ee236028d6aee8e910aec89cb66954ae719a05a6866111d",
    26: "174f544c0afed660fb0aebf7457da4d78a26889b8d40922533473bdf0a6b5c9e",
    27: "23bea40e1fe0484c39df438112c9cf728df29f3c97d9c465f1b1aaa194840ab6",
}
CACHE = Path.home() / ".cache" / "weft" / "lsj" / LSJ_COMMIT[:7]
HEADWORDS = CACHE / "headwords-bare.txt"

GRC_TO_BETA = dict(zip("αβγδεζηθικλμνξοπρσςτυφχψω", "abgdezhqiklmncoprsstufxyw"))
_KEY = re.compile(r'<entryFree[^>]*\bkey="([^"]+)"')


def bare_beta(key: str) -> str:
    """A Beta Code key -> bare letters: 'a)/po-kri^sis' -> 'apokrisis', '*ba/ktra' -> 'baktra'."""
    return re.sub(r"[^a-z]", "", key.lower())


def bare_grc(word: str) -> str:
    """A Unicode Greek word -> the same bare letters: 'ἀπόκρισις' -> 'apokrisis'."""
    s = "".join(c for c in ud.normalize("NFD", word.lower()) if not ud.combining(c))
    return "".join(GRC_TO_BETA.get(c, "") for c in s)


def fetch(log=print) -> Path:
    """Download the pinned LSJ files (checked by sha256) and write the bare headword list."""
    CACHE.mkdir(parents=True, exist_ok=True)
    keys: set[str] = set()
    for n, want in LSJ_SHA256.items():
        p = CACHE / f"grc.lsj.perseus-eng{n}.xml"
        if not p.exists() or hashlib.sha256(p.read_bytes()).hexdigest() != want:
            log(f"fetching LSJ part {n} of {len(LSJ_SHA256)}")
            req = urllib.request.Request(LSJ_URL.format(commit=LSJ_COMMIT, n=n), headers={"User-Agent": "weft-lexica/0.1"})
            with urllib.request.urlopen(req, timeout=300) as r:
                data = r.read()
            if hashlib.sha256(data).hexdigest() != want:
                raise SystemExit(f"weft lexica: LSJ part {n} does not match its pinned sha256")
            p.write_bytes(data)
        keys.update(bare_beta(k) for k in _KEY.findall(p.read_text(encoding="utf-8")))
    keys.discard("")
    HEADWORDS.write_text("\n".join(sorted(keys)), encoding="utf-8")
    log(f"{len(keys)} bare LSJ headwords -> {HEADWORDS}")
    build_quantities(log)
    fetch_ls(log)
    return HEADWORDS


_SET: set[str] | None = None


def lsj_headwords() -> set[str] | None:
    """The bare headword set, or None when `weft lexica` has not been run on this machine."""
    global _SET
    if _SET is None and HEADWORDS.exists():
        _SET = set(HEADWORDS.read_text(encoding="utf-8").split())
    return _SET


def grc_lemma_ok() -> dict[str, str]:
    """Lemmas checked as Greek words though LSJ has no headword for them, each with the reason
    (data/grc_lemma_ok.yaml): the sensor's declared exceptions, so it stays strict everywhere else."""
    import yaml
    p = Path(__file__).parent / "data" / "grc_lemma_ok.yaml"
    return (yaml.safe_load(p.read_text(encoding="utf-8")) or {}) if p.exists() else {}


# ---------------------------------------------------------------- vowel length from LSJ headwords (pin 17)
# LSJ's headword spellings (the entry's first orth) mark doubtful vowels in Beta Code: _ after a long one, ^ after a
# short one (neo/-xu^tos). The map below keeps, for each headword, its letters with the long marks, so a word's
# long α, ι, υ can be taken from its lemma's headword (greek.lsj_quantity).
QUANTITIES = CACHE / "headwords-quantity.tsv"
_ORTH = re.compile(r'<entryFree[^>]*\bkey="([^"]+)"[^>]*>\s*(?:<[^o][^>]*>\s*)*<orth [^>]*>([^<]+)</orth>')   # the first orth, full or suff (yu_x-h/)


def beta_letters(orth: str) -> list[tuple[str, bool]]:
    """A Beta Code headword -> [(bare letter, long?)]: a letter followed by _ is long."""
    out: list[tuple[str, bool]] = []
    for ch in orth.lower():
        if "a" <= ch <= "z":
            out.append((ch, False))
        elif ch == "_" and out:
            out[-1] = (out[-1][0], True)
    return out


def build_quantities(log=print) -> Path:
    """From the fetched LSJ files: bare headword -> its letters, long ones capitalized (q_ta^ -> 'qTa' style)."""
    rows: dict[str, str] = {}
    gcands: dict[str, set[str]] = {}
    for n in LSJ_SHA256:
        text = (CACHE / f"grc.lsj.perseus-eng{n}.xml").read_text(encoding="utf-8")
        for key, orth in _ORTH.findall(text):
            letters = beta_letters(orth)
            bare = "".join(c for c, _ in letters)
            if bare != bare_beta(key):
                continue
            gcands.setdefault(bare, set()).add("".join(c.upper() if long else c for c, long in letters))
    # homographs that mark the word differently are left out (as for Lewis and Short)
    for b, ms in gcands.items():
        if len(ms) == 1 and any(c.isupper() for c in next(iter(ms))):
            rows[b] = next(iter(ms))
    QUANTITIES.write_text("\n".join(f"{k}\t{v}" for k, v in sorted(rows.items())), encoding="utf-8")
    log(f"{len(rows)} LSJ headwords with a marked long vowel -> {QUANTITIES}")
    return QUANTITIES


_QSET: dict[str, str] | None = None


def lsj_long_marks() -> dict[str, str] | None:
    """bare headword -> its letters with the long ones upper-cased, or None before `weft lexica` has run."""
    global _QSET
    if _QSET is None and QUANTITIES.exists():
        _QSET = dict(line.split("\t", 1) for line in QUANTITIES.read_text(encoding="utf-8").splitlines() if "\t" in line)
    return _QSET


# ---------------------------------------------------------------- Latin: Lewis and Short (pin 21)
# Lewis and Short, A Latin Dictionary (1879), in the Perseus TEI edition (CC BY-SA 3.0), from the same pinned
# commit. Its headwords print length in Unicode: ō long, ŏ short (ălĭmōnĭa). Only the macrons are taken: an
# unmarked vowel is not a short one (abhorreo's final o is long and unmarked).
LS_URL = "https://raw.githubusercontent.com/PerseusDL/lexica/{commit}/CTS_XML_TEI/perseus/pdllex/lat/ls/lat.ls.perseus-eng{n}.xml"
LS_SHA256 = {
    1: "421782f2b444f2705077745e7b0455314bb0ebaee3d66acf0110f88e4b5a121c",
    2: "933ba8fde0ef06823f69a130c95ba6f345ece3cb1603514b17972d1edd421d32",
}
LS_QUANTITIES = CACHE / "ls-headwords-quantity.tsv"
_LS_ORTH = re.compile(r'<entryFree[^>]*\bkey="([^"]+)"[^>]*>\s*<orth [^>]*>([^<]+)</orth>')
_MACRON_LETTERS = {"ā": "a", "ē": "e", "ī": "i", "ō": "o", "ū": "u", "ȳ": "y"}


def bare_lat(word: str) -> str:
    """Lower-case Latin letters only, j as i and v as u (the dictionary and the editions differ)."""
    s = "".join(c for c in ud.normalize("NFD", word.lower().replace("æ", "ae").replace("œ", "oe")) if not ud.combining(c))
    return re.sub(r"[^a-z]", "", s).replace("j", "i").replace("v", "u")


def ls_letters(orth: str) -> str:
    """A headword -> its bare letters with the long (macron) ones upper-cased: ălĭmōnĭa -> alimOnia."""
    out = []
    for ch in ud.normalize("NFC", orth.lower().replace("æ", "ae").replace("œ", "oe")):
        if ch in _MACRON_LETTERS:
            out.append(_MACRON_LETTERS[ch].upper())
        else:
            b = bare_lat(ch)
            out.append(b)
    return "".join(out).replace("J", "I").replace("V", "U")


def fetch_ls(log=print) -> Path:
    """Download the pinned Lewis and Short (sha256-checked) and write the headword list with long marks."""
    CACHE.mkdir(parents=True, exist_ok=True)
    rows: dict[str, str] = {}
    cands: dict[str, set[str]] = {}
    for n, want in LS_SHA256.items():
        p = CACHE / f"lat.ls.perseus-eng{n}.xml"
        if not p.exists() or hashlib.sha256(p.read_bytes()).hexdigest() != want:
            log(f"fetching Lewis and Short part {n} of {len(LS_SHA256)}")
            req = urllib.request.Request(LS_URL.format(commit=LSJ_COMMIT, n=n), headers={"User-Agent": "weft-lexica/0.1"})
            with urllib.request.urlopen(req, timeout=300) as r:
                data = r.read()
            if hashlib.sha256(data).hexdigest() != want:
                raise SystemExit(f"weft lexica: Lewis and Short part {n} does not match its pinned sha256")
            p.write_bytes(data)
        for key, orth in _LS_ORTH.findall(p.read_text(encoding="utf-8")):
            marked = ls_letters(orth)
            bare = marked.lower()
            if bare != bare_lat(re.sub(r"\d+$", "", key)):
                continue
            cands.setdefault(bare, set()).add(marked)
    # homographs (solum 'ground', sōlum 'only') that mark the word differently are left out: a guess between
    # them is worse than the default
    rows = {b: next(iter(ms)) for b, ms in cands.items() if len(ms) == 1 and any(c.isupper() for c in next(iter(ms)))}
    dropped = sum(1 for ms in cands.values() if len(ms) > 1)
    LS_QUANTITIES.write_text("\n".join(f"{k}\t{v}" for k, v in sorted(rows.items())), encoding="utf-8")
    log(f"{len(rows)} Lewis and Short headwords with a marked long vowel ({dropped} homographs that disagree left out) -> {LS_QUANTITIES}")
    return LS_QUANTITIES


_LSQ: dict[str, str] | None = None


def ls_long_marks() -> dict[str, str] | None:
    global _LSQ
    if _LSQ is None and LS_QUANTITIES.exists():
        _LSQ = dict(l.split("\t", 1) for l in LS_QUANTITIES.read_text(encoding="utf-8").splitlines() if "\t" in l)
    return _LSQ
