---
id: 167
title: Fix oshb_to_ud IndexError on a Daniel chapter other than 5 (found by the 2026...
state: DONE
priority: 3
tags:
  - hebrew
  - pipeline
created_at: 2026-10-10T16:00:08.472319562-05:00
updated_at: 2026-10-30T09:18:14.190830584-05:00
completed_at: 2026-10-30T09:18:14.190822337-05:00
---

# Fix oshb_to_ud IndexError on a Daniel chapter other than 5 (found by the 2026-10-10 skeptic scan of load_oshb over whole books); also sound the prefixed divine name (לַיהוָה, ~40 cases Gen+Deut) instead of reporting qere-perpetuum-prefixed

## Notes

- 2026-10-30T14:18:14Z: Fixed: substring membership ('' in '123') replaced by tuples in oshb_to_ud; empty features dropped; all 12 Daniel chapters load. Prefixed divine name now sounded (prefix as written + אדני minus the aleph's hateph; accents from the unprefixed part only): 21 cases in Genesis. qere-perpetuum-prefixed failure class retired. test_oshb_short_segments_and_prefixed_divine_name.

## Log

- 2026-10-10T21:00:08Z: Created task
- 2026-10-30T14:18:14Z: State changed from TODO to DONE
