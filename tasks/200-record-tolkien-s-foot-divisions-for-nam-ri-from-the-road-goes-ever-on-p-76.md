---
id: 200
title: Record Tolkien's foot divisions for Namárië from The Road Goes Ever On p. 76 ...
state: BEGUN
priority: 4
tags:
  - tolkien
  - metre
created_at: 2026-10-30T09:03:29.018072577-05:00
updated_at: 2026-10-30T09:15:59.762901774-05:00
started_at: 2026-10-30T09:15:59.752792819-05:00
---

# Record Tolkien's foot divisions for Namárië from The Road Goes Ever On p. 76 as the line metre

## Problem

(what's wrong + root cause + evidence — fill me in)

## Approach

(the fix — fill me in)

## Acceptance

- [ ] (testable post-condition that proves the fix durably landed — fill me in)

## Notes

- 2026-10-30T14:03:29Z: Problem: Tolkien's handwritten Namárië divides every line into iambic feet with thin hairlines (line 5: Àndú|ne pél|la Vár|do tél|lumàr), matching his note that the metre is iambic in lines of 5 or 6 feet (RGEO p. 68). The page shows no metre row. Approach: read each hairline at 600 dpi; record a curated line field 'metre' (the existing metre row splits on |), status draft. Acceptance: every line's metre string reproduces the hairlines on the page, with 5 or 6 feet per line as Tolkien's note on the metre gives them, pinned in a test.
- 2026-10-30T14:15:59Z: 2026-10-30: 13 lines recorded in private/tolkien-namarie/curated/metre.yaml (draft): 1, 2, 3, 5, 6, 7 in full; parts of 4, 8, 9, 11, 13, 15, 17. Every clear hairline falls on an iambic foot boundary; Tolkien omits some (line 3 after Yéni; line 17 only él|yë). Automatic detection failed: the printed hairlines break into runs no longer than ascenders. Not recorded (faint dotted traces only): lines 10, 12, 14, the left half of 4, and the possible thin stroke after Namárië!||| in 16. Page shows the dividers (CSS .metre-text .ft + .ft::before). test_namarie_feet pins the strings. Remaining: a reading of those lines against p. 76, in print or the PDF at higher zoom.

## Log

- 2026-10-30T14:03:29Z: Created task
- 2026-10-30T14:15:59Z: State changed from TODO to BEGUN
