"""weft build: gen + curated + sense + notes (+ private) -> one self-contained HTML page.

The page inlines its CSS, JS and data so it opens from file:// with no server.
The public build reads only texts/. The private build also reads private/<work>/ and
writes to private/build/, which is gitignored, so licensed translations never leak.
"""
from __future__ import annotations

import json
import os
import re
from pathlib import Path

import yaml

from . import __version__, treebank
from .draft import PHON, load_manifest

HTML_LANG = {"grc": "grc", "lat": "la", "non": "non", "ang": "ang", "hbo": "he", "arc": "arc", "lzh": "lzh", "runic": "gmq", "ja": "ja", "san": "sa", "akk": "akk", "fa": "fa", "ta": "ta", "it": "it", "fr": "fr", "es": "es", "nl": "nl", "fro": "fro", "de": "de", "egy": "egy", "sux": "sux", "orv": "orv", "xng": "xng", "cop": "cop", "sw": "sw", "qya": "qya", "sjn": "sjn", "pt": "pt", "eo": "eo"}
RTL = {"hbo", "arc", "fa"}
LANG_NAMES = {"grc": "Ancient Greek", "lat": "Latin", "non": "Old Norse", "ang": "Old English", "hbo": "Biblical Hebrew", "arc": "Biblical Aramaic", "lzh": "Classical Chinese", "runic": "Runic Norse", "ja": "Early modern Japanese", "san": "Vedic Sanskrit", "akk": "Akkadian", "fa": "Classical Persian", "ta": "Old Tamil", "it": "Renaissance Italian", "fr": "Middle French", "es": "Early Modern Spanish", "nl": "Early Modern Dutch", "fro": "Old French", "de": "German", "egy": "Old Egyptian", "sux": "Sumerian", "orv": "Old East Slavic", "xng": "Middle Mongolian", "cop": "Sahidic Coptic", "sw": "Swahili", "qya": "Quenya", "sjn": "Sindarin", "pt": "Portuguese", "eo": "Esperanto"}


def _load_yaml_dir(d: Path) -> list[tuple[Path, object]]:
    if not d.is_dir():
        return []
    return [(p, yaml.safe_load(p.read_text())) for p in sorted(d.glob("*.yaml")) if not p.name.endswith(".run.yaml")]


def inside(repo: Path, rel: str, what: str) -> Path:
    """A repository-relative path from committed data (a figure, an illustration), confined to the
    repository. Data files are reviewed as text, so a path that climbs out ('../', an absolute path)
    is refused loudly rather than read into a published page."""
    # lexical, not resolved: a symlink inside the repository (as the test fixtures use) stays inside;
    # an absolute path or a path with enough '..' to climb out does not
    root = Path(os.path.normpath(repo))
    p = Path(os.path.normpath(root / rel))
    if Path(rel).is_absolute() or not p.is_relative_to(root):
        raise SystemExit(f"weft: {what} path escapes the repository: {rel}")
    return p


def edition_dialects(work_dir: Path, m: dict) -> set[str]:
    """The reading dialects a Weft edition's sections declare (`dialect`), for a key narrowed to them."""
    ed = m.get("edition") or {}
    if ed.get("format") != "weft-edition" or not (work_dir / str(ed.get("file"))).exists():
        return set()
    e = yaml.safe_load((work_dir / ed["file"]).read_text()) or {}
    return {str(g["dialect"]) for g in (e.get("sections") or e.get("inscriptions") or []) if g.get("dialect")}


