---
id: 205
title: 'Culhwch ac Olwen opening (Arthurian prose, c. 1100): find a verifiable Welsh ...'
state: TODO
priority: 3
tags:
  - later
  - welsh
  - arthur
created_at: 2026-10-31T06:56:38.612066074-05:00
updated_at: 2026-10-31T06:56:45.745100968-05:00
---

# Culhwch ac Olwen opening (Arthurian prose, c. 1100): find a verifiable Welsh text

## Problem

(what's wrong + root cause + evidence — fill me in)

## Approach

(the fix — fill me in)

## Acceptance

- [ ] (testable post-condition that proves the fix durably landed — fill me in)

## Notes

- 2026-10-31T11:56:45Z: Problem: Rhys & Evans 1887 Red Book diplomatic text (archive.org textofmabinogion00evanuoft) has r rotunda/long s/ỽ that the OCR mangles (z for r, f for s, broken words); Welsh Wikisource 'Kulhwch ac Olwen' names no source edition and differs from Rhys (a geffyt vs ageffynt), likely White Book. Approach: pin J. G. Evans, The White Book Mabinogion (1907) or hand-transcribe the opening from the Rhys scan pages (n-leaf images) and declare verify_fold/verify_wildcard for ꝛ, ſ, ỽ as in preiddeu-annwn; Guest's translation is Gutenberg 5160 (KILHWCH AND OLWEN at line ~3948). welsh.py module exists. Acceptance: weft check culhwch ok; every line verified against a pinned source; Guest spans verbatim.

## Log

- 2026-10-31T11:56:38Z: Created task
