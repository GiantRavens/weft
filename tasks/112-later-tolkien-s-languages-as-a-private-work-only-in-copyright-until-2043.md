---
id: 112
title: 'Later: Tolkien''s languages as a PRIVATE work only (in copyright until 2043): ...'
state: BEGUN
priority: 3
tags:
  - later
  - private
created_at: 2026-10-01T17:45:33.848351-05:00
updated_at: 2026-10-02T11:56:24.722111189-05:00
started_at: 2026-10-02T11:56:24.716712913-05:00
---

# Later: Tolkien's languages as a PRIVATE work only (in copyright until 2043): Namárië with Tolkien's own pronunciation guide; never published

## Notes

- 2026-10-01T23:35:34Z: Sources: The Road Goes Ever On arriving in the kf library (2026-10-01). Tolkien Estate audio page https://www.tolkienestate.com/audio-visual/audio/ streams his 1952 recordings: Namárië sung 'in the style of a Gregorian chant' (Quenya) and A Elbereth Gilthoniel read (Sindarin), plus the Ents' marching song in Entish; no download or licence terms on the page, so listen-and-check only (private), never redistribute. Build Namárië and A Elbereth Gilthoniel together: one Quenya, one Sindarin.
- 2026-10-01T23:44:13Z: Source policy for the Tolkien work: every form and rule must trace to Tolkien's own text (LotR App. E/F, Silmarillion, The Road Goes Ever On, PE 17 and 19, VT, Letters); secondary work only points to it, and 'neo-Quenya'/'neo-Sindarin' (fan-reconstructed forms) is excluded. Useful secondary: Stainton, 'Quenya Prosodic Structure', Western Papers in Linguistics (stress and vowel length; cites PE 17, PE 19); Kelsey Ryan, 'Tolkien's tongues' (Swarthmore thesis 2014, open); Eldamo (Paul Strack), which cites primary sources and flags neo forms. Not useful: Nimavat 2016 (Vidhyayana e-journal), thin and mis-cited.
- 2026-10-01T23:46:49Z: Ryan 2014 (Swarthmore undergraduate thesis, 33 pp., read in full): useful for (1) Praat vowel-formant measurements of Tolkien's own recorded Namárië (from the Road Goes Ever On recording): long vowels peripheral, short vowels centralized, i.e. length came with a quality difference in his speech; (2) a syllabified IPA transcription of Namárië (no stress marked) to check our syllable division; (3) its note that about 7.7 s (2.5 lines) of the recording do not match the published text. Limits: cites LotR, RGEO, Letters and secondary Tolkien Studies papers but not PE 17 or PE 19 (both available by 2014), so rules come from App. E and PE 19, not from Ryan. Copy at ~/Desktop/2014RyanK_thesis.pdf.
- 2026-10-01T23:48:03Z: Appendix E is in the kf library three times: 'The Lord of the Rings by JRR Tolkien 1954' (HarperCollins, md + PDF; Appendix E around md line 21411: use the PDF for exact wording and page numbers), the 2012 HMH one-volume (md only; cleanest text, Appendix E at md line 19839), and The Return of the King (2005 HM, md only, line 789).
- 2026-10-01T23:52:46Z: Eldamo reviewed (v0.8.13, 2026-05-31): github.com/pfstrack/eldamo, data at src/data/eldamo-data.xml (30 MB; Paul Strack; data CC BY 4.0, code MIT). Use it as the lexicon layer, like a treebank: each <word l='q' v='laurië' gloss=...> carries <element> parts and <ref source='PE17/058.4404'> citations to the exact page and line of Tolkien's text. Neo forms are quarantined in separate languages (nq Neo-Quenya, ns Neo-Sindarin, np), and Tolkien's periods are separate too (q Quenya vs mq Middle Quenya vs eq Early Qenya): take lemmas only from q and s, never nq/ns. Its 2,508 phonetic-rule entries are historical sound changes with examples (useful for notes); synchronic pronunciation still comes from App. E and PE 19. Pin the XML by commit sha256 in the private manifest.
- 2026-10-02T16:56:24Z: 2026-10-02 BUILT on futhark: private/tolkien-namarie (Quenya, 17 lines, 79 tokens) and private/tolkien-elbereth (Sindarin, 7 lines, 23 tokens) draft/check/build --private green. pipeline/weft/elvish.py (public, rules only) reproduces all 12 App. E stress examples and every RGEO stress mark on Namárië (via Eldamo refs). Sources: owner's 2012 HMH e-text passages (local: true, sha256) + Eldamo XML pinned at 4071c9c. Lemma/gloss from Tolkien's own word glosses via Eldamo citations (LotR/0377, LotR/0238). OPEN: add RGEO when the kf copy lands (sense + stress check); Sam's invocation (Book IV) as a third text; scholar review of the hand annotation.

## Log

- 2026-10-01T22:45:33Z: Created task
- 2026-10-02T16:56:24Z: State changed from TODO to BEGUN
