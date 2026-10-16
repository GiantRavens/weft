---
id: 168
title: 'Build speaker-review intake for Cherokee pages: recording page, consent sheet...'
state: TODO
priority: 2
tags:
  - cherokee
  - stewardship
  - audio
created_at: 2026-10-13T15:16:46.374594428-05:00
updated_at: 2026-10-13T15:17:06.753354905-05:00
---

# Build speaker-review intake for Cherokee pages: recording page, consent sheet, non-GitHub correction route

## Problem

Skip intends to send the Cherokee Constitution page (cherokee-constitution-1827) to a fluent speaker for review and pronunciation. The page's only reply channels are GitHub issue forms (site/weft.js issueUrl: correction.yml, pronunciation.yml, recording.yml). A Cherokee speaker is unlikely to use GitHub; recording.yml offers only CC BY-SA 4.0 or CC0, with no way for the speaker to keep rights, choose display-only, withdraw, or refuse AI training (the Cherokee Nation AI policy of 21 Aug 2025 asks for fluent speakers' input on Cherokee language applications). No way exists to record a reading line by line from the page.

## Approach

1. Recording page (plain HTML/JS, works from file://): one line at a time in large syllabary only (romanization and sound guide hidden, so the reading is the speaker's own); record / re-record / next via MediaRecorder; files named by line id (chcon.pre.1.webm ...); export at the end. Primary unit is the line (connected speech carries tone, vowel length, sandhi); a short isolated-word list only for words in doubt (lemma ? words such as ᏙᎦᏙᎥ, ᎪᎪᏪᎳ; the curled-U Ꮰ words of Article I), each said twice with the speaker's own gloss.
2. Easiest path for the speaker: a session with Skip (call or in person, decent mic); Weft segments by line afterwards. The recording page supports this but is not required.
3. Consent sheet: what is published and where; licence chosen by the speaker (including all rights retained, display by permission); credit by name or anonymous; right to withdraw; no AI training; dialect recorded (Oklahoma / Kituwah); Local Contexts TK/BC labels as an option; honorarium offered.
4. Indigenous-strand pages (INDIGENOUS = True) get a plain email route beside the GitHub links; Skip to choose the address. recording.yml gains the speaker-held licence options.
5. A speaker's recording is labelled as a modern reading in a named dialect, a living witness, not the c1828 reconstruction.

## Acceptance

- [ ] Recording page records, replays and exports one file per line id for the preamble from file:// and from weftlibrary.org, romanization hidden while recording
- [ ] Consent sheet exists in docs/ and is linked from the Cherokee page's stewardship notice
- [ ] Cherokee page shows a non-GitHub contact route (address chosen by Skip) beside the issue links
- [ ] recording.yml and the schema accept a speaker-held licence and a no-AI-training condition; weft check passes on all works
- [ ] Audio layer schema can label a recording as a modern speaker's reading with dialect, distinct from scheme c1828

## Notes

- 2026-10-13T20:17:06Z: context: Article I calibration and the pronunciation-capture recommendation are in pin 134 and docs/languages.md (Cherokee).

## Log

- 2026-10-13T20:16:46Z: Created task
