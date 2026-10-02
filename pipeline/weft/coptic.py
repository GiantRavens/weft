"""Sahidic Coptic: treebank lemma and morphology through the token hook, a check against the SWORD
source, and two sound schemes.

Weft's first Coptic work is Mark 1:1-20 in Sahidic, from the Sahidic Bible 2 text of the CrossWire
SWORD project (CopSahBible2, CC BY-SA). Each token in the edition carries:

  t        the word as the source prints it, verbatim. The source separates words by the
           conventions of its editors (articles and prefixes written onto the noun or verb, most
           prepositions apart). Where one printed word holds two Coptic bound groups, as the
           Coptic Scriptorium treebank divides them, Weft splits it into two tokens joined with
           `glue`, so the line still reproduces the source
  ud       the treebank words the token covers, "<sentence>:<first>-<last>" in the Mark 1 document
           of UD_Coptic-Scriptorium (CC BY 4.0). Through it this module reads lemma, part of speech
           and features (the treebank, rule 3)
  ud_part  where the source writes apart what the treebank keeps as one word (ⲁⲩϫⲓ ⲃⲁⲡⲧⲓⲥⲙⲁ, the
           compound verb ϫⲓⲃⲁⲡⲧⲓⲥⲙⲁ "receive baptism"), the part of that word this token carries
  n        the full form of an abbreviated sacred name (nomen sacrum): ⲓⲏⲥ for ⲓⲏⲥⲟⲩⲥ, ⲡⲉⲭⲥ for
           ⲡⲉⲭⲣⲓⲥⲧⲟⲥ, ⲡⲛⲁ for ⲡⲛⲉⲩⲙⲁ. A reader said the full word; the sound row is built from n

The treebank is the Coptic Scriptorium annotation of a different digital text of Mark, Sahidica
(J. Warren Wells). The two texts differ in spelling (ⲙⲟⲓⲧ / ⲙⲟⲉⲓⲧ, ⲑ / ⲧϩ), in the abbreviation of
sacred names, and in word division. The sensor `edition-differs-from-treebank` compares letters
after normalizing those spelling habits and reports what remains.

Morphology is the treebank's UPOS and features. The Coptic Scriptorium part-of-speech tag (XPOS)
names the conjugation base or converter of each auxiliary (perfect ⲁ-, circumstantial ⲉ-,
conjunctive ⲛ-) and the stative of the verb; where it does, this module adds it as a Conj feature
(Conj=Perf, Conj=Circumstantial), so the page can say which form the auxiliary is.

Pronunciation
-------------
sahidic   Sahidic as it may have been read in the 4th and 5th centuries, approximate. Letter
          values follow the reconstruction tabulated by Peust (Egyptian Phonology, 1999): ⲃ a
          bilabial fricative β; ⲏ a close e and ⲉ an open ɛ (reduced to ə when unstressed); ⲟ an
          open ɔ and ⲱ a close o; ϫ the affricate tʃ and ϭ a palatalized kʲ; ⲑ ⲫ ⲭ the
          aspirates tʰ, pʰ, kʰ (in Sahidic ⲑ is also written ⲧϩ). The Greek letters for voiced sounds in Greek words, ⲅ ⲇ ⲍ, are
          read k t s, because Sahidic had no voiced stops and scribes interchange the letters.
          This text writes no supralinear stroke; a consonant that stands between two
          consonants or at a word's edge with no vowel beside it is read as syllabic, with ə
          before it, as the stroke marks in other manuscripts (ⲛϭⲓ ən-kʲi, ⲥⲟⲩⲧⲛ sou-tən).
          A doubled vowel (ⲟⲟ, ⲁⲁ) is read as the vowel followed by a glottal stop, one of the
          readings Layton gives. Stress falls on the last syllable with a full vowel (not ⲉ or
          ə), or failing that on the last ⲉ; Greek loanwords keep the Greek accent, from the table in
          data/cop_stress.yaml, which also lists the unstressed particles. Each word is
          phonemized alone
bohairic  The modern Coptic church pronunciation (the reformed, Greco-Bohairic pronunciation
          taught since the 1850s), applied to these Sahidic spellings. It is how a reader trained
          in today's liturgy would sound the letters. The church reads Bohairic, not Sahidic,
          so this is a convention applied to a text it was not made for, not a tradition of
          reading this text. Letter values follow the table published by the Coptic Orthodox
          Diocese of the Southern United States: ⲃ v, ⲅ gh (g before e and i), ⲇ dh (d in names),
          ⲏ ee, ⲑ th, ⲩ i (v after ⲁ and ⲉ), ϫ g (j before e and i), ϭ ch, ⲭ kh in Greek words.
          A syllabic consonant takes e before it. Stress is placed as in the first scheme
"""
from __future__ import annotations

