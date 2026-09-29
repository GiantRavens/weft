# Rhapsode

Living interlinear editions of classical texts. Every line of the source is stitched to
its sound, its literal word-for-word gloss, and one or more published translations,
with scholarly notes attached to the words themselves.

    Ἄνδρα     μοι      ἔννεπε,   Μοῦσα,   πολύτροπον,        ὃς     μάλα    πολλὰ
    AHN-dra   moy      EN-ne-pe  MOO-sa   po-LOO-tro-pon     hos    MA-la   pol-LA
    man       for-me   tell      Muse     of-many-turns      who    very    many-things

    Tell me, O Muse, of that ingenious hero who travelled far and wide   (Butler, 1900)

The name: a ῥαψῳδός was the reciter who "stitched songs" together.

## The four layers

| Layer   | What it is                                                | Source of truth              |
|---------|-----------------------------------------------------------|------------------------------|
| source  | the text in its own script, pinned to one edition         | Perseus / PROIEL / Menota    |
| sound   | pronunciation respelling, derived from IPA per scheme      | rules over the orthography   |
| gloss   | one English cell per source word, order preserved         | treebank lemma + lexicon     |
| sense   | published translations, any number, each attributed       | public domain editions       |

Later layers: metre, notes, audio. Layers are named, never numbered.

## Principles

- **Text as code.** Every passage is a YAML file under `texts/`, addressed by CTS URN, versioned in git.
- **Generated and curated never share a file.** `gen/` is regenerable by the pipeline. `curated/` is a sparse human overlay that wins on conflict and carries attribution.
- **Provenance on every field.** Each value says what produced it and how confident it is.
- **Translations are a list, not a slot.** Adding one costs one alignment pass.
- **Public and private builds from one codebase.** Copyrighted translations live in `private/` (gitignored) and appear only in your own build.
- **No framework.** The site is static HTML, CSS and JS that works offline and prints.

## Layout

    texts/<work>/manifest.yaml   what, from where, which schemes, predicted gaps
    texts/<work>/sources/        raw fetched files, hashed, never edited
    texts/<work>/gen/            machine output, fully regenerable
    texts/<work>/curated/        human overlay, sparse, wins on conflict
    texts/<work>/notes/          harvested and authored commentary
    private/                     licensed material, never committed
    pipeline/                    the lifecycle steps as CLI commands
    site/                        renderer
    docs/                        schema, lifecycle, decisions

## Status

Founded 2026-09-29. Phase 0: hand-built Odyssey proem and a first renderer. See `docs/lifecycle.md`
and `pin ls`.

## License

Code: MIT. Text data under `texts/`: CC BY-SA 4.0, because Perseus treebank data is share-alike.
Every source records its own license in the work's manifest.
