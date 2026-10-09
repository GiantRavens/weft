"""Reader pages from docs/: docs/<name>.md -> site/build/<name>.html.

The Markdown files stay the single source (they read on GitHub as they are). This renderer covers
only what those files use: headings, paragraphs, bullet and numbered lists, fenced code, pipe
tables, inline code, bold, italic and links. Links to another rendered doc point at its page;
other repository paths point at the file on GitHub.
"""
from __future__ import annotations

import html as H
import re
from pathlib import Path

PAGES = {"about": "About Weft", "languages": "Languages and pronunciation"}
REPO_URL = "https://github.com/GiantRavens/weft"


def _slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def _href(url: str, here: str) -> str:
    if re.match(r"^[a-z]+:", url) or url.startswith("#"):
        return url
    path, _, frag = url.partition("#")
    name = Path(path).stem
    if path.endswith(".md") and name in PAGES:
        return f"{name}.html" + (f"#{frag}" if frag else "")
    # any other repository path, resolved from docs/
    target = (Path("docs") / path).as_posix() if here == "docs" else path
    parts = []
    for p in target.split("/"):
        if p == "..":
            parts and parts.pop()
        elif p and p != ".":
            parts.append(p)
    return f"{REPO_URL}/blob/main/{'/'.join(parts)}" + (f"#{frag}" if frag else "")


def inline(text: str, here: str = "docs") -> str:
    out, pos = [], 0
    for m in re.finditer(r"`([^`]+)`|\[([^\]]+)\]\(([^)]+)\)", text):
        out.append(_emph(H.escape(text[pos:m.start()])))
        if m.group(1) is not None:
            out.append(f"<code>{H.escape(m.group(1))}</code>")
        else:
            out.append(f'<a href="{H.escape(_href(m.group(3), here))}">{inline(m.group(2), here)}</a>')
        pos = m.end()
    out.append(_emph(H.escape(text[pos:])))
    return "".join(out)


def _emph(s: str) -> str:
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    return re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"<em>\1</em>", s)


def render(md: str) -> tuple[str, list[tuple[int, str, str]]]:
    """Markdown -> (html, headings as (level, id, text))."""
    lines = md.split("\n")
    out, heads, i = [], [], 0
    para: list[str] = []

    def flush():
        if para:
            out.append(f"<p>{inline(' '.join(para))}</p>")
            para.clear()

    while i < len(lines):
        ln = lines[i]
        if ln.startswith("```"):
            flush()
            j = i + 1
            while j < len(lines) and not lines[j].startswith("```"):
                j += 1
            out.append("<pre><code>" + H.escape("\n".join(lines[i + 1:j])) + "</code></pre>")
            i = j + 1
            continue
        m = re.match(r"^(#{1,4})\s+(.*)$", ln)
        if m:
            flush()
            lvl, text = len(m.group(1)), m.group(2).strip()
            hid = _slug(text)
            heads.append((lvl, hid, text))
            out.append(f'<h{lvl} id="{hid}">{inline(text)}</h{lvl}>')
            i += 1
            continue
        if ln.startswith("|") and i + 1 < len(lines) and re.match(r"^\|[\s:|-]+\|\s*$", lines[i + 1]):
            flush()
            cells = lambda r: [c.strip() for c in r.strip().strip("|").split("|")]
            head = cells(ln)
            rows = []
            j = i + 2
            while j < len(lines) and lines[j].startswith("|"):
                rows.append(cells(lines[j]))
                j += 1
            out.append('<div class="tbl"><table><thead><tr>' + "".join(f"<th>{inline(c)}</th>" for c in head)
                       + "</tr></thead><tbody>" + "".join("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>" for r in rows)
                       + "</tbody></table></div>")
            i = j
            continue
        m = re.match(r"^(\s*)(-|\d+\.)\s+(.*)$", ln)
        if m:
            flush()
            tag = "ol" if m.group(2)[0].isdigit() else "ul"
            items = []
            while i < len(lines):
                m = re.match(r"^(\s*)(-|\d+\.)\s+(.*)$", lines[i])
                if m and ((tag == "ol") == m.group(2)[0].isdigit()) and len(m.group(1)) < 2:
                    items.append([m.group(3)])
                elif items and lines[i].startswith("  ") and lines[i].strip():
                    if lines[i].strip().startswith("```"):        # a code block inside an item
                        j = i + 1
                        while j < len(lines) and not lines[j].strip().startswith("```"):
                            j += 1
                        items[-1].append("\x00" + "\n".join(l.strip() if not l.startswith("      ") else l[3:] for l in lines[i + 1:j]))
                        i = j
                    else:
                        items[-1].append(lines[i].strip())
                elif not lines[i].strip() and i + 1 < len(lines) and lines[i + 1].startswith("  "):
                    pass
                else:
                    break
                i += 1
            def item(parts):
                text = " ".join(p for p in parts if not p.startswith("\x00"))
                code = "".join(f"<pre><code>{H.escape(p[1:])}</code></pre>" for p in parts if p.startswith("\x00"))
                return f"<li>{inline(text)}{code}</li>"
            out.append(f"<{tag}>" + "".join(item(p) for p in items) + f"</{tag}>")
            continue
        if not ln.strip():
            flush()
        else:
            para.append(ln.strip())
        i += 1
    flush()
    return "\n".join(out), heads


