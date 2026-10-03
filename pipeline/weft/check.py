"""weft check: selftest of an assembled work. Every token has every layer; every reference resolves."""
from __future__ import annotations

from collections import Counter
from pathlib import Path

from .build import assemble


def run(repo: Path, work: str) -> dict:
    from .paths import work_dir
    data = assemble(work_dir(repo, work))
    problems: Counter[str] = Counter()
    warnings: Counter[str] = Counter()         # reported and counted, but not a failure of the work
    samples: dict[str, list[str]] = {}

    def bad(cls: str, s: str, warn: bool = False):
        (warnings if warn else problems)[cls] += 1
        samples.setdefault(cls, [])
        if len(samples[cls]) < 5:
            samples[cls].append(s)

    ids, line_ids, order = set(), [], {}
    ntok = 0
    for i, line in enumerate(data["lines"]):
        ids.add(line["id"]); line_ids.append(line["id"]); order[line["id"]] = i
        # verse carries metre; prose (unit: sentence) has none to carry
        if data["work"].get("unit") not in ("sentence", "verse", "inscription", "section") and not line.get("metre"):
            bad("line-no-metre", line["id"])
        for t in line["tokens"]:
            ntok += 1
            ids.add(t["id"])
            for f in ("surface", "lemma", "morph", "gloss"):
                v = t.get(f)
                if v is None or v == "":
                    bad(f"token-no-{f}", t["id"])
                elif not isinstance(v, str):
                    # YAML 1.1 turns bare on/off/yes/no into booleans: quote them in the overlay
                    bad(f"{f}-not-string", f"{t['id']} {v!r}")
            for s in data["schemes"]:
                rs = t.get("sound", {}).get(s, {}).get("respell")
                if not rs:
                    bad(f"token-no-sound-{s}", t["id"])
                elif rs == "?":
                    # a module's "I could not read this word" (a character with no Tang reading in Unihan, a
                    # Sumerian sign without a value): shown on the page as ?, counted here as a warning so the
                    # gap stays visible without failing a work whose manifest predicts it
                    bad(f"token-sound-unknown-{s}", t["id"], warn=True)
            if isinstance(t.get("gloss"), str) and " " in t["gloss"]:
                bad("gloss-has-space", f"{t['id']} {t['gloss']!r}")
    for m in data["_curated_missing"]:
        bad("curated-unknown-id", m["missing"])
    if not data["notes"]:
        # every work in the library carries notes; none at all means a file failed to land
        bad("no-notes", work)
    for n in data["notes"]:
        if n.get("attach") not in ids:
            bad("note-unattached", n.get("id", "?"))
        if n.get("kind") == "quoted" and not n.get("source"):
            bad("quoted-note-no-source", n.get("id", "?"))
    for s in data["sense"]:
        covered = []
        for sp in s["spans"]:
            a, b = sp["lines"]
            if a not in order or b not in order or order[a] > order[b]:
                bad("sense-bad-span", f"{s['tr']} {a}-{b}")
                continue
            covered.extend(line_ids[order[a]: order[b] + 1])
        dup = [k for k, v in Counter(covered).items() if v > 1]
        if dup:
            bad("sense-overlap", f"{s['tr']} {dup[:3]}")
        gaps = [l for l in line_ids if l not in covered]
        partial = any(t["id"] == s["tr"] and t.get("partial") for t in data["translations"])
        if gaps and not partial:            # a translation declared partial may skip lines
            bad("sense-gap", f"{s['tr']} {gaps[:3]}")
    return {"work": work, "lines": len(line_ids), "tokens": ntok,
            "translations": len(data["sense"]), "notes": len(data["notes"]),
            "problems": dict(problems), "warnings": dict(warnings), "samples": samples, "ok": not problems}
