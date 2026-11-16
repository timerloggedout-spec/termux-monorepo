# Collector Bootstrap — Replicable-Safer Protocol

A release-facing guideline for running this type of collection operation safely,
and the standing guideline for any such operation. It ships with Releases so
that other users provisioning their own accounts can run it safely.

Write for a fresh provisioner on a fresh account: every number that depends on
an account limit is a formula derived from that account's own `/rate_limit`
response. Never assume another account's limit, and never copy another
account's identifiers, token names, or internal chat/lane names into your
deployment. Credential handling is names-only: give secrets placeholder names
and map them to your own vault / secret store.

## Derived quantities (read these from your own account first)

Let `L` = `resources.core.limit` and `R` = `resources.core.remaining` from one
uncounted `GET /rate_limit` read. Then:

- Reserve fraction: `reserve = L / 10`.
- Defer threshold for a planned batch: defer fail-soft when
  `R < planned_calls + reserve`. Never retry-loop against a 403; report the
  `reset` time from the same reading and resume in the next window.
- Session cap: a per-session hourly cap on counted calls, set in budget
  configuration (reference default: 400 counted calls / session / hour —
  a worked-example default, not a limit). Re-allocate by editing the budget
  configuration, never by editing code.
- Chunk cap: a bootstrap chunk must satisfy `chunk_calls <= session_cap`.

Worked example only: if your account reads `L = 5000`, then `reserve = 500`
and a planned batch of, say, 9 calls defers when `R < 509`.

## Provisioning

1. **Create a dedicated token for the operation**, with the least scopes that
   work, and store it only in your secret store. Never paste a token value
   into a document, a chat message, a commit, or a workflow file.
2. **Wire it as the workflow secret and as the local helper credential.**
   Use placeholder names in documentation — for example
   `<YOUR_OPERATION_TOKEN>` for the workflow secret and
   `<YOUR_LOCAL_HELPER_CREDENTIAL>` for the local helper — and map each
   placeholder to the real name in your own secret store.
3. **Set the budget configuration from the derived formulas above:**
   reserve fraction, per-run chunk cap, and session cap. The operator who
   owns scheduling approves the budget numbers for a deployment.
4. **First run = dispatch-only smoke (below).** Do not schedule a collector
   before it has two clean dispatch-only runs.

## Re-provision testing

Re-provision testing is a lightweight, optional smoke only: one uncounted
`/rate_limit` read, one Tier-1 count probe (step 1 below), and ONE chunk.
That is sufficient to prove a fresh provisioning end-to-end.

A full re-bootstrap as a test is explicitly NOT required, and this document
says so on purpose: it would burn the new account's window for no signal.

## Protocol

This protocol generalizes two prior instances: a repository index and a
social-following index. In the originating deployment, the cadence owner is
the approver for the budget numbers.

### 1. Estimate before spend

Run a Tier-1 count probe first: a small GraphQL batch on its separate
bucket (worked example: about 3 calls for about 285 accounts). Compute
`planned_calls` from those live counts — never guess it. Run the
derived-reserve preflight above before any REST call, and defer before
spending if the threshold is hit.

### 2. Chunked and checkpointed

Run the bootstrap in account-cohort chunks, each sized to a budget slice
(`chunk_calls <= session_cap`). Commit durable state per chunk through the
refresh-PR pattern: progress lives in the repository, never only on a
provisioner's machine. An interrupted bootstrap resumes from committed
state; it never restarts from scratch.

State location: state lives IN the plane's own index file — per-record /
per-source `observed_at` + `snapshot_hash` + counts — never in a separate
state file. Derived views likewise carry, in-index, per-source
`{observed_at, snapshot_hash, records}`.

### 3. Verify per chunk

Reconcile each chunk's slice totals against the Tier-1 counts before any
account is marked done. A mismatch means the chunk fails closed: state is
not advanced.

### 4. Steady state is not bootstrap

After bootstrap, passes are delta-only:

- Count probe (about 3 GraphQL calls, separate bucket) against stored counts.
- Watermark stop: unchanged accounts cost no further calls; changed
  accounts are traversed only to the stored watermark.
- ETag conditional GETs: a 304 for an unchanged resource does not count
  against the primary limit.
- Rotating full-audit cohort: audit 1/7 of accounts per weekly pass to
  catch count-neutral swaps that a count probe alone would miss.

Watermark definition: there is NO standalone `watermark` field. The
watermark is the `(observed_at, snapshot_hash)` pair, exactly as the
landed repository-index schema (version 1.1) already carries it.
List-position cursors (for example, last-seen starred-at / record id, or a
pushed-at cutoff) are collector-internal cursors, not schema fields. Do not
mint new field names other deployments would then owe.

Worked example (a prior social-following index, about 285 accounts —
labelled as an example, not a guarantee): bootstrap about 1050–1370 core
calls one-time; steady state about 200 calls per pass worst case, typically
far less.

### 5. Rails (every instance, no exceptions)

- Dispatch-only until two clean runs, then schedule.
- Workflow concurrency = 1.
- No tight polling.
- DEFER fail-soft between chunks when the reserve is hit.
- Batching (dedupe + memo + ETag) applies to read-only shared-state
  recon reads only — never to writes, never to verify-after-write reads,
  never to pre-write state reads. A stale base identifier means a rejected
  or wrong-base publish, so a publish path is batch-ineligible and stays
  all-direct (worked example: an entire publish path of at most about 20
  calls is batch-ineligible).

## Exempt by construction

A pass that is offline over committed indexes — 0 API calls, with
regeneration in Actions on an installation token — has no collector to
size. Do not create a chunk variant for it.

## Template

A new plane (or a new provisioner) fills a small configuration — entity
source, count-probe query, cursor fields, chunk cap — and inherits this
protocol unchanged. Only the configuration and the derived budget numbers
change between deployments.
