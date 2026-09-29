---
id: 4
title: 'pipeline acquire: fetch Perseus edition + AGDT treebank + Butler epub into so...'
state: DONE
priority: 2
tags:
  - phase1
  - pipeline
created_at: 2026-09-29T13:54:31.658832-05:00
updated_at: 2026-09-29T14:23:22.543424-05:00
completed_at: 2026-09-29T14:23:22.543419-05:00
---

# pipeline acquire: fetch Perseus edition + AGDT treebank + Butler epub into sources/ with sha256

## Notes

- 2026-09-29T19:14:38Z: Partial: sources fetched by hand with sha256 pinned in manifest; weft draft verifies hashes (source-hash-drift class). Still needed: an acquire subcommand that fetches from manifest URLs.
- 2026-09-29T19:23:22Z: Done: weft acquire lists sources with license links and local status; --accept-licenses downloads missing files and verifies sha256 (mismatch saved as *.unverified). sources/ gitignored except README; draft points to acquire when a source is missing.

## Log

- 2026-09-29T18:54:31Z: Created task
- 2026-09-29T19:23:22Z: State changed from TODO to DONE
