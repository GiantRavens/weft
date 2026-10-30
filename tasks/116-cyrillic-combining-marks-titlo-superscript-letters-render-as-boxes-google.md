---
id: 116
title: 'Cyrillic combining marks (titlo, superscript letters) render as boxes: Google...'
state: BEGUN
priority: 3
tags:
  - fonts
  - russian
created_at: 2026-10-01T18:21:23.779849-05:00
updated_at: 2026-10-30T09:24:46.048515101-05:00
started_at: 2026-10-30T09:24:46.041801682-05:00
---

# Cyrillic combining marks (titlo, superscript letters) render as boxes: Google Fonts' Gentium split; self-host a full Gentium or add Noto Serif with cyrillic-ext so the Primary Chronicle can print its marks instead of parentheses

## Notes

- 2026-10-30T14:24:46Z: 2026-10-30, font half done: site/fonts/NotoSerif-Cyrillic.woff2 (Noto Serif, SIL OFL, subset to Latin + Cyrillic + U+0300-036F, 0400-052F, 1C80-1C8F, 2DE0-2DFF, A640-A69F; 44 KB) applied to lang=orv (.src, .word .big, .lemma); render test: titlo, pokrytie and superscript letters (2DEF, 2DF6) sit on their letters, where Gentium shows boxes. Remaining: convert the Primary Chronicle edition from parentheses to the marks. Not mechanical: the parentheses now mean both a raised letter and an expanded abbreviation (ни(х) for a pokrytie), so each needs the print (Lavrentiev text as edited) checked; then letters_of in oldeastslavic.py and the manifest gap text change with it.

## Log

- 2026-10-01T23:21:23Z: Created task
- 2026-10-30T14:24:46Z: State changed from TODO to BEGUN
