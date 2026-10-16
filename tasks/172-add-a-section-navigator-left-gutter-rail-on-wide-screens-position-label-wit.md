---
id: 172
title: 'Add a section navigator: left-gutter rail on wide screens, position label wit...'
state: DONE
priority: 2
tags:
  - site
  - reader
created_at: 2026-10-16T12:54:35.818358726-05:00
updated_at: 2026-10-16T14:47:35.836527422-05:00
started_at: 2026-10-16T14:21:26.238655367-05:00
completed_at: 2026-10-16T14:47:35.836517199-05:00
---

# Add a section navigator: left-gutter rail on wide screens, position label with bottom sheet on phones

## Problem

Long pages (Hávamál 164 stanzas, the Yijing 64 hexagrams, the 95 Theses) give a reader no way to see how far the work runs or to jump to a stanza. The byline says "stanzas 1–164" and that is all. Every stanza already has an h2 with id sec-N, hash navigation (goToHash in site/weft.js) scrolls and highlights a target, and the Yijing cast panel already builds #sec-N links, so the pieces exist and only the surface is missing. Decided with Skip 2026-10-16.

## Approach

Wide screens: a fixed rail in the left gutter (the text column is 1120px centred, so 80px+ is free from 1280px up), listing stanza numbers as a vertical ruler, the stanza in view marked by an IntersectionObserver, hover or click expanding to the full grid. Hidden below about 1250px. Never collides with the Word and Loom panels, which dock right.
Phones: no rail. The sticky masthead shows a position label ("Stanza 12 of 164"); tapping it opens a bottom sheet with the grid, reusing the Word panel's phone layout. Nothing is stacked at the top of the page.
Threshold: only pages with 12 or more sections (or more than a screenful of lines) get either.
Both read one list built once from the stanza headings. Named parts (Gestaþáttr, Loddfáfnismál, Rúnatal; the Yijing's two canons) come later as a `parts` manifest field with a check rule, after the rail proves itself.

## Acceptance

- [x] On edda-havamal.html at 1440px wide, a rail lists 164 stanzas; clicking 100 scrolls to #sec-100 and highlights it; the rail marks the stanza in view while scrolling
- [x] At 390px wide the rail is absent, the masthead shows "Stanza N of 164", and tapping it opens a sheet whose links jump to the stanza
- [x] beowulf.html (11 lines) and runes-kylver.html show neither rail nor label
- [x] Word and Loom panels open and close with the rail present and never overlap it
- [x] weft check passes on all works; tests pass

## Notes

- 2026-10-16T19:34:25Z: Built 2026-10-16. Headless Chromium runs: Hávamál 1440 (rail 164 ticks, click #sec-100 highlights hav.100.1, label 'Stanza 100 of 164'), 1000 (no rail, label), 390 (bottom sheet, cell 50 jumps and closes); Beowulf shows nothing; Iliad and Inferno 1 run in line mode; Yijing says 'Hexagram 1 of 64'. Rail ticks own tiled slices of the track so hit areas never overlap; labels are pointer-transparent; current and hovered labels carry a surface backing. Section links now light the first line under the heading (goToHash).

## Log

- 2026-10-16T17:54:35Z: Created task
- 2026-10-16T19:21:26Z: State changed from TODO to BEGUN
- 2026-10-16T19:47:35Z: State changed from BEGUN to DONE
