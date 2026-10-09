---
id: 166
title: 'Fix German lexicon monosyllables that lost their stress mark (38 entries: zeh...'
state: DONE
priority: 2
tags:
  - german
  - sound
  - bug
created_at: 2026-10-09T09:41:32.540258449-05:00
updated_at: 2026-10-09T14:42:45.251890493-05:00
completed_at: 2026-10-09T14:42:45.251883549-05:00
---

# Fix German lexicon monosyllables that lost their stress mark (38 entries: zehn, gleich, Papst, Tod, schön, führt ...)

## Problem

german.py's rule: monosyllables in UNSTRESSED are said without stress, 'every other monosyllable is stressed'. But a de_lexicon.yaml entry overrides the rule, and 38 monosyllabic entries carry no stress mark (ˈ): ab, dar, zwar, fur, papst, zar, staats, plan, jüngst, nebst, erg, zehn, schön, schwur, tod, not, wär, her, wen, ists, ichs, wahl, stern, gleich, eins, null, plus, mal, klein, ha, ka, phi, fau, tse, el, xi, führt, nimmt. Most arrived with the 10-04 opera and Einstein commits (51b2def, 1ad96d9).
Evidence (2026-10-09, found during the split, pin 165): re-drafting the untouched nietzsche work changes zehn (nz.za1.2.12, nz.za1.5.1) from TSAYN to tsayn and gleich (nz.za1.10.3) from GLAIHY to glaihy; re-drafting mozart-zauberfloete changes führt from FÜÜRT to füürt. Committed gen/ of works drafted before 10-04 still shows the stressed forms, so pages disagree with the pipeline until redrafted.

## Approach

Decide per entry (ists, ichs and the spoken letter names may be deliberate), then either add ˈ to the lexicon entries or make german.py stress a monosyllabic lexicon entry that is not in UNSTRESSED. Add a sensor to weft check or a test: no monosyllabic lexicon entry outside UNSTRESSED lacks ˈ unless listed as deliberately unstressed. Redraft every German work (kant-*, nietzsche-*, marx-manifest, einstein-1905-energieinhalt, luther-*, mozart-zauberfloete) and diff gen: only stress changes.

## Acceptance

- [x] a test fails when a monosyllabic de_lexicon entry outside UNSTRESSED lacks a stress mark and is not declared deliberately unstressed
- [x] every German work redrafted; the gen diff shows only stress changes; weft check passes on all

## Notes

- 2026-10-09T19:31:58Z: Fixed upstream: german.lex_entry gives a monosyllabic entry without ˈ the same stress as no entry (stressed unless UNSTRESSED); word_ipa stresses a monosyllable given as IPA (el, fau, phi, tse, xi) by the same rule; an explicit ˈ still wins (war). Per-entry review: 32 stressed (content words, separable particles ab/dar, adverbs, numerals, letter names, units); 6 added to UNSTRESSED as function words (fur, wen, wär, nebst, ichs, ists). All 8 German works redrafted: 144 sound fields changed across 7 works, every change stress-only (verified against HEAD with marks and case stripped). Test: test_german_monosyllables_stress_by_one_rule.

## Log

- 2026-10-09T14:41:32Z: Created task
- 2026-10-09T19:42:45Z: State changed from TODO to DONE
