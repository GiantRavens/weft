# Keyed treebanks: a design note for pin 70

Status: decided 2026-10-30: option C, with the module failure classes renamed to the core names. Implemented the same day (see the format in `docs/schema.md`).

## The question

Two works take their lemma and morphology from a corpus that draft does not read: Enheduanna's temple
hymns from Oracc's lemmatized JSON (epsd2/literary, P346196), and the Pyramid Texts of Unas from the
Thesaurus Linguae Aegyptiae (TLA) through the AES corpus. Both manifests declare `treebank: {format:
"none"}`, and the language module reads the corpus itself inside `token_fields`. Pin 70 asks whether draft
should read such corpora directly, and in what form.

## How it works now

Both corpora are keyed rather than aligned. Every edition token carries the corpus's own identifier for
that word (`ref` for Oracc, `tla` for the TLA), and the module looks the word up by that identifier. This
differs from the formats draft already reads (AGDT, LDT, GLAUx, CoNLL-U), where the edition's words are
aligned with the treebank's in order and the two are reconciled.

For each token, `sumerian.token_fields` and `egyptian.token_fields`:

1. find the corpus file through a key on the edition's section (`oracc_json`, `tla_file`);
2. look the word up by its identifier;
3. compare the edition's form with the corpus's form;
4. return `lemma`, `morph` and `tb` as ordinary token fields, beside the fields that belong to the module
   (signs, script row, normalized form, sound provenance).

Provenance is correct: each module declares its own `LAYERS`, which override the `none` that draft would
otherwise record for lemma and morph. The pages are right. The costs are structural.

## What the workaround costs

- **The manifest misstates the work.** `format: "none"` is read by draft and check as "no treebank". Every
  core sensor keyed to a treebank format is off for these two works, among them `no-treebank-word`,
  `morph-empty-declinable` and the treebank word count.
- **Each module reimplements those sensors under its own names.** `oracc-ref-missing` and
  `tla-token-missing` do the work of `no-treebank-word`; `token-not-in-oracc` and
  `edition-differs-from-tla` do the work of a form mismatch. Telemetry cannot be compared across works.
- **The corpus file is named twice, in two conventions.** The manifest names it (`treebank.file`) and so
  does the edition's section key. `oracc_json` is relative to the work's folder; `tla_file` is relative to
  the repository. Nothing checks that the two names agree.
- **`token_fields` mixes two concerns.** Corpus lookup and the module's own fields share one function, so
  neither can be tested or replaced alone.

None of this is a fault on a page today. It is the kind of drift that produces one later.

## Options

**A. Name the arrangement honestly; change nothing else.** Replace `format: "none"` with `format: module`,
which draft would read as "a treebank exists and the language module reads it". Small and safe, but it
leaves the duplicated sensors, the duplicated file name and the mixed function in place.

**B. One format per corpus in core.** Add `oracc-json` and `tla-json` to draft beside the existing formats,
each with its loader in `treebank.py`. This follows the existing pattern, but draft's format dispatch,
already six branches in two places, grows by one branch per corpus. The keyed lookup, which the two cases
share, is written twice.

**C. One keyed format in core, with the reading supplied by the module (recommended).** Draft gains a
single format, `keyed`, in which a token's identifier is looked up in a table the language module builds:

```yaml
treebank:
  id: oracc-epsd2-literary
  format: keyed
  key: ref                      # the edition token field that holds the corpus identifier
  file: sources/P346196.json    # the one place the file is named, relative to the work
```

```python
# in the language module
def load_treebank(path: Path, spec: dict) -> dict[str, dict]:
    """{identifier: {form, lemma, postag, extra: {...}}} for the whole corpus file."""
```

Draft then does what it already does for aligned formats: looks each token up, sets `lemma`, `morph` and
`tb`, and runs the core sensors (identifier missing, form differs, lemma empty, morphology empty) under the
core class names. Fields that only one corpus has (Oracc's sense and morpheme string, the TLA's sign codes)
travel in `extra` and are copied onto the token. `token_fields` keeps only what belongs to the module.

## Recommendation

Option C. The keyed lookup is the part the two corpora share, and C writes it once; the corpus formats are
the part they do not share, and C leaves those in the modules that know them. It removes the second
naming of the file, puts the two works under the core sensors, and gives any later keyed corpus (another
Oracc project, a lemmatized Coptic or Akkadian edition keyed by word id) a route that needs no change to
draft.

What C does not settle: whether the module-specific failure classes are kept as they are or renamed to the
core names. Renaming makes telemetry comparable but changes the two works' run reports; keeping them means
the core sensors and the module's run side by side for a time. The note leans to renaming, since the run
reports are telemetry and nothing on a page depends on the names.

## Plan, if C is chosen

1. Draft: a `keyed` branch in the treebank load and in the per-token match; the core sensors for keyed
   lookups; layer provenance from the manifest's `treebank.id`, as for the other formats.
2. Sumerian and Egyptian: move the corpus reading into `load_treebank`; trim `token_fields` to signs,
   script, normalized form and sound provenance.
3. Manifests and editions: set `format: keyed` and `key:`; remove `oracc_json` and `tla_file` from the
   editions.
4. Verify by redrafting both works. The token layers (lemma, morph, tb, script, sound) must come out
   byte-identical; the run reports change only in the failure class names, if renaming is chosen.
5. Docs: the format in `docs/schema.md`, and a recipe in `docs/building.md` for adding a keyed corpus.

## Where the evidence is weakest

Two works are a small base for a general interface. The proposal assumes that later keyed corpora will
offer a stable per-word identifier and a single file to read, which Oracc and the TLA do; a corpus split
across many files, or keyed by position rather than by identifier, would need the interface widened.
