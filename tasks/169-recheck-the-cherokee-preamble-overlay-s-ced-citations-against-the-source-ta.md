---
id: 169
title: Recheck the Cherokee preamble overlay's [CED] citations against the source ta...
state: DONE
priority: 2
tags:
  - cherokee
  - provenance
created_at: 2026-10-13T17:04:39.480573525-05:00
updated_at: 2026-10-17T19:27:07.417469825-05:00
completed_at: 2026-10-17T19:27:07.417461165-05:00
---

# Recheck the Cherokee preamble overlay's [CED] citations against the source tag of each entry

## Problem

curated/preamble.yaml tags citations [CED] (Feeling's Cherokee-English Dictionary) and its header says only Feeling, the 1860 NT and Wiktionary were consulted. cherokeedictionary.net serves several word lists beside Feeling (NOQ Noquisi, CWL Consortium Word List, RRD Raven Rock, CN Cherokee Nation list, SSKIL Shadow of Sequoyah), each labelled on the page. In Article I (2026-10-13) a skeptic found about 25 of 299 [CED] tags were entries from those other lists (e.g. ᎤᏁᎬ "white" is NOQ; Feeling has ᎤᏁᎦ). The preamble was annotated the same way, so the same class is likely there.

## Approach

Run scratchpad-style src lookup (source label per entry; the tool at the session scratchpad sk3/src.py queries newSearchForm with includeCED/includeSentences/includeCNT and parses 'Source: ... English: ... Cherokee Syllabary') for every [CED] citation in curated/preamble.yaml; relabel to the true source; update the overlay header and the manifest gap text to name the word lists, as curated/article1.yaml now does.

## Acceptance

- [x] Every [CED ...] citation in curated/preamble.yaml resolves to an entry the site labels Cherokee English Dictionary; others carry NOQ/CWL/RRD/CN/SSKIL
- [x] preamble.yaml header names the word lists consulted; weft check cherokee-constitution-1827 ok

## Notes

- 2026-10-18T00:27:07Z: 2026-10-17: rechecked by exact-match search (lists each entry's source). 7 of 10 [CED] were Feeling; ᏚᏳᎪᏛ -> CN/NOQ, ᏂᎦᎵᏍᏓᏂᏏᏒ -> CWL, ᏂᎬᎾᏛ -> NT Mt 4:23 (ADV 'everywhere'). Lemma for pre.2.2/6.5 corrected ᎧᏁᎦ -> ᎧᏁᎢᏍᏗᎭ (mention). Note claim 'ᎤᎾᏝᎢ in Feeling' false. Skeptic refuted 4.4 'our-owner': NT ᏗᎨᏥᎾᏝᎢ = bond vs ᏂᏗᎨᏥᎾᏝᎥᎾ free (Rev 6:15), 2 Pet 2:19 same negation for liberty -> 4.4 now 'we-bondservants'. Article I Feeling claims in notes (7) verified. Gotcha: the site's substring search caps results and drops CED entries; use searchForExactMatch.

## Log

- 2026-10-13T22:04:39Z: Created task
- 2026-10-18T00:27:07Z: State changed from TODO to DONE
