# About Weft

Weft is a library of interlinear editions. Each page sets a passage of a classical text in its original form and,
under every word, two further rows: how the word most likely sounded when the text was first
written, and a literal word-for-word English gloss. Under each line come one or more published
translations. Notes attach to words and lines. The library runs from the Pyramid Texts of Unas
(about 2350 BC) to the General Act of the Berlin Conference (1885), in twenty-four languages.

It is dedicated to Neith, goddess of the loom, and to the author's mother. The weft is the thread
carried back and forth across the warp; the source text is the warp, and sound, gloss and sense are
the weft.

## Reading a page

- **The original line** is set in its own script. Egyptian, Sumerian and Akkadian lines are set in
  transliteration, with a hieroglyphic or cuneiform row generated from it; Hebrew and Persian run
  right to left.
- **The sound row** respells each word for an English reader. Capitals mark the stressed syllable,
  or the raised pitch in languages with a pitch accent; hyphens separate syllables. The Sound key
  in the masthead explains every symbol for the scheme in use.
- **The gloss row** gives one English cell per source word, in the source's word order. Several
  English words join with hyphens, and grammar rides in the English: `of-the-guest` for a genitive,
  `she-saw` for a verb with its person. It is a crib for following the original, not a translation.
- **Translations** sit under each line or group of lines, each attributed with its translator and
  year. Where a good translation is still in copyright, the page cites it as a reference and does not
  print it.
- **Tap a word** to open its detail: the dictionary headword (lemma), its grammatical form, the
  gloss, its sound in every scheme with the IPA, any notes on it, and where each of those came from.
- **The Loom** (the settings panel) turns rows on and off, switches the pronunciation scheme,
  chooses translations, and can veil the gloss and translations so you read the original first and
  tap to check yourself. Settings are kept in your browser.

Every page is one self-contained file. It opens from disk without a server and prints cleanly; the
fonts load from Google Fonts when you are online, and some scripts need them to display.

## Why the editions are built like software

A printed interlinear fixes one editor's judgments in one state. Weft keeps every layer of a page
as a plain text file in a public repository, under version control. Four consequences follow.

1. **Every judgment is attributed.** A correction is a small entry that names who made it, when, and
   why. The page shows where each value came from.
2. **Machine work and human work are kept apart.** The pipeline generates a first layer (the text,
   lemma and grammar from a treebank where one exists, the sound from rules) into `gen/`. Human
   corrections go in a separate overlay, `curated/`, which wins where the two differ. The generated
   layer can be rebuilt at any time without losing a single human decision.
3. **Every change is reviewable and reversible.** A correction arrives as a proposal, is discussed
   in the open, and can be undone. The history of each reading is kept.
4. **Rules improve the whole library at once.** When a pronunciation rule is corrected, the works in that language are regenerated from it, and
   the change in each generated file can be inspected before it
   is accepted. A specialist's correction to a rule reaches every line it governs.

## What the sound row claims

The first pronunciation scheme on every page is the reconstruction Weft judges best supported of how the text most likely
sounded when it was first written: Dante in the Florentine of about 1307, Luther's theses in Latin as it was read in
Saxony, the Rigveda with its pitch accent. Where the evidence for a text's own period is thin, the
nearest well-studied stage stands in, and the page says so: Homer is read in the reconstructed
classical Attic of the fifth century BC, about three centuries after the poems took shape. Later traditions (the
Erasmian Greek of schools, the ecclesiastical Latin of the church, modern Icelandic) are offered
second, and the reader can switch between them.

The evidence differs greatly by language. For classical Latin and Greek it is strong and well
studied. Egyptian writing records no vowels at all, so any vocalized reading is a conjecture; Sumerian's
sounds are known only indirectly, through Akkadian scribal usage, and its stress and vowel length
are unknown. Pages whose first scheme rests on indirect evidence say so at the top and invite
specialists to correct it. [Languages and pronunciation](languages.md) sets out, language by language, what each scheme
rests on and where it is weakest.

The respelling approximates the reconstruction for an English reader. It is not a claim that the
original speakers sounded like English speakers.

## Draft and reviewed

Much of the library is draft. Where no treebank exists (Eddic poetry, the Bayeux captions, Hammurabi), the lemma, grammar and gloss were annotated by hand against a named dictionary, and
the notes were written for this edition. All of it is marked `draft` on the page. Only a human
reviewer lifts that status, by checking the material and recording the review under their name.

Generated material is labelled by what produced it. Material produced by rule or by a treebank is
not reviewed by default either; where a value is doubtful, the corrections overlay is where the
better reading goes.

## Sources and licences

- Every source text, treebank and translation is public domain or openly licensed (CC BY-SA, CC BY, CC0,
  and the Unicode License for the Chinese reading tables). Material under non-commercial licences is not used. Each work's manifest records the
  licence, the address and a checksum of every source.
- Sources are not stored in the repository. Each reader fetches their own copy with `weft acquire`,
  which shows the licences first and verifies the checksums.
- Modern scholarship is quoted only in short phrases, attributed, in the notes. Quoted words remain
  under their owners' copyright.
- Weft's own data is released under CC BY-SA 4.0; the code under the MIT licence.

## How to take part

You do not need to use git. Each kind of contribution has a short
[form on GitHub](https://github.com/GiantRavens/weft/issues/new/choose) that asks the right
questions; a maintainer turns the answer into a correction with your name on it.

- **A gloss, parse, scansion or note is wrong:** the Correction form.
- **A pronunciation is wrong, or a scheme should be added:** the Pronunciation form. A citation is
  required.
- **You would record a passage:** the Recording form. Audio is not yet played on the pages;
  recordings are collected now and added with credit when it is.
- **A text belongs in the library:** the Propose a text form.

Each page links to the correction, pronunciation and recording forms from its foot and, where the pronunciation is reconstructed,
from its top. Contributors who do use git can submit the correction directly;
[Contributing](../CONTRIBUTING.md) describes both routes.

## Further reading

- [Contributing](../CONTRIBUTING.md): how corrections, recordings and new texts are submitted and reviewed.
- [Languages and pronunciation](languages.md): each language's schemes, evidence and weak points.
- [The lifecycle of a text](lifecycle.md): how a text moves from selection to a published page.
- [The data schema](schema.md): the data formats, and the conventions for gloss, sound and notes.
- [The repository](https://github.com/GiantRavens/weft) and its [open issues](https://github.com/GiantRavens/weft/issues).
