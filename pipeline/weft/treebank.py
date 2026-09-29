"""AGDT treebank access and edition-to-treebank token reconciliation."""
from __future__ import annotations

import unicodedata as ud
import xml.etree.ElementTree as ET
from pathlib import Path

from .greek import PUNCT, normalize_elision

POS = {"n": "noun", "v": "verb", "t": "participle", "a": "adjective", "d": "adverb",
       "l": "article", "g": "particle", "c": "conjunction", "r": "preposition",
       "p": "pronoun", "m": "numeral", "i": "interjection", "e": "exclamation", "x": "irregular"}
FIELDS = [
    None,
    {"1": "1st person", "2": "2nd person", "3": "3rd person"},
    {"s": "singular", "p": "plural", "d": "dual"},
    {"p": "present", "i": "imperfect", "r": "perfect", "l": "pluperfect",
     "t": "future perfect", "f": "future", "a": "aorist"},
    {"i": "indicative", "s": "subjunctive", "o": "optative", "n": "infinitive",
     "m": "imperative", "p": "participle"},
    {"a": "active", "p": "passive", "m": "middle", "e": "middle-passive"},
    {"m": "masculine", "f": "feminine", "n": "neuter"},
    {"n": "nominative", "g": "genitive", "d": "dative", "a": "accusative",
     "v": "vocative", "l": "locative"},
    {"c": "comparative", "s": "superlative"},
]


UD_POS = {"NOUN": "noun", "PROPN": "proper noun", "VERB": "verb", "AUX": "auxiliary verb",
          "ADJ": "adjective", "ADV": "adverb", "ADP": "preposition", "PRON": "pronoun", "DET": "article",
          "NUM": "numeral", "CCONJ": "conjunction", "SCONJ": "subordinating conjunction",
          "PART": "particle", "INTJ": "interjection"}
UD_ORDER = ["Stem", "Conj", "Person", "Number", "Tense", "Mood", "VerbForm", "Voice", "Gender", "Case",
            "State", "Degree", "Reflex", "PronType", "PartType", "Polarity"]
UD_VAL = {"Sing": "singular", "Plur": "plural", "Dual": "dual", "Pres": "present", "Past": "past",
          "Pret": "past", "Ind": "indicative", "Sub": "subjunctive", "Imp": "imperative",
          "Inf": "infinitive", "Part": "participle", "Mid": "middle", "Pass": "passive", "Act": "active",
          "Masc": "masculine", "Fem": "feminine", "Neut": "neuter", "Nom": "nominative", "Acc": "accusative",
          "Gen": "genitive", "Dat": "dative", "Voc": "vocative", "Cmp": "comparative", "Sup": "superlative",
          "Neg": "negative", "Rel": "relative", "Dem": "demonstrative", "Prs": "personal", "Int": "interrogative",
          "Aor": "aorist", "Imperf": "imperfect", "Perf": "perfect", "Pqp": "pluperfect", "Fut": "future",
          "Opt": "optative",
          # Biblical Hebrew (OSHB)
          "Qal": "qal stem", "Niphal": "niphal stem", "Piel": "piel stem", "Pual": "pual stem",
          "Hiphil": "hiphil stem", "Hophal": "hophal stem", "Hithpael": "hithpael stem",
          "Qatal": "perfect (qatal)", "Weqatal": "sequential perfect (weqatal)", "Yiqtol": "imperfect (yiqtol)",
          "Wayyiqtol": "narrative past (wayyiqtol)", "Cohortative": "cohortative", "Jussive": "jussive",
          "PartAct": "active participle", "PartPass": "passive participle", "InfAbs": "infinitive absolute",
          "InfCons": "infinitive construct", "Abs": "absolute state", "Cons": "construct state",
          "Det": "determined", "Both": "masculine or feminine", "Com": "common gender",
          "Obj": "direct-object marker", "Art": "definite article", "Aff": "affirmation", "Exh": "exhortation",
          "Suffix": "suffixed pronoun"}


