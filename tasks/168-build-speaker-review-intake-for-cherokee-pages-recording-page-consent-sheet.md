---
id: 168
title: 'Build speaker-review intake for Cherokee pages: recording page, consent sheet...'
state: BEGUN
priority: 2
tags:
  - cherokee
  - stewardship
  - audio
created_at: 2026-10-13T15:16:46.374594428-05:00
updated_at: 2026-10-17T19:44:59.104502499-05:00
started_at: 2026-10-17T19:36:23.343476033-05:00
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
- [x] Consent sheet exists in docs/ and is linked from the Cherokee page's stewardship notice
- [x] Cherokee page shows a non-GitHub contact route (address chosen by Skip) beside the issue links
- [x] recording.yml and the schema accept a speaker-held licence and a no-AI-training condition; weft check passes on all works
- [x] Audio layer schema can label a recording as a modern speaker's reading with dialect, distinct from scheme c1828

## Notes

- 2026-10-13T20:17:06Z: context: Article I calibration and the pronunciation-capture recommendation are in pin 134 and docs/languages.md (Cherokee).
- 2026-10-18T00:36:23Z: 2026-10-17: built. record.py writes <work>.record.html for every stewardship work (syllabary only, MediaRecorder, store-zip export with speaker.json; doubtful-word pass = lemma ? or uncertain sign, optional). Verified in headless Chromium from file:// with a fake mic: record/listen/re-record/save, zip valid, no romanization in DOM. docs/speakers.md (consent sheet; no honorarium line per Skip) -> speakers.html, linked from the stewardship notice. stewardship.CONTACT = speakers@weftlibrary.org (Skip's choice) shown as mailto. recording.yml: speaker reading kind, rights-kept license, no-AI checkbox. audio.py + schema section: speaker vs scheme readings, consent, withdrawal; wired into weft check; all 82 works ok; tests/test_audio.py. OPEN: (1) acceptance 1 weftlibrary.org half needs a deploy; (2) speakers@ currently hits the Cloudflare catch-all (domains@legacyportal.com), add a routing rule to skip@ if wanted.
- 2026-10-18T00:44:59Z: skeptic round 2026-10-17 fixed: GitHub attachments are public, so rights-kept readings go by email (recording.yml); *.webm/m4a/ogg/flac gitignored; check refuses rights-retained files outside private/ or a URL; no-ai-training required on speaker readings; speakers.md: publication scope, ~70 unknown words, no playback yet, withdrawal cannot revoke open licenses, opt-out of AI handling of corrections (hand entry); record page: mic released after each take, valid zip dates, optional sense box per doubtful word; contact link hidden on private works.

## Log

- 2026-10-13T20:16:46Z: Created task
- 2026-10-18T00:36:23Z: State changed from TODO to BEGUN
