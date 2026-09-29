"""weft acquire: fetch a work's sources into texts/<work>/sources/, never into git.

Sources are third-party files under their own licenses. The repository ships only the manifest,
which names each file, where it comes from, its license, and the sha256 we built against.
Each user reads the licenses and fetches their own copy:

    weft acquire homer-odyssey                     # list sources, licenses, and local status
    weft acquire homer-odyssey --accept-licenses   # download what is missing, verify hashes
"""
from __future__ import annotations

import hashlib
import urllib.request
from pathlib import Path

from .draft import load_manifest


def sources(m: dict) -> list[dict]:
    out = [dict(m["edition"], role="edition")]
    if m.get("treebank"):
        out.append(dict(m["treebank"], role="treebank"))
    out += [dict(t, role="translation", name=f"{t['translator']}, {t['year']}") for t in m.get("translations", [])]
    out += [dict(x, role="data") for x in m.get("sources_extra", [])]
    return [s for s in out if s.get("file")]


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def status(work_dir: Path, s: dict) -> str:
    p = work_dir / s["file"]
    if not p.exists():
        return "missing"
    if s.get("sha256") and sha256(p) != s["sha256"]:
        return "hash-mismatch"
    return "ok"


def run(work_dir: Path, accept: bool = False) -> dict:
    m = load_manifest(work_dir)
    rows = []
    for s in sources(m):
        st = status(work_dir, s)
        if st != "ok" and accept:
            p = work_dir / s["file"]
            p.parent.mkdir(parents=True, exist_ok=True)
            tmp = p.with_suffix(p.suffix + ".part")
            req = urllib.request.Request(s["url"], headers={"User-Agent": "weft-acquire/0.1"})
            with urllib.request.urlopen(req, timeout=120) as r, tmp.open("wb") as f:
                while chunk := r.read(1 << 20):
                    f.write(chunk)
            if s.get("extract"):
                # the download is a zip that changes daily; keep and hash only the member we use
                import re
                import zipfile
                with zipfile.ZipFile(tmp) as z:
                    names = [n for n in z.namelist() if re.search(s["extract"], n)]
                    data = z.read(names[0]) if names else b""
                tmp.write_bytes(data)
            got = sha256(tmp)
            if s.get("sha256") and got != s["sha256"]:
                # upstream changed since the manifest was pinned: keep it aside, do not use it
                tmp.rename(p.with_suffix(p.suffix + ".unverified"))
                st = "downloaded-hash-mismatch"
            else:
                tmp.rename(p)
                st = "downloaded"
        rows.append({
            "file": s["file"], "role": s["role"], "name": s.get("name", s.get("id")),
            "license": s.get("license"), "license_url": s.get("license_url"),
            "terms": s.get("terms"), "url": s["url"], "status": st,
        })
    need = [r for r in rows if r["status"] in ("missing", "hash-mismatch")]
    return {
        "work": m["work"],
        "sources": rows,
        "next": ("Read the licenses above, then rerun with --accept-licenses to download."
                 if need and not accept else "All sources present and verified."
                 if all(r["status"] in ("ok", "downloaded") for r in rows)
                 else "Some downloads did not match the pinned sha256; see *.unverified files."),
    }
