# private/: your own layer of Weft

Everything in this folder except this README stays on your machine. Git ignores it, the public
build never reads it, and the published library never lists it. Use it for material you own or
may use privately but cannot publish: a copyrighted translation you bought, your own annotations,
long quotations from a commentary, or a whole text from your own library.

## Two kinds of folder

**An overlay on a public work.** `private/<work>/`, where `texts/<work>/` exists, adds to that
work in your build only:

    private/homer-iliad/
      manifest.yaml      translations: the ones you own (id, translator, year, form, license)
      sense/<id>.yaml    their alignment, in the same format as texts/<work>/sense/
      curated/*.yaml     your own changesets (by, date, why, status, set); they override the public layers
      notes/*.yaml       your notes, including longer quotations than the public pages allow

A translation listed as `kind: reference` on the public page (cited, not printed) is printed in
full in your build once you supply your copy here.

**A private work.** `private/<work>/`, where no public work has that name, is a whole work with
the same layout as `texts/<work>/`: `manifest.yaml`, `edition.yaml` or a fetched edition,
`gen/`, `curated/`, `sense/`, `notes/`, `sources/`. Every step works on it as usual:

    .venv/bin/weft acquire <work> --accept-licenses
    .venv/bin/weft draft <work>
    .venv/bin/weft check <work>
    .venv/bin/weft build <work> --private

A file you supply yourself (a scan, a purchased e-text) is listed in the manifest with
`local: true` and its `sha256` instead of a `url`; `weft acquire` checks it is present and
unchanged and never tries to download it. An illustration for a private work goes in
`private/art/credits.yaml`, in the format of `art/works/credits.yaml`, with its image under
`private/art/`.

## Building

    .venv/bin/weft build all --private

writes every public work (with your overlays) and every private work to `private/build/`, with a
library index that lists them together and marks the private ones. Private pages say they are a
private build in the footer, and pages of private works carry no links to the public issue
tracker. Do not publish or share `private/build/`: the pages are single files, so they are easy to
send by mistake.

## Keeping it safe

- Enable the leak guard once per clone. It refuses any commit that stages a file from here or a
  fetched source:

      git config core.hooksPath .githooks

- The test suite has a second sensor (`test_private_never_tracked`): it fails if anything under
  `private/` other than this README, or any fetched source, is tracked by git.
- To keep a history of your private work, make this folder its own repository, local or private:

      cd private && git init

  Weft's repository ignores it either way.
