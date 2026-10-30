---
id: 114
title: 'Graduate the closeness sensor (scratchpad kirk/closeness.py) into weft: a ''we...'
state: DONE
priority: 2
tags:
  - notes
  - sensor
created_at: 2026-10-01T18:05:32.768368-05:00
updated_at: 2026-10-30T09:46:24.433479072-05:00
completed_at: 2026-10-30T09:46:24.433473146-05:00
---

# Graduate the closeness sensor (scratchpad kirk/closeness.py) into weft: a 'weft notes-check <work> --against <file>' command or a test, so every commentary-derived public note is measured (max shared run < 6 words, quotes < 15 words)

## Notes

- 2026-10-30T14:46:24Z: Done: weft notes-check <work> --against <file> (pipeline/weft/notescheck.py): longest shared word run (limit 5) and longest quotation (limit 14) per editorial note; exit 1 on any. Not applied library-wide: of 732 editorial notes, the 11 quotes of 15+ words are all from public-domain sources, which the rules allow. Try-out: Odyssey notes vs Butcher-Lang 1879 (PD) give max run 6 ('in the tenth year of the'), a common phrase. docs/schema.md; test_notes_check_measures_closeness.

## Log

- 2026-10-01T23:05:32Z: Created task
- 2026-10-30T14:46:24Z: State changed from TODO to DONE
