---
id: 164
title: 'Add library search: weft about (Wikipedia + Wikidata descriptions), search in...'
state: BEGUN
priority: 1
tags:
  - search
  - about
  - wikipedia
  - wip
created_at: 2026-10-09T09:24:59.623586338-05:00
updated_at: 2026-10-09T11:19:10.726287792-05:00
started_at: 2026-10-09T09:25:20.698051302-05:00
---

# Add library search: weft about (Wikipedia + Wikidata descriptions), search index, search page, line deep links

## Problem

The library has no search. Two layers of evidence (session 2026-10-09):
- Content is ready: 40,004 tokens, 100% gloss and lemma coverage, 6,036 lines, 3,079 translation spans, 614 notes. A prototype gloss concordance put 'god' across 14 languages (אֱלֹהִים, deus, θεός, Gott, nṯr, deva); the index is 2.5 MB raw, about 400 KB gzipped.
- Work-level metadata is too thin: manifests describe how a text was made, not what it is. 'fable' finds no work (the Swahili tale is one); 'saga' finds only Grettir; internal fields (predicted_gaps) give false hits ('Baxter-Sagart').
- Data wrinkles: composite lemmas ('ⲛ + ⲡ + ⲛⲟⲩⲧⲉ', 'il + amore'); one lemma spelled two ways ('úlfr' and 'ulfr').

## Approach

1. `wikipedia: {title, match: work|author|parent|none}` in each manifest, named by hand. `weft about <work>|all` fetches the Wikipedia lead (verbatim, CC BY-SA, revision-pinned, attributed) and the Wikidata item (CC0: instance of, genre, main subject) into texts/<work>/about.yaml; reports found / author / parent / none / failed per work.
2. Works with no article: hand-written about in curated/, status: draft.
3. `weft index`: search-index.js (script, not JSON, so it loads from file://), built from assemble() so the reference/private boundary holds. Indexes reader-visible fields only.
4. search.html: works first (title, author, date line, kind, language, about), then lines (translation, note, gloss), then the cross-language word view by lemma. Accent-folded matching, whole words, light plural handling.
5. weft.js: scroll to #line-id after render and highlight the word.

## Acceptance

- [x] weft about all runs on every work and its report counts found, author, parent, none and failed; about.yaml carries revision, URL, attribution and Wikidata ID
- [x] weft check validates the wikipedia field and about.yaml (match value, verbatim text present, QID format); warns where a work has neither about.yaml nor a curated about
- [x] Search for fable, saga and pope returns the expected works first (Kites and the Crows; Grettir and the Eddic poems; Inter caetera and the 95 Theses)
- [x] Search for god returns grouped lemmas across at least 10 languages, and a result link opens the work scrolled to that line with the word highlighted
- [x] search.html and search-index.js work from file:// and on weftlibrary.org; the public index contains no private work or reference-only translation (test)
- [x] Odyssey proem golden diff unchanged; tests pass

## Notes

- 2026-10-09T14:34:44Z: Step 1 done: weft about (pipeline/weft/about.py), wikipedia field on all 73 manifests, about.yaml for 70 (59 work, 6 author, 5 parent), check_about in weft check, tests/test_about.py, docs (schema, building step 9, README layout). Declared none, awaiting hand-written about: runes, science-latin, swahili-tales-steere. Next: step 2 curated about shape, then weft index. Search must match whole words ('epic' must not hit Epictetus).
- 2026-10-09T15:31:08Z: Step 1b: five collection pages split (pin 165) so each work has its own article; 78 of 79 now about.yaml, only swahili-tales-steere needs a hand-written about.
- 2026-10-09T16:18:59Z: Steps 2-5 done (uncommitted): curated/about.yaml for swahili-tales-steere (all 79 works have an about); weft index -> search-index.js (79 works, 40004 tokens, 2.5 MB, 815 KB gzipped) and search.html; site/search.js shared by page and node tests; weft.js scrolls to #line/#token after render; Search in nav and library page. 78 tests pass.
- 2026-10-09T16:19:10Z: Acceptance nuance: 'pope' puts Inter caetera first among works and the 95 Theses first among passages (34 hits); 'saga' puts Grettir first among works and the Eddic poems among passages (they are poems, not sagas). weftlibrary.org not yet verified: needs a push.

## Log

- 2026-10-09T14:24:59Z: Created task
- 2026-10-09T14:25:20Z: State changed from TODO to BEGUN
