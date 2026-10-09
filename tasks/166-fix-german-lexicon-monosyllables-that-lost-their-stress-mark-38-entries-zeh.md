---
id: 166
title: 'Fix German lexicon monosyllables that lost their stress mark (38 entries: zeh...'
state: TODO
priority: 2
tags:
  - german
  - sound
  - bug
created_at: 2026-10-09T09:41:32.540258449-05:00
updated_at: 2026-10-09T09:41:47.126518924-05:00
---

# Fix German lexicon monosyllables that lost their stress mark (38 entries: zehn, gleich, Papst, Tod, schön, führt ...)

## Problem

german.py's rule: monosyllables in UNSTRESSED are said without stress, 'every other monosyllable is stressed'. But a de_lexicon.yaml entry overrides the rule, and 38 monosyllabic entries carry no stress mark (ˈ): ab, dar, zwar, fur, papst, zar, staats, plan, jüngst, nebst, erg, zehn, schön, schwur, tod, not, wär, her, wen, ists, ichs, wahl, stern, gleich, eins, null, plus, mal, klein, ha, ka, phi, fau, tse, el, xi, führt, nimmt. Most arrived with the 10-04 opera and Einstein commits (51b2def, 1ad96d9).
Evidence (2026-10-09, found during the split, pin 165): re-drafting the untouched nietzsche work changes zehn (nz.za1.2.12, nz.za1.5.1) from TSAYN to tsayn and gleich (nz.za1.10.3) from GLAIHY to glaihy; re-drafting mozart-zauberfloete changes führt from FÜÜRT to füürt. Committed gen/ of works drafted before 10-04 still shows the stressed forms, so pages disagree with the pipeline until redrafted.

## Approach

Decide per entry (ists, ichs and the spoken letter names may be deliberate), then either add ˈ to the lexicon entries or make german.py stress a monosyllabic lexicon entry that is not in UNSTRESSED. Add a sensor to weft check or a test: no monosyllabic lexicon entry outside UNSTRESSED lacks ˈ unless listed as deliberately unstressed. Redraft every German work (kant-*, nietzsche-*, marx-manifest, einstein-1905-energieinhalt, luther-*, mozart-zauberfloete) and diff gen: only stress changes.

## Acceptance

- [ ] a test fails when a monosyllabic de_lexicon entry outside UNSTRESSED lacks a stress mark and is not declared deliberately unstressed
- [ ] every German work redrafted; the gen diff shows only stress changes; weft check passes on all

## Log

- 2026-10-09T14:41:32Z: Created task
