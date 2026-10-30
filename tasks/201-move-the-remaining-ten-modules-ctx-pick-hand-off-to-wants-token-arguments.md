---
id: 201
title: Move the remaining ten modules' _CTX/_PICK hand-off to WANTS_TOKEN arguments ...
state: DONE
priority: 4
tags:
  - pipeline
  - refactor
created_at: 2026-10-30T09:50:11.407296133-05:00
updated_at: 2026-10-30T09:56:57.816502933-05:00
completed_at: 2026-10-30T09:56:57.816495626-05:00
---

# Move the remaining ten modules' _CTX/_PICK hand-off to WANTS_TOKEN arguments (cherokee, dutch, elvish, esperanto, german, japanese, oldfrench, portuguese, spanish, swahili), each verified byte-identical by redrafting its works, as pin 58 did for chinese and french

## Notes

- 2026-10-30T14:56:57Z: Done: dutch, elvish, esperanto, german, japanese, oldfrench, portuguese, spanish, swahili, cherokee now take etok/group/surface (WANTS_TOKEN) instead of _CTX/_PICK; each context is computed in phonemize (helpers context() or _printed_word()). Verified: all 22 works these modules serve (incl. 3 private Elvish) redrafted byte-identical (44 gen files). test_cherokee updated to the explicit interface. No module-global hand-off remains.

## Log

- 2026-10-30T14:50:11Z: Created task
- 2026-10-30T14:56:57Z: State changed from TODO to DONE
