"""weft ocr: read a pinned page scan with Tesseract into a generated witness, and collate it with the edition.

A script without a usable text layer (Cherokee in the 1828 New Echota type, which archive.org's OCR reads as Latin)
is transcribed by hand into the edition and read a second time by machine. The machine reading is a witness, not the
text: it is written to gen/ocr/<page>.txt, and the edition names it in `ocr_check: {file}` (or `{files: [...]}`, the
pages in reading order, joined into one witness). Where the print agrees with
the edition and not the witness, the token declares the OCR's reading as `ocr` (an empty string for a word the OCR
dropped), each settled on the scan; the language module's line_checks call `witness_check`, which compares by letters
only and refuses a line with an undeclared difference. The two readings make different kinds of error (a hand
confuses look-alike signs; the machine inserts noise and misses line starts), so the disagreements are where the scan
is consulted.

    ocr:
      model: {lang: chr, url: <a commit-pinned tessdata url>, sha256: ..., license: Apache-2.0}
      pages:
      - id: title                    # writes gen/ocr/title.txt and title.yaml (the provenance)
        source: scan-title           # a sources_extra id: the scan, pinned by sha256
        crop: [960, 1500, 800, 1180] # x, y, width, height in the scan's pixels (optional)
        threshold: 50                # binarize at this percent of the grey range before reading (optional)
        psm: 6                       # Tesseract page segmentation mode (6: one block of text)
        sections: [preamble]         # the edition sections this page carries, for the collation report
      hand: curated/hand-reading.txt # optional: the first hand reading, made before the collation, kept to measure it

The report gives each line of the edition beside the stretch of the witness that best matches it, and, when the
first hand reading is kept, the error rate of each reading against the settled edition, by signs.

Needs the `tesseract` program (5.x) and Pillow (`uv pip install -e '.[images]'`). The model is downloaded once into
~/.cache/weft/tessdata/<sha256>/ and verified against the manifest's sha256 on every run.
"""
from __future__ import annotations

import difflib
import hashlib
import shutil
import subprocess
import urllib.request
from pathlib import Path

import yaml

from .draft import load_manifest

VERSION = "0.1"
CACHE = Path.home() / ".cache" / "weft" / "tessdata"


def letters(s: str, lang: str) -> str:
    """The signs that count in a comparison: the script's own letters, without punctuation, spaces or line-end hyphens."""
    if lang == "chr":
        return "".join(c for c in s if "Ꭰ" <= c <= "Ᏽ")
    return "".join(c for c in s if c.isalpha())


def distance(a: str, b: str) -> int:
    p = list(range(len(b) + 1))
    for i, x in enumerate(a, 1):
        c = [i]
        for j, y in enumerate(b, 1):
            c.append(min(p[j] + 1, c[j - 1] + 1, p[j - 1] + (x != y)))
        p = c
    return p[-1]


def best_window(seg: str, text: str) -> tuple[int, int, int]:
    """Semi-global alignment: the edit distance of `seg` against its best-matching stretch of `text`, and that
    stretch's start and end."""
    if not seg:
        return 0, 0, 0
    n = len(text)
    prev = [(0, j) for j in range(n + 1)]          # (cost, start of the stretch in text)
    for i, x in enumerate(seg, 1):
        cur = [(i, 0)]
        for j, y in enumerate(text, 1):
            cur.append(min((prev[j - 1][0] + (x != y), prev[j - 1][1]), (prev[j][0] + 1, prev[j][1]),
                           (cur[j - 1][0] + 1, cur[j - 1][1])))
        prev = cur
    end = min(range(n + 1), key=lambda j: prev[j][0])
    return prev[end][0], prev[end][1], end


def sign_diff(edition: str, witness: str) -> list[str]:
    """Each difference as `edition/witness` with a sign of context on either side; ∅ marks a sign one reading lacks."""
    out = []
    for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, edition, witness, autojunk=False).get_opcodes():
        if op != "equal":
            ctx_l, ctx_r = edition[max(0, i1 - 1):i1], edition[i2:i2 + 1]
            out.append(f"{ctx_l}[{edition[i1:i2] or '∅'}/{witness[j1:j2] or '∅'}]{ctx_r}")
    return out


_WITNESS: dict[str, str] = {}