def _decode_ud(tag: str) -> str:
    """'VERB|Mood=Ind|Number=Sing|Person=3|Tense=Pres' -> 'verb, 3rd person, singular, present, indicative'."""
    pos, *feats = tag.split("|")
    fd = dict(f.split("=", 1) for f in feats if "=" in f)
    parts = [UD_POS.get(pos, pos.lower())]
    for k in UD_ORDER:
        v = fd.get(k)
        if not v or v == "Fin":
            continue
        if k == "Person":
            parts.append({"1": "1st person", "2": "2nd person", "3": "3rd person"}.get(v, v))
        elif k == "Reflex" and v == "Yes":
            parts.append("reflexive")
        else:
            parts.append(UD_VAL.get(v, v.lower()))
    return ", ".join(parts)


def decode_morph(tag: str) -> str:
    """AGDT 9-position postag, or a UD 'UPOS|Feat=Val' string -> readable English."""
    if tag and ("|" in tag or tag.isupper()):
        return _decode_ud(tag)
    if not tag or len(tag) < 9:
        return ""
    parts = [POS.get(tag[0], tag[0])]
    for i, table in enumerate(FIELDS[1:], start=1):
        v = tag[i]
        if v != "-" and v in table:
            parts.append(table[v])
    # reorder for readability: pos, person, number, tense, mood, voice, gender, case, degree
    return ", ".join(parts)


def load_lines(tb_path: Path, book: int, first: int, last: int) -> dict[str, list[dict]]:
    """Return {'1.1': [word, ...]} for the requested lines, punctuation dropped."""
    want = {f"{book}.{n}" for n in range(first, last + 1)}
    out: dict[str, list[dict]] = {k: [] for k in sorted(want, key=lambda s: int(s.split('.')[1]))}
    started = False
    for _, el in ET.iterparse(tb_path):
        if el.tag != "sentence":
            continue
        hit = False
        for w in el.findall("word"):
            cite = (w.get("cite") or "").rsplit(":", 1)[-1]
            if cite in want and not (w.get("postag") or "").startswith("u"):
                out[cite].append({
                    "sentence": el.get("id"), "word": w.get("id"), "form": w.get("form"),
                    "lemma": w.get("lemma"), "postag": w.get("postag"),
                    "relation": w.get("relation"), "head": w.get("head"),
                })
                hit = True
        if hit:
            started = True
        elif started:
            break
        el.clear()
    return out


def comparable(form: str) -> str:
    s = normalize_elision(form)
    for p in PUNCT:
        s = s.replace(p, "")
    return ud.normalize("NFC", s).lower()


def reconcile(edition_tokens: list[str], tb_words: list[dict]) -> tuple[list[dict | None], list[str]]:
    """Pair edition tokens with treebank words in order. Returns pairs and failure classes."""
    failures: list[str] = []
    if len(edition_tokens) != len(tb_words):
        failures.append(f"count-mismatch:{len(edition_tokens)}vs{len(tb_words)}")
        return [None] * len(edition_tokens), failures
    pairs: list[dict | None] = []
    for t, w in zip(edition_tokens, tb_words):
        if comparable(t) != comparable(w["form"]):
            failures.append(f"form-mismatch:{t}|{w['form']}")
        pairs.append(w)
    return pairs, failures


# ---------------------------------------------------------------- stream treebanks (LDT)
# The Latin Dependency Treebank carries no per-word citation, only a sentence-level
# `subdoc` range like "1.2-1.4". We read the sentences that overlap the passage as one word
# stream and walk it against the edition, handling enclitics the treebank splits off.
ENCLITIC_LEMMAS = {"que", "ve", "-que", "-ve"}


def _range(subdoc: str) -> tuple[tuple[int, int], tuple[int, int]] | None:
    try:
        a, b = subdoc.split("-") if "-" in subdoc else (subdoc, subdoc)
        (ab, al), (bb, bl) = (tuple(int(x) for x in a.split(".")), tuple(int(x) for x in b.split(".")))
        return (ab, al), (bb, bl)
    except ValueError:
        return None


def load_stream(tb_path: Path, book: int, first: int, last: int) -> list[dict]:
    words: list[dict] = []
    started = False
    for _, el in ET.iterparse(tb_path):
        if el.tag != "sentence":
            continue
        r = _range(el.get("subdoc") or "")
        hit = r is not None and r[0] <= (book, last) and r[1] >= (book, first)
        if hit:
            started = True
            for w in el.findall("word"):
                if (w.get("postag") or "").startswith("u"):
                    continue
                words.append({"sentence": el.get("id"), "word": w.get("id"), "form": w.get("form"),
                              "lemma": w.get("lemma"), "postag": w.get("postag"),
                              "relation": w.get("relation"), "head": w.get("head")})
        elif started:
            break
        el.clear()
    return words


