---
id: 134
title: 'Indigenous: Cherokee: Sequoyah''s syllabary as a generated script row (like th...'
state: BEGUN
priority: 2
tags:
  - indigenous
  - cherokee
  - script
  - pilot
created_at: 2026-10-02T19:33:06.62895023-05:00
updated_at: 2026-10-13T12:02:52.152307578-05:00
started_at: 2026-10-13T10:06:02.334506774-05:00
---

# Indigenous: Cherokee: Sequoyah's syllabary as a generated script row (like the runes); texts: Cherokee Phoenix 1828-34 (bilingual newspaper, PD), Cherokee Constitution 1827; Cherokee NT 1860; tone is under-recorded in old texts: say so; Feeling 1975 dictionary as reference; Cherokee Nation language program position

## Notes

- 2026-10-10T21:08:08Z: Calibration 2026-10-10, John 1 (1860 Worcester-Boudinot NT, IA itsekanohedvdatl00worc leaf n139): blind hand reading of v10-12,17-20 (299 signs) vs IA Cherokee OCR, disagreements adjudicated on the full-res scan. Hand: 14 errors (4.7%), systematic glyph pairs (Ꮟ/Ꮣ x5, Ᏹ/Ꮝ x2, ℓ read Ꮭ for Ꮅ, Ꮒ/Ꮵ, Ꮪ/Ꮥ, Ꮔ/Ꮈ, Ꮧ/Ꮨ). OCR: 21 (7.0%), mostly insertions and noise; gets the look-alike pairs right. Where the two independent readings agreed, no error found in the sample. 2 signs unresolvable at this res (Ꮤ/Ꮃ in v17, first sign of v12 ᏚᎤᎵ/ᎦᎤᎵ). Wikisource ᎪᏪᎭᎨᏛ/ᏣᏂ (rev 901723, anonymous edit, no edition named) stops at 1:10 and has errors of the same classes (Latin U in v7; v3 omits ᏥᎩ and reads ᎸᏬᏢᏅᎾ for ᏄᏬᏢᏅᎾ; v5 Ꮭ for Ꮅ, Ꮟ for Ꮣ). Method that works: two independent witnesses (hand + OCR), collate, adjudicate disagreements on the scan, flag unresolved signs.
- 2026-10-13T14:39:47Z: 2026-10-13: weft ocr landed (pipeline/weft/ocr.py): pinned scan -> Tesseract chr (tessdata_best commit 9ddc24e, sha256 b3a0da90...) -> gen/ocr/<page>.txt + provenance; sign-level collation report; ocr.witness_check for the Cherokee module's line_checks (edition ocr_check + token ocr). Tesseract chr on the 1860 NT page: 6.3-6.7% on hand+IA consensus signs, binarized slightly better. Pilot candidate: Constitution of the Cherokee Nation (New Echota 1828, Newberry Ayer 251 C211 1828 on archive.org, bilingual, same press/type as the Phoenix); archive.org OCR reads its Cherokee as Latin, so Tesseract is the machine witness. Preamble OCR'd (crop 815,1500,950,1180 of image 00007_o2_right); first two lines settled; uncertain Ꮧ/Ꮨ in ᎠᏫᏂᏗᏢ; lexical check settled ᏚᏳᎪᏛ. My reading of that page is NOT blind (saw OCR first): the published hand error rate for 1828 type needs a blind reading of another page (Article I). Next: Cherokee module (syllabary->romanization, INDIGENOUS = True, line_checks via ocr.witness_check).
- 2026-10-13T15:06:02Z: 2026-10-13: Cherokee module landed (pipeline/weft/cherokee.py, chr; INDIGENOUS = True). Sign table from Unicode names (86 signs, lowercase folded); generated romanization row; schemes c1828 (g, d, v, ts after Worcester, Cherokee Phoenix 6 Aug 1828 answer to Rafinesque; rest from present descriptions) and modern (Oklahoma); no accent caps since tone/length unwritten; Ꮝ closes the syllable before it; token fields ocr, uncertain {alt, why} (dotted underline + detail line), sound override; line_checks = ocr.witness_check. Page: Noto Sans Cherokee. Skeptic-reviewed; attributions corrected (d-row signs are an inference; ts not settled by the letter; Ᏽ). Next: the pilot work (Constitution 1827 preamble): blind hand reading of Article I for the 1828 error rate, a gloss source decision (Feeling 1975 is in copyright: reference only), the English column as the translation.
- 2026-10-13T17:00:08Z: 2026-10-13: pilot built: texts/cherokee-constitution-1827 (preamble, 8 lines, 59 tokens; check ok). Transcribed from the archive.org scan of the Newberry copy (Ayer 251 C211 1828) by hand + Tesseract, settled on the scan with NT-1860/CED lookups via cherokeedictionary.net. Findings: the 1828 type casts Ꮩ (do) as Λ and Ꮅ (li) as a plain F; Tesseract reads them Ꭺ and Ꮲ; Tesseract 31/252 signs (12.3%) on this page; a ';' from OCR (Ꭵ misread) slipped in and was caught by review: punctuation is not covered by the letters-only witness check. Two signs uncertain (Ꮒ/Ᏺ, Ꮣ/Ꮦ). Overlay drafted by Claude against CED/NT/Wiktionary; 4 words unanalysed. Stewardship cites Cherokee Nation AI policy (21 Aug 2025: fluent speakers' input on Cherokee language applications): glosses held as draft pending speaker review. Open: blind hand reading of Article I (calibration), speaker review, image, Cherokee title lines, the six articles.
- 2026-10-13T17:02:52Z: 2026-10-13 review fixes: line 3 word is ᏦᎩᎸᏫᏍᏓᏁᏗᏱ (Ꮈ, lv: ~ tail as the page's other Ꮈ; Ꮔ has an = bar), not ᏦᎩᏄᏫᏍᏓᏁᏗᏱ: a dictionary lookup had overridden the scan. Lesson: lexical attestation decides only between readings the scan allows, never against it. A ';' read from OCR (Ꭵ) removed. ᏦᎩᎾᏝᎢ is Galatians 2:4 (bondage), not Jude 4.

## Log

- 2026-10-03T00:33:06Z: Created task
- 2026-10-13T15:06:02Z: State changed from TODO to BEGUN
