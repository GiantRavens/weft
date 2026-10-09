# Data schema v0 (frozen 2026-09-29)

All files are YAML. IDs are CTS-style short forms: `od.1.1` is Odyssey book 1 line 1,
`od.1.1.5` its fifth word. The manifest's `urn` and `prefix` map short forms to full CTS URNs.

A work lives in `texts/<work>/`:

| Path                 | Written by        | Holds                                                    |
|----------------------|-------------------|----------------------------------------------------------|
| `manifest.yaml`      | human             | what, from where, hashes, licenses, schemes, predicted gaps |
| `sources/`           | `acquire` (later) | raw fetched files, never edited                           |
| `gen/bookNN.yaml`    | `weft draft`      | text, lemma, morph, sound. Regenerable. Never hand-edited |
| `gen/bookNN.run.yaml`| `weft draft`      | run telemetry: counts, failure classes, shift-left flags  |
| `curated/bookNN.yaml`| humans            | overlay changesets; win over gen on conflict              |
| `sense/<tr>.yaml`    | align (hand in phase 0) | one file per translation, spans keyed to line IDs  |
| `notes/bookNN.yaml`  | harvest + humans  | notes attached to token or line IDs                       |
| `about.yaml`         | `weft about`      | what the work is: Wikipedia lead and Wikidata subjects. Regenerable |

`private/<work>/` mirrors this layout for licensed material, with its own `manifest.yaml`
listing private translations. Only `weft build --private` reads it.

## Provenance encoding (decision)

Provenance is data, not comments, so tools can read it.

1. **File-level defaults.** `gen` files open with a `layers` map giving the default `src` for
   each field: `lemma: {src: agdt-2.1}`.
2. **Per-token exceptions.** A token carries `prov: {field: "src string"}` only where it differs
   from the default, e.g. a sound layer that used the quantity table.
3. **Human changes carry their changeset.** The build stamps every curated field with
   `curated: {field: {by, date, status}}`, so the page can show who changed what.
4. **Judgment carries confidence.** When a generated step makes a judgment call (the future gloss
   step), it writes `conf: {field: 0.0-1.0}` beside the value. Below the review threshold the item
   goes to the review queue.

## gen/bookNN.yaml

```yaml
work: homer-odyssey
pipeline: {weft: 0.1.0, greek: '0.1'}
layers:
  text: {src: perseus-grc2}
  lemma: {src: agdt-2.1}
  morph: {src: agdt-2.1}
  sound: {src: weft.greek 0.1}
lines:
- id: od.1.1
  cite: urn:cts:greekLit:tlg0012.tlg002.perseus-grc2:1.1
  text: ἄνδρα μοι ἔννεπε, μοῦσα, πολύτροπον, ὃς μάλα πολλὰ
  tokens:
  - id: od.1.1.5
    surface: πολύτροπον
    punct: ','                 # trailing punctuation, kept apart from the word
    lemma: πολύτροπος
    morph: a-s---ma-           # AGDT 9-position tag; the build adds readable morph_text
    tb: 2185541/7              # treebank sentence/word
    sound:
      restored: {ipa: po.lý.tro.pon, respell: po-LÜ-tro-pon}
      erasmian: {ipa: po.ˈly.tro.pon, respell: po-LÜ-tro-pon}
    prov: {sound: weft.greek 0.1 + quantity table}   # only when it differs from layers
```

## curated/bookNN.yaml

A list of changesets. Each is one person's one act of judgment, so it maps onto one pull request.

```yaml
- by: A. Scholar
  date: 2026-10-02
  why: keep the etymology visible; the smooth reading belongs in sense
  status: reviewed           # draft | reviewed
  set:
    od.1.1.5: {gloss: much-turned}
    od.1.1: {metre: "—◡◡|—◡◡|—◡◡|—◡◡|—◡◡|—×"}
```

Keys under `set` are line or token IDs. Later changesets win over earlier ones.
**Quote any value YAML 1.1 would read as a boolean**: `on`, `off`, `yes`, `no`. `weft check`
flags the class as `gloss-not-string`.

## sense/<translation>.yaml

```yaml
translation: butler1900      # must match an id in the manifest's translations
aligned_by: hand, phase 0
spans:
  - lines: [od.1.1, od.1.2]  # first and last line covered, inclusive
    text: "Tell me, O Muse, of that ingenious hero ..."
```

Spans must not overlap and should cover every line. `weft check` reports `sense-overlap` and
`sense-gap`. The page shows a span after the last line it covers.

## Translations: partial and editorial

A translation entry may carry `partial: "<reason>"` when it covers only some lines (Stephens
predates the Kylver find), and `kind: editorial` when the text is Weft's own translation rather
than a published one. The page labels editorial translations "editorial, draft" with a dashed rule.

## Section images

A section in a Weft edition file may carry `figure: {file, caption, alt, credit, license, source}`,
with `file` a path from the repository root (for example `art/works/<work>/scene-57.jpg`). The build
embeds it, so the page stays one file, and shows it under the section heading. Use it for an image that
belongs to that passage only: a tapestry scene, a manuscript page, an inscription. Images must be
public domain or openly licensed, like every other source.

## The date in the library

`written: {year, display, label}` in the manifest. `year` sorts the library and places the work in an
age (negative for BC). `display` is the short date shown in bold in the library's left column, above
the language: a single year ("1517"), a range ("1755–1750 BC"), or an approximate date ("c. 2350 BC",
"4th–3rd c. BC"). Without it the column shows the year. `label` is the longer sentence under the
title. A work can override the language name shown there with `lang_name`.

## About the work: wikipedia and about.yaml

