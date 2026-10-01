<h1 align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="art/weft-lockup-reverse.svg">
    <img alt="Weft" src="art/weft-lockup.svg" width="320">
  </picture>
</h1>

<p align="center"><strong><a href="https://giantravens.github.io/weft/">Read the library</a></strong></p>

Living interlinear editions of classical texts. Every line of the source is stitched to
its sound, its literal word-for-word gloss, and one or more published translations,
with scholarly notes attached to the words themselves.

    Ἄνδρα     μοι      ἔννεπε,   Μοῦσα,   πολύτροπον,        ὃς     μάλα    πολλὰ
    AHN-dra   moy      EN-ne-pe  MOO-sa   po-LOO-tro-pon     hos    MA-la   pol-LA
    man       for-me   tell      Muse     of-many-turns      who    very    many-things

    Tell me, O Muse, of that ingenious hero who travelled far and wide   (Butler, 1900)

The name: the weft is the thread carried back and forth across the warp. The source text is the warp;
sound, gloss and sense are the weft that turns it into cloth. Dedicated to Neith, goddess of the loom,
and to my mother.

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
    texts/<work>/sources/        raw fetched files, hashed, never edited, never in git (weft acquire)
    texts/<work>/gen/            machine output, fully regenerable
    texts/<work>/curated/        human overlay, sparse, wins on conflict
    texts/<work>/notes/          harvested and authored commentary
    private/                     licensed material, never committed
    pipeline/                    the lifecycle steps as CLI commands
    site/                        renderer
    docs/                        schema, lifecycle, decisions

## Viewing

The library is published to GitHub Pages on every push to `main`:
<https://giantravens.github.io/weft/>. The workflow in `.github/workflows/pages.yml` runs the
tests, builds every work with `weft build all`, and deploys `site/build/`. It needs no source
files, because the build reads only what is committed.

Each page is also a single self-contained file. `site/build/<work>.html` opens from disk with no
server, so a page or the whole folder can be sent as an attachment.

## Quickstart

    uv venv && uv pip install -e .
    .venv/bin/weft acquire homer-odyssey    # lists each source and its license; nothing downloads yet
    .venv/bin/weft acquire homer-odyssey --accept-licenses   # fetch, verify sha256 against the manifest
    .venv/bin/weft draft homer-odyssey      # text, lemma, morph, sound -> gen/, telemetry -> gen/*.run.yaml
    .venv/bin/weft check homer-odyssey      # selftest: every token has every layer, every reference resolves
    .venv/bin/weft build homer-odyssey      # -> site/build/homer-odyssey.html, opens from file://
    .venv/bin/weft build homer-odyssey --private   # adds licensed translations from private/
    .venv/bin/weft say πολύτροπον ψυχὴν      # phonemize words in every scheme

## Status

Twenty-three works built across twelve languages, oldest first in the library:

