---
id: 70
title: Add an oracc-json treebank format to draft (lemma cf[gw]POS, morph from Oracc...
state: DONE
priority: 3
tags:
  - pipeline
  - treebank
  - sumerian
created_at: 2026-10-01T10:18:23.286867-05:00
updated_at: 2026-10-30T10:31:40.967287387-05:00
completed_at: 2026-10-30T10:31:40.967280988-05:00
meta:
  draft: docs/design/keyed-treebanks.md
---

# Add an oracc-json treebank format to draft (lemma cf[gw]POS, morph from Oracc morphemes), replacing the module-hook workaround in sumerian.py

## Notes

- 2026-10-01T15:22:52Z: Also the Egyptian work reads TLA JSON through the module hook (format none); a general 'language hook supplies treebank pairs' option in draft would serve Oracc, TLA and similar.
- 2026-10-30T15:14:48Z: 2026-10-30: design note drafted, docs/design/keyed-treebanks.md: options A (format: module, rename only), B (one core format per corpus), C (recommended: one core 'keyed' format, module supplies load_treebank -> {id: row}, core sensors, file named once). Open choice: rename the module failure classes to core names (note leans yes). Awaiting Skip's decision.
- 2026-10-30T15:31:40Z: Done 2026-10-30, option C with renamed classes: draft format 'keyed' (treebank.key; module load_treebank -> rows; core sensors no-treebank-word, form-mismatch, new treebank-lemma-missing; extra fields copied; row passed to token_fields as tb_row). sumerian and egyptian converted; oracc_json/tla_file removed from the editions (the file is named once, in the manifest); draft now sets edition.work for sensors. Verified: both works' gen content-identical to before; Enheduanna's oracc-unlemmatized:4 is now treebank-lemma-missing:4. test_keyed_treebank_core_sensors. Docs: schema.md, building.md, design note marked decided.

## Log

- 2026-10-01T15:18:23Z: Created task
- 2026-10-30T15:31:40Z: State changed from TODO to DONE
