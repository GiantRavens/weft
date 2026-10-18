"""Stewardship of a community's text: the manifest's `stewardship` block, its check, and what the page shows.

A work in the language of a living Indigenous community (a language module with `INDIGENOUS = True`) states on
its page whose transcription and translation it is, the community's own stated position where one can be
found, and whether the content is secular or ceremonial. The doctrine is in docs/about.md ("Texts of living
communities"); the block's fields are in docs/schema.md. A work outside that strand may carry the block too, and
it is held to the same rules.

    stewardship:
      community: Cherokee Nation, Eastern Band of Cherokee Indians, United Keetoowah Band
      content: secular                  # secular | ceremonial
      transcription: {by: ..., relation: outsider, method: ...}
      translations: {<translation id>: {relation: outsider}}
      position: {source: <url>, summary: ...}      # or {none_found: what was searched, and when}
      consent: {source: <url>, summary: ...}       # required when content is ceremonial
"""
from __future__ import annotations

RELATIONS = ("community", "outsider", "mixed")
# the route for readers without a GitHub account: shown beside the issue links on every page with this block
CONTACT = "speakers@weftlibrary.org"
CONTENT = ("secular", "ceremonial")


def indigenous(language_module) -> bool:
    return bool(getattr(language_module, "INDIGENOUS", False))


def problems(manifest: dict, required: bool) -> list[tuple[str, str]]:
    """(failure class, detail) for the manifest's stewardship block; `required` for an Indigenous-strand language."""
    s = manifest.get("stewardship")
    if s is None:
        return [("stewardship-missing", "this language's texts state their stewardship: add a stewardship block "
                 "(docs/schema.md)")] if required else []
    if not isinstance(s, dict):
        return [("stewardship-malformed", repr(s)[:80])]
    out = []
    for f in ("community", "content", "transcription", "position"):
        if not s.get(f):
            out.append(("stewardship-incomplete", f"no {f}"))
    if s.get("content") and s["content"] not in CONTENT:
        out.append(("stewardship-content", f"{s['content']!r}; one of {', '.join(CONTENT)}"))
    tr = s.get("transcription") or {}
    if tr:
        if not tr.get("by") or not tr.get("method"):
            out.append(("stewardship-incomplete", "transcription needs by and method"))
        if tr.get("relation") not in RELATIONS:
            out.append(("stewardship-relation", f"transcription {tr.get('relation')!r}; one of {', '.join(RELATIONS)}"))
    stated = s.get("translations") or {}
    for t in manifest.get("translations") or []:
        r = (stated.get(t.get("id")) or {}).get("relation")
        if r is None:
            out.append(("stewardship-translation-unstated", f"{t.get('id')}: whose translation is it?"))
        elif r not in RELATIONS:
            out.append(("stewardship-relation", f"translation {t.get('id')} {r!r}; one of {', '.join(RELATIONS)}"))
    pos = s.get("position") or {}
    if pos and not ((pos.get("source") and pos.get("summary")) or pos.get("none_found")):
        out.append(("stewardship-position", "position needs source and summary, or none_found saying what was searched"))
    if s.get("content") == "ceremonial":
        c = s.get("consent") or {}
        if not (c.get("source") and c.get("summary")):
            # Authority to control (CARE): ceremonial material is not set out without the community's recorded consent
            out.append(("stewardship-ceremonial-no-consent", "ceremonial content needs consent: {source, summary}"))
    return out


def for_page(manifest: dict, translations: list[dict]) -> dict | None:
    """The block as the page shows it, with each translation's translator beside its relation."""
    s = manifest.get("stewardship")
    if not isinstance(s, dict):
        return None
    names = {t.get("id"): f"{t.get('translator')} ({t.get('year')})" for t in translations}
    return {
        "community": s.get("community"),
        "content": s.get("content"),
        "transcription": {k: (s.get("transcription") or {}).get(k) for k in ("by", "relation", "method")},
        "translations": [{"who": names.get(k, k), "relation": (v or {}).get("relation")}
                         for k, v in (s.get("translations") or {}).items()],
        "position": {k: (s.get("position") or {}).get(k) for k in ("source", "summary", "none_found")},
        "contact": CONTACT,
        # the recording page build writes beside the work page (record.py)
        "record_page": f"{manifest.get('work')}.record.html",
    }
