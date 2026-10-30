---
id: 154
title: 'Unknown sound rows: 386 Yijing + 12 Sunzi + 2 Daodejing characters have no Ta...'
state: DONE
priority: 2
tags:
  - chinese
  - sumerian
  - sensor
created_at: 2026-10-02T21:03:19.084242875-05:00
updated_at: 2026-10-30T09:44:57.337400573-05:00
completed_at: 2026-10-30T09:44:57.337395388-05:00
---

# Unknown sound rows: 386 Yijing + 12 Sunzi + 2 Daodejing characters have no Tang reading in Unihan kTang (page shows ?), and 2 Enheduanna signs have no value; add a fallback (Middle Chinese via Baxter-Sagart kBaxterSagart / kMandarin-derived note) or an explicit 'no Tang reading recorded' marker, and clear the token-sound-unknown warnings

## Notes

- 2026-10-30T14:44:57Z: Done: chinese.phonemize falls back to Baxter's Middle Chinese (Baxter-Sagart list, mc field) when Unihan has no kTang, shown as °reading; key explains ° (Qieyun 601, Baxter notation, X rising, H departing) and ?. token-sound-unknown-tang: Yijing 386 -> 130, Sunzi 12 -> 1, Daodejing 2 -> 0; the rest have no reading in either source and stay visible as warnings. Enheduanna's 2 signs untouched (different module). test_tang_falls_back_to_baxter_middle_chinese.

## Log

- 2026-10-03T02:03:19Z: Created task
- 2026-10-30T14:44:57Z: State changed from TODO to DONE