def witness_check(etoks: list[dict], edition: dict, lang: str) -> list[tuple[str, str]]:
    """Sensor for a language module's line_checks: with the edition's `ocr_check: {file}` naming a witness written by
    weft ocr (gen/ocr/<page>.txt), the line, with each token's declared `ocr` reading in place of the settled word,
    must occur in the witness, compared by letters only (the OCR's punctuation and line-end hyphens do not count).
    A token whose `ocr` equals its own text declares nothing and is reported, so a stale reading cannot linger."""
    oc = edition.get("ocr_check")
    if not oc:
        return []
    from .paths import work_dir
    wd = work_dir(Path(__file__).resolve().parents[2], edition["work"])
    # one witness file, or several pages read in order and joined, so a word the print carries over a page still matches
    files = oc.get("files") or [oc["file"]]
    p = wd / "+".join(files)
    if str(p) not in _WITNESS:
        missing = [f for f in files if not (wd / f).exists()]
        if missing:
            return [("ocr-witness-missing", f"{', '.join(missing)}: run weft ocr {edition['work']}")]
        _WITNESS[str(p)] = "".join(letters((wd / f).read_text(encoding="utf-8"), lang) for f in files)
    out = [("ocr-reading-unneeded", t["t"]) for t in etoks if t.get("ocr") is not None and letters(t["ocr"], lang) == letters(t["t"], lang)]
    want = letters("".join(t["ocr"] if t.get("ocr") is not None else t["t"] for t in etoks), lang)
    if want not in _WITNESS[str(p)]:
        cost, a, b = best_window(want, _WITNESS[str(p)])
        out.append(("edition-not-in-ocr", " ".join(sign_diff(want, _WITNESS[str(p)][a:b]))))
    return out


def model_path(model: dict) -> Path:
    d = CACHE / model["sha256"]
    p = d / f"{model['lang']}.traineddata"
    if not p.exists():
        d.mkdir(parents=True, exist_ok=True)
        req = urllib.request.Request(model["url"], headers={"User-Agent": "weft-ocr/0.1"})
        with urllib.request.urlopen(req, timeout=120) as r:
            data = r.read()
        if hashlib.sha256(data).hexdigest() != model["sha256"]:
            raise SystemExit(f"weft ocr: the model at {model['url']} does not match the manifest's sha256")
        p.write_bytes(data)
    if hashlib.sha256(p.read_bytes()).hexdigest() != model["sha256"]:
        raise SystemExit(f"weft ocr: {p} does not match the manifest's sha256; delete it to fetch again")
    return d


def tesseract_version() -> str:
    exe = shutil.which("tesseract")
    if not exe:
        raise SystemExit("weft ocr needs the tesseract program (5.x): apt install tesseract-ocr, or brew install tesseract")
    out = subprocess.run([exe, "--version"], capture_output=True, text=True)
    return (out.stdout or out.stderr).split("\n")[0].strip()


def read_page(work_dir: Path, page: dict, sources: dict, tessdata: Path, lang: str) -> str:
    try:
        from PIL import Image
    except ImportError:
        raise SystemExit("weft ocr needs Pillow: uv pip install -e '.[images]'")
    src = sources.get(page["source"])
    if not src:
        raise SystemExit(f"weft ocr: page {page['id']}: no sources_extra entry {page['source']!r}")
    im = Image.open(work_dir / src["file"]).convert("L")
    if page.get("crop"):
        x, y, w, h = page["crop"]
        im = im.crop((x, y, x + w, y + h))
    if page.get("threshold") is not None:
        # stretch the grey range (as ImageMagick's -normalize does), then cut at the threshold
        lo, hi = im.getextrema()
        cut = lo + (hi - lo) * page["threshold"] / 100
        im = im.point(lambda v: 255 if v > cut else 0)
    out = work_dir / "gen" / "ocr"
    out.mkdir(parents=True, exist_ok=True)
    tmp = out / f".{page['id']}.png"
    im.save(tmp)
    try:
        r = subprocess.run(["tesseract", str(tmp), "-", "-l", lang, "--psm", str(page.get("psm", 6)),
                            "--tessdata-dir", str(tessdata)], capture_output=True, text=True)
    finally:
        tmp.unlink(missing_ok=True)
    if r.returncode != 0:
        raise SystemExit(f"weft ocr: tesseract failed on {page['id']}: {r.stderr.strip()[:300]}")
    return r.stdout


