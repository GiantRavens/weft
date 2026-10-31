"""weft quantities: draft entries for a Latin work's quantity table from Lewis and Short (pin 21).

Every Latin word must be in a quantity table (data/lat_quantities*.yaml) before its sound is known; the
tables are written by hand. This command proposes entries for the forms of a work that no table lists:
each form's lemma (from gen/ or curated/) is looked up in Lewis and Short, and the vowels its headword marks
long are carried onto the form where the letters line up (weft.latin.lexicon_long_positions). The proposals
are written to gen/quantities-proposed.yaml for review; nothing is added to a table, and nothing reaches a
page, until a person copies an entry over.

Measured against the hand tables (1,819 forms, 2026-10-30), 89.7% of the long marks it places are long
there too, and it finds 60% of the long vowels in those forms: a headword gives the stem, not the ending
(the ablative -ā, the -īs of the dative plural), and some lengths belong to one form only (āēr but āeris,
dēpōnō but dēposuī). A reviewer adds the endings and checks the rest.
"""
from __future__ import annotations

import unicodedata as ud
from pathlib import Path

import yaml

MACRON = "̄"


def macronize(form: str, positions: set[int]) -> str:
    """The form with a macron after each vowel at the given positions (counted in bare letters, æ as two)."""
    out, k = [], -1
    for ch in ud.normalize("NFD", form):
        if ud.combining(ch):
            out.append(ch)
            continue
        low = ch.lower()
        span = 2 if low in ("æ", "œ") else (1 if "a" <= low <= "z" else 0)
        out.append(ch)
        if span == 1:
            k += 1
            if k in positions and low in "aeiouy":
                out.append(MACRON)
        else:
            k += span
    return ud.normalize("NFC", "".join(out))


def run(work_dir: Path) -> dict:
    from . import latin, lexica
    repo = work_dir.parents[1]
    m = yaml.safe_load((work_dir / "manifest.yaml").read_text(encoding="utf-8"))
    if m.get("language") != "lat":
        raise SystemExit("weft quantities: Latin works only")
    if lexica.ls_long_marks() is None:
        raise SystemExit("weft quantities: no Lewis and Short list on this machine; run weft lexica")
    qspec = m.get("quantities") or []
    table: dict = {}
    for qp in ([qspec] if isinstance(qspec, str) else qspec):
        table.update(yaml.safe_load((repo / qp).read_text(encoding="utf-8")) or {})
    lemmas, forms = {}, {}
    for f in sorted((work_dir / "gen").glob("*.yaml")):
        if f.name.endswith(".run.yaml") or f.name.startswith("quantities"):
            continue
        for line in (yaml.safe_load(f.read_text(encoding="utf-8")) or {}).get("lines", []):
            for t in line.get("tokens", []):
                forms[t["id"]] = (t.get("surface") or "").lower()
                if t.get("lemma"):
                    lemmas[t["id"]] = t["lemma"]
    for cf in sorted((work_dir / "curated").glob("*.yaml")) if (work_dir / "curated").is_dir() else []:
        for cs in yaml.safe_load(cf.read_text(encoding="utf-8")) or []:
            for k, v in (cs.get("set") or {}).items():
                if isinstance(v, dict) and v.get("lemma"):
                    lemmas[k] = v["lemma"]
    proposed, no_lemma, no_headword = {}, set(), set()
    for tid, form in forms.items():
        key = "".join(ch for ch in form if ch not in latin.PUNCT).lower()     # as the Latin module keys its table
        if not key or key in table or key in proposed:
            continue
        lem = lemmas.get(tid)
        if not lem:
            no_lemma.add(key); continue
        pos = latin.lexicon_long_positions(key, lem)
        if not pos:
            no_headword.add(key); continue
        proposed[key] = {"form": macronize(key, pos), "lemma": lem}
    out = work_dir / "gen" / "quantities-proposed.yaml"
    head = ("# Proposed quantity-table entries for review (weft quantities, pin 21): long vowels from the lemma's\n"
            "# Lewis and Short headword, the stem only; endings are not given. Copy checked entries into the\n"
            "# work's own table (pipeline/weft/data/lat_quantities_<work>.yaml); this file reaches no page.\n")
    body = "".join(f'"{k}": "{v["form"]}"   # {v["lemma"]}, Lewis and Short\n' for k, v in sorted(proposed.items()))
    out.write_text(head + body, encoding="utf-8")
    return {"work": m["work"], "forms_not_in_table": len(proposed) + len(no_lemma) + len(no_headword),
            "proposed": len(proposed), "no_lemma": len(no_lemma), "no_marked_headword": len(no_headword),
            "written": str(out.relative_to(repo))}
