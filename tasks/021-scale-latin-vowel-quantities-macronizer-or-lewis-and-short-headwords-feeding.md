---
id: 21
title: 'Scale Latin vowel quantities: macronizer or Lewis and Short headwords feeding...'
state: DONE
priority: 2
tags:
  - phase1
  - latin
  - sound
created_at: 2026-09-29T14:37:21.423509-05:00
updated_at: 2026-10-30T11:19:06.553342101-05:00
completed_at: 2026-10-30T11:19:06.553336543-05:00
---

# Scale Latin vowel quantities: macronizer or Lewis and Short headwords feeding lat_quantities, with the hexameter scanner as a cross-check

## Notes

- 2026-10-30T16:19:06Z: Done 2026-10-30. Lewis and Short (Perseus, pinned commit, 2 files by sha256) fetched by weft lexica; 25,850 headwords with a marked long vowel (359 disagreeing homographs left out). latin.lexicon_long_positions carries macrons onto a form's stem (aligned runs >= 3 letters, never a consonantal v/j, never the headword's own final syllable onto another form). weft quantities <work> writes gen/quantities-proposed.yaml for review (applies nothing; Latin endings decide stress). Measured: 90.5% of placed long marks agree with the hand tables (1,819 forms), recall 59% (endings). test_latin_quantities_draft_from_lewis_and_short (Res Gestae, own table withheld). Docs: languages.md, building.md.

## Log

- 2026-09-29T19:37:21Z: Created task
- 2026-10-30T16:19:06Z: State changed from TODO to DONE
