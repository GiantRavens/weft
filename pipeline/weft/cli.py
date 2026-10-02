"""weft CLI. Each subcommand reads the manifest, does one step, and reports counts and failure classes."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml


def repo_root() -> Path:
    p = Path.cwd().resolve()
    for d in [p, *p.parents]:
        if (d / "texts").is_dir() and (d / "pipeline" / "weft").is_dir():
            return d
    sys.exit("weft: run inside the weft repo")


def show(obj) -> None:
    print(yaml.dump(obj, allow_unicode=True, sort_keys=False, width=120).rstrip())


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="weft", description="Living interlinear editions")
    sub = ap.add_subparsers(dest="cmd", required=True)
    q = sub.add_parser("acquire", help="list a work's sources and licenses; download with --accept-licenses")
    q.add_argument("work")
    q.add_argument("--accept-licenses", action="store_true", help="I have read the licenses listed; download missing sources")
    d = sub.add_parser("draft", help="generate source, lemma, morph and sound layers into gen/")
    d.add_argument("work")
    d.add_argument("--book", type=int)
    d.add_argument("--lines", help="first-last, e.g. 1-10")
    b = sub.add_parser("build", help="assemble all layers into one self-contained HTML page")
    b.add_argument("work", help="a work's folder name, or 'all' for the whole library")
    b.add_argument("--private", action="store_true", help="include private/ overlays and private works; writes to private/build/")
    pv = sub.add_parser("previews", help="screenshot built pages for link cards (needs the previews extra)")
    pv.add_argument("work", help="a work's folder name, or 'all' for every built page")
    c = sub.add_parser("check", help="selftest: every token has every layer, every reference resolves")
    c.add_argument("work")
    al = sub.add_parser("align", help="align verse-numbered translations (USFM) to the work automatically")
    al.add_argument("work")
    ph = sub.add_parser("say", help="phonemize Greek words in every scheme")
    ph.add_argument("words", nargs="+")
    a = ap.parse_args(argv)
    repo = repo_root()
    from . import paths

    if a.cmd == "acquire":
        from . import acquire
        r = acquire.run(paths.work_dir(repo, a.work), a.accept_licenses)
        show(r)
        return 0 if r["next"].startswith("All") else 1
    if a.cmd == "draft":
        from . import draft
        first = last = None
        if a.lines:
            first, last = (int(x) for x in a.lines.split("-"))
        show(draft.run(paths.work_dir(repo, a.work), a.book, first, last))
    elif a.cmd == "build":
        from . import build
        works = ([m["work"] for m in build.library_order(repo, a.private)
                  if list((paths.work_dir(repo, m["work"]) / "gen").glob("*.yaml"))]
                 if a.work == "all" else [a.work])
        for w in works:
            out = build.run(repo, w, a.private)
            print(f"built {out.relative_to(repo)} ({out.stat().st_size // 1024} KB)")
    elif a.cmd == "previews":
        from . import build, previews
        out = repo / "site" / "build"
        works = ([m["work"] for m in build.library_order(repo) if (out / f"{m['work']}.html").exists()]
                 if a.work == "all" else [a.work])
        r = previews.run(out, works)
        show(r)
        return 0 if not (r["not_rendered"] or r["oversize"] or r["missing_page"]) else 1
    elif a.cmd == "check":
        from . import check
        r = check.run(repo, a.work)
        show(r)
        return 0 if r["ok"] else 1
    elif a.cmd == "align":
        from . import usfm
        for f in usfm.align(paths.work_dir(repo, a.work)):
            print(f"wrote {f}")
    elif a.cmd == "say":
        from . import greek
        q = yaml.safe_load((repo / "pipeline/weft/data/grc_quantities.yaml").read_text())
        for w in a.words:
            for s in ("restored", "erasmian"):
                r = greek.phonemize(w, s, q)
                print(f"{w}\t{s}\t{r['respell']}\t/{r['ipa']}/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
