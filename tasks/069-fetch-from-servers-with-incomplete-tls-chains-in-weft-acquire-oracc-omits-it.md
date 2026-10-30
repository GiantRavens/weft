---
id: 69
title: Fetch from servers with incomplete TLS chains in weft acquire (Oracc omits it...
state: DONE
priority: 3
tags:
  - pipeline
  - acquire
created_at: 2026-10-01T10:18:23.280795-05:00
updated_at: 2026-10-30T09:47:52.486497949-05:00
completed_at: 2026-10-30T09:47:52.486493148-05:00
---

# Fetch from servers with incomplete TLS chains in weft acquire (Oracc omits its intermediate): certifi + AIA fallback or curl, so live Oracc URLs can be pinned instead of Archive captures

## Notes

- 2026-10-30T14:47:52Z: Done: pipeline/weft/tls.py supplies pinned intermediates (InCommon RSA Server CA 2, which Oracc omits; sha256-pinned, chains to USERTrust root in the system store, checked with openssl verify) with partial-chain verification off and hostname checking on; acquire and scaffold fetches use it. https://oracc.museum.upenn.edu/ now 200; expired.badssl.com and wrong.host.badssl.com still rejected. test_tls_context_supplies_intermediates_without_weakening. Enheduanna still pins its Archive capture (a live Oracc export would be a different, later build: a separate decision).

## Log

- 2026-10-01T15:18:23Z: Created task
- 2026-10-30T14:47:52Z: State changed from TODO to DONE