NAV = [("index.html", "The library"), ("search.html", "Search"), ("about.html", "About Weft"), ("languages.html", "Languages and pronunciation")]


def nav_html(current: str) -> str:
    return '<nav class="docnav">' + " · ".join(
        f'<span aria-current="page">{t}</span>' if href == current else f'<a href="{href}">{t}</a>' for href, t in NAV) + "</nav>"


PAGE = """<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1"><title>{{TITLE}} · Weft</title>
<link rel="icon" type="image/svg+xml" href="{{FAVICON}}">
<link href="https://fonts.googleapis.com/css2?family=Gentium+Book+Plus:ital,wght@0,400;0,700;1,400&family=Inter:wght@400;600&display=swap" rel="stylesheet">
<style>
:root{--bg:#f6f1e6;--ink:#221d16;--soft:#5d5446;--rule:#ddd3c0;--accent:#9a3b1f;--code:#ebe3d3;color-scheme:light}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#15130f;--ink:#ece4d2;--soft:#b9ad96;--rule:#342f26;--accent:#e08a5f;--code:#221f19;color-scheme:dark}}
:root[data-theme="dark"]{--bg:#15130f;--ink:#ece4d2;--soft:#b9ad96;--rule:#342f26;--accent:#e08a5f;--code:#221f19;color-scheme:dark}
body{margin:0;background:var(--bg);color:var(--ink);font:1.08rem/1.6 "Gentium Book Plus",Palatino,serif}
main{max-width:760px;margin:0 auto;padding:40px 16px 80px}
.lockup{display:block;width:150px;color:var(--ink);margin:0 0 14px}.lockup svg{width:100%;height:auto}
.docnav{font:600 .78rem/1.4 Inter,system-ui,sans-serif;letter-spacing:.04em;color:var(--soft);margin:0 0 28px}
.docnav a{color:var(--accent);text-decoration:none}.docnav a:hover{text-decoration:underline}.docnav span{color:var(--ink)}
h1{font-size:2.1rem;line-height:1.2;margin:.2rem 0 1rem}
h2{font-size:1.45rem;margin:2.2rem 0 .6rem;padding-top:.6rem;border-top:1px solid var(--rule)}
h3{font-size:1.15rem;margin:1.6rem 0 .4rem}h4{font:600 .8rem/1.3 Inter,system-ui,sans-serif;letter-spacing:.1em;text-transform:uppercase;color:var(--accent);margin:1.4rem 0 .3rem}
a{color:var(--accent)}p,li{margin:.5rem 0}ul,ol{padding-left:1.4rem}
code{font:.86em/1.4 ui-monospace,Menlo,monospace;background:var(--code);padding:.1em .3em;border-radius:3px}
pre{background:var(--code);padding:12px 14px;border-radius:6px;overflow-x:auto}pre code{background:none;padding:0}
.tbl{overflow-x:auto;margin:1rem 0}table{border-collapse:collapse;font:.85rem/1.45 Inter,system-ui,sans-serif}
th,td{border-bottom:1px solid var(--rule);padding:6px 10px 6px 0;text-align:left;vertical-align:top}th{color:var(--soft);font-weight:600}
.toc{font:.85rem/1.6 Inter,system-ui,sans-serif;color:var(--soft);margin:0 0 1.6rem}.toc a{text-decoration:none}
.toc ul{list-style:none;padding:0;margin:0;columns:2;column-gap:28px}.toc li{margin:0}
@media (max-width:560px){.toc ul{columns:1}}
@media print{.docnav,.toc{display:none}a{color:inherit}}
</style></head><body><main><a class="lockup" href="index.html" aria-label="Weft library">{{LOCKUP}}</a>{{NAV}}
{{BODY}}
</main></body></html>
"""


def build_docs(repo: Path, out_dir: Path, art: dict) -> list[Path]:
    written = []
    for name, title in PAGES.items():
        src = repo / "docs" / f"{name}.md"
        if not src.exists():
            continue
        body, heads = render(src.read_text())
        h2 = [(i, t) for lvl, i, t in heads if lvl == 2]
        toc = ('<div class="toc"><ul>' + "".join(f'<li><a href="#{i}">{inline(t)}</a></li>' for i, t in h2)
               + "</ul></div>") if len(h2) > 5 else ""
        page = out_dir / f"{name}.html"
        page.write_text(PAGE.replace("{{TITLE}}", H.escape(title)).replace("{{NAV}}", nav_html(page.name))
                        .replace("{{BODY}}", body.replace("</h1>", "</h1>" + toc, 1))
                        .replace("{{LOCKUP}}", art.get("weft-lockup", "Weft")).replace("{{FAVICON}}", art.get("favicon", "")))
        written.append(page)
    return written
