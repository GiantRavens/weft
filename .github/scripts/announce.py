"""Announce what a Weft deploy published, on Bluesky and X.

Two steps, so the owner approves a post after reading it:
  compose BASE HEAD OUT.json   classify the deploy; write the post (or nothing) and a summary
  send OUT.json                post it, with the featured work's rendered page as the link card;
                               to Bluesky, and to X when its four OAuth 1.0a secrets are set

The range BASE..HEAD runs from the previous successful deploy to this one, so commits whose own
deploy was cancelled are still covered, and nothing is announced twice.

What makes a deploy worth a post (measured on weft's history, 2026-10-02):
  - a work is NEW when its texts/<work>/manifest.yaml was added
  - a work is UPDATED when its texts/<work>/ files changed by at least UPDATE_MIN lines
    (the smallest real content push was 478 lines; a notes touch-up was 33)
  - README, docs, tasks, site, pipeline and test changes never trigger a post on their own
  - an `Announce: <your words>` commit trailer always posts, in those words
One post per deploy. The work with the most changed lines is named first, and the card shows
the first work the post mentions. Stdlib only. DRY_RUN=1, or a network with no credentials: print,
do not send. Each network is sent independently: one failing does not hold back the other.

X: the same text, checked at compose time against X's 280-unit count (a link counts 23, CJK and
most non-Latin characters 2). X draws the link card itself from the page's og: tags, so no image is
uploaded. Billing (pay-per-use, checked 2026-10-02): $0.20 per post that carries a URL.
"""
from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import secrets
import time
import urllib.error
import urllib.parse
import re
import subprocess
import sys
import urllib.request
from collections import Counter
from datetime import datetime, timezone

SITE = "https://weftlibrary.org/"
PDS = "https://bsky.social/xrpc/"
LIMIT = 300            # Bluesky's limit is 300 graphemes; characters are a safe stand-in here
UPDATE_MIN = 300       # changed lines in one work's folder that count as an update worth a post
URL_RE = re.compile(r"https?://\S+?(?=[.,;:!?)\]]*(?:\s|$))")   # the sentence's punctuation is not part of the link
X_API = "https://api.x.com/2/tweets"
X_LIMIT = 280          # weighted: see x_length
X_URL = 23             # every link counts as a t.co link of 23
X_KEYS = ("X_API_KEY", "X_API_SECRET", "X_ACCESS_TOKEN", "X_ACCESS_SECRET")
# twitter-text v3 weighting: these code point ranges count 1, everything else 2
X_LIGHT = ((0, 4351), (8192, 8205), (8208, 8223), (8242, 8247))


def git(*args: str) -> str:
    return subprocess.run(["git", *args], check=True, capture_output=True, text=True).stdout


def manifest_field(text: str, key: str) -> str:
    m = re.search(rf"^{key}:\s*(.+?)\s*(?:#.*)?$", text, re.M)
    return m.group(1).strip().strip("\"'") if m else ""


def short(title: str) -> str:
    """The name a list of works can carry; the card and the page give the full title.
    'Völuspá (The Seeress's Prophecy)' -> 'Völuspá'; 'Il Principe, chapters 17 and 18: ...' ->
    'Il Principe'; 'Sunzi, The Art of War (孫子兵法), chapter 1' -> 'Sunzi, The Art of War'.
    A manifest's short_title overrides this."""
    t = re.sub(r"\s*\([^)]*\)", "", title)
    t = t.split(":", 1)[0]
    t = re.split(r",\s+(?=[a-z0-9])", t, maxsplit=1)[0]
    return t.strip() or title


def works_at(head: str) -> dict[str, dict]:
    out = {}
    for path in git("ls-tree", "-r", "--name-only", head, "texts/").split():
        m = re.fullmatch(r"texts/([^/]+)/manifest\.yaml", path)
        if m:
            text = git("show", f"{head}:{path}")
            title = manifest_field(text, "title") or m.group(1)
            out[m.group(1)] = {"work": m.group(1), "title": title, "short": manifest_field(text, "short_title") or short(title),
                               "author": manifest_field(text, "author"), "url": f"{SITE}{m.group(1)}.html"}
    return out


def classify(base: str, head: str, works: dict) -> tuple[list[dict], list[dict]]:
    added = {p.split("/")[1] for p in
             git("diff", "--name-only", "--diff-filter=A", f"{base}..{head}", "--", "texts/*/manifest.yaml").split()}
    lines: Counter = Counter()
    for row in git("diff", "--numstat", f"{base}..{head}", "--", "texts/").splitlines():
        a, d, path = row.split("\t", 2)
        m = re.match(r"texts/([^/]+)/", path)
        if m and m.group(1) in works:
            lines[m.group(1)] += (0 if a == "-" else int(a)) + (0 if d == "-" else int(d))
    new = [dict(works[w], lines=lines[w]) for w in added if w in works]
    upd = [dict(works[w], lines=n) for w, n in lines.items() if w not in added and n >= UPDATE_MIN]
    by_size = lambda xs: sorted(xs, key=lambda x: -x["lines"])
    return by_size(new), by_size(upd)


