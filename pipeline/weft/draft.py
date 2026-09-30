"""weft draft: manifest + sources -> gen/<book>.yaml (source, lemma, morph, sound layers).

The generated file is pure data. The run's telemetry (counts, failure classes, predicted vs
actual) goes to gen/<book>.run.yaml so the data diff stays clean between runs.
"""
from __future__ import annotations

import hashlib
import re
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path

import yaml

from . import __version__, akkadian, chinese, greek, hebrew, japanese, latin, norse, oldenglish, persian, runic, sanskrit, tamil, treebank

TEI = "{http://www.tei-c.org/ns/1.0}"
INDECLINABLE = set("dcgriebz")   # b: GLAUx coordinating conjunction
PHON = {"grc": greek, "lat": latin, "non": norse, "ang": oldenglish, "hbo": hebrew, "lzh": chinese, "runic": runic, "ja": japanese, "san": sanskrit,
        "akk": akkadian, "fa": persian, "ta": tamil}
NORMALIZE = {"heyne-to-macron": oldenglish.heyne_to_macron}
LEAD = re.compile(r"^([(\[“]+|[-–—]\u00a0)")
TRAIL = re.compile(r"((?:[,.·;:!?)\]”\u0387\u037e]|\u00a0[-–—])+)$")


def load_manifest(work_dir: Path) -> dict:
    return yaml.safe_load((work_dir / "manifest.yaml").read_text())


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def edition_lines(xml_path: Path, book: int, first: int, last: int) -> dict[int, str]:
    root = ET.parse(xml_path).getroot()
    for div in root.iter(f"{TEI}div"):
        if (div.get("subtype") or "").lower() == "book" and div.get("n") == str(book):
            out = {}
            for l in div.iter(f"{TEI}l"):
                n = int(l.get("n"))
                if first <= n <= last:
                    out[n] = " ".join("".join(l.itertext()).split())
            return out
    raise SystemExit(f"book {book} not found in {xml_path}")


def stanza_lines(path: Path, stanzas: list[int]) -> dict[int, list[str]]:
    """Plain-text poems laid out as a number line ("76.") followed by the stanza's lines."""
    out: dict[int, list[str]] = {}
    cur = None
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if re.fullmatch(r"\d+\.", line):
            cur = int(line[:-1])
            out[cur] = []
        elif cur is not None and line:
            out[cur].append(" ".join(line.split()))
        elif not line:
            cur = cur if cur is None or not out.get(cur) else None
    return {k: v for k, v in out.items() if k in stanzas}


def verse_lines(path: Path, start_after: str, first: int, last: int) -> dict[int, str]:
    """A plain-text poem after a heading, one verse per line, margin line numbers optional.
    Lines are counted from the heading; wide gaps (the caesura) are kept."""
    lines = path.read_text(encoding="utf-8").splitlines()
    i = next(k for k, l in enumerate(lines) if l.strip() == start_after)
    out: dict[int, str] = {}
    n = 0
    for raw in lines[i + 1:]:
        if not raw.strip():
            continue
        n += 1
        out[n] = re.sub(r"^\s*\d+\s+", "", raw.rstrip()).strip()
        if n >= last:
            break
    return {k: v for k, v in out.items() if first <= k <= last}


