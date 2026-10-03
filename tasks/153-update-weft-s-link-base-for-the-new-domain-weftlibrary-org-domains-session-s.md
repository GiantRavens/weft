---
id: 153
title: Update weft's link base for the new domain weftlibrary.org (domains session s...
state: TODO
priority: 2
tags:
  - domain
  - announce
created_at: 2026-10-02T20:52:18.053107548-05:00
updated_at: 2026-10-02T20:52:18.065467615-05:00
---

# Update weft's link base for the new domain weftlibrary.org (domains session sets the GitHub Pages custom domain; old giantravens.github.io/weft/* links will redirect)

## Notes

- 2026-10-03T01:52:18Z: From the domains session (2026-10-02): captain chose weftlibrary.org (+ weftlibrary.com redirecting to it), registered at Cloudflare. When it goes live, GitHub Pages serves the library at the apex https://weftlibrary.org/ and giantravens.github.io/weft/* redirects there. Places with the old base: pipeline/weft/build.py SITE_URL default (og:url/og:image), .github/scripts/announce.py SITE (post links + card thumbnails), README links. GitHub redirects keep old links working, but post links and link cards should use the new address. Do NOT set the custom domain yourselves; the domains session does it together with DNS.

## Log

- 2026-10-03T01:52:18Z: Created task
