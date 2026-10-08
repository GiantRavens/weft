"""Tools for building a work: pin a source by revision, fetch and size an image, scaffold a folder,
expand a compact overlay spec. Each is a `weft` subcommand; docs/building.md is the playbook.

pin       `weft pin <work> <url>`: fetch a source, save it under sources/, hash it, append the entry to
          the manifest's sources_extra (or set the edition's file with --edition). A Wikisource page URL
          is resolved to its current revision and pinned by oldid.
image     `weft image <work> "File:Name.jpg"`: fetch a Commons image and its metadata, write the page
          (760 px) and row (220 px) JPEGs under art/works/, append the credits record.
scaffold  `weft scaffold <work> --lang <code>`: the folder, a manifest skeleton with the language's
          schemes, an edition skeleton.
overlay   `weft overlay <work> <spec.yaml> --out <file>`: the compact spec (see docs/building.md) to a
          curated overlay, every surface checked against gen/.
"""
from __future__ import annotations

import hashlib
import json
import re
import urllib.parse
import urllib.request
from collections import Counter, defaultdict
from pathlib import Path

import yaml

UA = "Weft/0.1 (https://weftlibrary.org; a living interlinear library)"


def fetch(url: str, timeout: int = 60) -> bytes:
    """One retry after a server-side error: heimskringla's API answers 500 now and then and 200 a moment later."""
    import time
    import urllib.error
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    for attempt in (1, 2):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            if e.code < 500 or attempt == 2:
                raise SystemExit(f"weft: {url} answered HTTP {e.code}" + (" twice" if attempt == 2 else ""))
            time.sleep(3)
    raise AssertionError("unreachable")


def fetch_json(url: str) -> dict:
    return json.loads(fetch(url).decode("utf-8"))


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


# ---------------------------------------------------------------- pin
HK = re.compile(r"^https?://(?:www\.)?heimskringla\.no/(?:wiki/(?P<title>[^?#]+)|index\.php\?(?P<q>.*))$")


def resolve_heimskringla(url: str) -> tuple[str, str, int | None, str | None, str | None]:
    """heimskringla.no refuses action=raw; its API serves the wikitext of a revision as JSON.
    -> (api url for the wikitext, display name, revid, title, page url by oldid)."""
    m = HK.match(url)
    if not m:
        return url, url, None, None, None
    if m.group("q"):
        q = urllib.parse.parse_qs(m.group("q")); title = q.get("title", [""])[0]; rev = int(q["oldid"][0]) if "oldid" in q else None
    else:
        title, rev = urllib.parse.unquote(m.group("title")), None
    if rev is None:
        pages = fetch_json("https://heimskringla.no/api.php?action=query&prop=revisions&rvprop=ids&format=json&titles=" + urllib.parse.quote(title))["query"]["pages"]
        page = next(iter(pages.values()))
        if "revisions" not in page:
            raise SystemExit(f"weft pin: no such page on heimskringla.no: {title}")
        rev = page["revisions"][0]["revid"]
    api = f"https://heimskringla.no/api.php?action=parse&oldid={rev}&prop=wikitext&format=json"
    page_url = f"https://heimskringla.no/index.php?title={urllib.parse.quote(title)}&oldid={rev}"
    return api, f"{title}, heimskringla.no, revision {rev}", rev, title, page_url


def wikitext_to_stanza_text(data: bytes) -> bytes:
    """A heimskringla poem page (API parse JSON, or bare wikitext) -> the stanza-text layout draft reads:
    a speaker line where the page has one, the stanza number on its own line, the lines, a blank line."""
    raw = data.decode("utf-8")
    if raw.lstrip().startswith('{"'):          # the API envelope; bare wikitext may itself start with a table ({|)
        raw = json.loads(raw)["parse"]["wikitext"]["*"]
    i = re.search(r"^::\s*1\.\s*$", raw, re.M)
    if not i:
        raise SystemExit("weft pin: no '::1.' stanza marker in the wikitext; is this a poem page?")
    pre = raw[:i.start()].rstrip().splitlines()
    last = pre[-1].strip() if pre else ""
    head = [last] if last.endswith(":") and len(last.split()) <= 6 else []     # a speaker line, not a prose paragraph ending in "kvað:"
    body = raw[i.start():]
    for stop in ("{{DEFAULTSORT", "[[Kategori:", "[[Category:"):
        if stop in body:
            body = body[:body.index(stop)]
    out = []
    for l in head + body.splitlines():
        l = l.strip()
        if l.startswith("::"):
            l = l[2:].strip()
        l = re.sub(r"<[^>]+>", "", l.replace("&nbsp;", "").replace("'''", "").replace("''", "")).strip()
        out.append(l)
    txt = re.sub(r"\n{3,}", "\n\n", "\n".join(out)).strip() + "\n"
    return txt.encode("utf-8")


