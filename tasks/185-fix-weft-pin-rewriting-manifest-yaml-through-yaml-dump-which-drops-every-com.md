---
id: 185
title: Fix weft pin rewriting manifest.yaml through yaml.dump, which drops every com...
state: DONE
priority: 2
tags:
  - pipeline
  - bug
  - pin
created_at: 2026-10-18T04:45:05.051883394-05:00
updated_at: 2026-10-18T05:07:27.729987297-05:00
completed_at: 2026-10-18T05:07:27.729982471-05:00
---

# Fix weft pin rewriting manifest.yaml through yaml.dump, which drops every comment (hit saga-grettir 2026-10-18; restored from git): append the sources_extra entry as text, or round-trip with comments kept

## Notes

- 2026-10-18T10:07:27Z: Fixed for sources_extra: a manifest with comments is edited as text (_add_source_text in scaffold.py), tested on saga-grettir (comment count unchanged). --edition still rewrites through yaml.dump; it is used on freshly scaffolded manifests, which carry one comment.

## Log

- 2026-10-18T09:45:05Z: Created task
- 2026-10-18T10:07:27Z: State changed from TODO to DONE
