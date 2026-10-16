---
id: 169
title: Recheck the Cherokee preamble overlay's [CED] citations against the source ta...
state: TODO
priority: 2
tags:
  - cherokee
  - provenance
created_at: 2026-10-13T17:04:39.480573525-05:00
updated_at: 2026-10-13T17:04:39.480581601-05:00
---

# Recheck the Cherokee preamble overlay's [CED] citations against the source tag of each entry

## Problem

curated/preamble.yaml tags citations [CED] (Feeling's Cherokee-English Dictionary) and its header says only Feeling, the 1860 NT and Wiktionary were consulted. cherokeedictionary.net serves several word lists beside Feeling (NOQ Noquisi, CWL Consortium Word List, RRD Raven Rock, CN Cherokee Nation list, SSKIL Shadow of Sequoyah), each labelled on the page. In Article I (2026-10-13) a skeptic found about 25 of 299 [CED] tags were entries from those other lists (e.g. ᎤᏁᎬ "white" is NOQ; Feeling has ᎤᏁᎦ). The preamble was annotated the same way, so the same class is likely there.

## Approach

Run scratchpad-style src lookup (source label per entry; the tool at the session scratchpad sk3/src.py queries newSearchForm with includeCED/includeSentences/includeCNT and parses 'Source: ... English: ... Cherokee Syllabary') for every [CED] citation in curated/preamble.yaml; relabel to the true source; update the overlay header and the manifest gap text to name the word lists, as curated/article1.yaml now does.

## Acceptance

- [ ] Every [CED ...] citation in curated/preamble.yaml resolves to an entry the site labels Cherokee English Dictionary; others carry NOQ/CWL/RRD/CN/SSKIL
- [ ] preamble.yaml header names the word lists consulted; weft check cherokee-constitution-1827 ok

## Log

- 2026-10-13T22:04:39Z: Created task