CONVERTERS = {"heimskringla-stanza-text": wikitext_to_stanza_text}

WS = re.compile(r"^https?://(?P<lang>[a-z\-]+)\.wikisource\.org/(?:wiki/(?P<title>[^?#]+)|w/index\.php\?(?P<q>.*))$")


def resolve_wikisource(url: str) -> tuple[str, str, int | None, str | None]:
    """A Wikisource page URL -> (raw url pinned by oldid, display name, revid, title). A URL already
    carrying oldid is kept. Anything else is returned unchanged."""
    m = WS.match(url)
    if not m:
        return url, url, None, None
    lang = m.group("lang")
    if m.group("q"):
        q = urllib.parse.parse_qs(m.group("q"))
        if "oldid" in q:
            rev = int(q["oldid"][0])
            return f"https://{lang}.wikisource.org/w/index.php?oldid={rev}&action=raw", f"{lang}.wikisource revision {rev}", rev, q.get("title", [None])[0]
        title = q.get("title", [""])[0]
    else:
        title = urllib.parse.unquote(m.group("title"))
    api = f"https://{lang}.wikisource.org/w/api.php?action=query&prop=revisions&rvprop=ids&format=json&titles=" + urllib.parse.quote(title)
    pages = fetch_json(api)["query"]["pages"]
    page = next(iter(pages.values()))
    if "revisions" not in page:
        raise SystemExit(f"weft pin: no such page on {lang}.wikisource: {title}")
    rev = page["revisions"][0]["revid"]
    return f"https://{lang}.wikisource.org/w/index.php?oldid={rev}&action=raw", f"{title}, {lang}.wikisource, revision {rev}", rev, title


def pin(repo: Path, work: str, url: str, sid: str | None = None, name: str | None = None, license_: str | None = None,
        license_url: str | None = None, edition: bool = False, as_: str | None = None) -> dict:
    from .paths import work_dir
    wd = work_dir(repo, work)
    mp = wd / "manifest.yaml"
    if not mp.exists():
        raise SystemExit(f"weft pin: {mp} does not exist; scaffold the work first")
    convert = page_url = None
    if HK.match(url):
        raw_url, display, rev, title, page_url = resolve_heimskringla(url)
        if as_ == "stanza-text":
            convert = "heimskringla-stanza-text"
        elif as_:
            raise SystemExit(f"weft pin: unknown conversion {as_!r}")
    else:
        raw_url, display, rev, title = resolve_wikisource(url)
    data = fetch(raw_url)
    if convert:
        data = CONVERTERS[convert](data)
    stem = sid or (re.sub(r"[^a-z0-9]+", "-", (title or Path(urllib.parse.urlparse(url).path).stem).lower()).strip("-")[:40] or "source")
    if rev and not sid:
        stem = f"{stem}-{rev}"
    ext = ".txt" if rev or convert or not Path(urllib.parse.urlparse(raw_url).path).suffix else Path(urllib.parse.urlparse(raw_url).path).suffix
    if page_url and not convert:
        ext = ".json"      # the API's wikitext envelope, as fetched
    (wd / "sources").mkdir(exist_ok=True)
    out = wd / "sources" / f"{stem}{ext}"
    out.write_bytes(data)
    rec = {"id": sid or stem, "name": name or display, "file": f"sources/{out.name}", "url": raw_url, "sha256": sha256(data),
           "license": license_ or ("poem public domain; normalized text credited to heimskringla.no" if page_url else
                                   "text public domain; Wikisource transcription CC BY-SA 4.0" if rev else "TODO: the source's licence"),
           **({"license_url": license_url} if license_url else {"license_url": "http://heimskringla.no/wiki/Heimskringla.no:Copyright"} if page_url else {}),
           **({"page": page_url} if page_url else {}),
           **({"convert": convert, "note": "the file is the page's wikitext converted by weft to the stanza-text layout (speaker lines and stanza numbers kept, markup dropped); weft acquire reproduces it"} if convert else {})}
    m = yaml.safe_load(mp.read_text())
    if edition:
        m.setdefault("edition", {}).update({"file": rec["file"], "url": rec["url"], "sha256": rec["sha256"],
                                            **{k: rec[k] for k in ("page", "convert", "note", "license_url") if k in rec}})
        if sid: m["edition"]["id"] = sid
        if name or str(m["edition"].get("name", "TODO")).startswith("TODO"): m["edition"]["name"] = rec["name"]
        if str(m["edition"].get("license", "TODO")).startswith("TODO"): m["edition"]["license"] = rec["license"]
        if convert == "heimskringla-stanza-text": m["edition"]["format"] = "stanza-text"
    else:
        m.setdefault("sources_extra", [])
        m["sources_extra"] = [s for s in m["sources_extra"] if s.get("id") != rec["id"]] + [rec]
    mp.write_text(yaml.dump(m, allow_unicode=True, sort_keys=False, width=130))
    return {"saved": str(out.relative_to(repo)), "bytes": len(data), "sha256": rec["sha256"], "revision": rev, "manifest": "edition" if edition else "sources_extra"}


