---
id: 19
title: Keep veil reveals across re-render (scheme or translation switch currently re...
state: DONE
priority: 4
tags:
  - site
created_at: 2026-09-29T14:14:38.200496-05:00
updated_at: 2026-10-30T09:20:39.121416238-05:00
completed_at: 2026-10-30T09:20:39.121410719-05:00
---

# Keep veil reveals across re-render (scheme or translation switch currently resets them)

## Notes

- 2026-10-30T14:20:39Z: Fixed in site/weft.js: reveals kept in a Set keyed 'g:<token id>' and 't:<translation>:<span>', reapplied in renderText; cleared when the veil is turned off. Browser-tested on homer-odyssey: gloss and translation reveals survive a scheme switch; veil off clears.

## Log

- 2026-09-29T19:14:38Z: Created task
- 2026-10-30T14:20:39Z: State changed from TODO to DONE
