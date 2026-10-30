---
id: 192
title: 'Build Saxo, Gesta Danorum 9.3-9.5 (Ragnar Lothbrok and his sons): Holder 1886...'
state: DONE
priority: 2
tags:
  - latin
  - ragnar
  - saxo
  - pilot
created_at: 2026-10-22T06:47:02.943742119-05:00
updated_at: 2026-10-22T08:07:10.990188313-05:00
completed_at: 2026-10-22T08:07:10.990181116-05:00
---

# Build Saxo, Gesta Danorum 9.3-9.5 (Ragnar Lothbrok and his sons): Holder 1886 Latin from OCR, Elton 1894, hand annotation

## Notes

- 2026-10-22T11:47:02Z: Problem: Saxo's Ragnar (Gesta Danorum 9.3-9.5, ~4,800 words, 51 paragraphs, 256 sentences) is the Danish-Latin counterpart to the three Norse Ragnar works. Recon 2026-10-22: Latin Wikisource Gesta Danorum/Liber IX (rev 255865) = Royal Library e-text of Olrik-Raeder 1931 word for word, but the KB colophon claims copyright in the digital text (Det Danske Sprog- og Litteraturselskab), against hard rule 4. Holder 1886 (Strassburg; Holder d. 1916) is clean PD and is the text Elton translated; OCR archive.org saxonisgrammatic00saxouoft, medieval spelling (u for v, e for ae). Elton 1894 on Gutenberg #1150 (Elton d. 1945, PD worldwide). No treebank: hand annotation after Lewis and Short.
- 2026-10-22T11:47:02Z: Approach: edition.yaml from Holder's OCR, every OCR correction declared and checked on the page images; sections = standard paragraphs 9.3.1-9.5.8 (citation numbers only), lines = sentences; overlays by parallel annotators under one convention table; Elton aligned sentence by sentence; notes on Saxo vs the saga; skeptic pass.
- 2026-10-22T11:47:02Z: Acceptance: weft check ok; every edition line verbatim in Holder OCR after declared corrections; every correction seen on a page image; every token lemma+morph+gloss; Elton covers every line; weft build all and pytest pass; README and languages rows.
- 2026-10-22T12:36:30Z: 2026-10-22 built: edition (Holder 1886, 256 lines, 121 OCR corrections, all verified on images; four-OCR vote + 318 suspect words read on images; two Toronto-copy type defects corrected from the Oxford copy), 5 annotators 4776 tokens + 2 harmonization changesets, lat_quantities_saxo.yaml (3054 forms), new danish-medieval scheme (latin.py, tests, docs), Elton 1894 (Norroena 1905 reprint text) aligned 256 spans, 6 notes, Moe 1898 image. Skeptics: text (diu diu, Dani, fixed), annotation (~0.6% content errors; consistency and quantity fixes applied), notes and scheme (Holder spelling, michi/nichil evidence, 3 titles, revenge overclaim, manifest fixed). Open: scheme comment cites Arnold of Lübeck and the date of þ>t from memory; a scholar should check.

## Log

- 2026-10-22T11:47:02Z: Created task
- 2026-10-22T13:07:10Z: State changed from BEGUN to DONE
