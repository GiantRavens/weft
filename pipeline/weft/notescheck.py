"""weft notes-check: how close a work's editorial notes stand to a commentary they draw on.

Notes retell a scholar's argument in Weft's own words (docs/schema.md, "Quoting modern scholarship"). Given the
commentary's text as a file, this measures each editorial note: the longest run of words it shares with the
commentary, and the length of each quotation it makes. A shared run of 6 words or more, or a quotation of 15
words or more, is reported. It is run against copyrighted commentary; public-domain sources may be quoted at
length as kind: quoted, so the library-wide check does not apply these limits.
"""
from __future__ import annotations

import re
from pathlib import Path

import yaml

MAX_RUN = 5          # longest allowed shared run of words
MAX_QUOTE = 14       # longest allowed quotation, in words
QUOTE = re.compile(r"[“\"]([^”\"]+)[”\"]|‘([^’]+)’|(?<![^\W\d_])'([^']{3,}?)'(?![^\W\d_])")


def words(text: str) -> list[str]:
    return re.findall(r"[^\W_]+(?:['’][^\W_]+)*", text.lower())


def longest_shared_run(note: list[str], source_grams: dict[int, set], source: list[str]) -> tuple[int, str]:
    """The longest run of consecutive words of the note that also stands, in order, in the source."""
    best, at = 0, ""
    n = 1
    while n <= len(note):
        grams = source_grams.setdefault(n, {tuple(source[i:i + n]) for i in range(len(source) - n + 1)})
        hit = next((note[i:i + n] for i in range(len(note) - n + 1) if tuple(note[i:i + n]) in grams), None)
        if not hit:
            break
        best, at = n, " ".join(hit)
        n += 1
    return best, at


def run(work_dir: Path, against: Path) -> dict:
    source = words(against.read_text(encoding="utf-8"))
    grams: dict[int, set] = {}
    notes = []
    for f in sorted((work_dir / "notes").glob("*.yaml")):
        notes += [n for n in (yaml.safe_load(f.read_text(encoding="utf-8")) or []) if n.get("kind") == "editorial"]
    failures, rows = {}, []
    for n in notes:
        text = n.get("text", "")
        k, at = longest_shared_run(words(text), grams, source)
        quotes = [next(g for g in m.groups() if g) for m in QUOTE.finditer(text)]
        longq = max((len(q.split()) for q in quotes), default=0)
        row = {"id": n.get("id"), "longest_shared_run": k, "longest_quote": longq}
        if k > MAX_RUN:
            failures.setdefault("note-shares-run", []).append(f"{n.get('id')}: {k} words: {at}")
        if longq > MAX_QUOTE:
            failures.setdefault("note-quote-too-long", []).append(f"{n.get('id')}: {longq} words")
        rows.append(row)
    return {"work": work_dir.name, "against": str(against), "notes": len(notes),
            "max_shared_run": max((r["longest_shared_run"] for r in rows), default=0),
            "failures": {k: len(v) for k, v in failures.items()}, "samples": {k: v[:5] for k, v in failures.items()},
            "ok": not failures}
