# Building a work: the playbook

This page is the working method for adding a text to the library. `CLAUDE.md` gives the rules,
`docs/schema.md` the shape of every file, `docs/lifecycle.md` the steps in principle. This page is
the order in which the work is actually done, the recipes that recur, the patterns in the edition
file that solve the common source problems, and the mistakes already made once. A session that has
read `CLAUDE.md` and this page can build a work without reading the others first.

A work is a folder `texts/<work>/` with a manifest, an edition or a pointer to one, generated
layers, a human overlay, aligned translations and notes. The acceptance gate is `weft check`
reporting `ok: true`, the page building, the test suite passing, and the row in `README.md`. Nothing
is "done" before that.

## The sequence

1. **Recon the source.** Find a public-domain edition of the original and at least one
   public-domain English translation, and establish how lemma and grammar will be had (a treebank,
   an automatic parse, or hand annotation against a named dictionary). Record what you find in the
   Pin task. Do not start the folder until the four things in `CONTRIBUTING.md` ("Proposing a
   text") exist.
2. **Scaffold the folder:** `weft scaffold <work> --lang <code>` writes the manifest skeleton with
   the language's schemes in the right order and the empty folders.
3. **Pin every source by revision:** `weft pin <work> <url>` fetches a page or file, saves it under
   `sources/`, records the sha256, and appends the entry to `sources_extra` (or sets the edition's
   file with `--edition`). A Wikisource page URL is resolved to its current revision and pinned by
   `oldid`, so the citation names a fixed text. Sources are never committed; the manifest's sha is
   how another clone verifies its own copy.
4. **Write `edition.yaml`** in the `weft-edition` format when the source cannot be read line by
   line as it stands (most prose, inscriptions, anything needing Weft's own line division). Each
   token is the word as printed with its punctuation attached; the patterns below handle markup,
   OCR and symbols. Run `weft draft <work>` and read the failure classes before anything else:
   `edition-not-in-source` means a line does not reproduce its source, and that is fixed first.
5. **Annotate.** Where a treebank exists the draft supplies lemma and morphology and you correct in
   `curated/`. Where none exists, write the overlay by hand: lemma, morphology in Universal
   Dependencies features, a gloss, and for verse the staves and metre. The compact spec and
   `weft overlay` (below) make this a page of text rather than a thousand lines of YAML. Reuse
   from sibling works is a hint, not an answer: the same form means different things in context.
6. **Align the translations** in `sense/`: one span per unit, verbatim from the pinned translation
   file; verse-numbered Bibles align with `weft align`; everything else by hand. A translation that
   covers only part of the text is declared `partial: true`; one still in copyright is
   `kind: reference` and is named, not printed.
7. **Write the notes**, five or six for a short work: the text's origin and date, the spelling of
   the print, the two or three passages a reader will ask about, and the connections to works
   already in the library. Every note names what it leans on.
8. **Finish the manifest:** title, `short_title`, author with dates, `lang_name`, `written` with a
   label, the edition record, schemes and their labels for this time and place,
   `sound_confidence`, translations with licences, and `predicted_gaps`, which states what the
   work does not yet do and what is approximate.
9. **Image:** `weft image <work> "File:Name.jpg"` fetches a Commons image, writes the two sizes
   under `art/works/`, and appends the credits record; the caption and alt text are yours.
10. **Rows:** add the work to the table in `README.md` and to the summary table in
    `docs/languages.md` (and a language section there if the language is new).
11. **Gate:** `weft check <work>`, `weft build <work>`, `weft build all`, then the suite. Run the
    suite so a failure cannot hide behind a pipe:

        set -o pipefail; uv run --with pytest pytest -q tests | tail -3; echo rc=$?

    Re-check the other works in the language after any change to a module or a shared lexicon.
12. **Record** the work in its Pin task, and leave the commit to the owner of the repository.

## Recipes

**Wikisource.** The API gives a page's current revision and the raw wikitext:

    https://<lang>.wikisource.org/w/api.php?action=query&prop=revisions&titles=<title>&rvprop=ids&format=json
    https://<lang>.wikisource.org/w/index.php?oldid=<revid>&action=raw

Prefer the `Page:` or `Seite:`/`Pagina:` scan pages (one per printed page, with a proofreading
level) over the transcluded whole; pin each page you use. A section whose lines cross a page break
names its pages as a list in `verify_in`, and the pages are read together. `weft pin` does the
resolution and the hashing. Always send a User-Agent that names Weft and a contact; the APIs
refuse anonymous bursts.

**heimskringla.no** (the Eddic poems and sagas in Guðni Jónsson's normalized text) refuses `action=raw`
and answers 500 now and then; `weft pin` reads the revision through its API and retries once. A poem page
is pinned as the edition with `weft pin <work> 'https://heimskringla.no/wiki/<Title>' --edition --as
stanza-text`, which converts the wikitext to the stanza-text layout (speaker lines such as `Óðinn kvað:`
and the stanza numbers kept, markup dropped), records the conversion in the manifest, and lets
`weft acquire` reproduce the file and verify its sha. A dialogue poem's speaker lines become the stanza
headings on the page. Scaffold such a work with `--unit stanza --format stanza-text`.

**Internet Archive.** `https://archive.org/download/<id>/<id>_djvu.txt` is the OCR text of a scan.
Fraktur OCR is usable with the German module's `check` (below); the long s, the superscript-e
umlauts and the Fraktur hyphen are normalized, and the misreadings are declared token by token.

**Commons.** The imageinfo query returns the original's URL and the metadata (artist, date,
licence) that the credits record needs:

    https://commons.wikimedia.org/w/api.php?action=query&titles=File:<name>&prop=imageinfo&iiprop=url|size|extmetadata&format=json

Images are stored as JPEG, the longest side 760 px for the page and 220 px for the library row.
Public domain or CC BY-SA only, and the credits say which.

**Translations.** Project Gutenberg and the English Wikisource carry most of what is public domain.
"Public domain" is judged by the translator's death plus seventy years, not by US publication
alone; a translation that is free only in the United States is cited as a reference.

## Patterns in the edition file

The verbatim check joins each line's tokens and looks for the result in the source after
`verify_strip` has removed markup and `verify_corrections` have been applied. The patterns:

- **Templates and tags.** `\{\{[^{}]*\}\}` removes a simple template; a nested one needs its outer
  name spelled out, `\{\{CRef\|\|(?:[^{}]|\{\{[^{}]*\}\})*\}\}`. `<[^>]+>` removes tags and leaves
  their content, which is what you want for `<math>` and `<i>`. Put the specific alternatives
  before the general ones; the engine tries them in order. A flag such as `(?s)` or `(?m)` must
  stand at the very start of the pattern or Python rejects it.
- **Spaced-type markup** that wraps a word (`{{ss|Maxwell|.2}}`) is stripped in two pieces,
  `\{\{ss\|` and `\|\.2\}\}`, so the word stays.
- **Punctuation the print sets off** (French ` :` and ` ;`, the German dash) goes in the token's
  `p`; an elision (`l’`, `qu’`, `d’`) is its own token with `glue: true`; a dash the print runs
  into the next word stays with the first token with `glue: true`.
- **OCR and transcription slips** are `verify_corrections`, each `{ocr, print, in}`; a correction
  that matches nothing is itself reported, so a stale one cannot linger.
- **A symbol or formula** is a token printed as the paper prints it (`E₀`, `L/V²`), with the
  transcription's TeX as `src`, the words a reader says for it as `n`, and its sound given outright
  in `ipa`. A displayed equation is a line of its own, `{equation: {tex, say, gloss}}`: the TeX is
  checked against the source, the page builds MathML from it, and `say` is sounded in each scheme.
- **Liaison and sound marks** are per language: French `z` and `zf`, Italian `m` and `dialefe`,
  German `src` and `ipa`, Norse nothing. The module's docstring lists its fields; read it before
  the first token.
- **An OCR source** for German uses the section field `check: {file, format: fraktur-ocr, strip}`
  instead of `verify_in`; the comparison is without spaces and each token's `src` is the OCR's
  reading where it differs from the print.

## The overlay

Where no treebank exists, the overlay carries lemma, morphology and gloss for every token (and for
verse the metre and staves). Write it in the compact spec and expand it:

    weft overlay <work> <spec.yaml> --out stanzas-81-110.yaml

The spec is a YAML file: `by`, `date`, `why`, `status`, and `lines`, a map from line id to the line's
annotation. A line is its tokens as `Surface|gloss|lemma|code`, separated by ` ;; `; a stave word
carries a leading `*`; a verse line may begin with its metre, `a g ::` (long line, a-verse, stave g),
`b g ::` or `f sk ::` (full line, staves sk), with ` | note` at the end for an irregular line. The
code is a shorthand for Universal Dependencies features, the grammar the Hávamál overlays were
written in: `N.afp` is a noun, accusative feminine plural; `PN.gms` a proper noun; `A.nms.c` a
comparative adjective; `V.i3s.pr` a verb, indicative third singular present, `V.s2p.pa` subjunctive
past, `.neg` for the suffixed negative, `.m` for the middle voice; `V.inf`, `V.pp.nms` (past
participle), `V.prp.nfs`, `V.imp2s`; `AUX.i3s.pr`; `P.ns1` a personal pronoun by case, number and
person (`P.as3m` adds gender; `P.ds3` is the reflexive); `DEM.nms`, `POSS.ams`, `INDEF.nms`,
`INT.nns`, `REL` for the other pronouns and determiners; `D.fs`, `Di.ms` the definite and
indefinite article; `NUM.dfp`; and `ADV`, `ADP`, `CC`, `SC`, `PART`, `INTJ`, `SYM` bare. A code
already written as UD features is passed through. The expander checks every surface against the
generated text and refuses a spec that does not match it, so the ids cannot drift; it is the same
expansion the Hávamál overlays for stanzas 81 to 164 were produced with.

Method: build a reuse map from the overlays of sibling works (`weft overlay --reuse <work>` prints
the most common annotation for each form), fill the matches, and then read every line in context
and override what the context changes. The overlay's `by:` names the method; `status: draft`
stays until a human reviewer lifts it.

## Gotchas already paid for

- The Italian lexicon sensor reads only the shared `it_lexicon.yaml`; a work-local pronunciation
  table is used for the sound but flags every word as missing. Put Italian words in the shared table.
- German loanwords (Latin `-tion`, French names) cannot be read by the letter rules; give them an
  IPA map entry `{syl, northern, modern}` as Kant's Latin has.
- The German module reads a polysyllable missing from its lexicon by rule and reports it as
  `syllables-by-rule`; add the word, do not ignore the report.
- The gloss convention is one gloss per token; the count must match the token count line by line.
  Check all lines before writing, not one per attempt.
- Test fixtures that need `site/` must link its three files and make their own `build/`; a symlink
  to the whole folder writes the fixture's output into the real library.
- A run that pipes `pytest` into `tail` hides the exit code; use `pipefail` and print the code.
- Bellows's Hávamál, Thorpe's Edda, and the Kerr Manifesto number differently from the standard
  text in places; align by content and say so in the sense file's `aligned_by`.
- In a spec written with Python templates, `.replace("logi|", ...)` on a refrain line hits the lemma field
  as well as the surface; replace a longer key (`"logi|flame"`). `weft overlay` refuses a lemma that
  carries punctuation, which is how that slip shows itself.
- The CLTK copy of the heimskringla Hávamál stops at stanza 145. Check a "complete" file against
  the standard count before building on it.
