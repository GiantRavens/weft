# The lifecycle of a text

Ten steps. Each is a `pipeline/` subcommand except 1 and 9, which are human.

| # | Step        | Input                          | Output                          | Judgment? |
|---|-------------|--------------------------------|---------------------------------|-----------|
| 1 | select      | a candidate text                | `manifest.yaml`                 | human     |
| 2 | acquire     | manifest URLs                   | `sources/` with sha256          | no        |
| 3 | identify    | source text                     | line IDs (CTS)                  | no        |
| 4 | tokenize    | lines + treebank                | token to treebank mapping       | edge cases|
| 5 | phonemize   | tokens + scheme                 | IPA, respelling, metre          | no        |
| 6 | gloss       | lemma + morph + lexicon         | gloss cell + conf               | LLM pick  |
| 7 | align       | translation text                | span map to line IDs            | some      |
| 8 | harvest     | PD commentaries                 | `notes/` keyed by line/token    | some      |
| 9 | review      | low-conf queue                  | `curated/` overlay              | human     |
|10 | build       | gen + curated + notes + private | `site/build/`                   | no        |

Versioning: every gen file records the pipeline version that produced each layer. Upgrading a
rule re-runs one step; the git diff is the review task; the count of changes per class is the sensor.

## Pilot passages

| Work                      | Passage           | Language        | Why                                   |
|---------------------------|-------------------|-----------------|---------------------------------------|
| Homer, Odyssey            | 1.1-10            | Homeric Greek   | **done**: golden passage; AGDT treebank |
| John                      | 1:1-5             | Koine Greek     | Bible in its source language (Skip, 2026-09-29) |
| Ovid, Metamorphoses       | 1.1-9             | Latin           | **done**: LDT stream treebank, enclitics, stress rule |
| Virgil, Aeneid            | 1.1-11            | Latin           | no treebank for book 1: first treebank-free text |
| Poetic Edda, Hávamál      | st. 1, 76, 77     | Old Norse       | **done**: no treebank, hand annotation, alliteration staves |
| Chaucer, General Prologue | 1-18              | Middle English  | rule-based pre-GVS vowels             |
| Beowulf                   | 1-11              | Old English     | **done**: Heyne accents to macrons, caesura, staves, compound stress |
| Grettis saga              | ch. 14, s. 1-9    | Old Icelandic   | **done**: IcePaHC treebank is the edition; prose, sentence unit |

## Phases

0. **Done 2026-09-29.** `od.1.1-10` as the golden passage: generated text, lemma, morphology and
   sound; hand-made gloss, metre, alignment and notes; the renderer, the Loom settings panel, veil
   mode, print and phone layouts.
1. **In progress.** Readers for six source formats and phonology for six languages are built, with
   eight works in the library (see the pilot table and `pin ls`). Open: a generated gloss step with
   confidence scores, the hexameter scanner, and a path for texts with no treebank.
2. Audio: an espeak-ng baseline, then IPA-driven speech synthesis, then forced alignment for
   word-level highlighting.
3. Notes: commentaries harvested from public-domain editions, alongside lexicon-grounded notes.
4. Scale: whole works, further languages, and a review queue ordered by confidence.
