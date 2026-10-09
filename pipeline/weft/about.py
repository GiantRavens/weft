"""weft about: what a work is, from its Wikipedia article and Wikidata item, into texts/<work>/about.yaml.

The manifest names the article by hand, so a judgment is never made silently:

    wikipedia: {title: Inter_caetera, match: work}    # work | author | parent | none
    wikipedia: {title: Enheduanna, match: author}     # the hymns have no article; their author does
    wikipedia: {match: none}                          # nothing fits; the about goes in curated/ by hand

`match` says what the article describes. A `work` article describes this text; an `author` or `parent`
article (the poet, the collection an excerpt comes from) is still shown, labelled as such, so the page
never presents an article on Enheduanna as an article on the Temple Hymns. An optional `lang` picks
another Wikipedia (default en).

Two sources, two licenses:
- the Wikipedia lead, quoted verbatim, pinned by revision, attributed: CC BY-SA 4.0, the same license
  as texts/, so it may be committed (LICENSE-DATA.md);
- the Wikidata item's short description and three statements, instance of (P31), genre (P136) and
  main subject (P921), as English labels: CC0. These are the work's subjects, which search reads.

about.yaml is regenerable: never edit it by hand. Correct the manifest's `wikipedia` field and rerun,
or override in curated/.

`weft about all --suggest` writes nothing: for each work without a `wikipedia` field it lists search
candidates, so the field is filled with evidence in view.
"""
from __future__ import annotations

import datetime as dt
import re
import urllib.parse
from collections import Counter
from pathlib import Path

import yaml

from .scaffold import fetch_json

VERSION = "weft.about 0.1"
MATCHES = ("work", "author", "parent", "none")
PROPS = {"P31": "instance_of", "P136": "genre", "P921": "main_subject"}
QID = re.compile(r"^Q[1-9][0-9]*$")
LEAD_MIN = 200          # a first paragraph shorter than this takes the second one with it


# ---------------------------------------------------------------- pure: API replies -> record

def lead_of(extract: str) -> str:
    """The lead paragraph of a plain-text intro extract: the first paragraph, and the second as well
    when the first is a stub ('X may refer to', a one-line definition)."""
    paras = [p.strip() for p in (extract or "").split("\n") if p.strip()]
    if not paras:
        return ""
    lead = paras[0]
    if len(lead) < LEAD_MIN and len(paras) > 1:
        lead += "\n\n" + paras[1]
    return re.sub(r"[ \t]+", " ", lead)


def page_of(reply: dict) -> dict:
    """The one page of an action=query reply, with the title it resolved to after redirects.
    Raises LookupError with a failure class when the page is missing or a disambiguation page."""
    q = reply.get("query", {})
    pages = list(q.get("pages", {}).values())
    if not pages or "missing" in pages[0] or "invalid" in pages[0]:
        raise LookupError("article-missing")
    p = pages[0]
    if "disambiguation" in (p.get("pageprops") or {}):
        raise LookupError("article-disambiguation")
    return p


def subjects_of(entity: dict, labels: dict[str, str]) -> dict[str, list[dict]]:
    """instance_of, genre and main_subject from a Wikidata entity's claims, each value {id, label}.
    A value with no English label keeps its id and has no label, so nothing is invented."""
    out: dict[str, list[dict]] = {}
    for pid, name in PROPS.items():
        vals = []
        for c in entity.get("claims", {}).get(pid, []):
            dv = (c.get("mainsnak") or {}).get("datavalue") or {}
            qid = (dv.get("value") or {}).get("id") if isinstance(dv.get("value"), dict) else None
            if qid and qid not in [v["id"] for v in vals]:
                vals.append({"id": qid, **({"label": labels[qid]} if labels.get(qid) else {})})
        if vals:
            out[name] = vals
    return out


def claim_ids(entity: dict) -> list[str]:
    ids: list[str] = []
    for pid in PROPS:
        for c in entity.get("claims", {}).get(pid, []):
            v = ((c.get("mainsnak") or {}).get("datavalue") or {}).get("value")
            if isinstance(v, dict) and v.get("id") and v["id"] not in ids:
                ids.append(v["id"])
    return ids


def record(work: str, match: str, lang: str, page: dict, entity: dict | None, labels: dict[str, str], today: str) -> dict:
    title = page["title"]
    rev = page["revisions"][0]["revid"]
    url = f"https://{lang}.wikipedia.org/w/index.php?title={urllib.parse.quote(title.replace(' ', '_'))}&oldid={rev}"
    rec = {
        "work": work,
        "src": VERSION,
        "fetched": today,
        "match": match,
        "wikipedia": {
            "title": title, "lang": lang, "revision": rev, "url": url, "license": "CC BY-SA 4.0",
            "attribution": f"From the Wikipedia article “{title}” ({lang}.wikipedia.org, revision {rev}), CC BY-SA 4.0",
            "lead": lead_of(page.get("extract", "")),
        },
    }
    if entity:
        desc = ((entity.get("descriptions") or {}).get("en") or {}).get("value")
        rec["wikidata"] = {"id": entity["id"], "revision": entity.get("lastrevid"), "license": "CC0",
                           **({"description": desc} if desc else {}), **subjects_of(entity, labels)}
    return rec


# ---------------------------------------------------------------- network

def wp_api(lang: str) -> str:
    return f"https://{lang}.wikipedia.org/w/api.php"


def fetch_page(title: str, lang: str, get=fetch_json) -> dict:
    q = urllib.parse.urlencode({"action": "query", "format": "json", "redirects": 1, "titles": title,
                                "prop": "extracts|revisions|pageprops", "exintro": 1, "explaintext": 1, "rvprop": "ids"})
    return page_of(get(f"{wp_api(lang)}?{q}"))