# ---------------------------------------------------------------- image
def strip_tags(s: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", s or "")).strip()


def image(repo: Path, work: str, commons_file: str, caption: str | None = None, alt: str | None = None) -> dict:
    try:
        from PIL import Image
    except ImportError:
        raise SystemExit("weft image needs Pillow: uv pip install -e '.[images]'")
    import io
    title = commons_file if commons_file.startswith("File:") else "File:" + commons_file
    api = ("https://commons.wikimedia.org/w/api.php?action=query&prop=imageinfo&iiprop=url|size|extmetadata&iiurlwidth=1920&format=json&titles="
           + urllib.parse.quote(title))
    page = next(iter(fetch_json(api)["query"]["pages"].values()))
    if "imageinfo" not in page:
        raise SystemExit(f"weft image: not found on Commons: {title}")
    ii = page["imageinfo"][0]; em = ii.get("extmetadata", {})
    lic = strip_tags(em.get("LicenseShortName", {}).get("value", ""))
    if not (lic.lower().startswith("public domain") or lic.lower().startswith("cc0") or lic.lower().startswith("pd") or "cc by" in lic.lower()):
        raise SystemExit(f"weft image: licence is {lic!r}; only public domain, CC0 and CC BY / BY-SA images are used")
    url = ii.get("thumburl") if ii.get("width", 0) > 1920 else ii["url"]
    data = fetch(url, timeout=180)
    im = Image.open(io.BytesIO(data)).convert("RGB")
    (repo / "art" / "works" / "thumb").mkdir(parents=True, exist_ok=True)
    outs = {}
    for size, path in ((760, repo / "art" / "works" / f"{work}.jpg"), (220, repo / "art" / "works" / "thumb" / f"{work}.jpg")):
        r = im.copy(); r.thumbnail((size, size), Image.Resampling.LANCZOS)
        r.save(path, "JPEG", quality=84, optimize=True, progressive=True); outs[size] = f"{r.size[0]}x{r.size[1]}"
    desc = strip_tags(em.get("ImageDescription", {}).get("value", ""))[:200]
    rec = {"image": f"art/works/{work}.jpg", "thumb": f"art/works/thumb/{work}.jpg",
           "caption": caption or f"TODO: {desc}", "alt": alt or "TODO: describe the image for a reader who cannot see it",
           "credit": strip_tags(em.get("Artist", {}).get("value", "")) or "Unknown", "date": (strip_tags(em.get("DateTimeOriginal", {}).get("value", "")) or strip_tags(em.get("DateTime", {}).get("value", "")))[:40] or "unknown",
           "license": lic, "source": "https://commons.wikimedia.org/wiki/" + urllib.parse.quote(title.replace(" ", "_"), safe=":()'"), "commons_file": title}
    cp = repo / "art" / "works" / "credits.yaml"
    text = cp.read_text()
    if re.search(rf"(?m)^{re.escape(work)}:", text):
        text = re.sub(rf"(?ms)^{re.escape(work)}:\n(?:  .*\n)*", "", text)
    lines = [f"{work}:"] + [f"  {k}: " + (json.dumps(v, ensure_ascii=False) if isinstance(v, str) and (":" in v or v.startswith(("'", '"')) or v.startswith("TODO")) else str(v)) for k, v in rec.items()]
    cp.write_text(text.rstrip("\n") + "\n" + "\n".join(lines) + "\n")
    return {"sizes": outs, "license": lic, "credit": rec["credit"], "date": rec["date"], "todo": [k for k in ("caption", "alt") if rec[k].startswith("TODO")]}


# ---------------------------------------------------------------- scaffold
def scaffold(repo: Path, work: str, lang: str, title: str | None = None, author: str | None = None, prefix: str | None = None, unit: str = "section",
             fmt: str = "weft-edition") -> list[Path]:
    from .draft import PHON
    if lang not in PHON:
        raise SystemExit(f"weft scaffold: no language module for {lang!r}; known: {', '.join(sorted(PHON))}")
    mod = PHON[lang]
    schemes = list(getattr(mod, "SCHEME_LABELS", {}) or {})
    wd = repo / "texts" / work
    if wd.exists():
        raise SystemExit(f"weft scaffold: {wd} exists")
    for d in ("curated", "sense", "notes", "sources"):
        (wd / d).mkdir(parents=True)
    prefix = prefix or re.sub(r"[^a-z]", "", work.split("-")[0])[:4] or "w"
    manifest = {
        "work": work, "title": title or f"TODO: {work}", "short_title": "TODO", "author": author or "TODO", "language": lang,
        "lang_name": f"TODO: {getattr(mod, '__name__', lang).split('.')[-1]} of <year>", "prefix": prefix, "urn": f"urn:weft:{lang}:TODO.{work}",
        "unit": "stanza-line" if unit == "stanza" else unit, **({"section_noun": "section"} if unit != "stanza" else {}),
        "written": {"year": 0, "display": "TODO", "label": "TODO: when, where, by whom; the library sorts by year"},
        "status": "phase-0", "pilot": ({"stanzas": []} if fmt == "stanza-text" else {"sections": []}),
        "edition": {"id": "TODO", "name": "TODO: the edition, its date, and the transcription used (pin it with weft pin --edition)", "format": fmt,
                    "file": "edition.yaml" if fmt == "weft-edition" else "sources/TODO.txt",
                    "license": "TODO: text public domain (author d. ...); transcription CC BY-SA 4.0; Weft line division CC BY-SA 4.0"},
        "treebank": None, "schemes": schemes, "scheme_labels": {s: "TODO: the time and place this scheme models for this work" for s in schemes[:1]},
        "sound_confidence": "medium", "sources_extra": [],
        "translations": [{"id": "weft-editorial", "kind": "editorial", "translator": "Weft editorial translation, draft", "year": 2026, "form": "prose, close to the original", "license": "CC BY-SA 4.0"}],
        "predicted_gaps": ["TODO: what this work does not yet do, and what is approximate"],
    }
    (wd / "manifest.yaml").write_text("# Scaffolded by weft scaffold; every TODO must go before the work is built. docs/building.md is the playbook.\n"
                                      + yaml.dump(manifest, allow_unicode=True, sort_keys=False, width=130))
    if fmt != "weft-edition":
        return [wd / "manifest.yaml"]
    (wd / "edition.yaml").write_text(f"""# Weft edition of TODO. Text of TODO (pinned in the manifest); each line is checked verbatim against the pinned
# source. verify_strip sets aside the page's markup. See docs/building.md, "Patterns in the edition file".
#   t     the word as printed, punctuation attached
#   Lines are Weft's division of the text; sections are TODO.
work: {work}
joiner: ' '
verify_in: sources/TODO.txt
verify_strip: \\{{\\{{[^{{}}]*\\}}\\}}|<[^>]+>|''
sections:
- id: '1'
  title: TODO
  lines:
  - tokens:
    - t: TODO
""")
    return [wd / "manifest.yaml", wd / "edition.yaml"]


# ---------------------------------------------------------------- overlay: the compact spec
POS = {"N": "NOUN", "PN": "PROPN", "A": "ADJ", "ADV": "ADV", "ADP": "ADP", "CC": "CCONJ", "SC": "SCONJ", "PART": "PART", "INTJ": "INTJ", "NUM": "NUM",
       "D": "DET", "Di": "DET", "Dd": "DET", "POSS": "DET", "Dp": "DET", "Dt": "DET",
       "P": "PRON", "PRON": "PRON", "DEM": "PRON", "REL": "PRON", "INT": "PRON", "INDEF": "PRON", "REFL": "PRON", "NEGP": "PRON",
       "V": "VERB", "AUX": "AUX", "SYM": "SYM", "X": "X"}
FIXED = {"D": ["Definite=Def", "PronType=Art"], "Di": ["Definite=Ind", "PronType=Art"], "Dd": ["PronType=Dem"], "POSS": ["Poss=Yes"], "Dp": ["Poss=Yes", "PronType=Prs"],
         "Dt": ["PronType=Tot"], "DEM": ["PronType=Dem"], "REL": ["PronType=Rel"], "INT": ["PronType=Int"], "INDEF": ["PronType=Ind"],
         "REFL": ["PronType=Prs", "Reflex=Yes"], "NEGP": ["PronType=Neg"]}
CASE = {"n": "Nom", "a": "Acc", "d": "Dat", "g": "Gen", "v": "Voc", "l": "Loc", "i": "Ins", "b": "Abl"}
GEN = {"m": "Masc", "f": "Fem", "n": "Neut"}; NUM = {"s": "Sing", "p": "Plur", "u": "Dual"}
MOOD = {"i": "Ind", "s": "Sub", "o": "Opt", "c": "Cnd"}
TENSE = {"pr": "Pres", "pa": "Past", "fut": "Fut", "aor": "Aor", "perf": "Perf", "impf": "Imp", "plup": "Pqp"}
VOICE = {"act": "Act", "m": "Mid", "mid": "Mid", "pass": "Pass"}
DEGREE = {"c": "Cmp", "cmp": "Cmp", "sup": "Sup", "spl": "Sup"}
ORDER = ["Aspect", "Case", "Definite", "Degree", "Gender", "Mood", "Number", "Person", "Polarity", "Poss", "PronType", "Reflex", "Tense", "VerbForm", "Voice"]


def _cgn(tok: str, feats: dict) -> bool:
    """case[gender]number: 'nms' -> Nom Masc Sing; 'ap' -> Acc Plur; 'nm' -> Nom Masc. True if it matched."""
    if re.fullmatch(r"[nadgvlib][mfn][spu]", tok):
        feats.update(Case=CASE[tok[0]], Gender=GEN[tok[1]], Number=NUM[tok[2]]); return True
    if re.fullmatch(r"[nadgvlib][spu]", tok):
        feats.update(Case=CASE[tok[0]], Number=NUM[tok[1]]); return True
    if re.fullmatch(r"[nadgvlib][mfn]", tok):
        feats.update(Case=CASE[tok[0]], Gender=GEN[tok[1]]); return True
    return False


def expand_code(code: str) -> str:
    """The compact morphology code of the overlay spec -> Universal Dependencies features. The grammar is
    the one the Hávamál overlays were written in:
      N.afp            NOUN Acc Fem Plur            PN.gms         PROPN Gen Masc Sing
      A.nms  A.nms.c   ADJ (comparative .c, superlative .sup)      NUM.dfp
      D.nms DEM.ans POSS.ams INDEF.nms INT.nns REL  determiners and pronouns, PronType from the head
      P.ns1 P.as3m P.ds3 (reflexive)                personal pronoun: case, number, person [gender]
      V.i3s.pr  V.s2p.pa  AUX.i3s.pr  V.i3s.pr.neg  finite: mood person number, tense, polarity
      V.inf  V.pp.nms  V.prp.nfs  V.imp2s  V.i1s.pr.m (middle voice)
      ADV ADP CC SC PART INTJ SYM                   bare heads
    A code already in UD form (contains '|' or '=') or a fused form ('X + Y') is returned unchanged."""
    if "|" in code or " + " in code or "=" in code:
        return code
    head, *rest = code.split(".")
    if head not in POS:
        raise ValueError(f"unknown part of speech code {head!r} in {code!r}")
    pos = POS[head]
    feats: dict[str, str] = {}
    for f in FIXED.get(head, []):
        k, v = f.split("="); feats[k] = v
    if head == "P" and rest and re.fullmatch(r"[nadgvlib][spu][123][mfn]?", rest[0]):
        x = rest.pop(0)
        feats.update(Case=CASE[x[0]], Number=NUM[x[1]], Person=x[2])
        if len(x) == 4: feats["Gender"] = GEN[x[3]]
        if x in ("ds3", "as3", "gs3"):          # sér, sik, sín: the reflexive has no number
            feats.pop("Number"); feats["Reflex"] = "Yes"
    for tok in rest:
        if tok == "inf": feats["VerbForm"] = "Inf"
        elif tok == "fin": feats["VerbForm"] = "Fin"
        elif tok == "pp": feats.update(Tense="Past", VerbForm="Part")
        elif tok == "prp": feats.update(Tense="Pres", VerbForm="Part")
        elif tok == "part": feats["VerbForm"] = "Part"
        elif tok == "ger": feats["VerbForm"] = "Ger"
        elif tok == "sup" and pos in ("VERB", "AUX"): feats["VerbForm"] = "Sup"
        elif tok in DEGREE and pos == "ADJ": feats["Degree"] = DEGREE[tok]
        elif tok in DEGREE and pos == "ADV": feats["Degree"] = DEGREE[tok]
        elif tok in TENSE: feats["Tense"] = TENSE[tok]
        elif tok in VOICE and pos in ("VERB", "AUX"): feats["Voice"] = VOICE[tok]
        elif tok == "neg": feats["Polarity"] = "Neg"
        elif tok == "refl": feats["Reflex"] = "Yes"
        elif tok == "poss": feats["Poss"] = "Yes"
        elif tok == "def": feats["Definite"] = "Def"
        elif tok == "ind": feats["Definite"] = "Ind"
        elif tok in ("dem", "rel", "int", "tot", "prs"): feats["PronType"] = tok.capitalize()
        elif re.fullmatch(r"imp[123][spu]", tok):
            feats.update(Mood="Imp", Person=tok[3], Number=NUM[tok[4]], Tense="Pres")
        elif re.fullmatch(r"[isoc][123][spu]", tok) and pos in ("VERB", "AUX"):
            feats.update(Mood=MOOD[tok[0]], Person=tok[1], Number=NUM[tok[2]])
        elif re.fullmatch(r"[123][spu]", tok):
            feats.update(Person=tok[0], Number=NUM[tok[1]])
        elif _cgn(tok, feats):
            pass
        elif re.fullmatch(r"[mf][spu]", tok):
            feats.update(Gender=GEN[tok[0]], Number=NUM[tok[1]])
        elif re.fullmatch(r"[spu]", tok):
            feats["Number"] = NUM[tok]
        else:
            raise ValueError(f"unknown feature code {tok!r} in {code!r}")
    return "|".join([pos] + [f"{k}={feats[k]}" for k in ORDER if k in feats])


EDGE_PUNCT = ",.;:!?\"“”«»‘’()[]-–—"
METRE_ROLE = {"a": "long line, a-verse · stave {s}", "b": "long line, b-verse · stave {s}", "f": "full line · staves {s}",
              "list": "line of a name list{s}"}      # list lines (þulur) often rhyme or pair names without a stave


def parse_line_spec(spec: str) -> tuple[str | None, list[dict]]:
    """'a g :: *Surf|gloss|lemma|code ;; ...' -> (metre string or None, tokens)."""
    metre = None
    body = spec
    if " :: " in spec:
        head, body = spec.split(" :: ", 1)
        role, *stave = head.split()
        if role in METRE_ROLE:
            metre = METRE_ROLE[role].format(s=" ".join(stave))
        else:
            metre = head
    note = None
    if " | " in body:
        body, note = body.rsplit(" | ", 1)
    if metre and note:
        metre = f"{metre} · {note}"
    toks = []
    for item in body.split(" ;; "):
        parts = item.split("|")
        if len(parts) < 4:
            raise ValueError(f"token needs Surface|gloss|lemma|code: {item!r}")
        surf, gloss, lemma = parts[0], parts[1], parts[2]
        code = "|".join(parts[3:])
        bare = surf.lstrip("*").strip(EDGE_PUNCT)       # gen surfaces carry no punctuation; the spec may copy the print's
        if lemma != lemma.strip(EDGE_PUNCT) or not lemma:
            raise ValueError(f"lemma {lemma!r} carries punctuation (a template slip?) in {item!r}")
        toks.append({"surface": bare, "stave": surf.startswith("*"), "gloss": gloss, "lemma": lemma, "morph": expand_code(code)})
    return metre, toks


def gen_lines(work_dir: Path) -> dict[str, list[str]]:
    """line id -> surfaces, from every gen file of the work."""
    out: dict[str, list[str]] = {}
    for gp in sorted((work_dir / "gen").glob("*.yaml")):
        if gp.name.endswith(".run.yaml"):
            continue
        g = yaml.safe_load(gp.read_text())
        for l in g.get("lines", []):
            out[l["id"]] = [t["surface"] for t in l["tokens"]]
    return out


def overlay(repo: Path, work: str, spec_path: Path, out_name: str) -> dict:
    from .paths import work_dir
    wd = work_dir(repo, work)
    spec = yaml.safe_load(spec_path.read_text())
    lines = gen_lines(wd)
    if not lines:
        raise SystemExit("weft overlay: no gen/ for this work; run weft draft first")
    out, problems, ntok = [], [], 0
    for lid, s in spec["lines"].items():
        if lid not in lines:
            problems.append(f"{lid}: not in gen"); continue
        metre, toks = parse_line_spec(s)
        if [t["surface"] for t in toks] != lines[lid]:
            problems.append(f"{lid}: spec {[t['surface'] for t in toks]} vs gen {lines[lid]}"); continue
        if metre:
            out.append(f'    {lid}: {{metre: {json.dumps(metre, ensure_ascii=False)}}}')
        for i, t in enumerate(toks, 1):
            q = lambda v: json.dumps(v, ensure_ascii=False)     # JSON strings are valid YAML flow scalars, quotes included
            out.append(f'    {lid}.{i}: {{lemma: {q(t["lemma"])}, morph: {q(t["morph"])}, gloss: {q(t["gloss"])}' + (", stave: true" if t["stave"] else "") + f'}}   # {t["surface"]}')
            ntok += 1
    if problems:
        raise SystemExit("weft overlay: the spec does not match the text:\n  " + "\n  ".join(problems[:20]))
    head = spec.get("header", "# Human overlay, written in the compact spec and expanded by weft overlay.")
    body = (f"{head}\n- by: \"{spec.get('by', 'TODO')}\"\n  date: \"{spec.get('date', 'TODO')}\"\n  why: \"{spec.get('why', 'TODO')}\"\n  status: \"{spec.get('status', 'draft')}\"\n  set:\n" + "\n".join(out) + "\n")
    (wd / "curated").mkdir(exist_ok=True)
    (wd / "curated" / out_name).write_text(body)
    return {"wrote": str((wd / "curated" / out_name).relative_to(repo)), "lines": len(spec["lines"]), "tokens": ntok}


def reuse_map(repo: Path, works: list[str]) -> dict[str, list]:
    """surface form -> most common (lemma, morph, gloss) across the named works' overlays: a hint for a new overlay."""
    from .paths import work_dir
    seen: dict[str, Counter] = defaultdict(Counter)
    pat = re.compile(r'\s*[\w.]+\.\d+\.\d+: \{lemma: "([^"]*)", morph: "([^"]*)", gloss: "([^"]*)"(?:, stave: true)?\}\s*#\s*(\S+)')
    for w in works:
        for f in (work_dir(repo, w) / "curated").glob("*.yaml"):
            for line in f.read_text(encoding="utf-8").splitlines():
                m = pat.match(line)
                if m:
                    lem, morph, gloss, surf = m.groups()
                    seen[surf.strip(",.;:!?-\"“”«»").lower()][(lem, morph, gloss)] += 1
    return {k: [list(x) for x, _ in v.most_common(3)] for k, v in seen.items()}