def _bare(lemma: str) -> str:
    import re
    return re.sub(r"\d+$", "", lemma or "")


def _norm(form: str) -> str:
    return ud.normalize("NFC", (form or "").lower().lstrip("-"))


def reconcile_stream(tokens: list[str], stream: list[dict], cursor: int) -> tuple[list[dict | None], list[str], int]:
    """Match edition tokens against the treebank stream from `cursor`. Returns pairs, failures, new cursor.

    Handles: exact match; a host plus an enclitic the treebank split off, in either order
    (primaque = que + prima; nec = c + ne). The host keeps lemma and morph; the enclitic is
    recorded beside it."""
    pairs: list[dict | None] = []
    fails: list[str] = []
    for tok in tokens:
        t = _norm(comparable(tok))
        w0 = stream[cursor] if cursor < len(stream) else None
        w1 = stream[cursor + 1] if cursor + 1 < len(stream) else None
        if w0 and _norm(w0["form"]) == t:
            pairs.append(dict(w0, lemma=_bare(w0["lemma"]), ref=f"{w0['sentence']}/{w0['word']}"))
            cursor += 1
            continue
        if w0 and w1:
            a, b = _norm(w0["form"]), _norm(w1["form"])
            for x, y in ((w0, w1), (w1, w0)):
                if _norm(x["form"]) + _norm(y["form"]) == t:
                    # host = the part that is not a -que/-ve enclitic; `nec` (c + ne) keeps ne
                    enc, host = (x, y) if _bare(x["lemma"]) in ENCLITIC_LEMMAS else (y, x)
                    if _bare(host["lemma"]) in ENCLITIC_LEMMAS:
                        host, enc = x, y
                    pairs.append(dict(host, lemma=_bare(host["lemma"]),
                                      ref=f"{x['sentence']}/" + "+".join(sorted((x["word"], y["word"]), key=int)),
                                      enclitic={"form": "-" + _norm(enc["form"]) if _norm(enc["form"]) != "c" else "-c(e)",
                                                "lemma": _bare(enc["lemma"]), "morph": enc["postag"]}))
                    cursor += 2
                    break
            else:
                fails.append(f"form-mismatch:{tok}|{w0['form']}")
                pairs.append(None)
                cursor += 1
            continue
        fails.append(f"stream-exhausted:{tok}")
        pairs.append(None)
    return pairs, fails, cursor


# ---------------------------------------------------------------- CoNLL-U (UD) treebanks
def load_conllu_text(path: Path, text_id: str, first: int, last: int) -> dict[int, dict]:
    """Sentences of one text in a UD file whose sent_id looks like '<text_id>,<n>.<global>'.
    Returns {n: {"sent_id", "text", "rows": [ {id, form, lemma, upos, feats} ]}} for first..last."""
    import re
    out: dict[int, dict] = {}
    cur: dict | None = None
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            if line.startswith("# sent_id = "):
                sid = line[len("# sent_id = "):].strip()
                m = re.match(re.escape(text_id) + r",(\d+)\.", sid)
                cur = None
                if m and first <= int(m.group(1)) <= last:
                    cur = {"sent_id": sid, "text": "", "rows": []}
                    out[int(m.group(1))] = cur
            elif cur is not None and line.startswith("# text = "):
                cur["text"] = line[len("# text = "):]
            elif cur is not None and line and not line.startswith("#"):
                c = line.split("\t")
                if "-" in c[0] or "." in c[0]:
                    continue                       # multiword ranges and empty nodes
                cur["rows"].append({"id": c[0], "form": c[1], "lemma": c[2], "upos": c[3], "feats": c[5],
                                    "misc": c[9] if len(c) > 9 else "_"})
    return out


