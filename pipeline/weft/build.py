"""weft build: gen + curated + sense + notes (+ private) -> one self-contained HTML page.

The page inlines its CSS, JS and data so it opens from file:// with no server.
The public build reads only texts/. The private build also reads private/<work>/ and
writes to private/build/, which is gitignored, so licensed translations never leak.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import yaml

from . import __version__, treebank
from .draft import PHON, load_manifest

HTML_LANG = {"grc": "grc", "lat": "la", "non": "non", "ang": "ang", "hbo": "he", "lzh": "lzh", "runic": "gmq"}
RTL = {"hbo"}


def _load_yaml_dir(d: Path) -> list[tuple[Path, object]]:
    if not d.is_dir():
        return []
    return [(p, yaml.safe_load(p.read_text())) for p in sorted(d.glob("*.yaml")) if not p.name.endswith(".run.yaml")]


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
            for cs in sets or []:
                for key, fields in (cs.get("set") or {}).items():
                    target = index.get(key)
                    if target is None:
                        curated_log.append({"missing": key, "file": path.name})
                        continue
                    target.update(fields)
                    target.setdefault("curated", {}).update({f: {"by": cs.get("by"), "date": str(cs.get("date")), "status": cs.get("status", "draft")} for f in fields})

    # translations: public from manifest, private ones from private/<work>/manifest.yaml
    translations = {t["id"]: {k: v for k, v in t.items() if k in ("id", "translator", "year", "form", "license", "kind", "partial")}
                    for t in m.get("translations", [])}
    sense_roots = [work_dir / "sense"]
    if private_dir:
        pm = private_dir / "manifest.yaml"
        if pm.exists():
            for t in (yaml.safe_load(pm.read_text()) or {}).get("translations", []):
                translations[t["id"]] = {k: v for k, v in t.items() if k in ("id", "translator", "year", "form", "license")}
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

    # render-time conveniences: readable morphology; Hebrew without cantillation for easy reading
    for line in lines:
        for t in line["tokens"]:
            if t.get("morph"):
                t["morph_text"] = treebank.decode_morph(t["morph"])
            for pf in t.get("prefixes") or []:
                if pf.get("morph"):
                    pf["morph_text"] = treebank.decode_morph(pf["morph"])
            if m["language"] == "hbo":
                from .hebrew import strip_cantillation
                t["surface_plain"] = strip_cantillation(t["surface"])

    return {
        "work": dict({k: m.get(k) for k in ("work", "title", "author", "language", "urn", "unit")},
                     lang_html=HTML_LANG.get(m["language"], m["language"]),
                     dir="rtl" if m["language"] in RTL else "ltr"),
        "edition": {k: m["edition"].get(k) for k in ("id", "name", "license")},
        "treebank": ({k: m["treebank"].get(k) for k in ("id", "name", "license")} if m.get("treebank")
                     else {"id": "hand annotation", "name": "no treebank: hand annotation, draft", "license": "CC BY-SA 4.0"}),
        "schemes": m["schemes"],
        "keys": {s: PHON[m["language"]].KEY[s] for s in m["schemes"]},
        "scheme_labels": {s: PHON[m["language"]].SCHEME_LABELS.get(s, s) for s in m["schemes"]},
        "translations": list(translations.values()),
        "lines": lines,
        "sense": sense,
        "notes": notes,
        "build": {"weft": __version__, "private": bool(private_dir)},
        "_curated_missing": curated_log,
    }


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


def library_order(repo: Path) -> list[dict]:
    """Every work's manifest, oldest composition first: the library's reading order."""
    ms = [yaml.safe_load(mp.read_text()) for mp in (repo / "texts").glob("*/manifest.yaml")]
    ms.sort(key=lambda m: ((m.get("written") or {}).get("year", 10**6), m["work"]))
    return ms


def render(data: dict, site_dir: Path) -> str:
    tpl = (site_dir / "template.html").read_text()
    css = (site_dir / "weft.css").read_text()
    js = (site_dir / "weft.js").read_text()
    payload = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    title = f"{data['work']['title']} · Weft"
    art = data.pop("_art", {})
    tpl = (tpl.replace("{{LOCKUP}}", art.get("weft-lockup", "Weft"))
              .replace("{{FAVICON}}", art.get("favicon", "")))
    return (tpl.replace("{{TITLE}}", title)
               .replace("/*{{CSS}}*/", css)
               .replace("/*{{DATA}}*/", f"window.WEFT = {payload};")
               .replace("/*{{JS}}*/", js))


def run(repo: Path, work: str, private: bool = False) -> Path:
    work_dir = repo / "texts" / work
    private_dir = repo / "private" / work if private else None
    data = assemble(work_dir, private_dir)
    # previous and next work in the library's date order, so the pages read as one collection
    order = [m["work"] for m in library_order(repo)]
    i = order.index(work)
    titles = {m["work"]: m["title"] for m in library_order(repo)}
    data["nav"] = {
        "prev": {"href": f"{order[i-1]}.html", "title": titles[order[i-1]]} if i > 0 else None,
        "next": {"href": f"{order[i+1]}.html", "title": titles[order[i+1]]} if i + 1 < len(order) else None,
    }
    data["_art"] = load_art(repo)
    html = render(data, repo / "site")
    out_dir = (repo / "private" / "build") if private else (repo / "site" / "build")
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / f"{work}.html"
    out.write_text(html)
    write_index(repo, out_dir)
    return out


LANG_NAMES = {"grc": "Ancient Greek", "lat": "Latin", "non": "Old Norse", "ang": "Old English", "hbo": "Biblical Hebrew", "lzh": "Classical Chinese", "runic": "Runic Norse"}


def write_index(repo: Path, out_dir: Path) -> Path:
    """A plain front door listing every built work in out_dir."""
    import html as H
    rows = []
    for m in library_order(repo):   # oldest composition first; works without a date go last
        page = out_dir / f"{m['work']}.html"
        if not page.exists():
            continue
        written = (m.get("written") or {}).get("label", "")
        pl = m.get("pilot", {})
        if pl.get("inscriptions"):
            span = f"{len(pl['inscriptions'])} inscriptions"
        elif pl.get("stanzas"):
            span = "stanzas " + ", ".join(str(x) for x in pl["stanzas"])
        else:
            span = (f"{pl.get('book')}.{pl.get('first')}–{pl.get('last')}" if pl.get("book")
                    else f"chapter {pl['chapter']}, {m.get('unit', 'line')}s {pl.get('first')}–{pl.get('last')}" if pl.get("chapter")
                    else f"lines {pl.get('first')}–{pl.get('last')}") if pl else ""
        trs = ", ".join(f"{t['translator']} ({t['year']})" for t in m.get("translations", []))
        rows.append(f'<li><a href="{H.escape(page.name)}"><span class="t">{H.escape(m["title"])}</span>'
                    f'<span class="a">{H.escape(m["author"])} · {span}</span></a>'
                    + (f'<p class="w">{H.escape(written[:1].upper() + written[1:])}</p>' if written else "")
                    + f'<p>{H.escape(LANG_NAMES.get(m["language"], m["language"]))} · '
                    f'{H.escape(", ".join(m["schemes"]))} · {H.escape(trs)}</p></li>')
    idx = out_dir / "index.html"
    art = load_art(repo)
    idx.write_text(INDEX.replace("{{ROWS}}", "\n".join(rows))
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
main{max-width:720px;margin:0 auto;padding:48px 16px}
.k{font:600 .7rem/1 Inter,system-ui,sans-serif;letter-spacing:.14em;text-transform:uppercase;color:var(--accent);margin:0}
h1{font-size:2.2rem;margin:.3rem 0 .4rem}.lede{color:var(--soft);margin:0 0 2rem;font-size:1.1rem}
ul{list-style:none;padding:0;margin:0}li{border-top:1px solid var(--rule);padding:18px 0}
a{color:inherit;text-decoration:none;display:flex;flex-wrap:wrap;gap:4px 14px;align-items:baseline}
a:hover .t{color:var(--accent)}.t{font-size:1.6rem;font-weight:700}.a{color:var(--soft)}
li p{margin:6px 0 0;font:.85rem/1.5 Inter,system-ui,sans-serif;color:var(--soft)}
li p.w{margin-top:4px;font:italic .95rem/1.4 "Gentium Book Plus",Palatino,serif;color:var(--accent)}
</style></head><body><main><div class="lockup" role="img" aria-label="Weft">{{LOCKUP}}</div><h1>Interlinear library</h1>
<p class="lede">Classic texts ordered by date: the original text, a phonetic guide to pronouncing it in English, a literal word-for-word translation called a 'gloss', and well-known published translations, together in one evolving, community-led interlinear presentation.</p>
<ul>
{{ROWS}}
</ul></main></body></html>
"""
