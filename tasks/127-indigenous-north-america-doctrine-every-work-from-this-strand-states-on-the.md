---
id: 127
title: 'Indigenous North America, doctrine: every work from this strand states on the...'
state: BEGUN
priority: 2
tags:
  - indigenous
  - doctrine
created_at: 2026-10-02T19:33:06.582569067-05:00
updated_at: 2026-10-13T09:45:54.50698441-05:00
started_at: 2026-10-13T09:39:47.213248834-05:00
---

# Indigenous North America, doctrine: every work from this strand states on the page whose transcription and translation it is (outsider ethnographer or community), the community's own stated position where known (e.g. tribal language programs), and prefers published secular texts first (newspapers, councils, poetry) over ceremonial ones; cite CARE principles in docs/about.md

## Notes

- 2026-10-13T14:39:47Z: 2026-10-13: implemented. pipeline/weft/stewardship.py (block: community, content secular|ceremonial, transcription {by, relation, method}, relation per translation, position {source, summary} or {none_found}, consent required for ceremonial); weft check requires it when the language module has INDIGENOUS = True; page notice #steward-note ('Whose text this is'); docs/about.md 'Texts of living communities' (CARE, scoped as Weft's extension); docs/schema.md block. tests/test_stewardship.py. Uncommitted; skeptic review pending.
- 2026-10-13T14:45:54Z: 2026-10-13: skeptic review done; fixed: about.md numbers (IA OCR vs Tesseract separated, Tesseract 6-7% on hand+IA agreed signs, up to 14% at a bad threshold), removed unbuilt 'uncertain signs' promise, notice prints only stated fields, reference translations named, aligned agreement measure, ocr '' for dropped words. Open: uncertain-sign token field and its page display; build not gated on check. Suite 91/91, all works check ok.

## Log

- 2026-10-03T00:33:06Z: Created task
- 2026-10-13T14:39:47Z: State changed from TODO to BEGUN
