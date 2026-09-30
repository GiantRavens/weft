---
id: 47
title: Add lemma-not-in-lexicon sensor for automatic parses (GLAUx)
state: TODO
priority: 2
tags:
  - sensor
  - pipeline
  - greek
created_at: 2026-09-29T20:27:05.942099-05:00
updated_at: 2026-09-29T20:27:14.710419-05:00
---

# Add lemma-not-in-lexicon sensor for automatic parses (GLAUx)

## Problem

(what's wrong + root cause + evidence — fill me in)

## Approach

(the fix — fill me in)

## Acceptance

- [ ] (testable post-condition that proves the fix durably landed — fill me in)

## Notes

- 2026-09-30T01:27:14Z: Problem: GLAUx lemma errors pass every current check because the forms align. 16 hand corrections in Epictetus Ench. 1.1-3 and Marcus Med. 2.1 (2026-09-29); 4 were lemmas that are not Greek words (ταραχθαίνω, περιβαλέω, ἀπαραποδύς, συντεύχω). Approach: load a headword list (LSJ via Perseus/Logeion, or the Morpheus stem list), emit failure class lemma-not-in-lexicon from weft draft for any treebank lemma absent from it. Acceptance: redrafting the two works with curated corrections removed reports lemma-not-in-lexicon >= 4, and 0 with corrections applied.

## Log

- 2026-09-30T01:27:05Z: Created task