def assemble(work_dir: Path, private_dir: Path | None = None) -> dict:
    m = load_manifest(work_dir)
    lines, index = [], {}
    for _, g in _load_yaml_dir(work_dir / "gen"):
        for line in g["lines"]:
            lines.append(line)
            index[line["id"]] = line
            for t in line["tokens"]:
                index[t["id"]] = t

    # curated overlays, in file order then changeset order; later wins
    curated_log = []
    roots = [work_dir] + ([private_dir] if private_dir else [])
    for root in roots:
        for path, sets in _load_yaml_dir(root / "curated"):
            if path.name == "about.yaml":      # the hand-written about (weft about), not a changeset
                continue
            for cs in sets or []:
                for key, fields in (cs.get("set") or {}).items():
                    target = index.get(key)
                    if target is None:
                        curated_log.append({"missing": key, "file": path.name})
                        continue
                    target.update(fields)
                    target.setdefault("curated", {}).update({f: {"by": cs.get("by"), "date": str(cs.get("date")), "status": cs.get("status", "draft")} for f in fields})

    # translations: public from manifest, private ones from private/<work>/manifest.yaml
    # a reference translation (kind: reference) is still in copyright: the page cites it and never inlines it
    translations = {t["id"]: {k: v for k, v in t.items() if k in ("id", "translator", "year", "form", "license", "kind", "partial")}
                    for t in m.get("translations", []) if t.get("kind") != "reference"}
    references = {t["id"]: {k: v for k, v in t.items() if k in ("id", "translator", "year", "title", "publisher", "note")}
                  for t in m.get("translations", []) if t.get("kind") == "reference"}
    sense_roots = [work_dir / "sense"]
    if private_dir:
        pm = private_dir / "manifest.yaml"
        if pm.exists():
            for t in (yaml.safe_load(pm.read_text()) or {}).get("translations", []):
                translations[t["id"]] = {k: v for k, v in t.items() if k in ("id", "translator", "year", "form", "license")}
                references.pop(t["id"], None)      # owned copy in private/: shown inline, no citation notice
        sense_roots.append(private_dir / "sense")
    sense = []
    for d in sense_roots:
        for _, s in _load_yaml_dir(d):
            if s["translation"] in translations:
                sense.append({"tr": s["translation"], "spans": s["spans"]})

    notes = []
    for root in roots:
        for _, ns in _load_yaml_dir(root / "notes"):
            notes.extend(ns or [])

    # render-time conveniences: readable morphology; Hebrew without cantillation for easy reading;
    # section images embedded so the page stays one file
    import base64
    repo_root = work_dir.parents[1]
    for line in lines:
        fig = line.get("figure")
        if isinstance(fig, dict) and fig.get("file") and not fig.get("src"):
            fp = inside(repo_root, fig["file"], "figure")
            if fp.exists():
                kind = "png" if fp.suffix.lower() == ".png" else "jpeg"
                fig["src"] = f"data:image/{kind};base64," + base64.b64encode(fp.read_bytes()).decode()
        for t in line["tokens"]:
            if t.get("morph"):
                t["morph_text"] = treebank.decode_morph(t["morph"])
            for pf in t.get("prefixes") or []:
                if pf.get("morph"):
                    pf["morph_text"] = treebank.decode_morph(pf["morph"])
            if m["language"] in ("hbo", "arc"):      # the Aramaic chapters carry the same pointing
                from .hebrew import strip_cantillation
                t["surface_plain"] = strip_cantillation(t["surface"])

    return {
        "work": dict({k: m.get(k) for k in ("work", "title", "author", "language", "urn", "unit", "section_noun")},
                     lang_html=HTML_LANG.get(m["language"], m["language"]),
                     dir="rtl" if m["language"] in RTL else "ltr",
                     lang_name=m.get("lang_name") or LANG_NAMES.get(m["language"], m["language"]),
                     script_label=getattr(PHON[m["language"]], "SCRIPT_LABEL", "Script (runes)"),
                     script_word=getattr(PHON[m["language"]], "SCRIPT_WORD", "runes"),
                     show_translit=getattr(PHON[m["language"]], "SHOW_TRANSLIT", m["language"] == "san"),
                     translit_label=getattr(PHON[m["language"]], "TRANSLIT_LABEL", "Transliteration"),
                     sound_confidence=m.get("sound_confidence"),
                     repo_url=REPO_URL),
        "edition": {k: m["edition"].get(k) for k in ("id", "name", "license")},
        "treebank": ({k: m["treebank"].get(k) for k in ("id", "name", "license")} if m.get("treebank")
                     else {"id": "hand annotation", "name": "no treebank: hand annotation, draft", "license": "CC BY-SA 4.0"}),
        "schemes": m["schemes"],
        "keys": {s: (PHON[m["language"]].key_for(s, edition_dialects(work_dir, m)) if hasattr(PHON[m["language"]], "key_for")
                     else PHON[m["language"]].KEY[s]) for s in m["schemes"]},
        # a work may override a scheme's label, e.g. to give its own date for a shared reconstruction
        "scheme_labels": {s: (m.get("scheme_labels") or {}).get(s) or PHON[m["language"]].SCHEME_LABELS.get(s, s) for s in m["schemes"]},
        "translations": list(translations.values()),
        "references": list(references.values()),
        "lines": lines,
        "sense": sense,
        "notes": notes,
        "build": {"weft": __version__, "private": bool(private_dir)},
        "_curated_missing": curated_log,
    }


REPO_URL = "https://github.com/GiantRavens/weft"   # corrections and recordings arrive as issues here
ART_INK = "#16181D"


