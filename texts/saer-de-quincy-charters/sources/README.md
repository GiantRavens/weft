# Sources (not in git)

This folder holds third-party files under their own licenses. They are never committed.
The manifest (`../manifest.yaml`) names each one, its origin, its license and the sha256
this edition was built against.

To get them:

    weft acquire saer-de-quincy-charters                     # shows each source, its license, and whether you have it
    weft acquire saer-de-quincy-charters --accept-licenses   # downloads what is missing and verifies each hash

A download whose hash differs from the manifest is saved as `*.unverified` and not used,
because upstream has changed since this edition was pinned.

Both files are Internet Archive OCR texts of public-domain volumes. Each serves twice: as the
source the Latin is checked against (edition.yaml, verify_in) and as the source of that volume's
English abstract (sense/).