| Work | Passage | Schemes | Translations |
|---|---|---|---|
| Laws of Hammurabi, prologue | column I, lines 1-53 | Old Babylonian (reconstructed), classroom Akkadian; cuneiform row generated | Harper 1904, King 1910 |
| Rigveda 1.1, Hymn to Agni | 9 verses | Vedic (with the pitch accent), modern Indian | Griffith 1896, Wilson 1850 |
| Homer, Iliad | 1.1-7 (the proem) | restored, Erasmian | Butler 1898, Lang, Leaf and Myers 1883 |
| Homer, Odyssey | 1.1-10 | restored, Erasmian | Butler 1900, Butcher and Lang 1879 |
| Aristotle, Metaphysics | A.1, 980a21-27 | restored, Erasmian | Taylor 1801, M'Mahon 1857 |
| Genesis (Bereshit) | 1:1-5 | Tiberian, modern Israeli | JPS 1917, Geneva 1599, King James 1611 |
| Gospel of John | 1:1-5 | Koine, Erasmian | Tyndale 1534, Geneva 1599, King James 1611 |
| Ovid, Metamorphoses | 1.1-9 | classical, ecclesiastical | Golding 1567, More 1922 |
| Sunzi, The Art of War | chapter 1, Laying Plans | Old Chinese (Baxter-Sagart), Tang, Mandarin | Giles 1910, Calthrop 1908 |
| Daodejing (Laozi) | chapters 1-2 | Old Chinese (Baxter-Sagart), Tang, Mandarin | Legge 1891, Chalmers 1868 |
| Epictetus, Enchiridion | 1.1-3 | Koine, restored, Erasmian | Long 1877, Higginson 1865 |
| Marcus Aurelius, Meditations | 2.1 | Koine, restored, Erasmian | Long 1862, Casaubon 1634 |
| Völuspá (Poetic Edda) | complete, stanzas 1-66 | Old Norse, modern Icelandic | Bellows 1923, Thorpe 1866 |
| Hávamál (Poetic Edda) | stanzas 1, 76, 77 | Old Norse, modern Icelandic | Bellows 1923, Thorpe 1866 |
| Li Bai, Quiet Night Thought | 4 lines | Tang, Mandarin, Cantonese | Cranmer-Byng 1909 |
| Tirukkural | chapter 1, kurals 1-10 | Old Tamil (reconstructed), modern | Pope 1886, Drew 1840 |
| Runic inscriptions: Kylver, Gallehus, Rök | 3 inscriptions | Proto-Norse, Old East Norse | Stephens 1884; Weft editorial reading |
| Beowulf | 1-11 | late West Saxon | Gummere 1910, Morris and Wyatt 1895 |
| Rubaiyat, quatrains attributed to Omar Khayyam | 6 quatrains | Early New Persian (about 1100), modern Persian | FitzGerald 1889, Heron-Allen 1899 |
| Magna Carta | chapters 39-40 | Anglo-Latin (England, 1215), classical | McKechnie 1905, Bell 1910 |
| Science in Latin: Descartes, Newton | cogito (1644); laws of motion (1687) | as first read (French, English manner), classical | Veitch 1853, Motte 1729 |
| Bashō, The Old Pond | 1 poem, 5-7-5 | Edo 1686, modern | Hearn 1898, Chamberlain 1902 |
| Grettis saga | chapter 14, sentences 1-9 | modern Icelandic, Old Norse | Morris and Magnússon 1869, Hight 1914 |

Homer, Ovid, John, Grettis saga and the Rigveda take lemma and grammar from treebanks (AGDT, LDT, MorphGNT, IcePaHC, the Vedic Treebank); Aristotle, Epictetus and Marcus Aurelius from GLAUx, an automatic parse, corrected by hand where it errs; Genesis from the Open Scriptures Hebrew Bible; Li Bai from the Kyoto Classical Chinese treebank, with Tang readings from Unicode's Unihan database. No open
treebank covers Eddic or Old English poetry or runic inscriptions, so Hávamál, the complete Völuspá, Beowulf and the
runes are hand-annotated and marked draft (see CLAUDE.md rule 3). The runic page adds a script
row, generated from the transliteration, and a labelled Weft translation where no public-domain
modern one exists. The Rigveda page reads the accent strokes of the Devanagari back into pitch
accents, checks them against the transliteration, and computes the gāyatrī metre.

`weft build` also writes `site/build/index.html`, a library page listing every built work.
Glosses, scansion, treebank corrections and editorial notes are drafts awaiting scholarly
review. See `docs/lifecycle.md` and `pin ls`.

## License

Code: MIT (`LICENSE`). Text data under `texts/`: CC BY-SA 4.0 (`LICENSE-DATA.md`), because the
Perseus treebank data is share-alike. Every source records its own license in the work's manifest,
and the sources themselves are fetched by `weft acquire`, never committed.

Corrections and new works are welcome: see `CONTRIBUTING.md`.
