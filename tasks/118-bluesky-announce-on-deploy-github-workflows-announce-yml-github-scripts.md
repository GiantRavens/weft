---
id: 118
title: 'Bluesky announce on deploy: .github/workflows/announce.yml + .github/scripts/...'
state: TODO
priority: 2
tags:
  - announce
  - bluesky
  - promotion
created_at: 2026-10-01T21:40:00.975534144-05:00
updated_at: 2026-10-02T09:26:45.356788048-05:00
---

# Bluesky announce on deploy: .github/workflows/announce.yml + .github/scripts/announce.py (drafted 2026-10-01, dry-run tested; captain commits). Setup: announce environment w/ required reviewer, var BLUESKY_IDENTIFIER, secret BLUESKY_APP_PASSWORD. Follow-ups: og:/twitter: preview tags in site/template.html (none today), X later (paid API)

## Notes

- 2026-10-02T13:42:41Z: 2026-10-02: PREVIEWS + CLASSIFIER BUILT. og:/twitter: tags in every public page (build.preview_meta, {{META}} in template; private builds emit none). 'weft previews all' (pipeline/weft/previews.py, optional extra [previews] = playwright) screenshots each page at 1200x630 JPEG (~50-75 KB), hiding #ref-note/#sound-note so the text shows; 57/57 rendered in 45 s; pages.yml step continue-on-error. announce.py now compose/send: one post per deploy; NEW = manifest added, UPDATED = >=300 changed lines in texts/<work>/; docs/README/pipeline never post; Announce: trailer always posts; card = first work mentioned, thumb = its preview uploaded as blob. announce.yml = compose job (post text in run summary, no approval) -> post job (announce env, approval) only if has_post. Replayed on all 24 real commits: 8 quiet (renames, licenses, notes 33 lines, docs), 16 posts (every content push). 34/34 tests pass. Not yet run in Actions or against the live Bluesky API.
- 2026-10-02T14:01:07Z: 2026-10-02 09:0x: Bluesky handle LIVE @activeskip.giantravens.com (dnsctl apply giantravens _atproto.activeskip; Bluesky verify via Chrome DOM over ssh/AppleScript; public API confirms, 15 followers + 6 posts kept). App password 'weft-announce' created (no DM access), value NOT read by agent: captain stores it with gh secret set. GitHub: vars BLUESKY_IDENTIFIER + ANNOUNCE_DRY_RUN=1 set; environment 'announce' with required reviewer GiantRavens. Remaining: secret, captain commit+push, read first dry-run summary, then delete ANNOUNCE_DRY_RUN.
- 2026-10-02T14:10:31Z: 2026-10-02: GitHub environment 'announce' created with GiantRavens as required reviewer and main allowed as deployment branch, BEFORE the workflow is pushed (a referenced environment is otherwise auto-created with no protection). No BLUESKY secret or vars set yet: add BLUESKY_APP_PASSWORD as an ENVIRONMENT secret on 'announce', not a repo secret.
- 2026-10-02T14:20:25Z: 2026-10-02 09:3x: X LEG BUILT (not yet live). announce.py send posts to Bluesky and X independently (one failing never blocks the other; exit 1 if any failed); X = POST api.x.com/2/tweets, OAuth 1.0a user context (HMAC-SHA1, stdlib; signature verified against X's published worked example in tests/test_announce.py), text only: X builds the card from og: tags. compose rejects text over X's weighted 280 (link=23, CJK=2). Secrets X_API_KEY, X_API_SECRET, X_ACCESS_TOKEN, X_ACCESS_SECRET go on the 'announce' ENVIRONMENT; absent -> X skipped and said so. Captain has NO X developer account yet (console.x.com -> onboarding/agreement); X Premium does not include API; pay-per-use $0.20 per post with URL. Live first run 37018503547 (deploy 9d8d79d) awaiting approval, dry run. Uncommitted: .github/scripts/announce.py, .github/workflows/announce.yml, tests/test_announce.py.
- 2026-10-02T14:26:45Z: 2026-10-02 09:25: secret BLUESKY_APP_PASSWORD stored (app password 'weft-announce-gh', piped from the Bluesky dialog into gh secret set; value never printed). First 'weft-announce' (09:00) is ORPHANED (value lost when the dialog closed); deleting it was permission-gated -> captain deletes in Bluesky Settings > App passwords. Note: announce.yml now also passes X_* secrets (edited outside this session).

## Log

- 2026-10-02T02:40:00Z: Created task
