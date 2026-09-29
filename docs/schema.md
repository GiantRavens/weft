# Data schema (v0)

All files YAML. IDs are CTS-style short forms; the manifest maps them to full URNs.

## manifest.yaml

```yaml
work: homer-odyssey
title: Odyssey
author: Homer
language: grc-homeric
urn: urn:cts:greekLit:tlg0012.tlg002
unit: line                       # line | sentence | verse
edition:
  name: Perseus perseus-grc2
  url: ...
  license: CC BY-SA 4.0
treebank:
  name: AGDT 2.x
  url: ...
  license: CC BY-SA 3.0
schemes: [homeric, erasmian]     # pronunciation schemes to generate
translations:
  - id: butler1900
    translator: Samuel Butler
    year: 1900
    form: prose
    license: public-domain
    source: private/...epub or url
commentaries:
  - id: merry-riddell
    title: Homer's Odyssey, Books I-XII
    year: 1886
    license: public-domain
predicted_gaps:
  - "alpha/iota/upsilon length ambiguous outside metre; scanner resolves ~90%"
```

## gen/<unit>.yaml

```yaml
pipeline: {tokenize: 0.1, phonemize: 0.1, gloss: 0.1, align: 0.1}
lines:
  - id: od.1.1
    text: "Ἄνδρα μοι ἔννεπε, Μοῦσα, πολύτροπον, ὃς μάλα πολλὰ"
    metre: "—◡◡ —◡◡ —◡◡ —◡◡ —◡◡ ——"       # src: scanner
    tokens:
      - id: od.1.1.5
        surface: πολύτροπον
        lemma: πολύτροπος          # src: agdt:1234
        morph: a-s---ma-           # src: agdt
        ipa: {homeric: polýtropon, erasmian: polútropon}   # src: rules 0.1
        respell: po-LOO-tro-pon    # src: derived
        gloss: of-many-turns       # src: llm+lsj, conf: 0.82
        notes: [n.od.1.1.polytropos]
    sense:
      - {tr: butler1900, span: "Tell me, O Muse, of that ingenious hero who travelled far and wide", covers: [od.1.1, od.1.2]}
```

Provenance is a per-field `src` with an optional `conf`. Exact encoding (inline comment vs
sibling map) is a Phase 0 decision; pick one and keep it.

## curated/<unit>.yaml

Sparse overlay. Only what a human changed.

```yaml
- id: od.1.1.5
  field: gloss
  value: much-turned
  by: skip
  date: 2026-09-29
  why: "keep the etymology visible; Butler's 'ingenious' belongs in sense"
```

## notes/<unit>.yaml

```yaml
- id: n.od.1.1.polytropos
  attach: od.1.1.5
  source: merry-riddell 1886, ad loc.
  text: "..."
```

## Conventions for the gloss layer

- One source word, one cell. English that needs several words is hyphenated: `of-many-turns`.
- Grammar rides in the English: `for-me` (dative), `of-Troy` (genitive), `he-sacked` (3 sg aorist).
- Word order is preserved. The sense layer does the repairing.
- Compounds get their literal etymology, not a smooth reading.

## Conventions for the sound layer

- Hyphenated syllables; stressed or accented syllable in caps.
- Vowel length shown. Greek pitch accent marked with ´ or ˆ on the caps syllable.
- One fixed respelling key per scheme, shown once per page.
- IPA is canonical; respelling is a projection. Switching scheme regenerates both.