def conllu_tokens(rows: list[dict], sent_id: str) -> tuple[list[str], list[str | None], list[dict]]:
    """Surfaces, trailing punctuation and treebank pairs for one sentence. Punctuation rows attach
    to the word before them."""
    surfaces: list[str] = []
    puncts: list[str | None] = []
    pairs: list[dict] = []
    for r in rows:
        if r["upos"] == "PUNCT" and surfaces:
            puncts[-1] = (puncts[-1] or "") + r["form"]
            continue
        feats = "" if r["feats"] in ("_", "") else "|" + r["feats"]
        surfaces.append(r["form"])
        puncts.append(None)
        pair = {"lemma": r["lemma"], "postag": r["upos"] + feats, "ref": f"{sent_id}/{r['id']}"}
        # some treebanks (Kyoto Classical Chinese) carry an English gloss in MISC
        for kv in (r.get("misc") or "_").split("|"):
            if kv.startswith("Gloss="):
                pair["tbgloss"] = "-".join(kv[len("Gloss="):].split())
        pairs.append(pair)
    return surfaces, puncts, pairs


# ---------------------------------------------------------------- MorphGNT (Greek New Testament)
MG_POS = {"N-": "NOUN", "V-": "VERB", "RA": "DET", "C-": "CCONJ", "P-": "ADP", "D-": "ADV",
          "A-": "ADJ", "RP": "PRON", "RR": "PRON", "RD": "PRON", "RI": "PRON", "X-": "PART", "I-": "INTJ"}
MG_PRONTYPE = {"RP": "Prs", "RR": "Rel", "RD": "Dem", "RI": "Int"}
MG_TENSE = {"P": "Pres", "I": "Imperf", "F": "Fut", "A": "Aor", "X": "Perf", "Y": "Pqp"}
MG_VOICE = {"A": "Act", "M": "Mid", "P": "Pass"}
MG_MOOD = {"I": ("Mood", "Ind"), "D": ("Mood", "Imp"), "S": ("Mood", "Sub"), "O": ("Mood", "Opt"),
           "N": ("VerbForm", "Inf"), "P": ("VerbForm", "Part")}
MG_CASE = {"N": "Nom", "G": "Gen", "D": "Dat", "A": "Acc", "V": "Voc"}
MG_NUM = {"S": "Sing", "P": "Plur"}
MG_GEN = {"M": "Masc", "F": "Fem", "N": "Neut"}
MG_DEG = {"C": "Cmp", "S": "Sup"}


def morphgnt_to_ud(pos: str, parse: str) -> str:
    """MorphGNT 'V- 3IAI-S--' -> 'VERB|Mood=Ind|Number=Sing|Person=3|Tense=Imperf|Voice=Act'."""
    feats: dict[str, str] = {}
    p = parse.ljust(8, "-")
    if p[0] in "123":
        feats["Person"] = p[0]
    if p[1] in MG_TENSE:
        feats["Tense"] = MG_TENSE[p[1]]
    if p[2] in MG_VOICE:
        feats["Voice"] = MG_VOICE[p[2]]
    if p[3] in MG_MOOD:
        k, v = MG_MOOD[p[3]]
        feats[k] = v
    if p[4] in MG_CASE:
        feats["Case"] = MG_CASE[p[4]]
    if p[5] in MG_NUM:
        feats["Number"] = MG_NUM[p[5]]
    if p[6] in MG_GEN:
        feats["Gender"] = MG_GEN[p[6]]
    if p[7] in MG_DEG:
        feats["Degree"] = MG_DEG[p[7]]
    if pos in MG_PRONTYPE:
        feats["PronType"] = MG_PRONTYPE[pos]
    upos = MG_POS.get(pos, "X")
    return upos + "".join(f"|{k}={v}" for k, v in sorted(feats.items()))


def load_morphgnt(path: Path, chapter: int, first: int, last: int) -> dict[int, list[dict]]:
    """{verse: [ {text, word, lemma, postag, ref} ]} for one chapter's verses first..last."""
    out: dict[int, list[dict]] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        c = line.split(" ")
        if len(c) < 7:
            continue
        bcv = c[0]
        ch, vs = int(bcv[2:4]), int(bcv[4:6])
        if ch != chapter or not first <= vs <= last:
            continue
        rows = out.setdefault(vs, [])
        rows.append({"text": c[3], "word": c[4], "lemma": c[6], "postag": morphgnt_to_ud(c[1], c[2]),
                     "ref": f"{bcv}/{len(rows) + 1}"})
    return out


# ---------------------------------------------------------------- OSHB (Open Scriptures Hebrew Bible)
OSHB_PREFIX = {"b": ("בְּ", "in"), "c": ("וְ", "and"), "d": ("הַ", "the"), "k": ("כְּ", "like"),
               "l": ("לְ", "to"), "m": ("מִ", "from"), "s": ("שֶׁ", "which"), "i": ("הֲ", "is it?")}
