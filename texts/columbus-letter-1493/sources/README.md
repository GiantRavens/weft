# Sources (not in git)

This folder holds third-party files under their own licenses. They are never committed.
The manifest (`../manifest.yaml`) names each one, its origin, its license and the sha256
this edition was built against.

To get them:

    weft acquire columbus-letter-1493                     # shows each source, its license, and whether you have it
    weft acquire columbus-letter-1493 --accept-licenses   # downloads what is missing and verifies each hash

A download whose hash differs from the manifest is saved as `*.unverified` and not used,
because upstream has changed since this edition was pinned.