def announcements(base: str, head: str) -> list[str]:
    log = git("log", "--reverse", "--format=%B%x1e", f"{base}..{head}")
    return [m.strip() for entry in log.split("\x1e") for m in re.findall(r"^Announce:\s*(.+)$", entry, re.M)]


def listing(items: list[dict], room: int) -> str:
    """'A, B and C', dropping names into 'and N more' until it fits in room characters."""
    names = [x["short"] for x in items]
    for k in range(len(names), 0, -1):
        shown, rest = names[:k], len(names) - k
        s = (", ".join(shown[:-1]) + " and " + shown[-1]) if len(shown) > 1 and not rest else ", ".join(shown)
        s += f" and {rest} more" if rest else ""
        if len(s) <= room:
            return s
    return f"{len(names)} works"


def first_mentioned(text: str, works: dict) -> dict | None:
    """The work the post names first: a page link, else a title, else a folder name."""
    hits = []
    for w in works.values():
        for needle in (w["url"], w["short"], w["work"]):
            i = text.find(needle)
            if i >= 0:
                hits.append((i, w))
                break
    return min(hits, key=lambda h: h[0])[1] if hits else None


def compose(base: str, head: str) -> dict | None:
    works = works_at(head)
    new, upd = classify(base, head, works)
    said = announcements(base, head)
    if said:
        text = "\n".join(said)
        featured = first_mentioned(text, works) or (new + upd or [None])[0]
        if not URL_RE.search(text):
            text += "\n" + (featured["url"] if featured else SITE)
    elif new or upd:
        featured = (new or upd)[0]
        link = featured["url"]
        room = LIMIT - len(link) - 40
        parts = []
        if new:
            parts.append(f"New in Weft: {listing(new, room // (2 if upd else 1))}.")
        if upd:
            parts.append(f"{'Updated' if new else 'Updated in Weft'}: {listing(upd, room // (2 if new else 1))}.")
        text = " ".join(parts) + "\n" + link
    else:
        return None
    if len(text) > LIMIT:
        raise SystemExit(f"post is {len(text)} characters, over {LIMIT}; shorten the Announce line:\n{text}")
    if x_length(text) > X_LIMIT:
        raise SystemExit(f"post counts {x_length(text)} on X, over {X_LIMIT}; shorten the Announce line:\n{text}")
    card = featured or {"work": "index", "title": "Weft", "author": "", "url": SITE}
    link = URL_RE.search(text)
    return {"text": text, "card": {"uri": link.group() if link else card["url"],
                                   "title": f"{card['title']} · Weft" if featured else "Weft",
                                   "description": (card["author"] + ". " if card["author"] else "")
                                                  + "The original text line by line, with sound and gloss.",
                                   "thumb": f"{SITE}previews/{card['work']}.jpg" if featured else ""},
            "new": [w["work"] for w in new], "updated": [w["work"] for w in upd]}


def link_facets(text: str) -> list[dict]:
    """Bluesky links are byte ranges in UTF-8, not character offsets."""
    out = []
    for m in URL_RE.finditer(text):
        start = len(text[:m.start()].encode())
        out.append({"index": {"byteStart": start, "byteEnd": start + len(m.group().encode())},
                    "features": [{"$type": "app.bsky.richtext.facet#link", "uri": m.group()}]})
    return out


def xrpc(method: str, body: bytes | dict, token: str | None = None, ctype: str = "application/json") -> dict:
    data = body if isinstance(body, bytes) else json.dumps(body).encode()
    headers = {"Content-Type": ctype, **({"Authorization": f"Bearer {token}"} if token else {})}
    with urllib.request.urlopen(urllib.request.Request(PDS + method, data=data, headers=headers), timeout=30) as r:
        return json.load(r)


def send(post: dict, identifier: str, password: str) -> str:
    s = xrpc("com.atproto.server.createSession", {"identifier": identifier, "password": password})
    card = post["card"]
    external = {"uri": card["uri"], "title": card["title"], "description": card["description"]}
    if card.get("thumb"):
        try:
            with urllib.request.urlopen(card["thumb"], timeout=30) as r:
                img = r.read()
            external["thumb"] = xrpc("com.atproto.repo.uploadBlob", img, s["accessJwt"], "image/jpeg")["blob"]
        except Exception as e:  # a missing image should be seen, not silently dropped
            print(f"::warning::card image not attached ({card['thumb']}): {e}")
    record = {"$type": "app.bsky.feed.post", "text": post["text"], "langs": ["en"],
              "createdAt": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
              "facets": link_facets(post["text"]),
              "embed": {"$type": "app.bsky.embed.external", "external": external}}
    r = xrpc("com.atproto.repo.createRecord",
             {"repo": s["did"], "collection": "app.bsky.feed.post", "record": record}, s["accessJwt"])
    return f"https://bsky.app/profile/{s['handle']}/post/{r['uri'].rsplit('/', 1)[-1]}"