import re
import struct
import unicodedata as ud
import zipfile
import zlib
from pathlib import Path

VERSION = "0.1"
SHOW_TRANSLIT = False
REPO = Path(__file__).resolve().parents[2]

XPOS_CONJ = {"APST": "Perf", "CCIRC": "Circumstantial", "CREL": "Relative", "CPRET": "Preterit",
             "ACONJ": "Conjunctive", "APREC": "Temporal", "FUT": "Fut", "VSTAT": "Stative",
             "CFOC": "Focalizing"}

LAYERS = {
    "lemma": {"src": "UD_Coptic-Scriptorium (CC BY 4.0), Mark 1, read through weft.coptic from the token's treebank reference"},
    "morph": {"src": f"UD_Coptic-Scriptorium UPOS and features; the Coptic Scriptorium XPOS added as Conj= where it names a conjugation base, converter or the stative (weft.coptic {VERSION})"},
}

# ---------------------------------------------------------------- treebank (UD CoNLL-U)
_UD: dict[str, dict[tuple[int, int], dict]] = {}


def ud_index(rel: str) -> dict[tuple[int, int], dict]:
    """(sentence number, word id) -> row, for the Mark 1 document of a UD Coptic file."""
    if rel in _UD:
        return _UD[rel]
    out: dict[tuple[int, int], dict] = {}
    s = None
    with (REPO / rel).open(encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            if line.startswith("# sent_id = "):
                m = re.search(r"Mark_01_s(\d+)$", line)
                s = int(m.group(1)) if m else None
                continue
            if s is None or not line or line.startswith("#"):
                continue
            c = line.split("\t")
            if "-" in c[0] or "." in c[0]:
                continue
            misc = dict(kv.split("=", 1) for kv in c[9].split("|") if "=" in kv) if len(c) > 9 else {}
            out[(s, int(c[0]))] = {"form": c[1], "lemma": c[2], "upos": c[3], "xpos": c[4],
                                   "feats": c[5], "mseg": misc.get("MSeg", "")}
    _UD[rel] = out
    return out


def ud_morph(r: dict) -> str:
    feats = {} if r["feats"] in ("_", "") else dict(f.split("=", 1) for f in r["feats"].split("|"))
    if r["xpos"] in XPOS_CONJ:
        feats["Conj"] = XPOS_CONJ[r["xpos"]]
    return r["upos"] + "".join(f"|{k}={v}" for k, v in sorted(feats.items()))


# spelling habits that differ between this edition and the treebank's text, not readings
SPELLING = [("ⲑ", "ⲧϩ"), ("ⲫ", "ⲡϩ"), ("ⲭ", "ⲕϩ"), ("ϯ", "ⲧⲓ"), ("ⲉⲓ", "ⲓ")]


def letters(s: str) -> str:
    s = "".join(ch for ch in ud.normalize("NFD", s.lower()) if not ud.combining(ch))
    for a, b in SPELLING:
        s = s.replace(a, b)
    return re.sub(r"[^Ⲁ-⳿Ϣ-ϯ]", "", s)


def token_fields(surface: str, et: dict, group: dict) -> tuple[dict, list[tuple[str, str]]]:
    fields: dict = {}
    fails: list[tuple[str, str]] = []
    rel = group.get("ud_file")
    m = re.fullmatch(r"(\d+):(\d+)(?:-(\d+))?", et.get("ud", ""))
    if not rel or not m:
        return fields, [("no-treebank-reference", surface)]
    s, a, b = int(m.group(1)), int(m.group(2)), int(m.group(3) or m.group(2))
    idx = ud_index(rel)
    rows = [idx.get((s, k)) for k in range(a, b + 1)]
    if not all(rows):
        return fields, [("treebank-word-missing", f"{surface} {et['ud']}")]
    fields["lemma"] = " + ".join(r["lemma"] for r in rows)
    fields["morph"] = " + ".join(ud_morph(r) for r in rows)
    fields["tb"] = f"Mark_01_s{s:04d}/{a}" + (f"-{b}" if b != a else "")
    # sensor: the treebank's words should spell this token. A compound the source writes apart
    # contributes only the part this token carries
    forms = [r["form"] for r in rows]
    if et.get("ud_part"):
        # the shared compound is the token's last treebank word; keep only the part written here
        part, whole = et["ud_part"], forms[-1]
        if part not in whole:
            fails.append(("treebank-part-not-found", f"{surface}: {part} in {whole}"))
        forms[-1] = part
        fields["prov"] = {"lemma": f"the treebank's one word {whole} is written as two words in this source; this token carries {part}"}
    said = et.get("n", surface)
    if letters(said) != letters("".join(forms)):
        fails.append(("edition-differs-from-treebank", f"{surface} vs {''.join(forms)}"))
    return fields, fails


# ---------------------------------------------------------------- verbatim check against the SWORD module
_SWORD: dict[str, str] = {}


def sword_text(rel: str, testament: str = "nt") -> str:
    """All verses of a SWORD zText module (a zip as CrossWire distributes it), markup removed,
    whitespace collapsed. A zText testament is a series of zlib blocks indexed by <t>.bzs."""
    key = f"{rel}:{testament}"
    if key not in _SWORD:
        with zipfile.ZipFile(REPO / rel) as z:
            bzs = next(n for n in z.namelist() if n.endswith(f"/{testament}.bzs"))
            idx, data = z.read(bzs), z.read(bzs[:-4] + ".bzz")
        parts = []
        for i in range(0, len(idx), 12):
            off, size, _ = struct.unpack("<III", idx[i:i + 12])
            parts.append(zlib.decompress(data[off:off + size]).decode("utf-8"))
        text = re.sub(r"</ab>", " ", "".join(parts))
        _SWORD[key] = " ".join(re.sub(r"<[^>]+>", "", text).split())
    return _SWORD[key]


def line_checks(text: str, etoks: list[dict], edition: dict) -> list[tuple[str, str]]:
    """Sensor: Weft's line must appear verbatim in the SWORD source (draft's verify_in reads only
    plain text files; a SWORD module is compressed)."""
    spec = edition.get("verify_sword") or {}
    if not spec:
        return []
    src = sword_text(spec["file"], spec.get("testament", "nt"))
    return [] if " ".join(text.split()) in src else [("edition-not-in-source", text[:40])]


# ---------------------------------------------------------------- sound
VOWELS = {"ⲁ": "a", "ⲉ": "ɛ", "ⲏ": "e", "ⲓ": "i", "ⲟ": "ɔ", "ⲱ": "o"}
SONORANTS = set("ⲙⲛⲣⲗⲃ")

# Sahidic consonants: (ipa, respelling); digraph letters are split into two units
SA_C = {"ⲃ": [("β", "v")], "ⲅ": [("k", "k")], "ⲇ": [("t", "t")], "ⲍ": [("s", "s")],
        "ⲑ": [("tʰ", "tʰ")], "ⲕ": [("k", "k")], "ⲗ": [("l", "l")], "ⲙ": [("m", "m")],
        "ⲛ": [("n", "n")], "ⲝ": [("k", "k"), ("s", "s")], "ⲡ": [("p", "p")], "ⲣ": [("r", "r")],
        "ⲥ": [("s", "s")], "ⲧ": [("t", "t")], "ⲫ": [("pʰ", "pʰ")],
        "ⲭ": [("kʰ", "kʰ")], "ⲯ": [("p", "p"), ("s", "s")], "ϣ": [("ʃ", "sh")],
        "ϥ": [("f", "f")], "ϧ": [("x", "kh")], "ϩ": [("h", "h")], "ϫ": [("tʃ", "ch")],
        "ϭ": [("kʲ", "ky")]}
SA_V = {"a": "a", "ɛ": "e", "e": "ay", "i": "i", "ɔ": "o", "o": "oh", "u": "oo", "y": "ü", "ə": "uh"}

GB_C = {"ⲃ": [("v", "v")], "ⲅ": [("ɣ", "gh")], "ⲇ": [("ð", "dh")], "ⲍ": [("z", "z")],
        "ⲑ": [("θ", "th")], "ⲕ": [("k", "k")], "ⲗ": [("l", "l")], "ⲙ": [("m", "m")],
        "ⲛ": [("n", "n")], "ⲝ": [("k", "k"), ("s", "s")], "ⲡ": [("p", "p")], "ⲣ": [("r", "r")],
        "ⲥ": [("s", "s")], "ⲧ": [("t", "t")], "ⲫ": [("f", "f")], "ⲭ": [("x", "kh")],
        "ⲯ": [("p", "p"), ("s", "s")], "ϣ": [("ʃ", "sh")], "ϥ": [("f", "f")], "ϧ": [("x", "kh")],
        "ϩ": [("h", "h")], "ϫ": [("g", "g")], "ϭ": [("tʃ", "ch")]}
GB_V = {"a": "a", "ɛ": "e", "e": "ee", "i": "i", "ɔ": "o", "o": "oh", "u": "oo", "y": "i", "ə": "e"}
GB_VIPA = {"ɛ": "e", "e": "iː", "ɔ": "o", "o": "oː", "y": "i", "ə": "e"}


def _units(word: str, scheme: str, names: set[str]) -> list[dict]:
    """Letters -> sound units {k: 'V'|'C', ipa, rsp, src}."""
    w = "".join(ch for ch in ud.normalize("NFC", word.lower()) if ch.isalpha() or ch in "ϯ")
    out: list[dict] = []
    i = 0
    gb = scheme == "bohairic"
    is_name = any(w.endswith(nm) for nm in names)

    def V(q, src):
        out.append({"k": "V", "q": q, "src": src})

    def C(ipa, rsp, src):
        out.append({"k": "C", "ipa": ipa, "rsp": rsp, "src": src})
    while i < len(w):
        ch, nx = w[i], w[i + 1] if i + 1 < len(w) else ""
        prev_v = bool(out) and out[-1]["k"] == "V"
        if ch == "ⲟ" and nx == "ⲩ":                       # ⲟⲩ: u, or w before a vowel
            after = w[i + 2] if i + 2 < len(w) else ""
            if not gb and prev_v and out[-1]["src"] == "ⲟ":
                C("ʔ", "'", ch)                            # ⲟⲟⲩ (ϩⲟⲟⲩ): doubled vowel, then w
            if after in VOWELS or prev_v:
                C("w", "w", "ⲟⲩ")
            else:
                V("u", "ⲟⲩ")
            i += 2
            continue
        if ch == "ⲉ" and nx == "ⲓ":                       # ⲉⲓ: i, or y beside a vowel
            after = w[i + 2] if i + 2 < len(w) else ""
            if prev_v or (after in VOWELS and after != "ⲓ"):
                C("j", "y", "ⲉⲓ")
            else:
                V("i", "ⲉⲓ")
            i += 2
            continue
        if ch == "ϯ":
            C("t", "t", "ϯ")
            V("i", "ϯ")
            i += 1
            continue
        if ch in VOWELS:
            q = VOWELS[ch]
            if ch == "ⲓ" and (prev_v or (not out and nx in VOWELS)):
                C("j", "y", ch)
            elif out and out[-1]["k"] == "V" and out[-1]["src"] == ch and ch != "ⲓ":
                if not gb:
                    C("ʔ", "'", ch)                        # doubled vowel: vowel + glottal stop
            else:
                V(q, ch)
            i += 1
            continue
        if ch == "ⲩ":
            if prev_v:
                if gb and out[-1]["src"] in ("ⲁ", "ⲉ"):
                    C("v", "v", ch)
                else:
                    C("w", "w", ch)
            else:
                V("y", ch)
            i += 1
            continue
        table = GB_C if gb else SA_C
        if ch in table:
            units = table[ch]
            if gb:
                nxv = nx in ("ⲉ", "ⲓ", "ⲏ") or nx == "ϯ"
                if ch == "ⲅ":
                    units = [("ŋ", "ng")] if nx in ("ⲅ", "ⲕ", "ⲭ") else [("g", "g")] if nxv else units
                elif ch == "ϫ" and nxv:
                    units = [("dʒ", "j")]
                elif ch == "ⲃ" and (not nx or (nx not in VOWELS and nx not in "ⲟⲩ")):
                    units = [("b", "b")]
                elif ch == "ⲇ" and is_name:
                    units = [("d", "d")]
            elif ch == "ⲅ" and nx in ("ⲅ", "ⲕ", "ⲭ"):
                units = [("ŋ", "ng")]
            for ipa, rsp in units:
                C(ipa, rsp, ch)
            i += 1
            continue
        i += 1                                             # anything else: not a letter we read
    # a sonorant with no vowel on either side is syllabic: ə before it (the supralinear stroke)
    res: list[dict] = []
    for k, u in enumerate(out):
        if u["k"] == "C" and u["src"] in SONORANTS:
            pv = k > 0 and (out[k - 1]["k"] == "V" or out[k - 1]["ipa"] == "ʔ")
            nv = k + 1 < len(out) and out[k + 1]["k"] == "V"
            if not pv and not nv:
                res.append({"k": "V", "q": "ə", "src": "stroke"})
        res.append(u)
    if not any(u["k"] == "V" for u in res):               # no vowel at all: a schwa before the last consonant
        res.insert(max(len(res) - 1, 0), {"k": "V", "q": "ə", "src": "stroke"})
    return res


def _syllables(units: list[dict]) -> list[list[dict]]:
    nuc = [k for k, u in enumerate(units) if u["k"] == "V"]
    bounds = [0]
    for a, b in zip(nuc, nuc[1:]):
        cl = b - a - 1                                    # consonants between two nuclei
        cut = b if cl == 0 else b - 1                     # one consonant goes to the next syllable
        if units[a]["src"] == "stroke":                   # a syllabic consonant keeps its own ə
            cut = max(cut, min(a + 2, b))
        bounds.append(cut)
    return [units[s:e] for s, e in zip(bounds, bounds[1:] + [len(units)])]


def _stress(sylls: list[list[dict]], word: str, table: dict) -> int | None:
    """Index of the stressed syllable, or None (an unstressed particle)."""
    bare = "".join(ch for ch in ud.normalize("NFD", word.lower()) if not ud.combining(ch))
    if bare in table.get("unstressed", ()):
        return None
    table = table.get("stress", {})
    best = max((k for k in table if bare.endswith(k)), key=len, default=None)
    if best is not None:
        return max(len(sylls) - table[best], 0)
    def nucleus(s):
        return next(u for u in s if u["k"] == "V")
    full = [k for k, s in enumerate(sylls) if nucleus(s)["q"] not in ("ɛ", "ə")]
    if full:
        return full[-1]
    written = [k for k, s in enumerate(sylls) if nucleus(s)["q"] == "ɛ"]   # ⲉ before a stroke vowel
    return written[-1] if written else len(sylls) - 1


def phonemize(word: str, scheme: str = "sahidic", quantities=None, **_) -> dict:
    table = quantities if isinstance(quantities, dict) else {}
    names = set((quantities or {}).get("names", [])) if isinstance(quantities, dict) else set()
    units = _units(word, scheme, names)
    sylls = _syllables(units)
    st = _stress(sylls, word, table)
    gb = scheme == "bohairic"
    ipa_s, rsp_s = [], []
    for k, s in enumerate(sylls):
        ipa, rsp = "", ""
        for u in s:
            if u["k"] == "V":
                q = u["q"]
                if not gb and q == "ɛ" and k != st:
                    q = "ə"                               # unstressed ⲉ is reduced
                ipa += GB_VIPA.get(q, q) if gb else q
                rsp += (GB_V if gb else SA_V)[q]
            else:
                ipa += u["ipa"]
                rsp += u["rsp"]
        ipa_s.append(("ˈ" if k == st and len(sylls) > 1 else "") + ipa)
        rsp_s.append(rsp.upper() if k == st and len(sylls) > 1 else rsp)
    return {"ipa": ".".join(ipa_s), "respell": "-".join(rsp_s), "syllables": len(sylls)}


KEY = {
    "sahidic": [
        ("", "Sahidic Coptic as it may have been read in the 4th and 5th centuries. This is an approximate reconstruction. Coptic writes its vowels, so the outline is better known than for older Egyptian, but the exact sound of several letters is debated. Letter values follow Peust (1999). This digital text omits the stroke that manuscripts write over syllabic consonants, so Weft supplies the syllabic vowel by rule. Each word is said on its own, with no linking between words."),
        ("CAPS", "the stressed syllable: the last one with a full vowel in Egyptian words; the Greek accent in Greek loanwords. Particles such as ϫⲉ, ⲇⲉ and ⲛϭⲓ are left unstressed"),
        ("uh", "ə, a short neutral vowel: the syllabic consonant that manuscripts mark with a stroke (ⲛ̄ is said ən), and unstressed ⲉ"),
        ("e", "ⲉ in a stressed syllable, as in bed"),
        ("ay", "ⲏ, a closer e, as in French été"),
        ("o", "ⲟ, an open o, as in British hot"),
        ("oh", "ⲱ, a closer o, as in French eau"),
        ("oo", "ⲟⲩ, as in food; before a vowel it is w"),
        ("i", "ⲓ and ⲉⲓ, as in machine; beside another vowel they are y"),
        ("ü", "ⲩ standing alone in a Greek word, as in German über; it may already have been said i"),
        ("'", "a glottal stop, the catch in uh-oh: one reading of a doubled vowel (ϩⲟⲟⲩ, ⲟⲩⲁⲁⲃ)"),
        ("v", "ⲃ, a b made without closing the lips, between b and v (β)"),
        ("ch", "ϫ, as in church"),
        ("ky", "ϭ, a k with the tongue raised toward the palate, close to the start of cute"),
        ("sh", "ϣ"),
        ("tʰ, pʰ, kʰ", "ⲑ ⲫ ⲭ: t, p, k with a puff of breath after them, as in English top; Sahidic scribes also write ⲑ as ⲧϩ"),
        ("k, t, s", "ⲅ ⲇ ⲍ in Greek words: Sahidic had no voiced stops, and scribes interchange these letters with ⲕ ⲧ ⲥ"),
        ("ng", "ⲅ before ⲅ or ⲕ, as in finger"),
    ],
    "bohairic": [
        ("", "The modern Coptic church pronunciation, the reformed or Greco-Bohairic pronunciation taught since the 1850s, applied to these Sahidic spellings. It shows how a reader trained in today's liturgy would sound the letters. The church reads Bohairic, not Sahidic, so this is a convention applied to a text it was not made for. It makes no claim about ancient speech. Stress is placed as in the first scheme."),
        ("CAPS", "the stressed syllable, placed as in the first scheme"),
        ("ee", "ⲏ, as in see"),
        ("e", "ⲉ, as in bed; also the vowel read before a syllabic consonant (ⲛ̄ is said en)"),
        ("v", "ⲃ before a vowel (b elsewhere), and ⲩ after ⲁ or ⲉ"),
        ("gh", "ⲅ before a, o: a g said without closing the throat (ɣ); g before e and i; ng before ⲅ or ⲕ"),
        ("dh", "ⲇ, as th in this; d in names"),
        ("th", "ⲑ, as in thin"),
        ("kh", "ⲭ in Greek words, as in Scottish loch"),
        ("g, j", "ϫ: g, and j as in jam before e and i"),
        ("ch", "ϭ, as in church"),
        ("i", "ⲓ, and ⲩ standing alone"),
        ("oo", "ⲟⲩ, as in food"),
        ("oh", "ⲱ, a long o"),
    ],
}
SCHEME_LABELS = {
    "sahidic": "Sahidic, 4th-5th century (approximate reconstruction)",
    "bohairic": "Modern Coptic church pronunciation, applied to Sahidic spelling",
}


if __name__ == "__main__":
    import sys
    import yaml
    q = yaml.safe_load((REPO / "pipeline/weft/data/cop_stress.yaml").read_text())
    for w in sys.argv[1:]:
        for s in KEY:
            print(w, s, phonemize(w, s, q))
