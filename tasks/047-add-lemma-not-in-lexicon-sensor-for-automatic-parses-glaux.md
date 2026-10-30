---
id: 47
title: Add lemma-not-in-lexicon sensor for automatic parses (GLAUx)
state: DONE
priority: 2
tags:
  - sensor
  - pipeline
  - greek
created_at: 2026-09-29T20:27:05.942099-05:00
updated_at: 2026-10-30T09:31:20.715457038-05:00
completed_at: 2026-10-30T09:31:20.715448229-05:00
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
- 2026-10-01T09:40:09Z: Marcus Book 2 telemetry (2026-10-01): 142 of 1,409 tokens corrected (10%): 32 lemmas, 122 morph. 26 lemmas not Greek words or not headwords (1.8% of tokens), e.g. πνευμάτιος, κροκύφω, εἱμίαρω, ριγεγραμ́ω, διηνύζω, κέμνω, λελ́ηθα, ἀφέλλυμι, στερείκνυμι, plus inflected forms as lemma (ὑπειδόμην, τεθνήξω, βλάψω). Morph: case 67 (54 neuter nom tagged acc), gender 39. A lexicon sensor would catch all 26.
- 2026-10-30T14:31:20Z: Done 2026-10-30. weft/lexica.py: Perseus LSJ pinned (commit 1c34cdf, 27 files by sha256), fetched by 'weft lexica' into ~/.cache/weft, 114,957 bare headwords. draft: lemma-not-in-lexicon for GLAUx works (names, adverbs skipped; curated lemmas skipped; data/grc_lemma_ok.yaml declares 11 real words with reasons); sensors_skipped telemetry when the list is absent. First run found 21 hits in 6 works: 7 GLAUx lemma errors corrected in Marcus curated (φοιτάω, ληρέω, ἐξηττάομαι, τερατεύομαι, ἐναφανίζω, προαφίσταμαι, ἀπολυπράγμων) + ἀτραγῴδως morph; 11 declared. Acceptance: test_lemma_not_in_lexicon_sensor (the 4 named non-words caught with curated ignored; 0 with it).

## Log

- 2026-09-30T01:27:05Z: Created task
- 2026-10-30T14:31:20Z: State changed from TODO to DONE
