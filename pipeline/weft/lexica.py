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