`wikipedia: {title, match, lang}` in the manifest names the Wikipedia article that describes the work.
`match` is one of `work` (the article is on this text, or on the work an excerpt comes from), `author`,
`parent` (a collection or book containing the text) or `none`; `lang` defaults to `en`. A human names
the article; `weft about` never guesses one. The page and search label an `author` or `parent` article
as such, so an article on Enheduanna is never presented as an article on the Temple Hymns.

`weft about <work>` writes `about.yaml`:

```yaml
work: inter-caetera-1493
src: weft.about 0.1
fetched: '2026-10-09'
match: work
wikipedia:                  # quoted verbatim, CC BY-SA 4.0 (the license of texts/), pinned by revision
  title: Inter caetera
  lang: en
  revision: 1367216393
  url: https://en.wikipedia.org/w/index.php?title=Inter_caetera&oldid=1367216393
  license: CC BY-SA 4.0
  attribution: From the Wikipedia article “Inter caetera” (en.wikipedia.org, revision 1367216393), CC BY-SA 4.0
  lead: Inter caetera ('Among other [works]') was a papal bull issued by Pope Alexander VI ...
wikidata:                   # CC0; English labels, ids kept so a missing label is never invented
  id: Q1134342
  revision: 2489002486
  license: CC0
  description: papal bull by Alexander VI (4 May 1493) ...
  instance_of: [{id: Q189867, label: papal bull}]
  main_subject: [{id: Q127834, label: New World}]
```

The lead is the article's first paragraph, with the second when the first is under 200 characters.
Unlike `sources/`, the file is committed: the build reads only what is committed, and the text is
under the same license as `texts/`. It is regenerable, so it is never edited by hand; correct the
manifest and rerun. `weft check` fails a bad `wikipedia` field or an incomplete or stale record, and
warns where the field is missing, the record not yet fetched, or `match: none` leaves the about to
be written by hand.

## The kind of a work

`kind` in the manifest places the work in one of seven groups on the library page, under "By kind":
`epic-and-myth` (narrative verse and prose, and the Norse poems with Snorri), `scripture`, shown as "Sacred texts" (scripture,
hymn, creed), `philosophy` (thought, including the Daodejing, the Yijing and Sunzi), `poetry`, shown as "Poetry,
literature and music" (lyric, song and the opera libretti), `law`, shown as "Law and politics" (codes,
charters, bulls, declarations and manifestos),
`correspondence` (letters, chronicles, travel accounts and inscriptions) and `science`. One value per
work; `weft check` refuses a manifest without one. A translation record's `kind: reference` or
`kind: editorial` is a different field and unrelated.

## Translations still in copyright: kind: reference

A translation that is still in copyright can be cited without being reproduced. In the manifest,
give it `kind: reference` with `translator`, `year`, `title`, `publisher` and an optional `note`, and
no file or url. The page shows a notice naming it; the gloss row carries the meaning. If you own the
translation, put it in `private/<work>/` under the same id: `weft build --private` then shows it inline
and drops the notice.

```yaml
translations:
  - id: harris1974
    kind: reference
    translator: Victor Harris
    year: 1974
    title: A Book of Five Rings
    publisher: Overlook Press
```

## notes/bookNN.yaml

```yaml
- id: n.od.1.1.polytropos
  attach: od.1.1.5            # token or line ID
  kind: editorial             # quoted | editorial
  status: draft               # draft | reviewed (editorial notes start as draft)
  leans_on: LSJ s.v. πολύτροπος
  text: "..."
- id: n.od.1.1.butler-construe
  attach: od.1.1
  kind: quoted                # verbatim; `source` is required
  source: Samuel Butler, preface to The Odyssey (1900)
  text: "..."
```

## Quoting modern scholarship in notes

Notes retell a scholar's argument in Weft's own words and name the source in `leans_on` (author,
title, year, and the line or page). Verbatim words from a work still in copyright are kept to a
short phrase, about fifteen words at most, used only where the wording itself matters (a
translator's rendering, a scholar's key judgement), set in quotation marks with the author named in
the sentence. No note quotes more than two such sources. Longer copyrighted material goes in
`private/` and is never published. Public-domain scholarship (Leaf, Monro, Jebb, Bellows's notes)
may be quoted at length as `kind: quoted`.

## Conventions for the gloss layer

- One source word, one cell. English that needs several words is hyphenated: `of-many-turns`.
- Grammar rides in the English: `to-me` (dative), `of-Troy` (genitive), `O-Muse` (vocative),
  `he-sacked` (3rd singular aorist).
- Word order is preserved. The sense layer does the repairing.
- Compounds get their literal etymology, not a smooth reading.
- Split compounds (tmesis) gloss each piece where it stands and carry a note.

## Conventions for the sound layer

- IPA is canonical; respelling is a projection of it. Switching scheme changes both.
- Hyphenated syllables. Medial consonant clusters split before the last consonant, except
  stop plus liquid (muta cum liquida), which goes whole to the next syllable.
- Length is shown: doubled letters (aa, ee, üü) or a dedicated long symbol (ê, aw, ay, oo).
- CAPS marks the accented syllable. In `restored` that means raised pitch on acute and
  circumflex only; a grave is not raised. In `erasmian` every written accent is stress.
- Long alpha, iota and upsilon not marked in the orthography come from
  `pipeline/weft/data/grc_quantities.yaml`, each entry citing LSJ and the metrical foot.
- Each word is phonemized alone. Sandhi, elision across words and correption are not modeled.

## Metre

A line-level string: `—` long, `◡` short, `×` anceps, `|` between feet. For Greek hexameter the
scanner in `greek.py` generates it into gen; the hand scansions in the curated overlay are its
regression test (62 lines, Odyssey 1.1-10 and Iliad 1.1-52). Other metres are generated by their
language modules or scanned by hand in `curated/`.