def edition_lines(work_dir: Path, m: dict, sections: list[str]) -> list[tuple[str, str]]:
    ed = yaml.safe_load((work_dir / m["edition"]["file"]).read_text()) or {}
    joiner = ed.get("joiner", " ")
    out = []
    for g in ed.get("sections") or []:
        if str(g["id"]) not in sections:
            continue
        for i, ln in enumerate(g["lines"], start=1):
            text = ln if isinstance(ln, str) else joiner.join(t["t"] for t in ln.get("tokens", []))
            out.append((f"{g['id']}.{i}", text))
    return out


def run(work_dir: Path) -> dict:
    m = load_manifest(work_dir)
    spec = m.get("ocr")
    if not spec:
        raise SystemExit("weft ocr: the manifest has no ocr block (see the docstring of weft.ocr)")
    model = spec["model"]
    lang = model["lang"]
    tessdata = model_path(model)
    version = tesseract_version()
    sources = {s["id"]: s for s in m.get("sources_extra") or []}
    report = {"work": m["work"], "engine": version, "model": model["sha256"][:12], "pages": []}
    witness_all = ""
    lines_all: list[tuple[str, str]] = []
    for page in spec["pages"]:
        text = read_page(work_dir, page, sources, tessdata, lang)
        (work_dir / "gen" / "ocr").mkdir(parents=True, exist_ok=True)
        (work_dir / "gen" / "ocr" / f"{page['id']}.txt").write_text(text, encoding="utf-8")
        prov = {"page": page["id"], "src": f"weft.ocr {VERSION}: {version}, model {model['lang']} sha256 {model['sha256']}",
                "scan": {"id": page["source"], "sha256": sources[page["source"]].get("sha256")},
                **{k: page[k] for k in ("crop", "threshold", "psm") if k in page},
                "note": "a machine witness, not the text: the edition is the settled reading"}
        (work_dir / "gen" / "ocr" / f"{page['id']}.yaml").write_text(yaml.dump(prov, allow_unicode=True, sort_keys=False))
        w = letters(text, lang)
        witness_all += w
        lines = edition_lines(work_dir, m, [str(s) for s in page.get("sections", [])])
        lines_all += lines
        rows = []
        for lid, line in lines:
            seg = letters(line, lang)
            cost, a, b = best_window(seg, w)
            rows.append({"line": lid, "differs": cost, **({"edition": line, "signs": sign_diff(seg, w[a:b])} if cost else {})})
        report["pages"].append({"page": page["id"], "witness_signs": len(w), "lines": len(lines),
                                "lines_differing": sum(1 for r in rows if r["differs"]), "collation": [r for r in rows if r["differs"]]})
    settled = "".join(letters(t, lang) for _, t in lines_all)
    if settled:
        rates = {"ocr": best_window(settled, witness_all)[0]}     # the witness may run past the edition's lines
        if spec.get("hand") and (work_dir / spec["hand"]).exists():
            rates["hand"] = distance(settled, letters((work_dir / spec["hand"]).read_text(encoding="utf-8"), lang))
        report["signs"] = len(settled)
        report["error_rate"] = {k: f"{v} in {len(settled)} signs ({100 * v / len(settled):.1f}%)" for k, v in rates.items()}
        # where the two readings agreed: the signs both got right is the measure of the method, not of either reading
        if "hand" in rates:
            hand = letters((work_dir / spec["hand"]).read_text(encoding="utf-8"), lang)
            # a hand sign is right where it sits in an unchanged stretch of the hand-to-settled alignment
            right = {i for op, i1, i2, _, _ in difflib.SequenceMatcher(None, hand, settled, autojunk=False).get_opcodes()
                     if op == "equal" for i in range(i1, i2)}
            agreed = {blk.a + k for blk in difflib.SequenceMatcher(None, hand, witness_all, autojunk=False).get_matching_blocks()
                      for k in range(blk.size)}
            report["agreed"] = f"{len(agreed)} signs read alike by both; {len(agreed - right)} of them wrong in the settled text"
    return report
