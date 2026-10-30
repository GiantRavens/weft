---
id: 197
title: Encode Tolkien's pause marks (| || |||) for Namárië from The Road Goes Ever O...
state: DONE
priority: 3
tags:
  - tolkien
  - sound
created_at: 2026-10-30T07:46:11.993996411-05:00
updated_at: 2026-10-30T09:03:29.009011728-05:00
completed_at: 2026-10-30T09:03:29.009005993-05:00
---

# Encode Tolkien's pause marks (| || |||) for Namárië from The Road Goes Ever On p. 76

## Problem

(what's wrong + root cause + evidence — fill me in)

## Approach

(the fix — fill me in)

## Acceptance

- [ ] (testable post-condition that proves the fix durably landed — fill me in)

## Notes

- 2026-10-30T12:46:12Z: Problem: Tolkien's handwritten Latin-letter Namárië (RGEO 3rd ed., PDF p. 92) marks the pauses of the chant: 'The marks | || ||| indicate the pauses in the chant in ascending order of time-length and tone-fall.' The sound row does not show them. Approach: read each mark's position off the page by hand, record it as a curated per-line or per-token field with status draft, show it in the sound row and the key. Acceptance: every mark on the page appears on the built page in the same place, a test pins their positions, and the key quotes Tolkien's definition.
- 2026-10-30T14:03:28Z: 2026-10-30: done. 16 marks read off RGEO p. 76 at 600 dpi (pz-092), recorded in private/tolkien-namarie/curated/pauses.yaml as token field 'pause'; weft.js shows it after the respelling (.snd .pause), key entry quotes Tolkien; test_namarie_pauses pins every position. Hairlines on the same page are foot divisions, told apart from single pauses by the iambic scansion (luini,| is a pause; tintilar| is a foot boundary).

## Log

- 2026-10-30T12:46:11Z: Created task
- 2026-10-30T14:03:29Z: State changed from TODO to DONE
