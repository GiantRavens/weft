"""Recordings of a work: texts/<work>/audio/recordings.yaml, and its check.

The audio layer holds two kinds of reading, and the page keeps them apart. A `scheme` reading follows one of
the work's pronunciation schemes (a reader of Greek reading the homeric scheme). A `speaker` reading is a
fluent speaker's own: a living witness in a named dialect, not a reconstruction, so it names its dialect and
never a scheme. The reader chooses the license, and may keep all rights and set conditions; Weft publishes
only what the record allows. The fields are in docs/schema.md; the speaker's side is in docs/speakers.md.

    recordings:
    - id: chcon-speaker-1
      kind: speaker                         # speaker | scheme
      dialect: Oklahoma                     # speaker: required; scheme: absent
      reader: {credit: ..., anonymous: false}
      license: rights-retained              # CC BY-SA 4.0 | CC0 | rights-retained
      conditions: [no-ai-training, display-by-permission]
      consent: {date: 2026-10-20, sheet: docs/speakers.md}
      files: {chcon.pre.1: private/texts/cherokee-constitution-1827/audio/chcon.pre.1.webm}
"""
from __future__ import annotations

from pathlib import Path

import yaml

KINDS = ("scheme", "speaker")
LICENSES = ("CC BY-SA 4.0", "CC0", "rights-retained")
CONDITIONS = ("no-ai-training", "display-by-permission")


def load(work_dir: Path) -> list:
    p = work_dir / "audio" / "recordings.yaml"
    if not p.exists():
        return []
    return (yaml.safe_load(p.read_text()) or {}).get("recordings") or []


def problems(recordings: list, schemes: list[str], ids: set[str]) -> list[tuple[str, str]]:
    """(failure class, detail) for each recording record; `ids` are the work's line and token ids."""
    out = []
    seen = set()
    for r in recordings:
        if not isinstance(r, dict):
            out.append(("audio-malformed", repr(r)[:80]))
            continue
        rid = r.get("id") or "?"
        if rid in seen:
            out.append(("audio-duplicate-id", rid))
        seen.add(rid)
        kind = r.get("kind")
        if kind not in KINDS:
            out.append(("audio-kind", f"{rid}: {kind!r}; one of {', '.join(KINDS)}"))
        elif kind == "scheme":
            if r.get("scheme") not in schemes:
                out.append(("audio-scheme", f"{rid}: {r.get('scheme')!r}; one of {', '.join(schemes)}"))
            if r.get("dialect"):
                out.append(("audio-scheme-has-dialect", f"{rid}: a scheme reading follows the scheme; a dialect belongs to a speaker reading"))
        else:
            # a speaker's reading is a modern witness, never presented as the reconstruction
            if not r.get("dialect"):
                out.append(("audio-speaker-no-dialect", f"{rid}: name the speaker's dialect (Oklahoma, Kituwah)"))
            if r.get("scheme"):
                out.append(("audio-speaker-has-scheme", f"{rid}: a speaker's reading is not a scheme reading"))
            c = r.get("consent") or {}
            if not (c.get("date") and c.get("sheet")):
                out.append(("audio-speaker-no-consent", f"{rid}: consent needs date and sheet (docs/speakers.md)"))
        reader = r.get("reader") or {}
        if not reader.get("credit") and not reader.get("anonymous"):
            out.append(("audio-reader", f"{rid}: reader needs credit, or anonymous: true"))
        lic = r.get("license")
        if lic not in LICENSES:
            out.append(("audio-license", f"{rid}: {lic!r}; one of {', '.join(LICENSES)}"))
        conds = r.get("conditions") or []
        for cond in conds:
            if cond not in CONDITIONS:
                out.append(("audio-condition", f"{rid}: {cond!r}; one of {', '.join(CONDITIONS)}"))
        if lic == "rights-retained" and "display-by-permission" not in conds:
            out.append(("audio-rights-retained", f"{rid}: a reader who keeps all rights lets Weft display by permission only"))
        if kind == "speaker" and "no-ai-training" not in conds:
            # docs/speakers.md promises this condition beside every speaker's recording
            out.append(("audio-speaker-no-ai-condition", f"{rid}: a speaker's reading carries no-ai-training"))
        files = r.get("files") or {}
        if r.get("withdrawn"):
            # withdrawal is honored by removing the files, not by hiding them
            if files:
                out.append(("audio-withdrawn-has-files", f"{rid}: remove the files of a withdrawn recording"))
            continue
        if not files:
            out.append(("audio-no-files", rid))
        for k, f in files.items():
            if k not in ids:
                out.append(("audio-unknown-id", f"{rid}: {k}"))
            # a reader who keeps all rights is never published through the repository: the file lives in
            # private/ (gitignored) or at an address Weft serves by permission
            if lic == "rights-retained" and not (str(f).startswith(("private/", "https://"))):
                out.append(("audio-rights-retained-public", f"{rid}: {k} -> {f}; keep it under private/ or at a URL"))
    return out
