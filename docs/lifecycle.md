# The lifecycle of a text

Ten steps. Steps 2 to 5, 7 and 10 are `pipeline/` subcommands (`weft acquire`, `weft draft`,
`weft align`, `weft build`); `weft check` tests the result. Steps 1, 6, 8 and 9 are human work.

| # | Step        | Input                          | Output                          | Judgment? |
|---|-------------|--------------------------------|---------------------------------|-----------|
| 1 | select      | a candidate text                | `manifest.yaml`                 | human     |
| 2 | acquire     | manifest URLs                   | `sources/` with sha256          | no        |
| 3 | identify    | source text                     | line IDs (CTS)                  | no        |
| 4 | tokenize    | lines + treebank                | token to treebank mapping       | edge cases|
| 5 | phonemize   | tokens + scheme                 | IPA, respelling, metre          | no        |
| 6 | gloss       | lemma + morph + lexicon         | gloss cell                      | human (one treebank, Kyoto, supplies one) |
| 7 | align       | translation text                | span map to line IDs            | some      |
| 8 | notes       | PD commentaries, authored notes | `notes/` keyed by line/token    | human     |
| 9 | review      | low-conf queue                  | `curated/` overlay              | human     |
|10 | build       | gen + curated + notes + private | `site/build/`                   | no        |

Versioning: every gen file records the pipeline version that produced each layer. Upgrading a
rule re-runs one step; the git diff is the review task; the count of changes per class is the sensor.

## Three paths for the lemma and grammar

1. **A treebank or lemmatized corpus exists for this text** (Homer, Ovid, the Greek New Testament,
   Grettis saga, the Rigveda, Genesis, Li Bai, Dante, the Pyramid Texts from the TLA, Enheduanna
   from Oracc). The treebank supplies lemma and morphology; `weft draft` maps
   it onto the edition's words and reports any it cannot match.
2. **An automatic parse exists** (GLAUx for Aristotle, Epictetus and Marcus Aurelius). It is used like
   a treebank, and its errors are corrected in `curated/`.
3. **No treebank exists** (Eddic poetry, Beowulf, the runes, the Bayeux captions, Hammurabi, most of the
   Renaissance and modern works). The manifest says `treebank: null`; lemma, morphology
   and gloss are annotated by hand in `curated/` against a named dictionary, marked `draft`, and the
   page says so. Only a human reviewer lifts the draft status.

## Weft's own edition files

Where no source file can be read line by line as it stands (inscriptions, captions, texts that need
Weft's own line division), the work carries an `edition.yaml` in the `weft-edition` format. Each line is checked against the pinned source (by `verify_in`, or for OCR and TEI
sources by a sensor in the language module); a line not found is reported as the failure class
`edition-not-in-source`. The runic inscriptions are not checked against a source. Sections may carry an image (`figure`), shown under the section heading.

## Translations

Public-domain translations are printed and aligned in `sense/`. A translation still in copyright is
listed with `kind: reference`: the page names it and does not print it. A reader who owns a copy can
add it to their own private build (`private/<work>/`, never committed). Where no usable translation
exists, Weft may supply one marked `kind: editorial` and `draft`.

## Phases

0. **Done 2026-09-29.** `od.1.1-10` as the golden passage: generated text, lemma, morphology and
   sound; hand-made gloss, metre, alignment and notes; the renderer, the Loom settings panel, veil
   mode, print and phone layouts.
1. **Done 2026-10-01.** Breadth: 46 works in 20 languages, from the Pyramid Texts to Nietzsche
   (the list is in `README.md`). Readers for the source formats, phonology for each language, the
   hexameter scanner (checked against 62 hand scansions), Weft's own edition format, reference
   translations, section images, and the invitation to specialists on reconstructed pronunciations.
2. **Next: review.** Scholars correct and review the draft layers, through the issue forms or pull
   requests (see `CONTRIBUTING.md`). The open questions logged for each work are in Pin.
3. Audio: recordings offered by readers, an espeak-ng baseline, then IPA-driven speech synthesis and
   forced alignment for word-level highlighting.
4. Depth: whole works rather than passages, a generated first-pass gloss with confidence scores (today glosses are written by hand, or taken from the one treebank that carries one), and a
   review queue ordered by confidence.
