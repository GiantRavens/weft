---
id: 153
title: Update weft's link base for the new domain weftlibrary.org (domains session s...
state: DONE
priority: 2
tags:
  - domain
  - announce
created_at: 2026-10-02T20:52:18.053107548-05:00
updated_at: 2026-10-04T10:22:50.890576301-05:00
started_at: 2026-10-04T10:16:19.014359816-05:00
completed_at: 2026-10-04T10:22:50.890563724-05:00
---

# Update weft's link base for the new domain weftlibrary.org (domains session sets the GitHub Pages custom domain; old giantravens.github.io/weft/* links will redirect)

## Notes

- 2026-10-03T01:52:18Z: From the domains session (2026-10-02): captain chose weftlibrary.org (+ weftlibrary.com redirecting to it), registered at Cloudflare. When it goes live, GitHub Pages serves the library at the apex https://weftlibrary.org/ and giantravens.github.io/weft/* redirects there. Places with the old base: pipeline/weft/build.py SITE_URL default (og:url/og:image), .github/scripts/announce.py SITE (post links + card thumbnails), README links. GitHub redirects keep old links working, but post links and link cards should use the new address. Do NOT set the custom domain yourselves; the domains session does it together with DNS.
- 2026-10-03T03:16:11Z: 2026-10-02 22:2x: LIVE. https://weftlibrary.org/ serves the library (GitHub Pages custom domain set by the domains session, cert approved, HTTPS enforced); giantravens.github.io/weft/* 301s to weftlibrary.org/*; weftlibrary.com 302s to it. Over to the weft session: switch SITE_URL (build.py) and SITE (announce.py) to https://weftlibrary.org/ and update README links. Newsletter (Kit, From skip@weftlibrary.org) + PostHog are next, set up by the domains session; the template work will come as a separate task.

## Log

- 2026-10-03T01:52:18Z: Created task
- 2026-10-04T15:16:19Z: State changed from TODO to BEGUN
- 2026-10-04T15:22:50Z: State changed from BEGUN to DONE