def x_length(text: str) -> int:
    """The length X counts: links are 23, characters outside the light ranges are 2."""
    n, pos = 0, 0
    for m in URL_RE.finditer(text):
        n += sum(1 if any(a <= ord(c) <= b for a, b in X_LIGHT) else 2 for c in text[pos:m.start()]) + X_URL
        pos = m.end()
    return n + sum(1 if any(a <= ord(c) <= b for a, b in X_LIGHT) else 2 for c in text[pos:])


def oauth1_header(method: str, url: str, keys: dict, params: dict | None = None,
                  nonce: str | None = None, timestamp: str | None = None) -> str:
    """OAuth 1.0a user-context Authorization header (HMAC-SHA1). A JSON body is not signed;
    only query or form parameters are. Access tokens made in the X console do not expire."""
    q = lambda s: urllib.parse.quote(str(s), safe="~")
    oauth = {"oauth_consumer_key": keys["X_API_KEY"], "oauth_nonce": nonce or secrets.token_hex(16),
             "oauth_signature_method": "HMAC-SHA1", "oauth_timestamp": timestamp or str(int(time.time())),
             "oauth_token": keys["X_ACCESS_TOKEN"], "oauth_version": "1.0"}
    pairs = sorted((q(k), q(v)) for k, v in {**oauth, **(params or {})}.items())
    base = "&".join([method.upper(), q(url), q("&".join(f"{k}={v}" for k, v in pairs))])
    signing_key = f"{q(keys['X_API_SECRET'])}&{q(keys['X_ACCESS_SECRET'])}"
    oauth["oauth_signature"] = base64.b64encode(hmac.new(signing_key.encode(), base.encode(), hashlib.sha1).digest()).decode()
    return "OAuth " + ", ".join(f'{q(k)}="{q(v)}"' for k, v in sorted(oauth.items()))


def send_x(post: dict, keys: dict) -> str:
    req = urllib.request.Request(X_API, data=json.dumps({"text": post["text"]}).encode(), method="POST",
                                 headers={"Content-Type": "application/json",
                                          "Authorization": oauth1_header("POST", X_API, keys)})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            data = json.load(r)["data"]
    except urllib.error.HTTPError as e:   # X explains a refusal (credits, permissions) in the body
        raise RuntimeError(f"X {e.code}: {e.read().decode(errors='replace')[:500]}") from None
    return f"https://x.com/i/web/status/{data['id']}"


def summary(md: str) -> None:
    path = os.environ.get("GITHUB_STEP_SUMMARY")
    if path:
        with open(path, "a") as f:
            f.write(md + "\n")


def main(argv: list[str]) -> int:
    if argv[0] == "compose":
        base, head, out = argv[1:4]
        post = compose(base, head)
        verdict = "post" if post else "quiet (no new or substantially updated work, no Announce line)"
        print(f"range {base[:8]}..{head[:8]}: {verdict}")
        if post:
            print(post["text"])
            # compose runs outside the announce environment and cannot see its secrets; the post job reports per network
            summary(f"### Post awaiting approval (Bluesky, and X where its secrets are set)\n\n```\n{post['text']}\n```\n\n"
                    f"Card: {post['card']['title']}, image {post['card']['thumb'] or 'none'}. "
                    f"Length: {len(post['text'])}/{LIMIT} on Bluesky, {x_length(post['text'])}/{X_LIMIT} on X.")
        else:
            summary(f"### No post\n\n{verdict}")
        with open(out, "w") as f:
            json.dump(post, f, ensure_ascii=False)
        gh_out = os.environ.get("GITHUB_OUTPUT")
        if gh_out:
            with open(gh_out, "a") as f:
                f.write(f"has_post={'true' if post else 'false'}\n")
        return 0
    if argv[0] == "send":
        post = json.load(open(argv[1]))
        if not post:
            print("nothing to send")
            return 0
        dry = os.environ.get("DRY_RUN") == "1"
        password = os.environ.get("BLUESKY_APP_PASSWORD", "")
        xkeys = {k: os.environ.get(k, "") for k in X_KEYS}
        targets = [("Bluesky", bool(password), lambda: send(post, os.environ["BLUESKY_IDENTIFIER"], password)),
                   ("X", all(xkeys.values()), lambda: send_x(post, xkeys))]
        failed = False
        for name, ready, go in targets:
            if dry or not ready:
                why = "DRY_RUN=1" if dry else "no credentials"
                print(f"{name}: not sent ({why}):\n{post['text']}")
                summary(f"{name}: not sent ({why})")
                continue
            try:
                url = go()
                print(f"{name}: posted {url}")
                summary(f"{name}: posted {url}")
            except Exception as e:   # the other network still gets its post
                failed = True
                print(f"::error::{name} not posted: {e}")
                summary(f"{name}: FAILED, {e}")
        return 1 if failed else 0
    raise SystemExit("usage: announce.py compose BASE HEAD OUT.json | send OUT.json")


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