def fetch_entity(qid: str, get=fetch_json) -> tuple[dict, dict[str, str]]:
    """The entity, then English labels for the values of its three statements, in one more call."""
    q = urllib.parse.urlencode({"action": "wbgetentities", "format": "json", "ids": qid, "props": "claims|descriptions|info", "languages": "en"})
    entity = get(f"https://www.wikidata.org/w/api.php?{q}")["entities"][qid]
    ids = claim_ids(entity)[:50]
    labels: dict[str, str] = {}
    if ids:
        q = urllib.parse.urlencode({"action": "wbgetentities", "format": "json", "ids": "|".join(ids), "props": "labels", "languages": "en"})
        for k, v in get(f"https://www.wikidata.org/w/api.php?{q}")["entities"].items():
            lab = ((v.get("labels") or {}).get("en") or {}).get("value")
            if lab:
                labels[k] = lab
    return entity, labels


def search(query: str, lang: str = "en", n: int = 3, get=fetch_json) -> list[dict]:
    q = urllib.parse.urlencode({"action": "query", "format": "json", "list": "search", "srsearch": query, "srlimit": n, "srprop": "snippet"})
    return [{"title": r["title"], "snippet": re.sub(r"<[^>]+>", "", r.get("snippet", ""))[:110]}
            for r in get(f"{wp_api(lang)}?{q}").get("query", {}).get("search", [])]


# ---------------------------------------------------------------- the step

def field(manifest: dict) -> dict | None:
    """The manifest's wikipedia field, validated. None when absent. Raises ValueError on a bad field."""
    w = manifest.get("wikipedia")
    if w is None:
        return None
    if not isinstance(w, dict) or w.get("match") not in MATCHES:
        raise ValueError(f"wikipedia.match must be one of {', '.join(MATCHES)}")
    if w["match"] != "none" and not w.get("title"):
        raise ValueError("wikipedia.title is required unless match is none")
    return w


def run_one(work_dir: Path, today: str | None = None, get=fetch_json) -> tuple[str, dict | None]:
    """(outcome, record). Outcomes: found-work, found-author, found-parent, declared-none, unnamed,
    and failure classes: bad-field, article-missing, article-disambiguation, lead-empty, fetch-failed."""
    m = yaml.safe_load((work_dir / "manifest.yaml").read_text())
    try:
        w = field(m)
    except ValueError:
        return "bad-field", None
    if w is None:
        return "unnamed", None
    if w["match"] == "none":
        return "declared-none", None
    lang = w.get("lang", "en")
    try:
        page = fetch_page(w["title"], lang, get)
        qid = (page.get("pageprops") or {}).get("wikibase_item")
        entity, labels = fetch_entity(qid, get) if qid else (None, {})
    except LookupError as e:
        return str(e), None
    except (SystemExit, OSError, KeyError, ValueError):
        return "fetch-failed", None
    rec = record(m["work"], w["match"], lang, page, entity, labels, today or dt.date.today().isoformat())
    if not rec["wikipedia"]["lead"]:
        return "lead-empty", rec
    return f"found-{w['match']}", rec


HEADER = ("# Written by `weft about` from the article named in manifest.yaml (wikipedia:). Regenerable: do not edit.\n"
          "# The lead is quoted verbatim from Wikipedia under CC BY-SA 4.0; the subjects are Wikidata labels, CC0.\n")


def write(work_dir: Path, rec: dict) -> Path:
    out = work_dir / "about.yaml"
    out.write_text(HEADER + yaml.dump(rec, allow_unicode=True, sort_keys=False, width=100))
    return out


def run(work_dirs: list[Path], get=fetch_json) -> dict:
    """Fetch and write about.yaml for each work; report outcome counts and the works in each failure class.
    Predicted vs actual: every named article is predicted to be found; each miss is listed by class."""
    outcomes: Counter[str] = Counter()
    by_class: dict[str, list[str]] = {}
    for wd in work_dirs:
        outcome, rec = run_one(wd, get=get)
        outcomes[outcome] += 1
        if rec and rec["wikipedia"]["lead"]:
            write(wd, rec)
        if not outcome.startswith("found-"):
            by_class.setdefault(outcome, []).append(wd.name)
    named = sum(n for o, n in outcomes.items() if o not in ("unnamed", "declared-none", "bad-field"))
    found = sum(n for o, n in outcomes.items() if o.startswith("found-"))
    return {"works": len(work_dirs), "outcomes": dict(sorted(outcomes.items())),
            "predicted_found": named, "actual_found": found,
            "not_found": {k: v for k, v in sorted(by_class.items())},
            "next": ("fill the wikipedia field for unnamed works (weft about all --suggest)" if outcomes["unnamed"]
                     else "write a curated about for declared-none works" if outcomes["declared-none"] else "all named")}


def suggest(work_dirs: list[Path], get=fetch_json) -> dict:
    """Search candidates for each work without a wikipedia field. Writes nothing."""
    out = {}
    for wd in work_dirs:
        m = yaml.safe_load((wd / "manifest.yaml").read_text())
        if m.get("wikipedia") is not None:
            continue
        title = re.sub(r"\s*\([^)]*\)", "", str(m["title"])).split(":")[0].strip()
        try:
            cands = search(title, get=get) + [c for c in search(f"{title} {m.get('author', '')}", get=get)]
        except SystemExit:
            cands = []
        seen, uniq = set(), []
        for c in cands:
            if c["title"] not in seen:
                seen.add(c["title"]); uniq.append(c)
        out[wd.name] = {"title": m["title"], "author": m.get("author"), "candidates": uniq[:5]}
    return out
