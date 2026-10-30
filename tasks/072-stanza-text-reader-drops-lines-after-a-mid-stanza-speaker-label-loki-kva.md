---
id: 72
title: stanza-text reader drops lines after a mid-stanza speaker label ('Loki kvað:'...
state: DONE
priority: 2
tags:
  - pipeline
  - norse
  - sensor
created_at: 2026-10-01T11:26:14.507707-05:00
updated_at: 2026-10-30T07:27:17.154472549-05:00
completed_at: 2026-10-30T07:27:17.154466452-05:00
---

# stanza-text reader drops lines after a mid-stanza speaker label ('Loki kvað:'): continue the stanza across the label (kept as a heading), and add a sensor for unnumbered text blocks; Þrymskviða worked around it with a weft-edition file

## Notes

- 2026-10-30T12:27:17Z: Cause was a blank line between the two halves of a stanza (Lokasenna 23, 33), not the speaker label: 6 lines lost. stanza_blocks keeps a verse block after a blank; speaker labels, speech-intro prose (ends in ':'), separators and prose (>70 chars) stay outside. Sensor: draft fails 'verse-outside-stanzas' for any short verse-like line left outside a stanza; 0 across all 6 stanza-text works. New lines annotated (draft), spans widened, stale manifest gap removed.

## Log

- 2026-10-01T16:26:14Z: Created task
- 2026-10-30T12:27:17Z: State changed from TODO to DONE
