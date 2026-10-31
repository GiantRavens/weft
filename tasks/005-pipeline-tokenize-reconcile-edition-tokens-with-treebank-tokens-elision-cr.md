---
id: 5
title: 'pipeline tokenize: reconcile edition tokens with treebank tokens (elision, cr...'
state: DONE
priority: 2
tags:
  - phase1
  - pipeline
created_at: 2026-09-29T13:54:31.667346-05:00
updated_at: 2026-10-30T10:58:46.674329439-05:00
completed_at: 2026-10-30T10:58:46.674323769-05:00
---

# pipeline tokenize: reconcile edition tokens with treebank tokens (elision, crasis, enclitics)

## Notes

- 2026-10-30T15:58:46Z: Closed 2026-10-30 as done: treebank.reconcile and reconcile_stream match edition tokens to treebank words across all 12 Greek works, merging elided and enclitic splits (οὐδʼ = οὐ + δ̓, kept as tok.enclitic) and borrowing words the treebank cites to the next line (tb-line-borrow); residuals are reported, not hidden (form-mismatch / no-treebank-word about 0.1% in Marcus, Metaphysics, Iliad).

## Log

- 2026-09-29T18:54:31Z: Created task
- 2026-10-30T15:58:46Z: State changed from TODO to DONE
