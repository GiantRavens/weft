---
id: 17
title: 'Scale vowel quantities beyond the hand table: Morpheus or LSJ headword macron...'
state: DONE
priority: 2
tags:
  - phase1
  - sound
created_at: 2026-09-29T14:14:38.184051-05:00
updated_at: 2026-10-30T11:19:06.559219026-05:00
completed_at: 2026-10-30T11:12:45.662526168-05:00
---

# Scale vowel quantities beyond the hand table: Morpheus or LSJ headword macrons as the source, confidence per entry

## Notes

- 2026-10-30T16:12:45Z: Done 2026-10-30. lexica.build_quantities: 7,568 LSJ headwords with a marked long vowel (first orth of each entry, full or suff). greek.quantity_from_lexicon = lsj_quantity (stem marks carried by letter alignment, through augments) + first_declension_as (-ας long). draft: hand table first, then lexicon (prov names LSJ and the lemma, conf 0.8), quantity_sources telemetry, sensors_skipped when the list is absent. Measured vs hand tables: 36/38 agree (misses: alpha purum ending; πολιτεία stem ι, where LSJ marks ῑ and the hand table does not: worth a look). Effect: 179 tokens lengthened across 12 Greek works; no line's metre changed (Iliad hexameters). test_greek_vowel_length_from_lexicon.
- 2026-10-30T16:19:06Z: Update: homographs that LSJ marks differently are now left out (7,470 headwords); 155 tokens lengthened across the Greek works, no metre changed.

## Log

- 2026-09-29T19:14:38Z: Created task
- 2026-10-30T16:12:45Z: State changed from TODO to DONE
