# License for the text data

Everything under `texts/` (manifests, generated layers, curated overlays, alignments and
notes) is licensed under the **Creative Commons Attribution-ShareAlike 4.0 International**
license (CC BY-SA 4.0): https://creativecommons.org/licenses/by-sa/4.0/

Share-alike is required because the generated layers derive from share-alike sources, among
them the Perseus treebanks (CC BY-SA 3.0) and MorphGNT (CC BY-SA 3.0). Each work's
`manifest.yaml` names its sources and their licenses; credit them when you reuse a layer.

The source files themselves are **not** in this repository. They belong to their owners
under their own licenses, and `weft acquire <work>` shows each license before downloading.

The code under `pipeline/`, `site/` and `tests/` is MIT licensed (see `LICENSE`).
The Weft artwork in `art/` (the mark, wordmark, lockup and favicon) is © Skip Levens, all rights
reserved, pending a decision on its license. The illustrations in `art/works/` are public-domain
images from Wikimedia Commons; `art/works/credits.yaml` records the source, license and credit for
each.

Notes may quote short phrases from modern translations and scholarship, attributed in the note and
named in its `leans_on` field. Those quoted words remain under their owners' copyright and are not
part of the CC BY-SA license; everything else in the note is Weft's own wording.