def run(work_dir: Path, book: int | None = None, first: int | None = None, last: int | None = None) -> dict:
    m = load_manifest(work_dir)
    pilot = m.get("pilot", {})
    ed_fmt = m["edition"].get("format", "tei")
    if ed_fmt in ("stanza-text", "weft-edition"):
        book = first = last = None
    elif ed_fmt == "conllu" and m["edition"].get("sent_prefix"):
        book = None
        first = first or pilot["first"]
        last = last or pilot["last"]
    elif ed_fmt in ("conllu", "morphgnt", "oshb"):
        book = pilot["chapter"]
        first = first or pilot["first"]
        last = last or pilot["last"]
    elif ed_fmt == "verse-text":
        book = None
        first = first or pilot["first"]
        last = last or pilot["last"]
    else:
        book = book or pilot["book"]
        first = first or pilot["first"]
        last = last or pilot["last"]
    repo = work_dir.parents[1]
    failures: Counter[str] = Counter()
    samples: dict[str, list[str]] = {}

    def fail(cls: str, sample: str):
        failures[cls] += 1
        samples.setdefault(cls, [])
        if len(samples[cls]) < 5:
            samples[cls].append(sample)

    # provenance: sources must exist locally and match the hashes the manifest pinned
    for spec in [m["edition"]] + ([m["treebank"]] if m.get("treebank") else []):
        if not spec.get("file"):
            continue
        p = work_dir / spec["file"]
        if not p.exists():
            raise SystemExit(f"weft: {spec['file']} is missing. Sources are not in git; "
                             f"run `weft acquire {m['work']}` to review licenses and download them.")
        if spec.get("sha256") and sha256(p) != spec["sha256"]:
            fail("source-hash-drift", spec["file"])

    quant_path = repo / m["quantities"] if m.get("quantities") else None
    quantities = yaml.safe_load(quant_path.read_text()) if quant_path else {}

    # units: (book-or-stanza, line number, text)
    if ed_fmt == "weft-edition":
        # Weft's own edition file: grouped units (inscriptions), tokens given explicitly
        edition = yaml.safe_load((work_dir / m["edition"]["file"]).read_text())
        glist = edition.get("inscriptions") or edition.get("sections")
        groups = {str(g["id"]): g for g in glist}
        # a line is either plain text (tokenized normally) or explicit tokens (runic inscriptions)
        # token lines join with the edition's joiner: a space for runes, nothing for Japanese
        joiner = edition.get("joiner", " ")

        def token_line(toks: list[dict]) -> str:
            # glue: no space after this word (Devanagari writes a final consonant with the next
            # word's vowel); p: a danda, set off by a space as the source prints it
            out = ""
            for k, t in enumerate(toks):
                out += t["t"] + (" " + t["p"] if t.get("p") else "")
                if k + 1 < len(toks) and not t.get("glue"):
                    out += joiner
            return out
        units = [(str(g["id"]), i, ln if isinstance(ln, str) else token_line(ln["tokens"]))
                 for g in glist for i, ln in enumerate(g["lines"], start=1)]
        # Weft's edition must reproduce its cited source verbatim, line by line; a section may
        # name its own source (verify_in), otherwise the edition-wide one applies
        cache: dict[str, str] = {}
        for gid, i, text in units:
            vpath = groups[gid].get("verify_in") or edition.get("verify_in")
            if not vpath:
                continue
            if vpath not in cache:
                raw_src = (work_dir / vpath).read_text(encoding="utf-8")
                if edition.get("verify_strip"):       # verse labels printed inside the source lines
                    raw_src = re.sub(edition["verify_strip"], "", raw_src)
                cache[vpath] = " ".join(raw_src.split())
            if " ".join(text.split()) not in cache[vpath]:
                fail("edition-not-in-source", f"{gid}.{i}")
    elif ed_fmt == "stanza-text":
        st = stanza_lines(work_dir / m["edition"]["file"], pilot["stanzas"])
        units = [(k, i, t) for k in pilot["stanzas"] for i, t in enumerate(st.get(k, []), start=1)]
        for k in pilot["stanzas"]:
            if k not in st:
                fail("stanza-missing-in-edition", str(k))
    elif ed_fmt == "oshb":
        lexicon = treebank.load_strong_lexicon(work_dir / m["edition"]["lexicon"])
        verses = treebank.load_oshb(work_dir / m["edition"]["file"], m["edition"]["osis_book"], book, first, last, lexicon)
        units = [(book, n, " ".join(r["word"] + (r.get("punct") or "") for r in verses[n])) for n in range(first, last + 1) if n in verses]
        for n in range(first, last + 1):
            if n not in verses:
                fail("verse-missing-in-edition", f"{book}.{n}")
    elif ed_fmt == "morphgnt":
        verses = treebank.load_morphgnt(work_dir / m["edition"]["file"], book, first, last)
        units = [(book, n, " ".join(r["text"] for r in verses[n])) for n in range(first, last + 1) if n in verses]
        for n in range(first, last + 1):
            if n not in verses:
                fail("verse-missing-in-edition", f"{book}.{n}")
    elif ed_fmt == "conllu" and m["edition"].get("sent_prefix"):
        sents = treebank.load_conllu_prefix(work_dir / m["edition"]["file"], m["edition"]["sent_prefix"])
        units = [(None, n, sents[n]["text"]) for n in range(first, last + 1) if n in sents]
        for n in range(first, last + 1):
            if n not in sents:
                fail("line-missing-in-edition", str(n))
    elif ed_fmt == "conllu":
        sents = treebank.load_conllu_text(work_dir / m["edition"]["file"], m["edition"]["text_id"], first, last)
        units = [(book, n, sents[n]["text"]) for n in range(first, last + 1) if n in sents]
        for n in range(first, last + 1):
            if n not in sents:
                fail("sentence-missing-in-edition", f"{book}.{n}")
    elif ed_fmt == "verse-text":
        ed = verse_lines(work_dir / m["edition"]["file"], m["edition"]["start_after"], first, last)
        units = [(None, n, ed[n]) for n in range(first, last + 1) if n in ed]
    else:
        ed = edition_lines(work_dir / m["edition"]["file"], book, first, last)
        units = []
        for n in range(first, last + 1):
            if n not in ed:
                fail("line-missing-in-edition", f"{book}.{n}")
            else:
                units.append((book, n, ed[n]))
    lang = m["language"]
    phon = PHON[lang]
    tb_fmt = m["treebank"].get("format", "agdt-cite") if m.get("treebank") else "none"
    tb_path = work_dir / m["treebank"]["file"] if m.get("treebank", {}) and m["treebank"].get("file") else None
    if tb_fmt == "agdt-cite":
        tb = treebank.load_lines(tb_path, book, first, last)
    elif tb_fmt == "ldt-stream":
        stream, cursor = treebank.load_stream(tb_path, book, first, last), 0
    elif tb_fmt == "glaux":
        stream, cursor = treebank.load_glaux(tb_path, [str(x) for x in m["treebank"]["subdocs"]]), 0
    elif tb_fmt == "conllu-citation":
        cit = m["treebank"]["citation"]
        stream, cursor = treebank.load_conllu_citation([tb_path], cit["text"], cit["chapter"]), 0
        need = sum(t.get("w", 1) for g in glist for ln in g["lines"] if not isinstance(ln, str) for t in ln["tokens"])
        if need != len(stream):
            fail("treebank-word-count", f"edition carries {need} treebank words, treebank has {len(stream)}")
    prefix = m["prefix"]
    lines = []
    ntok = 0
    norm = NORMALIZE.get(m["edition"].get("normalize") or "", None)
    extra = {}
    if m.get("stress_prefixes"):
        extra["prefixes"] = yaml.safe_load((repo / m["stress_prefixes"]).read_text()) or {}

    if m.get("readings"):
        # Chinese: one reading table for exactly the characters the passage uses
        chars = {c for _, _, t in units for c in t if not c.isspace()}
        rd = m["readings"]
        quantities = chinese.load_readings(work_dir / rd["table"], work_dir / rd["variants"], chars)

    def lid(book, n):
        return f"{prefix}.{book}.{n}" if book is not None else f"{prefix}.{n}"

    for book, n, text in units:
        # a wide gap inside a verse line is the caesura: remember where the second half starts
        halves = re.split(r"\s{3,}", text.strip())
        caesura_at = len(halves[0].split()) if len(halves) == 2 else None
        printed_text = text
        text = " ".join(text.split())
        token_edition = ed_fmt == "weft-edition" and not isinstance(groups[book]["lines"][n - 1], str)
        raw = [] if (ed_fmt in ("conllu", "morphgnt", "oshb") or token_edition) else text.split()
        # a dash standing alone (a parenthesis, or the dash after a refrain) is punctuation, not a
        # word: it joins the word before it, or the word after it at the start of a line
        merged: list[str] = []
        for k, t in enumerate(raw):
            if re.fullmatch(r"[-–—]+[,.;:!?]*", t):
                if merged:
                    merged[-1] += "\u00a0" + t
                elif k + 1 < len(raw):
                    raw[k + 1] = t + "\u00a0" + raw[k + 1]
                continue
            merged.append(t)
        raw = merged
        surfaces, puncts, leads = [], [], []
        if token_edition:
            g = groups[book]
            etoks = g["lines"][n - 1]["tokens"]
            surfaces = [t["t"] for t in etoks]
            puncts, leads = [t.get("p") for t in etoks], [None] * len(surfaces)
        if ed_fmt == "oshb":
            surfaces = [r["word"] for r in verses[n]]
            puncts = [r.get("punct") for r in verses[n]]
            leads = [None] * len(surfaces)
            conllu_pairs = [{k: r[k] for k in ("lemma", "postag", "ref", "lexgloss", "strong", "prefixes", "silluq") if r.get(k)}
                            for r in verses[n]]
        if ed_fmt == "morphgnt":
            surfaces = [r["word"] for r in verses[n]]
            puncts = [r["text"][len(r["word"]):] or None for r in verses[n]]
            leads = [None] * len(surfaces)
            conllu_pairs = [{"lemma": r["lemma"], "postag": r["postag"], "ref": r["ref"]} for r in verses[n]]
        if ed_fmt == "conllu":
            surfaces, puncts, conllu_pairs = treebank.conllu_tokens(sents[n]["rows"], sents[n]["sent_id"])
            leads = [None] * len(surfaces)
        for t in raw:
            ml = LEAD.search(t)
            leads.append(ml.group(1) if ml else None)
            t = LEAD.sub("", t)
            mt = TRAIL.search(t)
            puncts.append(mt.group(1) if mt else None)
            surfaces.append(TRAIL.sub("", t))
        if ed_fmt in ("conllu", "morphgnt", "oshb"):
            pairs, fl = conllu_pairs, []
        elif tb_fmt == "agdt-cite":
            pairs, fl = treebank.reconcile(surfaces, tb.get(f"{book}.{n}", []))
        elif tb_fmt in ("ldt-stream", "glaux"):
            pairs, fl, cursor = treebank.reconcile_stream(surfaces, stream, cursor)
        elif tb_fmt == "conllu-citation":
            pairs, fl = [], []
            for et in etoks:
                k = et.get("w", 1)
                rows, cursor = stream[cursor:cursor + k], cursor + k
                if len(rows) < k:
                    pairs.append(None); continue
                feats = lambda r: r["upos"] + ("" if r["feats"] in ("_", "") else "|" + r["feats"])
                pairs.append({"lemma": " + ".join(r["lemma"] for r in rows),
                              "postag": " + ".join(feats(r) for r in rows),
                              "ref": ", ".join(r["ref"] for r in rows)})
                # sensor: the treebank's word should be recognizably the printed one; sandhi changes
                # word ends, so compare the first three letters of the unaccented forms
                sn = lambda x: sanskrit.strip_accents(x).lstrip("'’").replace("ṃ", "m").replace("ḷ", "ḍ")
                said, tbw = sn(et["n"]), sn("".join(r["unsandhied"] for r in rows))
                k3 = max(1, min(3, len(said) - 1, len(tbw) - 1))   # word ends change in sandhi
                fused = k > 1 and (said[:1] == tbw[:1] or (said[:1] in "aāiīuūeo" and tbw[:1] in "aāiīuūeo"))
                if said[:k3] != tbw[:k3] and not fused and not (said.startswith("gne") and tbw.startswith("agne")):
                    fl.append(f"treebank-form-mismatch: {et['n']} vs {tbw}")
        else:
            pairs, fl = [None] * len(surfaces), []
        for f in fl:
            fail(f.split(":", 1)[0], f"{book}.{n} {f.split(':', 1)[1]}")
        toks = []
        for i, (s, p, lead, w) in enumerate(zip(surfaces, puncts, leads, pairs), start=1):
            tok: dict = {"id": f"{lid(book, n)}.{i}", "surface": s}
            if norm:
                ns = norm(s)
                # a length correction from the table shows in the spelling too, not only the sound
                if lang == "ang" and quantities and ns.lower() in quantities:
                    fixed = quantities[ns.lower()]
                    ns = fixed[0].upper() + fixed[1:] if ns[:1].isupper() else fixed
                if ns != s:
                    tok["printed"] = s
                    tok["surface"] = s = ns
            if caesura_at is not None and i == caesura_at + 1:
                tok["caesura"] = True
            if token_edition and etoks[i - 1].get("caesura"):
                tok["caesura"] = True
            if token_edition:
                et = etoks[i - 1]
                if g.get("alphabet"):
                    runes, missing = runic.to_runes(s, g["alphabet"])
                    tok["script"] = runes
                    if missing:
                        fail("rune-missing", f"{book}.{n} {s} {missing}")
                if et.get("n"):
                    tok["norm"] = et["n"]
                if et.get("m"):
                    tok["metre_form"] = et["m"]
                # language hook: extra token fields (a generated script row, a reading) from the module
                if hasattr(phon, "token_fields"):
                    fields, tfails = phon.token_fields(s, et, g)
                    tok.update(fields)
                    for cls, sample in tfails:
                        fail(cls, f"{book}.{n} {sample}")
            if lead:
                tok["lead"] = lead
            if p:
                tok["punct"] = p
            if w:
                tok["lemma"] = w["lemma"]
                tok["morph"] = w["postag"]
                tok["tb"] = w.get("ref") or f"{w['sentence']}/{w['word']}"
                if w.get("enclitic"):
                    tok["enclitic"] = w["enclitic"]
                for k in ("prefixes", "lexgloss", "strong"):
                    if w.get(k):
                        tok[k] = w[k]
                if w.get("tbgloss"):
                    tok["gloss"] = w["tbgloss"]
                # indeclinables (adverb, conjunction, particle, preposition, interjection) rightly
                # carry no inflection; an empty tag on anything that declines or conjugates is a gap
                if tb_fmt in ("agdt-cite", "ldt-stream", "glaux") and w["postag"][1:].strip("-") == "" and w["postag"][0] not in INDECLINABLE:
                    fail("morph-empty-declinable", f"{book}.{n} {s} ({w['postag']})")
            elif tb_fmt != "none":
                fail("no-treebank-word", f"{book}.{n} {s}")
            snd = {}
            if lang == "grc":
                _, qhit = greek.apply_quantity(greek.normalize_elision(s).rstrip("’"), quantities)
            say = tok.get("norm", s)          # runic: sound comes from the normalized form
            if ed_fmt == "weft-edition" and groups[book].get("dialect"):
                extra["dialect"] = groups[book]["dialect"]
            for k_s, scheme in enumerate(m["schemes"]):
                r = phon.phonemize(say, scheme, quantities, **extra,
                                   **({"silluq": True} if w and w.get("silluq") else {}))
                snd[scheme] = {"ipa": r["ipa"], "respell": r["respell"]}
                if k_s == 0:
                    first_syllables = r.get("syllables", 0)
            if lang == "ja":
                tok["morae"] = first_syllables
            tok["sound"] = snd
            if lang == "grc" and qhit:
                tok["prov"] = {"sound": f"weft.greek {greek.VERSION} + quantity table"}
            if lang == "lzh":
                tr = phon.phonemize(s, "tang", quantities)
                tok["tone"] = tr.get("tone")
                tok["final"] = tr.get("final")
                if tr.get("via"):
                    tok["prov"] = {"sound": f"Tang reading from the glyph variant {tr['via']}"}
                    fail("reading-from-variant", f"{n} {s}->{tr['via']}")
                if tr["respell"] == "?":
                    fail("reading-missing", f"{n} {s}")
            if lang == "lat" and not r["known"]:
                # stress depends on vowel length: a word missing from the table is a guess
                tok["prov"] = {"sound": f"weft.latin {latin.VERSION}, quantity unknown"}
                fail("quantity-unknown", f"{book}.{n} {s}")
            toks.append(tok)
            ntok += 1
        line_rec = {
            "id": lid(book, n),
            "cite": f"{m['urn']}.{m['edition']['id']}:" + (f"{book}.{n}" if book is not None else f"{n}"),
            **({"stanza": book} if ed_fmt == "stanza-text" else {}),
            **({"stanza": book, "stanza_title": groups[book]["title"]} if ed_fmt == "weft-edition" else {}),
            "text": text,
            "tokens": toks,
        }
        if lang == "ja" and toks:
            # Japanese verse counts morae; the first scheme is the as-first-spoken reading
            line_rec["metre"] = f"{sum(t.get('morae', 0) for t in toks)} morae"
        if token_edition and toks and hasattr(phon, "line_metre"):
            # language hook: metre computed from the line's tokens, with its own failure classes
            m_str, mfails = phon.line_metre(etoks, edition)
            if m_str:
                line_rec["metre"] = m_str
            for cls, sample in mfails:
                fail(cls, f"{book}.{n} {sample}")
        if token_edition and toks and hasattr(phon, "line_checks"):
            # language hook: sensors that compare the line against its source (spelling, marks)
            for cls, sample in phon.line_checks(text, etoks, edition):
                fail(cls, f"{book}.{n} {sample}")
        if lang == "san" and toks:
            ns = [et["n"] for et in etoks]
            # sensor 1: the hand-entered transliteration must spell the printed Devanagari
            deva_iast, marks = sanskrit.devanagari(text)
            said = sanskrit.strip_accents("".join(ns)).replace("'", "")
            if deva_iast.replace("'", "") != said:
                fail("translit-mismatch", f"{book}.{n} {deva_iast} vs {said}")
            # sensor 2: raised pitch written as acutes must match the manuscript's accent strokes
            decoded = sanskrit.decode_marks(marks)
            written = sanskrit.accents_from_words(ns)
            if len(decoded) != len(written):
                fail("syllable-count-mismatch", f"{book}.{n} {len(decoded)} vs {len(written)}")
            else:
                sy_word = [w for w in ns for _ in range(sanskrit.phonemize(w)["syllables"])]
                for k, (d, wr) in enumerate(zip(decoded, written)):
                    if (d == "U") != (wr == "U"):
                        fail("accent-mismatch", f"{book}.{n} syllable {k + 1} ({sy_word[k]}): strokes say {d}, written {wr or '-'}")
            starts = [k for k, et in enumerate(etoks) if et.get("caesura")]
            pattern, sizes = sanskrit.metre([et.get("m") or et["n"] for et in etoks], starts)
            line_rec["metre"] = pattern
            want = (edition.get("metre") or {}).get("pada")
            for k, size in enumerate(sizes):
                if want and size != want:
                    # the Rigveda often counts a syllable its written form lost (ī́ḍyo read ī́ḍiyo)
                    fail("pada-syllables-short" if size < want else "pada-syllables-long", f"{book}.{n} pāda {k + 1}: {size}")
        if lang == "lzh" and toks and not token_edition:
            # Tang level/oblique tones and rhyme: regulated verse only (Li Bai); a Weft edition of
            # Chinese prose-verse sets its own metre or none
            # regulated verse: level (○) or oblique (●) tone per syllable, and the rhyme of the last
            pattern = "".join("○" if t.get("tone") == "level" else "●" for t in toks)
            line_rec["metre"] = f"{pattern} · rhyme -{toks[-1].get('final', '?')}"
        if norm:
            line_rec["text"] = " ".join(((t.get("lead") or "") + t["surface"] + (t.get("punct") or "")) for t in toks)
            line_rec["printed"] = printed_text
        lines.append(line_rec)

    gen = {
        "work": m["work"],
        "pipeline": {"weft": __version__, phon.__name__.rsplit(".", 1)[-1]: phon.VERSION},
        "layers": {
            "text": {"src": m["edition"]["id"]},
            **({"gloss": {"src": m["treebank"]["id"] + " (MISC Gloss)"}, "metre": {"src": f"weft.chinese {chinese.VERSION}: Tang tones"}}
               if lang == "lzh" and m.get("treebank") else {}),
            **({"lemma": {"src": m["treebank"]["id"] + (" (homograph numbers stripped)" if tb_fmt == "ldt-stream" else "")},
                "morph": {"src": m["treebank"]["id"]}} if tb_fmt != "none" else
               {"lemma": {"src": "none: no treebank; hand annotation in curated/"},
                "morph": {"src": "none: no treebank; hand annotation in curated/"}}),
            "sound": {"src": f"weft.{phon.__name__.rsplit('.', 1)[-1]} {phon.VERSION}" + (" + quantity table" if lang == "lat" else "")
                      + (", from the normalized form" if ed_fmt == "weft-edition" else "")},
            **({"script": {"src": f"weft.runic {runic.VERSION}: generated from the transliteration"}} if ed_fmt == "weft-edition" and lang == "runic" else {}),
            **({"translit": {"src": "Weft edition: hand-entered accented IAST, checked against the Devanagari and its accent strokes"},
                "metre": {"src": f"weft.sanskrit {sanskrit.VERSION}: syllable weight across the line"}} if lang == "san" else {}),
        },
        "lines": lines,
    }
    if hasattr(phon, "LAYERS"):
        gen["layers"].update(phon.LAYERS)
    stem = ("inscriptions" if "inscriptions" in (yaml.safe_load((work_dir / m["edition"]["file"]).read_text()) or {}) else "sections") if ed_fmt == "weft-edition" else "lines" if book is None and ed_fmt != "stanza-text" else {"stanza-text": "stanzas", "verse-text": "lines"}.get(ed_fmt) or (
        f"chapter{book:02d}" if ed_fmt in ("conllu", "morphgnt", "oshb") else f"book{book:02d}")
    (work_dir / "gen").mkdir(exist_ok=True)
    out = work_dir / "gen" / f"{stem}.yaml"
    header = "# Generated by `weft draft`. Do not edit. Corrections go in curated/.\n"
    out.write_text(header + yaml.dump(gen, allow_unicode=True, sort_keys=False, width=200,
                                      default_flow_style=None))
    report = {
        "run": {"weft": __version__, **({"sections": [u[0] for u in units if u[1] == 1]} if ed_fmt == "weft-edition"
                                          else {"stanzas": pilot["stanzas"]} if ed_fmt == "stanza-text"
                                          else {"lines": f"{first}-{last}"} if ed_fmt == "verse-text"
                                          else {"book": book, "lines": f"{first}-{last}"})},
        "counts": {"lines": len(lines), "tokens": ntok},
        "failures": dict(failures),
        "samples": samples,
        "failure_rate": {k: round(v / max(ntok, 1), 3) for k, v in failures.items()},
        "shift_left": [k for k, v in failures.items() if v / max(ntok, 1) > 0.15],
        "predicted_gaps": m.get("predicted_gaps", []),
    }
    (work_dir / "gen" / f"{stem}.run.yaml").write_text(
        yaml.dump(report, allow_unicode=True, sort_keys=False, width=200))
    return report
