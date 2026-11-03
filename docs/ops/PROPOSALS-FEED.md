# Proposals index feed — contract

The dashboard's proposals page (`apps/tribute-dashboard/proposals.html`)
is the web display for the proposal registry of record. It renders
exactly one feed: `apps/tribute-dashboard/data/proposals-feed.json`
(schema `proposals-feed/v2`; v1 carried related PRs as bare numbers —
consumers must not mix shapes across the bump).

## Source of record

- `docs/proposals/registry.yaml` — every registered proposal pack
  (id, title, author, status, priority, path, related issues/PRs).
  Registry semantics are owned by the Delphi lane; this feed carries
  the registry's values **verbatim** — author strings, statuses and
  priorities are never normalized, merged or inferred.
- `docs/proposals/passes/<id>/pass.json` — the Oracle Method pass
  records (3 at contract landing). The feed carries the pass id, its
  recorded schema, its candidate count, and its own `status` read
  verbatim from the record (`recorded` — strands-rfp-response and
  temporal-durable-execution; `stated_not_run` —
  kiroween-delphi-concept). A pass whose record carries no status
  field renders status null with the absence named in `gaps` — a
  pass status is never inferred from the registry or the pass's age.
- `docs/proposals/passes/<id>/cycle/BALLOT-round1.json` — when a pass
  carries a round-1 ballot record, the feed also emits its `outcome`:
  the per-candidate scores verbatim from the ballot class that
  actually voted (the class named in the outcome; most ballots wins,
  precedence LOCAL_BASELINE > HUMAN_COLLABORATOR > MODEL_PROVIDER on
  ties), the total ballot count, and the source path. A ballot record
  with zero ballots emits no outcome and the absence is named in
  `gaps`. Equal scores stay equal — a tie is data; the feed never
  ranks and no consumer may render an ordinal from the ballot's
  internal ordering.

## Collector and refresh

- Collector: `scripts/proposals/proposals_feed.py` (stdlib-only;
  PyYAML when importable, otherwise a subset parser for the registry's
  regular shape — the two are differential-tested).
- Refresh: `.github/workflows/proposals-feed-collect.yml` runs on push
  to `docs/proposals/**` and on dispatch, and opens a **refresh PR** —
  it never commits to master directly.
- Each proposal links to its tree on GitHub:
  `https://github.com/timerloggedout-spec/termux-monorepo/tree/master/docs/proposals/<path>`.

## PR state (v2)

- Each entry in a proposal's `prs` list is an object
  `{number, state, merged_at}`. `state` is one of `open`, `merged`,
  `closed-unmerged` or `unknown`; `merged_at` carries the API's
  merge timestamp verbatim when the state is `merged`, and is null
  otherwise.
- States are resolved from the GitHub API **at collection time** —
  one read per unique PR number per run, using the collection job's
  token (`GITHUB_TOKEN` / `GH_TOKEN`). They are never read from the
  registry, never hand-entered and never copied forward from a
  previous feed: a refresh re-resolves every ref.
- A ref the API cannot resolve (missing PR, HTTP or network
  failure) is stamped `unknown` and named in `gaps`. The page
  renders a state chip for known states and no chip for `unknown`.
- A collection run without an API token stamps every ref `unknown`
  and names that fact once in `gaps` (`--skip-pr-states` does the
  same deliberately, for offline runs).

## Honesty rules

1. A field the registry omits renders as an empty list / absent —
   never a guessed value.
2. A pass whose `pass.json` cannot be read is named in the feed's
   `gaps` array and still listed, never silently dropped.
3. The page fetches only `./data/proposals-feed.json`; its filters
   (status / priority / author) are built from the feed's own values
   at runtime, never hardcoded.
4. Counts on the page come from the feed's `counts` object, computed
   by the collector from the registry — the page computes nothing
   beyond filtering what the feed carries.
5. A pass `outcome` is carried verbatim from the pass's own ballot
   record — scores are never recomputed, rescaled or tie-broken by
   the collector.
6. A PR's `state` is whatever the API reported at collection time —
   never inferred from the registry, the proposal's own status, or
   the PR's age or number; an unresolvable ref is `unknown`, never
   a guessed state.
