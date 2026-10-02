"""Link-preview images: each built page as a reader first sees it, at the 1200x630 size
that Bluesky, X and messaging apps show in a link card.

Renders site/build/<work>.html in headless Chromium after the page's own script has laid
out the text, and writes site/build/previews/<work>.jpg. The page's og:image tag (written
by build.render) points at that file. Needs the optional extra: uv pip install -e '.[previews]'
and `playwright install chromium`.
"""
from __future__ import annotations

from pathlib import Path

WIDTH, HEIGHT = 1200, 630
QUALITY = 82          # JPEG; keeps a text-heavy card well under Bluesky's 1 MB blob limit
MAX_BYTES = 950_000


def run(build_dir: Path, works: list[str]) -> dict:
    from playwright.sync_api import sync_playwright

    out_dir = build_dir / "previews"
    out_dir.mkdir(exist_ok=True)
    report = {"written": 0, "missing_page": [], "not_rendered": [], "oversize": []}
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": WIDTH, "height": HEIGHT}, device_scale_factor=1)
        for w in works:
            src = build_dir / f"{w}.html"
            if not src.exists():
                report["missing_page"].append(w)
                continue
            page.goto(src.resolve().as_uri(), wait_until="networkidle")
            # the text is drawn by weft.js from window.WEFT; an empty <main> means the page failed
            try:
                page.wait_for_function("document.querySelector('#text')?.children.length > 0", timeout=10_000)
            except Exception:
                report["not_rendered"].append(w)
                continue
            # the card shows the text: the copyright and reconstruction notices stay on the page,
            # but in a 630-pixel card they can push every line of the text out of frame
            page.add_style_tag(content="#ref-note, #sound-note { display: none !important; }")
            page.evaluate("document.fonts.ready")
            out = out_dir / f"{w}.jpg"
            page.screenshot(path=str(out), type="jpeg", quality=QUALITY)
            if out.stat().st_size > MAX_BYTES:
                page.screenshot(path=str(out), type="jpeg", quality=60)
                if out.stat().st_size > MAX_BYTES:
                    report["oversize"].append(w)
            report["written"] += 1
        browser.close()
    return report
