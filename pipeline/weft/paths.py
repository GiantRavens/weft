"""Where a work lives: public under texts/, or private under private/.

A folder private/<work>/ is one of two things:
- an overlay on the public work of the same name (licensed translations, your own curated
  changesets, notes that quote at length), read only by a private build; or
- a whole private work, when no public work has that name: manifest, edition, gen, curated,
  sense and notes, all under private/<work>/.

private/ is gitignored, and nothing in it reaches the public site: the public build refuses a
private work, and the public library lists only texts/.
"""
from __future__ import annotations

from pathlib import Path


def public_dir(repo: Path, work: str) -> Path:
    return repo / "texts" / work


def private_dir(repo: Path, work: str) -> Path:
    return repo / "private" / work


def is_private_work(repo: Path, work: str) -> bool:
    """A private work: has its own manifest under private/ and no public work of that name."""
    return (not (public_dir(repo, work) / "manifest.yaml").exists()
            and (private_dir(repo, work) / "manifest.yaml").exists())


def work_dir(repo: Path, work: str) -> Path:
    """The folder holding the work's manifest and layers (texts/<work> or private/<work>).
    Used by every step that does not publish (acquire, draft, check, align)."""
    if is_private_work(repo, work):
        return private_dir(repo, work)
    return public_dir(repo, work)


def resolve_for_build(repo: Path, work: str, private: bool) -> tuple[Path, Path | None]:
    """(work_dir, overlay_dir) for a build. A public build never touches private/."""
    if is_private_work(repo, work):
        if not private:
            raise SystemExit(f"weft: {work} is a private work (private/{work}); build it with --private")
        return private_dir(repo, work), None
    overlay = private_dir(repo, work) if private and private_dir(repo, work).is_dir() else None
    return public_dir(repo, work), overlay


def private_works(repo: Path) -> list[str]:
    root = repo / "private"
    if not root.is_dir():
        return []
    return sorted(p.parent.name for p in root.glob("*/manifest.yaml") if is_private_work(repo, p.parent.name))