def load_art(repo: Path) -> dict[str, str]:
    """Inline the artwork so pages stay single files that open from file://.
    The dark ink becomes currentColor, so one SVG follows the page's light and dark themes
    (the art/ folder's -reverse files are the same drawings in white)."""
    import base64
    art: dict[str, str] = {}
    for name in ("weft-lockup", "weft-mark", "weft-wordmark"):
        f = repo / "art" / f"{name}.svg"
        if f.exists():
            svg = f.read_text(encoding="utf-8").replace(ART_INK, "currentColor")
            svg = re.sub(r'\swidth="[^"]*"\s+height="[^"]*"', "", svg, count=1)
            art[name] = svg.replace("<svg ", '<svg aria-hidden="true" focusable="false" ', 1)
    fav = repo / "art" / "weft-favicon.svg"
    if fav.exists():
        svg = fav.read_text(encoding="utf-8").replace(ART_INK, "currentColor")
        svg = svg.replace(">", "><style>:root{color:#16181D}@media (prefers-color-scheme:dark){:root{color:#FFFFFF}}</style>", 1)
        art["favicon"] = "data:image/svg+xml;base64," + base64.b64encode(svg.encode()).decode()
    return art


AGES = [  # (label, span, first year after the age); years are negative BC, as in manifests
    ("Antiquity", "to AD 500", 500),
    ("Early Middle Ages", "500 to 1000", 1000),
    ("High and Late Middle Ages", "1000 to 1500", 1500),
    ("Early Modern", "1500 to 1800", 1800),
    ("Modern", "from 1800", 10**6),
]


def age_of(year) -> tuple[str, str]:
    """The age a composition date falls in. Undated works go in the last group."""
    y = 10**6 - 1 if year is None else year
    for label, span, end in AGES:
        if y < end:
            return label, span
    return AGES[-1][0], AGES[-1][1]


def load_illustration(repo: Path, work: str, size: str = "image", private: bool = False) -> dict | None:
    """The work's illustration from art/works/credits.yaml (and, in a private build, first from
    private/art/credits.yaml), embedded as a data URI so the page stays one file.
    size is "image" (frontispiece) or "thumb" (library row)."""
    import base64
    rec = None
    for cf in ([repo / "private" / "art" / "credits.yaml"] if private else []) + [repo / "art" / "works" / "credits.yaml"]:
        if cf.exists():
            rec = (yaml.safe_load(cf.read_text(encoding="utf-8")) or {}).get(work)
            if rec:
                break
    if not rec or not inside(repo, rec[size], "illustration").exists():
        return None
    b = inside(repo, rec[size], "illustration").read_bytes()
    return {**rec, "src": "data:image/jpeg;base64," + base64.b64encode(b).decode()}


def frontispiece(ill: dict | None) -> str:
    import html as H
    if not ill:
        return ""
    credit = ", ".join(str(x) for x in (ill.get("credit"), ill.get("date")) if x and str(x).lower() != "unknown")
    return (f'<figure class="frontis"><img src="{ill["src"]}" alt="{H.escape(ill["alt"])}">'
            f'<figcaption><span class="cap">{H.escape(ill["caption"])}</span>'
            f'<span class="cred">{H.escape(credit + " · " if credit else "")}{H.escape(ill.get("license", ""))} · '
            + (f'<a href="{H.escape(ill["source"])}">{"Wikimedia Commons" if "wikimedia" in ill["source"] else "source"}</a>' if ill.get("source") else "")
            + '</span></figcaption></figure>')


def library_order(repo: Path, private: bool = False) -> list[dict]:
    """Every work's manifest, oldest composition first: the library's reading order.
    The public library is texts/ only; a private build adds the private works (marked _private)."""
    from .paths import private_works
    ms = [yaml.safe_load(mp.read_text()) for mp in (repo / "texts").glob("*/manifest.yaml")]
    if private:
        for w in private_works(repo):
            ms.append(dict(yaml.safe_load((repo / "private" / w / "manifest.yaml").read_text()), _private=True))
    ms.sort(key=lambda m: ((m.get("written") or {}).get("year", 10**6), m["work"]))
    return ms


SITE_URL = os.environ.get("WEFT_SITE_URL", "https://weftlibrary.org/")   # the library's own domain since 2026-10-02; the GitHub Pages address redirects to it


def preview_meta(data: dict) -> str:
    """Link-card tags (Open Graph and Twitter) for a public page. The image is the page's own
    screenshot from `weft previews`; a private build gets no tags, so nothing points outward."""
    import html as H
    if data.get("build", {}).get("private"):
        return ""
    w = data["work"]
    slug = w["work"]
    title = f"{w['title']} · Weft"
    by = f"{w['author']}. " if w.get("author") else ""
    desc = f"{by}The original text line by line, with sound and gloss."
    url, img = f"{SITE_URL}{slug}.html", f"{SITE_URL}previews/{slug}.jpg"
    tags = [("property", "og:type", "article"), ("property", "og:site_name", "Weft"),
            ("property", "og:title", title), ("property", "og:description", desc),
            ("property", "og:url", url), ("property", "og:image", img),
            ("property", "og:image:width", "1200"), ("property", "og:image:height", "630"),
            ("name", "twitter:card", "summary_large_image"), ("name", "description", desc)]
    return "\n".join(f'<meta {k}="{v}" content="{H.escape(c)}">' for k, v, c in tags)


