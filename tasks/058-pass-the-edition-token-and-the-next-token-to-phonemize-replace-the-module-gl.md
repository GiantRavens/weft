---
id: 58
title: Pass the edition token and the next token to phonemize (replace the module-gl...
state: DONE
priority: 3
tags:
  - pipeline
  - refactor
created_at: 2026-09-30T19:54:19.709759-05:00
updated_at: 2026-10-30T09:50:11.397154368-05:00
completed_at: 2026-10-30T09:50:11.397148955-05:00
---

# Pass the edition token and the next token to phonemize (replace the module-global hand-off used by chinese.py _PICK and french.py)

## Notes

- 2026-10-01T00:55:09Z: Also: Pico's « » are stripped by verify_strip; the tokenizer now accepts «» ‹› as punctuation (2026-09-30), so the edition could keep them.
- 2026-10-30T14:50:11Z: Done for the two named modules: draft passes etok, group and the printed surface to phonemize for modules that set WANTS_TOKEN (chinese, french); french.context() replaces _CTX, chinese reads the reading choice from etok instead of _PICK; the Tang tone/final call gets the token too. Verified: all 9 French and Classical Chinese works redrafted byte-identical (18 gen files). Ten other modules still hand context through a global (cherokee, dutch, elvish, esperanto, german, japanese _PICK, oldfrench, portuguese, spanish, swahili): follow-up ticket.

## Log

- 2026-10-01T00:54:19Z: Created task
- 2026-10-30T14:50:11Z: State changed from TODO to DONE
