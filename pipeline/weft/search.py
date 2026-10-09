"""weft index: the library's search index and search page.

Writes search-index.js (window.WEFT_INDEX = {...}) and search.html beside the built pages. The index is
a script, not JSON, because a page opened from file:// may load a script but not fetch a file. It is
built from assemble(), the same data the pages carry, so the public index holds exactly what the public
pages show: no private work, no translation cited as kind: reference. A private build (--private) indexes
into private/build with the private works and translations.

Per work: what it is (title, author, date, kind, language, the about record from weft about), then its
lines with each token's surface, lemma and gloss, its translation spans and its notes. Token IDs are
not stored: a token's ID is its line's ID and its position from 1, which weft check's data keeps true.
The matching itself is in site/search.js, shared by the page and the tests.
"""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

from . import __version__, about
from .build import INDEX_FAMILY, KINDS, LANG_NAMES, assemble, display_date, library_order, short_title


def work_record(m: dict, data: dict, work_dir: Path) -> dict:
    a = about.load(work_dir) or {}
    lang = m["language"]
    return {
        "w": m["work"], "t": m["title"], "st": short_title(m), "a": m.get("author") or "",
        "d": display_date(m.get("written") or {}), "y": (m.get("written") or {}).get("year"),
        "wl": (m.get("written") or {}).get("label", ""),
        "k": KINDS.get(m.get("kind"), ""), "l": data["work"]["lang_name"],
        "f": INDEX_FAMILY.get(lang) or LANG_NAMES.get(lang, data["work"]["lang_name"]), "dir": data["work"]["dir"],
        "ab": {k: a.get(k) for k in ("summary", "subjects", "description", "source", "match", "title", "url", "attribution") if a.get(k)},
        "L": [[l["id"], l.get("text", ""), [t.get("surface", "") for t in l["tokens"]], [str(t.get("lemma") or "") for t in l["tokens"]],
               [str(t.get("gloss") or "") for t in l["tokens"]]] for l in data["lines"]],
        "S": [[s["spans"][i]["lines"][0], s["spans"][i]["lines"][1], tr["translator"], tr.get("year"), s["spans"][i]["text"]]
              for s in data["sense"] for tr in [next(t for t in data["translations"] if t["id"] == s["tr"])] for i in range(len(s["spans"]))],
        "N": [[n.get("attach", ""), str(n.get("text", ""))] for n in data["notes"]],
    }


def build_index(repo: Path, private: bool = False, out_dir: Path | None = None) -> dict:
    from .paths import resolve_for_build
    works = []
    for m in library_order(repo, private):
        if out_dir is not None and not (out_dir / f"{m['work']}.html").exists():
            continue                                    # index what is built, so every link resolves
        work_dir, private_dir = resolve_for_build(repo, m["work"], private)
        works.append(work_record(m, assemble(work_dir, private_dir), work_dir))
    return {"v": 1, "weft": __version__, "private": private, "works": works}


def report(idx: dict) -> dict:
    """Counts and failure classes: a work with no about, no lines, or a token without a gloss is reported."""
    fails: Counter[str] = Counter()
    samples: dict[str, list[str]] = {}
    for w in idx["works"]:
        for cls, bad in (("work-no-about", not w["ab"].get("summary")), ("work-no-subjects", not w["ab"].get("subjects")),
                         ("work-no-lines", not w["L"])):
            if bad:
                fails[cls] += 1; samples.setdefault(cls, []).append(w["w"])
        for l in w["L"]:
            for i, g in enumerate(l[4], 1):
                if not g:
                    fails["token-no-gloss"] += 1; samples.setdefault("token-no-gloss", []).append(f"{l[0]}.{i}")
    return {"works": len(idx["works"]), "lines": sum(len(w["L"]) for w in idx["works"]),
            "tokens": sum(len(l[2]) for w in idx["works"] for l in w["L"]),
            "spans": sum(len(w["S"]) for w in idx["works"]), "notes": sum(len(w["N"]) for w in idx["works"]),
            "failures": dict(fails), "samples": {k: v[:5] for k, v in samples.items()}}


def write(repo: Path, out_dir: Path, private: bool = False) -> dict:
    from . import docs
    from .build import load_art
    idx = build_index(repo, private, out_dir)
    payload = json.dumps(idx, ensure_ascii=False, separators=(",", ":")).replace("<", "\\u003c")
    js_path = out_dir / "search-index.js"
    js_path.write_text(f"window.WEFT_INDEX = {payload};\n", encoding="utf-8")
    site = repo / "site"
    art = load_art(repo)
    page = ((site / "search.html").read_text().replace("{{NAV}}", docs.nav_html("search.html"))
            .replace("{{LOCKUP}}", art.get("weft-lockup", "Weft")).replace("{{FAVICON}}", art.get("favicon", ""))
            .replace("/*{{SEARCHJS}}*/", (site / "search.js").read_text()))
    (out_dir / "search.html").write_text(page, encoding="utf-8")
    r = report(idx)
    r["bytes"] = js_path.stat().st_size
    return r