def copy_fonts(site_dir: Path, out_dir: Path) -> None:
    """The self-hosted fonts (site/fonts) sit beside the pages as build/fonts, so the pages' relative
    @font-face urls resolve on the published site and from file://. Copied only when changed."""
    import shutil
    src = site_dir / "fonts"
    if not src.is_dir():
        return
    dst = out_dir / "fonts"
    dst.mkdir(parents=True, exist_ok=True)
    for f in src.iterdir():
        if f.is_file() and (not (dst / f.name).exists() or (dst / f.name).stat().st_size != f.stat().st_size):
            shutil.copy2(f, dst / f.name)


def render(data: dict, site_dir: Path) -> str:
    import html as H
    tpl = (site_dir / "template.html").read_text()
    css = (site_dir / "weft.css").read_text()
    js = (site_dir / "weft.js").read_text()
    # the art and the frontispiece go into the HTML, not into the data payload (they were once in
    # both, which doubled the image in every page); _curated_missing is check's, not the page's
    art = data.pop("_art", {})
    frontis = frontispiece(data.pop("_illustration", None))
    data.pop("_curated_missing", None)
    # every < becomes \u003c, so no string in the data can open or close a tag or a comment inside
    # the <script> that carries it (</script>, <!--<script>); JSON reads the escape as a plain <
    payload = json.dumps(data, ensure_ascii=False).replace("<", "\\u003c")
    title = H.escape(f"{data['work']['title']} · Weft")
    tpl = (tpl.replace("{{LOCKUP}}", art.get("weft-lockup", "Weft"))
              .replace("{{FAVICON}}", art.get("favicon", ""))
              .replace("{{FRONTIS}}", frontis))
    return (tpl.replace("{{TITLE}}", title)
               .replace("{{META}}", preview_meta(data))
               .replace("/*{{CSS}}*/", css)
               .replace("/*{{DATA}}*/", f"window.WEFT = {payload};")
               .replace("/*{{JS}}*/", js))