OSHB_STEM = {"q": "Qal", "N": "Niphal", "p": "Piel", "P": "Pual", "h": "Hiphil", "H": "Hophal",
             "t": "Hithpael", "o": "Polel", "O": "Polal", "r": "Hithpolel", "m": "Poel", "M": "Poal",
             "Q": "QalPassive", "l": "Pilpel"}
OSHB_CONJ = {"p": "Qatal", "q": "Weqatal", "i": "Yiqtol", "w": "Wayyiqtol", "h": "Cohortative",
             "j": "Jussive", "v": "Imperative", "r": "PartAct", "s": "PartPass", "a": "InfAbs", "c": "InfCons"}
OSHB_GEN = {"m": "Masc", "f": "Fem", "b": "Both", "c": "Com"}
OSHB_NUM = {"s": "Sing", "p": "Plur", "d": "Dual"}
OSHB_STATE = {"a": "Abs", "c": "Cons", "d": "Det"}
OSHB_PART = {"o": ("PART", "Obj"), "d": ("DET", "Art"), "n": ("PART", "Neg"), "i": ("PART", "Int"),
             "r": ("PRON", "Rel"), "m": ("PRON", "Dem"), "a": ("PART", "Aff"), "e": ("PART", "Exh"),
             "j": ("INTJ", None)}


def oshb_to_ud(seg: str) -> str:
    """One OSHB morph segment ('Vqw3ms', 'Ncfsa', 'To', 'R') -> a UD-style string."""
    pos, rest = seg[:1], seg[1:]
    f: dict[str, str] = {}
    if pos == "V":
        f["Stem"] = OSHB_STEM.get(rest[:1], rest[:1])
        conj = rest[1:2]
        f["Conj"] = OSHB_CONJ.get(conj, conj)
        tail = rest[2:]
        if conj in "rs":                      # participle: gender, number, state
            g, n, st = (tail + "---")[:3]
        elif conj in "ac":                    # infinitive
            g = n = st = "-"
        else:                                 # finite: person, gender, number
            if tail[:1] in "123":
                f["Person"] = tail[0]
            g, n, st = (tail[1:] + "---")[0], (tail[1:] + "---")[1], "-"
        if g in OSHB_GEN: f["Gender"] = OSHB_GEN[g]
        if n in OSHB_NUM: f["Number"] = OSHB_NUM[n]
        if st in OSHB_STATE: f["State"] = OSHB_STATE[st]
        upos = "VERB"
    elif pos in "NA":
        kind = rest[:1]
        upos = "PROPN" if (pos == "N" and kind == "p") else ("NUM" if pos == "A" and kind in "co" else
                                                            "NOUN" if pos == "N" else "ADJ")
        g, n, st = (rest[1:] + "---")[:3]
        if g in OSHB_GEN: f["Gender"] = OSHB_GEN[g]
        if n in OSHB_NUM: f["Number"] = OSHB_NUM[n]
        if st in OSHB_STATE: f["State"] = OSHB_STATE[st]
    elif pos == "P":
        upos = "PRON"
        f["PronType"] = {"d": "Dem", "f": "Ind", "i": "Int", "p": "Prs", "r": "Rel"}.get(rest[:1], rest[:1])
        tail = rest[1:]
        if tail[:1] in "123":
            f["Person"] = tail[0]; tail = tail[1:]
        if tail[:1] in OSHB_GEN: f["Gender"] = OSHB_GEN[tail[0]]
        if tail[1:2] in OSHB_NUM: f["Number"] = OSHB_NUM[tail[1]]
    elif pos == "T":
        upos, pt = OSHB_PART.get(rest[:1], ("PART", None))
        if pt: f["PartType"] = pt
    elif pos == "S":
        upos = "PRON"
        f["PronType"] = "Suffix"
        tail = rest[1:]
        if tail[:1] in "123": f["Person"] = tail[0]; tail = tail[1:]
        if tail[:1] in OSHB_GEN: f["Gender"] = OSHB_GEN[tail[0]]
        if tail[1:2] in OSHB_NUM: f["Number"] = OSHB_NUM[tail[1]]
    else:
        upos = {"C": "CCONJ", "D": "ADV", "R": "ADP"}.get(pos, "X")
    return upos + "".join(f"|{k}={v}" for k, v in sorted(f.items()))


