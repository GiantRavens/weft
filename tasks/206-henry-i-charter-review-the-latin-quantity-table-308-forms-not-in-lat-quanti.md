---
id: 206
title: 'Henry I charter: review the Latin quantity table (308 forms not in lat_quanti...'
state: TODO
priority: 3
tags:
  - latin
  - quantities
  - henry-i
created_at: 2026-10-31T07:16:30.571500841-05:00
updated_at: 2026-10-31T07:16:30.581674554-05:00
---

# Henry I charter: review the Latin quantity table (308 forms not in lat_quantities.yaml; 477 of 688 tokens unmarked)

## Problem

(what's wrong + root cause + evidence — fill me in)

## Approach

(the fix — fill me in)

## Acceptance

- [ ] (testable post-condition that proves the fix durably landed — fill me in)

## Notes

- 2026-10-31T12:16:30Z: weft quantities henry-i-charter proposes 80 stem quantities from Lewis and Short (gen/quantities-proposed.yaml); 228 forms have no marked headword. Recipe: docs/building.md 'A Latin quantity table': check each, add ending lengths, write pipeline/weft/data/lat_quantities_henry-i-charter.yaml and list it in the manifest's quantities after lat_quantities.yaml (as saer-de-quincy-charters does). Acceptance: weft draft henry-i-charter reports quantity-unknown below 5% of tokens; check ok.

## Log

- 2026-10-31T12:16:30Z: Created task
