---
id: 63
title: Move the OCR-based verbatim check (hOCR page boxes, declared OCR misreadings)...
state: DONE
priority: 3
tags:
  - pipeline
  - verification
created_at: 2026-10-01T05:17:38.511518-05:00
updated_at: 2026-10-30T09:58:13.603644244-05:00
completed_at: 2026-10-30T09:58:13.603638354-05:00
---

# Move the OCR-based verbatim check (hOCR page boxes, declared OCR misreadings) from dutch.line_checks into core as a verify_ocr option, for editions transcribed from scans

## Notes

- 2026-10-30T14:58:13Z: Done: hocr_body + hocr_check moved from dutch.py to weft/ocr.py; draft runs it as a core sensor for any edition whose ocr_check names hOCR pages; dutch.line_checks removed. Verified: linschoten-japan redrafted byte-identical; test_hocr_check_is_core shows it passes the real lines and reports a changed word.

## Log

- 2026-10-01T10:17:38Z: Created task
- 2026-10-30T14:58:13Z: State changed from TODO to DONE