def load_strong_lexicon(path: Path) -> dict[str, dict]:
    """{ 'H7225': {'lemma': 'רֵאשִׁית', 'xlit': 'rêʼshîyth', 'def': 'first'} }"""
    ns = "{http://openscriptures.github.com/morphhb/namespace}"
    out: dict[str, dict] = {}
    for _, el in ET.iterparse(path):
        if el.tag != ns + "entry":
            continue
        w = el.find(ns + "w")
        d = el.find(f"{ns}meaning/{ns}def")
        out[el.get("id")] = {"lemma": (w.text or "") if w is not None else "",
                             "xlit": w.get("xlit") if w is not None else "",
                             "def": (d.text or "").strip() if d is not None else ""}
        el.clear()
    return out


def load_oshb(path: Path, book: str, chapter: int, first: int, last: int, lexicon: dict) -> dict[int, list[dict]]:
    """{verse: [ {word, punct, lemma, lexgloss, postag, prefixes, ref, silluq} ]} from OSHB OSIS XML."""
    import re
    ns = "{http://www.bibletechnologies.net/2003/OSIS/namespace}"
    root = ET.parse(path).getroot()
    out: dict[int, list[dict]] = {}
    for verse in root.iter(ns + "verse"):
        _, ch, vs = verse.get("osisID").split(".")
        if int(ch) != chapter or not first <= int(vs) <= last:
            continue
        rows: list[dict] = []
        for el in verse:
            tag = el.tag.replace(ns, "")
            if tag == "seg" and rows:
                rows[-1]["punct"] = (rows[-1].get("punct") or "") + (el.text or "")
                if el.get("type") == "x-sof-pasuq":
                    rows[-1]["silluq"] = True
                continue
            if tag != "w":
                continue
            lem_parts = el.get("lemma", "").split("/")
            morph = el.get("morph", "")
            morph_parts = morph[1:].split("/") if morph[:1] in "HA" else morph.split("/")
            text_parts = (el.text or "").split("/")
            prefixes, main_i = [], None
            for k, lp in enumerate(lem_parts):
                if re.match(r"^\d", lp.strip()):
                    main_i = k
                    break
                pf = OSHB_PREFIX.get(lp.strip(), (lp, lp))
                prefixes.append({"form": text_parts[k] if k < len(text_parts) else pf[0],
                                 "gloss": pf[1], "morph": oshb_to_ud(morph_parts[k]) if k < len(morph_parts) else ""})
            num = re.match(r"(\d+)", lem_parts[main_i]).group(1) if main_i is not None else None
            lex = lexicon.get(f"H{num}", {}) if num else {}
            main_morph = morph_parts[main_i] if main_i is not None and main_i < len(morph_parts) else ""
            rows.append({"word": (el.text or "").replace("/", ""),
                         "lemma": lex.get("lemma") or (f"H{num}" if num else ""),
                         "lexgloss": lex.get("def") or None,
                         "strong": f"H{num}" if num else None,
                         "postag": oshb_to_ud(main_morph) if main_morph else "X",
                         "prefixes": prefixes,
                         "ref": f"{verse.get('osisID')}/{el.get('id')}"})
        out[int(vs)] = rows
    return out


def load_conllu_prefix(path: Path, prefix: str) -> dict[int, dict]:
    """Sentences whose sent_id starts with `prefix`, numbered 1.. in file order (e.g. the lines of
    one poem in the Kyoto Classical Chinese treebank: KR4h0169_233_par1_1-5, _6-10, ...)."""
    out: dict[int, dict] = {}
    cur: dict | None = None
    n = 0
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            if line.startswith("# sent_id = "):
                sid = line[len("# sent_id = "):].strip()
                cur = None
                if sid.startswith(prefix):
                    n += 1
                    cur = {"sent_id": sid, "text": "", "rows": []}
                    out[n] = cur
            elif cur is not None and line.startswith("# text = "):
                cur["text"] = line[len("# text = "):]
            elif cur is not None and line and not line.startswith("#"):
                c = line.split("\t")
                if "-" in c[0] or "." in c[0]:
                    continue
                cur["rows"].append({"id": c[0], "form": c[1], "lemma": c[2], "upos": c[3], "feats": c[5],
                                    "misc": c[9] if len(c) > 9 else "_"})
    return out
