# Weft: agent orientation

Read `README.md` first, then `docs/lifecycle.md` and `docs/schema.md`. Before building or extending a work, read
`docs/building.md`: the order of operations, the source recipes, the edition patterns, and the gotchas already paid for.
Tasks live in Pin (`pin ls`).

## Hard rules

1. Never edit anything under `texts/*/sources/` or `texts/*/gen/` by hand. Sources are fetched; gen is produced by `pipeline/`. Human corrections go in `texts/*/curated/`.
2. Every generated field carries `src` (what produced it, with version) and, where a judgment was made, `conf` (0 to 1). Low confidence goes to the review queue, not silently into the page. (The `conf` field and the review queue belong to the generated gloss step, which is phase 4; today glosses are hand-written in `curated/` and carry `status: draft` instead.)
3. Lemma and morphology come from the treebank. An LLM may pick a sense from the lexicon entry for that lemma; it may not invent a lemma or a parse. **Exception, declared in the manifest (`treebank: null`):** when no treebank exists for a text (Eddic poetry, Chaucer), lemma and morphology are hand-annotated in `curated/` against a named dictionary, marked `status: draft`, and the page says so. The draft status is only lifted by a human reviewer.
4. Third-party sources are never committed: `texts/*/sources/` is gitignored and each user fetches their own copy with `weft acquire`, which shows the licenses first and verifies the manifest's sha256. Nothing copyrighted enters `texts/`. It goes in `private/` with the same layout, and the pipeline reads both.
5. Line IDs are CTS URNs or a CTS-style short form (`od.1.1`). Every layer, note and audio timing hangs off them.
6. Layers are named (source, sound, gloss, sense, metre, notes, audio), never numbered.
7. The site is plain HTML, CSS, JS. No build framework. It must work from `file://` and print cleanly.
8. **The first pronunciation scheme is the default, and it is always the best reconstruction of how the text most likely sounded when first written** (Skip, 2026-09-29). Later traditions (Erasmian, ecclesiastical, modern Icelandic) are offered second. Where the evidence is thin, the page says the reconstruction is approximate rather than dropping it.
9. Manifest before pipeline. A work is not processed until `manifest.yaml` names the edition, the treebank, the schemes, the translations with licenses, and the predicted gaps.

## Working style

- **Voice for all authored prose** (README, docs, guides, notes on the page, UI strings, repo
  description): Skip's clear, analytical voice, `~/.claude/skills/voice/voices/analyst-brief.md`,
  then a `humanize` pass. Calm and measured; definitions before claims; scope every claim and
  state where the evidence is weakest; relate a word rather than equate it; never add details the
  text does not contain. No em-dashes, superlatives, drama, exclamation points, or flourishes
  presented as findings ("the repetition is the point"). Quoted sources are left verbatim.

- Python with `uv`; one package, no sidecars.
- Each pipeline step is a CLI subcommand that reads the manifest, writes one layer, and reports counts and failure classes on exit.
- Golden passage: the Odyssey proem (`od.1.1-10`), hand-verified. Every pipeline change is diffed against it.
- Cognitive Honing applies: predicted vs actual on every run; when one failure class exceeds 15 percent, fix upstream.