def run(repo: Path, work: str, private: bool = False) -> Path:
    from .paths import is_private_work, resolve_for_build
    work_dir, private_dir = resolve_for_build(repo, work, private)
    data = assemble(work_dir, private_dir)
    if is_private_work(repo, work):
        # never offer to file a private work's title or lines as a public GitHub issue
        data["work"]["private_work"] = True
        data["build"]["private"] = True
    # previous and next work in the library's date order, so the pages read as one collection
    lib = library_order(repo, private)
    order = [m["work"] for m in lib]
    i = order.index(work)
    titles = {m["work"]: m["title"] for m in lib}
    data["nav"] = {
        "prev": {"href": f"{order[i-1]}.html", "title": titles[order[i-1]]} if i > 0 else None,
        "next": {"href": f"{order[i+1]}.html", "title": titles[order[i+1]]} if i + 1 < len(order) else None,
    }
    data["_art"] = load_art(repo)
    data["_illustration"] = load_illustration(repo, work, private=private)
    html = render(data, repo / "site")
    out_dir = (repo / "private" / "build") if private else (repo / "site" / "build")
    copy_fonts(repo / "site", out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / f"{work}.html"
    out.write_text(html)
    write_index(repo, out_dir, private)
    return out




def display_date(written: dict) -> str:
    """The date shown in the library's left column: the manifest's display string, else the year."""
    if written.get("display"):
        return str(written["display"])
    y = written.get("year")
    if y is None:
        return ""
    return f"{-y} BC" if y < 0 else (f"AD {y}" if y < 1000 else str(y))


def stanza_ranges(xs: list) -> str:
    """1, 2, 3, 76, 77 -> '1–3, 76–77'."""
    out: list[list] = []
    for x in xs:
        if out and isinstance(x, int) and isinstance(out[-1][1], int) and x == out[-1][1] + 1:
            out[-1][1] = x
        else:
            out.append([x, x])
    return ", ".join(str(a) if a == b else f"{a}–{b}" for a, b in out)


def short_title(m: dict) -> str:
    """The name a list can carry: 'Völuspá (The Seeress's Prophecy)' -> 'Völuspá'; 'Il Principe, chapters 17 and
    18: ...' -> 'Il Principe'. A manifest's short_title overrides this."""
    if m.get("short_title"):
        return str(m["short_title"])
    t = re.sub(r"\s*\([^)]*\)", "", str(m["title"]))
    t = t.split(":", 1)[0]
    t = re.split(r",\s+(?=[a-z0-9])", t, maxsplit=1)[0]
    return t.strip() or str(m["title"])


# the index files a language under its plain name where the works span periods (Montaigne and the Berlin Act are both French)
INDEX_FAMILY = {"fr": "French", "it": "Italian", "es": "Spanish", "nl": "Dutch", "ja": "Japanese", "pt": "Portuguese"}


KINDS = {"epic-and-myth": "Epic and myth", "scripture": "Sacred texts", "philosophy": "Philosophy", "poetry": "Poetry, literature and music",
         "law": "Law and politics", "correspondence": "Correspondence", "science": "Science"}      # manifest kind -> index heading, in this order


def kind_index(ms: list[dict], out_dir: Path) -> str:
    """The library by kind: the seven kinds in their fixed order, each with its built works in the library's
    date order. A manifest's `kind` is one of KINDS; weft check refuses any other value."""
    import html as H
    by: dict[str, list[tuple[str, str]]] = {}
    for m in ms:
        page = out_dir / f"{m['work']}.html"
        if page.exists() and m.get("kind") in KINDS:
            by.setdefault(m["kind"], []).append((short_title(m), page.name))
    if not by:
        return ""
    items = "".join(f'<li><b>{H.escape(KINDS[k])}</b> ' + " · ".join(f'<a href="{H.escape(href)}">{H.escape(t)}</a>' for t, href in by[k]) + "</li>"
                    for k in KINDS if k in by)
    n_works = sum(len(v) for v in by.values())
    return (f'<details class="langs kinds"><summary><span class="k2">By kind</span><span class="n">{len(by)} kinds, {n_works} works</span></summary>'
            f'<ul>{items}</ul></details>')


def language_index(ms: list[dict], out_dir: Path) -> str:
    """The library by language: every language that has a built page, alphabetically, with its works
    in the library's date order. Plain HTML, so the index page stays script-free."""
    import html as H
    by: dict[str, list[tuple[str, str]]] = {}
    for m in ms:
        page = out_dir / f"{m['work']}.html"
        if not page.exists():
            continue
        name = m.get("lang_name") or LANG_NAMES.get(m["language"], m["language"])
        # one entry per language family name: 'Latin of the charters (...)' and 'Medieval Latin' both file under Latin
        family = INDEX_FAMILY.get(m["language"]) or LANG_NAMES.get(m["language"], name)
        by.setdefault(family, []).append((short_title(m), page.name))
    if not by:
        return ""
    items = "".join(f'<li><b>{H.escape(lang)}</b> ' + " · ".join(f'<a href="{H.escape(href)}">{H.escape(t)}</a>' for t, href in works) + "</li>"
                    for lang, works in sorted(by.items(), key=lambda kv: kv[0].lower()))
    n_works = sum(len(v) for v in by.values())
    # a disclosure, closed by default: the library opens on its date order, and the index unfolds on request
    return (f'<details class="langs"><summary><span class="k2">By language</span><span class="n">{len(by)} languages, {n_works} works</span></summary>'
            f'<ul>{items}</ul></details>')


def added_dates(repo: Path, ms: list[dict]) -> dict[str, str]:
    """When each work arrived, as an ISO timestamp: the commit that first added its manifest, read from
    git in one call. A work git does not know (uncommitted, a private work, no git at all) dates by
    its manifest's modification time. CI must check out the full history (fetch-depth: 0), or every
    work looks added in the one commit it can see."""
    import datetime as dt
    import subprocess
    dates: dict[str, str] = {}
    try:
        out = subprocess.run(["git", "-C", str(repo), "log", "--diff-filter=A", "--format=%x00%ad", "--date=iso-strict",
                              "--name-only", "--", "texts/*/manifest.yaml"], capture_output=True, text=True, timeout=30).stdout
        day = ""
        for line in out.splitlines():
            if line.startswith("\x00"):
                day = line[1:].strip()
            elif line.strip():
                dates[line.split("/")[1]] = day   # newest first in the log, so the earliest add wins
    except (OSError, subprocess.SubprocessError):
        pass
    for m in ms:
        # a work split from an older page arrived when that page did; git still knows the old manifest's add
        if m.get("split_from") and m["split_from"] in dates:
            dates[m["work"]] = dates[m["split_from"]]
        if m["work"] not in dates:
            mp = (repo / ("private" if m.get("_private") else "texts") / m["work"] / "manifest.yaml")
            dates[m["work"]] = (dt.datetime.fromtimestamp(mp.stat().st_mtime) if mp.exists() else dt.datetime.now()).isoformat(timespec="seconds")
    return dates


def newest_index(ms: list[dict], out_dir: Path, dates: dict[str, str], n: int = 6) -> str:
    """The n works added most recently, newest first, each with the day it arrived. Plain HTML; it
    sits above the by-language disclosure so a returning reader sees what is new without unfolding anything."""
    import datetime as dt
    import html as H
    built = [m for m in ms if (out_dir / f"{m['work']}.html").exists()]
    order = {m["work"]: i for i, m in enumerate(built)}
    # the full timestamp orders works that landed on the same day; the library order breaks remaining ties
    newest = sorted(built, key=lambda m: (dates.get(m["work"], ""), -order[m["work"]]), reverse=True)[:n]
    if not newest:
        return ""
    def day(iso: str) -> str:
        try:
            d = dt.datetime.fromisoformat(iso).date()
            return f"{d.day} {d.strftime('%b %Y')}"
        except ValueError:
            return iso
    items = "".join(f'<li><a href="{H.escape(m["work"])}.html">{H.escape(short_title(m))}</a>'
                    f'<time datetime="{H.escape(dates[m["work"]][:10])}">{H.escape(day(dates[m["work"]]))}</time></li>' for m in newest)
    return f'<section class="newest"><h2>Newest texts</h2><ul>{items}</ul></section>'


def moved_pages(repo: Path, out_dir: Path, art: dict, private: bool = False) -> list[Path]:
    """A page at each old address of a work that was split into several (manifest `split_from`), so
    links already shared keep working. It lists the works the page became; a link to a line
    (old.html#kant.kpv.3) goes on to the work that now holds that line, since the split kept the IDs."""
    import html as H
    from . import docs
    ms = library_order(repo, private)
    live = {m["work"] for m in ms}
    groups: dict[str, list[dict]] = {}
    for m in ms:
        if m.get("split_from") and m["split_from"] not in live and (out_dir / f"{m['work']}.html").exists():
            groups.setdefault(m["split_from"], []).append(m)
    written = []
    for old, parts in groups.items():
        by_section = {str(s): f"{m['work']}.html" for m in parts
                      for s in ((m.get("pilot") or {}).get("sections") or (m.get("pilot") or {}).get("inscriptions") or [])}
        items = "".join(f'<li><a href="{H.escape(m["work"])}.html">{H.escape(m["title"])}</a> · {H.escape(display_date(m.get("written") or {}))}</li>'
                        for m in parts)
        body = (f"<h1>This page is now {len(parts)} works</h1>"
                f"<p>The texts that were together on this page each have a page of their own. Every line keeps its "
                f"identifier, so a link to a line opens it on its new page.</p><ul>{items}</ul>")
        # the line ID's second part is its section; the map sends a link to a line on to the work that holds it
        script = ("<script>(function(){var m=" + json.dumps(by_section) + ";var h=location.hash.slice(1);"
                  "var d=decodeURIComponent(h);var s=d.indexOf('sec-')===0?d.slice(4):d.split('.')[1];"
                  "if(s&&m[s])location.replace(m[s]+location.hash);})();</script>")
        page = out_dir / f"{old}.html"
        page.write_text(docs.PAGE.replace("{{TITLE}}", "Moved").replace("{{NAV}}", docs.nav_html(page.name))
                        .replace("{{BODY}}", body + script)
                        .replace("{{LOCKUP}}", art.get("weft-lockup", "Weft")).replace("{{FAVICON}}", art.get("favicon", "")))
        written.append(page)
    return written


def write_index(repo: Path, out_dir: Path, private: bool = False) -> Path:
    """A plain front door listing every built work in out_dir. A private build lists the
    private works with the public ones, each marked."""
    import html as H
    rows, age = [], None
    for m in library_order(repo, private):   # oldest composition first; works without a date go last
        page = out_dir / f"{m['work']}.html"
        if not page.exists():
            continue
        written = (m.get("written") or {}).get("label", "")
        pl = m.get("pilot", {})
        if pl.get("sections"):
            noun = m.get("section_noun", "section")
            k = len(pl["sections"])
            span = (f"{noun}{'' if k == 1 else 's'} " + stanza_ranges([int(x) if str(x).isdigit() else x for x in pl["sections"]])) if noun == "chapter" else f"{k} {noun if k == 1 else (noun[:-1] + 'ies' if noun.endswith('y') and noun[-2:-1] not in 'aeiou' else noun + 's')}"
        elif pl.get("inscriptions"):
            span = f"{len(pl['inscriptions'])} inscriptions"
        elif pl.get("stanzas"):
            span = "stanzas " + stanza_ranges(pl["stanzas"])
        else:
            span = (f"{pl.get('book')}.{pl.get('first')}–{pl.get('last')}" if pl.get("book")
                    else (f"{pl['chapter']}:{pl.get('first')}–{pl['also'][-1]['chapter']}:{pl['also'][-1]['last']}" if pl.get("also")
                          else f"chapter {pl['chapter']}, {m.get('unit', 'line')}s {pl.get('first')}–{pl.get('last')}") if pl.get("chapter")
                    else f"lines {pl.get('first')}–{pl.get('last')}") if pl else ""
        trs = ", ".join(f"{t['translator']} ({t['year']}" + (", cited, in copyright)" if t.get("kind") == "reference" else ")")
                        for t in m.get("translations", []))
        this_age = age_of((m.get("written") or {}).get("year"))
        if this_age != age:
            if age is not None:
                rows.append("</ul></section>")
            rows.append(f'<section class="age"><h2>{H.escape(this_age[0])}<span>{H.escape(this_age[1])}</span></h2><ul>')
            age = this_age
        ill = load_illustration(repo, m["work"], "thumb", private=private)
        thumb = (f'<a class="th" href="{H.escape(page.name)}" tabindex="-1" aria-hidden="true">'
                 f'<img src="{ill["src"]}" alt=""></a>') if ill else '<span class="th"></span>'
        lang_name = m.get("lang_name") or LANG_NAMES.get(m["language"], m["language"])
        when = f'<div class="when"><span class="yr">{H.escape(display_date(m.get("written") or {}))}</span>' \
               f'<span class="lg">{H.escape(lang_name)}</span></div>'
        rows.append(f'<li>{when}{thumb}<div class="body"><a href="{H.escape(page.name)}"><span class="t">{H.escape(m["title"])}</span>'
                    f'<span class="a">{H.escape(m["author"])} · {span}</span></a>'
                    + ('<p class="pv">Private: in your build only</p>' if m.get("_private") else "")
                    + (f'<p class="w">{H.escape(written[:1].upper() + written[1:])}</p>' if written else "")
                    + f'<p>{"Reads right to left · " if m["language"] in RTL else ""}'
                    f'{H.escape(", ".join(m["schemes"]))} · {H.escape(trs)}</p></div></li>')
    if age is not None:
        rows.append("</ul></section>")
    idx = out_dir / "index.html"
    ms = library_order(repo, private)
    art = load_art(repo)
    from . import docs
    docs.build_docs(repo, out_dir, art)
    moved_pages(repo, out_dir, art, private)
    html = INDEX if not private else INDEX.replace("<h1>Interlinear library</h1>", "<h1>Interlinear library</h1><p class=\"pv\">Private build: includes your own texts and licensed material. Do not publish this folder.</p>")
    idx.write_text(html.replace("{{ROWS}}", "\n".join(rows)).replace("{{NAV}}", docs.nav_html("index.html"))
                        .replace("{{NEWEST}}", newest_index(ms, out_dir, added_dates(repo, ms)))
                        .replace("{{LANGS}}", language_index(ms, out_dir))
                        .replace("{{KINDS}}", kind_index(ms, out_dir))
                        .replace("{{LOCKUP}}", art.get("weft-lockup", "Weft"))
                        .replace("{{FAVICON}}", art.get("favicon", "")))
    return idx


INDEX = """<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1"><title>Weft library</title>
<link rel="icon" type="image/svg+xml" href="{{FAVICON}}">
<link href="https://fonts.googleapis.com/css2?family=Gentium+Book+Plus:wght@400;700&family=Inter:wght@400;600&display=swap" rel="stylesheet">
<style>
.lockup{display:block;width:210px;height:auto;color:var(--ink);margin:0 0 18px}
:root{--bg:#f6f1e6;--ink:#221d16;--soft:#5d5446;--rule:#ddd3c0;--accent:#9a3b1f;color-scheme:light}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#15130f;--ink:#ece4d2;--soft:#b9ad96;--rule:#342f26;--accent:#e08a5f;color-scheme:dark}}
:root[data-theme="dark"]{--bg:#15130f;--ink:#ece4d2;--soft:#b9ad96;--rule:#342f26;--accent:#e08a5f;color-scheme:dark}
body{margin:0;background:var(--bg);color:var(--ink);font-family:"Gentium Book Plus",Palatino,serif}
main{max-width:860px;margin:0 auto;padding:48px 16px}
.k{font:600 .7rem/1 Inter,system-ui,sans-serif;letter-spacing:.14em;text-transform:uppercase;color:var(--accent);margin:0}
h1{font-size:2.2rem;margin:.3rem 0 .4rem}.lede{color:var(--soft);margin:0 0 .6rem;font-size:1.1rem}
ul{list-style:none;padding:0;margin:0}li{border-top:1px solid var(--rule);padding:18px 0;display:flex;gap:18px;align-items:flex-start}
.age{margin:2.4rem 0 0}.age h2{font:600 .75rem/1 Inter,system-ui,sans-serif;letter-spacing:.14em;text-transform:uppercase;color:var(--accent);margin:0 0 12px;display:flex;gap:12px;align-items:baseline}
.age h2 span{letter-spacing:.04em;text-transform:none;font-weight:400;color:var(--soft)}
.when{flex:0 0 8.6rem;display:flex;flex-direction:column;gap:5px;padding-top:4px}
.when .yr{font:700 1.02rem/1.15 Inter,system-ui,sans-serif;color:var(--ink);letter-spacing:-.01em;font-variant-numeric:tabular-nums}
.when .lg{font:600 .66rem/1.3 Inter,system-ui,sans-serif;letter-spacing:.1em;text-transform:uppercase;color:var(--accent)}
.th{flex:0 0 88px;width:88px;height:88px;border-radius:6px;overflow:hidden;background:var(--rule);display:block}
.th img{width:100%;height:100%;object-fit:cover;display:block}.body{flex:1;min-width:0}
.body>a{color:inherit;text-decoration:none;display:flex;flex-wrap:wrap;gap:4px 14px;align-items:baseline}
@media (max-width:560px){li{flex-wrap:wrap;gap:10px 14px}.when{flex:0 0 100%;flex-direction:row;align-items:baseline;gap:10px;padding-top:0}
.th{flex-basis:64px;width:64px;height:64px}}
.body>a:hover .t{color:var(--accent)}.t{font-size:1.6rem;font-weight:700}.a{color:var(--soft)}
li p{margin:6px 0 0;font:.85rem/1.5 Inter,system-ui,sans-serif;color:var(--soft)}
.docnav{font:600 .78rem/1.4 Inter,system-ui,sans-serif;letter-spacing:.04em;color:var(--soft);margin:.4rem 0 0}
.docnav a{color:var(--accent);text-decoration:none}.docnav a:hover{text-decoration:underline}.docnav span{color:var(--ink)}
p.pv{font:600 .72rem/1.4 Inter,system-ui,sans-serif;letter-spacing:.06em;text-transform:uppercase;color:var(--accent);margin:4px 0 0}
li p.w{margin-top:4px;font:italic .95rem/1.4 "Gentium Book Plus",Palatino,serif;color:var(--accent)}
.search{margin:1.2rem 0 0}.search input{width:100%;box-sizing:border-box;font:1.05rem/1.4 "Gentium Book Plus",Palatino,serif;padding:9px 13px;border:1px solid var(--rule);border-radius:8px;background:transparent;color:var(--ink)}
.search input:focus{outline:2px solid var(--accent);outline-offset:1px}
.newest{margin:1.6rem 0 0}.newest h2{font:600 .75rem/1 Inter,system-ui,sans-serif;letter-spacing:.14em;text-transform:uppercase;color:var(--accent);margin:0 0 8px}
.newest ul{list-style:none;padding:0;margin:0;display:flex;flex-wrap:wrap;gap:4px 22px}
.newest li{font:.84rem/1.5 Inter,system-ui,sans-serif;display:block;border:0;padding:0;margin:0;color:var(--soft)}
.newest li a{color:var(--ink);text-decoration:none;font-weight:600}.newest li a:hover{color:var(--accent)}.newest li time{margin-left:7px;font-size:.78rem}
.langs{margin:1rem 0 0;padding:10px 0 8px;border-top:1px solid var(--rule);border-bottom:1px solid var(--rule)}
.langs summary{cursor:pointer;list-style:none;display:flex;gap:12px;align-items:baseline;font:600 .75rem/1 Inter,system-ui,sans-serif;letter-spacing:.14em;text-transform:uppercase;color:var(--accent)}
.langs summary::-webkit-details-marker{display:none}
.langs summary::before{content:"▸";font-size:.8rem;transition:transform .15s}.langs[open] summary::before{transform:rotate(90deg)}
.langs summary .n{letter-spacing:.04em;text-transform:none;font-weight:400;color:var(--soft)}
.kinds ul{columns:1}.kinds li{margin-bottom:8px}
.langs ul{columns:2;column-gap:28px;list-style:none;padding:0;margin:12px 0 0}
.langs li{font:.82rem/1.5 Inter,system-ui,sans-serif;color:var(--soft);margin:0 0 5px;padding:0;border:0;display:block;break-inside:avoid}
.langs li b{color:var(--ink);font-weight:600;margin-right:4px}
.langs li a{color:var(--accent);text-decoration:none}.langs li a:hover{text-decoration:underline}
@media (max-width:560px){.langs ul{columns:1}}
</style></head><body><main><div class="lockup" role="img" aria-label="Weft">{{LOCKUP}}</div><h1>Interlinear library</h1>
<p class="lede">Classic texts ordered by date: the original text, a phonetic guide to pronouncing it in English, a literal word-for-word translation called a 'gloss', and well-known published translations, together in one evolving, community-led interlinear presentation.</p>
{{NAV}}
<form class="search" action="search.html" role="search"><input type="search" name="q" placeholder="Search the library: a word in any language, a name, a subject" aria-label="Search the library"></form>
{{NEWEST}}
{{KINDS}}
{{LANGS}}
{{ROWS}}
</main></body></html>
"""
