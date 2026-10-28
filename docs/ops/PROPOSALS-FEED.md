# Proposals index feed — contract

The dashboard's proposals page (`apps/help-wanted-dashboard/proposals.html`)
is the web display for the proposal registry of record. It renders
exactly one feed: `apps/help-wanted-dashboard/data/proposals-feed.json`
(schema `proposals-feed/v1`).

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

## Collector and refresh

- Collector: `scripts/proposals/proposals_feed.py` (stdlib-only;
  PyYAML when importable, otherwise a subset parser for the registry's
  regular shape — the two are differential-tested).
- Refresh: `.github/workflows/proposals-feed-collect.yml` runs on push
  to `docs/proposals/**` and on dispatch, and opens a **refresh PR** —
  it never commits to master directly.
- Each proposal links to its tree on GitHub:
  `https://github.com/timerloggedout-spec/termux-monorepo/tree/master/docs/proposals/<path>`.

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
