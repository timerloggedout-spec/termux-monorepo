# StudySprint — versioning & releases process

Owner-ordered 2026-10-30. This is the process of record for
timerloggedout-spec/studysprint.

## Scheme: SemVer, pre-1.0 until submission

- `MAJOR.MINOR.PATCH` (semver.org). Source of truth = the `VERSION`
  file at repo root; `agent.py` reads it into every receipt as
  `agent_version` (a test pins receipt == VERSION, so they cannot
  drift silently).
- **0.x = pre-submission iterations** (now → Nov 4). MINOR bumps
  for a feature batch (G2, G3, a polish pass with new behavior);
  PATCH bumps for fixes, docs, copy, receipt refreshes.
- **1.0.0 = the Nov 4 submission release** — the exact tree the
  Builder Center submission points at. It is cut only on submission
  day, from a green tree, and never moved afterward.
- Post-submission: normal SemVer (breaking behavior = MAJOR,
  features = MINOR, fixes = PATCH).

## What counts as a release

A release = a git tag `vX.Y.Z` on `main` + a GitHub Release with
that tag, whose notes are the CHANGELOG entry for X.Y.Z, verbatim.
No tag without notes; no notes without a green test run + a fresh
`evidence/demo-run.json` committed in the same tree.

## Flow (every release, in order)

1. Land the work on `main` (this repo lands direct commits via the
   PAT API; each commit names its item, e.g. `polish(1): …`).
2. Run the full offline suite: `python3 -m pytest tests/` — green
   or stop.
3. Run `python3 demo.py`; commit the refreshed
   `evidence/demo-run.json` if decisions changed (timestamp-only
   churn is fine to commit as the release's evidence snapshot).
4. Bump `VERSION` (+ the matching constant path — the receipt test
   reads the file, so the file is the only edit).
5. Add the `CHANGELOG.md` entry: date, version, Added / Changed /
   Fixed / Evidence (test count, demo decisions, HEAD sha).
6. Commit as `release: vX.Y.Z` and read back the tree.
7. Create the GitHub Release via the PAT API
   (`POST /repos/timerloggedout-spec/studysprint/releases`,
   `tag_name=vX.Y.Z`, `target_commitish=` the release commit,
   `name=vX.Y.Z — <one line>`, body = the CHANGELOG entry).
8. Verify: release + tag read back via API; report commit sha,
   tag, and release URL with commit/blob ids labeled.

## Rules

- **Receipts pin the version.** Every agent receipt carries
  `agent_version`; a demo or article claim names the version it
  was produced by.
- **Foundation files are vendored, not versioned with us.** The
  D0 blobs (oracle kernel 9a4a1c78, fetch_evidence 8442d813) keep
  their own provenance; if delphi-oracle ships a new foundation,
  re-vendoring is a MINOR bump and the CHANGELOG names both blob
  ids (old → new).
- **No silent re-release.** A tag, once published, is never
  re-pointed. A mistake = a new PATCH release that says so.
- **Submission freeze.** Between the Nov 4 project publish and
  judging, `main` takes no feature work; fixes only, as PATCH
  releases, each noted in the CHANGELOG (judges see the same repo).
- **Cadence until Nov 4:** one MINOR per landed gap/polish batch,
  PATCH as needed, daily at most — releases mark verified states,
  not activity.

## Roles

- Builder (this seat, challenge-entries-manager-d1): cuts releases,
  writes CHANGELOG entries.
- Entries lane: records release urls in the coordinator (single
  writer) when a release is submission-relevant (1.0.0 always).
- Owner: the only go/no-go on 1.0.0's submission-day timing
  (standing ruling: submit on Nov 4).
