---
id: 196
title: Generate a Tengwar script row for the Elvish works, verified against Tolkien'...
state: BEGUN
priority: 3
tags:
  - tolkien
  - script
  - sound
created_at: 2026-10-30T07:46:11.974337289-05:00
updated_at: 2026-10-30T08:02:26.745617364-05:00
started_at: 2026-10-30T08:02:26.745611023-05:00
---

# Generate a Tengwar script row for the Elvish works, verified against Tolkien's own Tengwar

## Problem

(what's wrong + root cause + evidence — fill me in)

## Approach

(the fix — fill me in)

## Acceptance

- [ ] (testable post-condition that proves the fix durably landed — fill me in)

## Notes

- 2026-10-30T12:46:11Z: Problem: the Elvish pages show Tolkien's Latin-letter spelling only; Weft has a per-word script row (runes, cuneiform: token field 'script', SCRIPT_LABEL in the module, .scr in weft.css) but no Tengwar. A row that disagrees with Tolkien's own hand would present Weft's transcription as his, so it must be checked against his. Evidence gathered 2026-10-30: (1) font: Alcarin Tengwar (Toshi Omagari, SIL OFL 1.1, github.com/Tosche/Alcarin-Tengwar, woff2 40 KB), Free Tengwar / CSUR mapping, letters E000-E03D, tehtar E040-E05F, punctuation E060-E06F; its Character mapping/README.md names every code point. (2) Ground truth: The Road Goes Ever On 3rd ed. p. 65 (PDF p. 81) is Tolkien's Tengwar of the whole of Namárië (Quenya mode), now the section figure of private/tolkien-namarie; identified by the question mark closing line 8. No full Sindarin Tengwar of the Elbereth hymn was identified in the book (the running heads and feet are Tengwar lines not yet read). Approach: elvish.py gains a tengwar() per language: Quenya mode from App. E (tehta on the preceding consonant, short carrier otherwise, long carrier for long vowels, yanta/ure for i- and u-diphthongs, romen before vowels / ore elsewhere, calma series for k, quesse for qu, two dots below for y after a consonant, doubling bar or esse for long consonants); Sindarin following App. E's general usage, marked approximate. Font bundled in site/fonts with OFL.txt. Acceptance: every word of Namárië's Tengwar row matches Tolkien's p. 65 letter by letter (a test lists each word's code points, read off the manuscript by a human); the Sindarin row is labelled as Weft's transcription, not Tolkien's; pages still work from file:// and print.
- 2026-10-30T13:02:26Z: 2026-10-30: built. elvish.py tengwar(): Quenya classical mode from App. E and Björkman's account of DTS 20 (= RGEO p. 65), Sindarin general use; token field 'script' (+ edition override 'tengwar:'), LAYERS src, key entries; Alcarin Tengwar woff2 + OFL in site/fonts (unicode-range PUA). Read off p. 65 so far and pinned in test_elvish_tengwar: laurië lantar súrinen yéni únótimë ve rámar aldaron yuldar avánier; one rule found and applied from the page: long é is a doubled accent, not the long carrier. Remaining acceptance: the other words read against the page by a person; private/tolkien-namarie/review/tengwar-review.html shows the page above and Weft's row per word, numbered line.word. Known departure (Björkman): caita, a-mark on calma. Stays open until that reading is done.

## Log

- 2026-10-30T12:46:11Z: Created task
- 2026-10-30T13:02:26Z: State changed from TODO to BEGUN
