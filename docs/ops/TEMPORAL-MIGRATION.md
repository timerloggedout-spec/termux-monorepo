# Temporal — migration off the VM (owner correction 2026-10-28)

**Ruling.** There is NO Temporal exception to the VM = sandbox-only
rule. The exception relayed 2026-10-27 was main's inference; the
owner rejected it 2026-10-28. Temporal is **REQUIRED as a
capability**; where it runs was never exempted. Under the VM rule
its continuous execution must home on a **GitHub-reachable surface**
— reachable via GitHub Workflows. The current VM systemd instance
(`temporal-selfhost` + `temporal-relay` + the keepalive cron) is a
**migration item**, owned by the temporal-integration lane.

**Owner definition (2026-10-28, verbatim sense):** "Self hosted =
via GITHUB | our accounts — we host on OUR services." The GitHub
Actions engagement home below is an owner-account surface under
that definition; the VM is not one of our services.

**Hard gate.** Nothing is torn down before the replacement home is
proven: the RFP §6 kill-resume proof
(`scripts/temporal/kill_resume_harness.py`) must PASS on the new
home, receipted, before stage 4 starts.

## Target home: GitHub Actions engagement runs

Temporal's fleet work is engagement-shaped: a pass starts, workers
poll, signals/queries flow, the cycle completes, receipts land in
the repo. That shape maps onto a workflow run:

- **Server:** an ephemeral Temporal dev server started inside the
  job (`.github/workflows/temporal-engagement.yml`), bound to the
  job's localhost — the same dev-server mode the VM instance runs,
  minus the standing host.
- **Workers:** job processes (cycle-scoped, per the N5 amendment) —
  `worker.py --exit-on-complete`, `client.py prove`, or the §6
  harness's own worker pair.
- **Durable record:** job artifacts (proof envelopes, cycle
  artifacts, history digests) + the repo addenda pattern. Server
  history was already non-durable across engagements (namespace
  retention 24h on the VM instance); nothing the fleet relies on
  reads history back after the fact — ledgers live in-repo.
- **Always-on surface:** the workflow itself — dispatchable and
  schedulable from GitHub, reviewable in the Actions UI, no VM in
  the loop.

**Named limits of the target home** (recorded, not hidden):

- A GitHub Actions job caps at 6 hours. An engagement longer than
  that must chunk: complete a cycle stage, persist artifacts,
  re-dispatch. Current fleet cycles are minutes-long; the Delphi
  cycle and the §6 proof both run in under 10 minutes in-job
  (delphi-cycle.yml dispatch 40758279842, success).
- No standing queryable endpoint between engagements: status is
  read from the run's artifacts/receipts, not from a live server.
  This matches how the fleet already consumes results (PRs,
  comments, addenda).
- Temporal Cloud and Codespaces are NOT candidate homes (card rule;
  owner-excluded respectively). A future always-on endpoint, if a
  consumer ever truly needs one, is a separate owner decision on a
  named GitHub-reachable host — not an inference from "required".

## Stages

| Stage | Work | Gate |
|---|---|---|
| 1 | This plan + `temporal-engagement.yml` (§6 proof in-job) landed | PR merged |
| 2 | §6 kill-resume PASS on the Actions home, receipted as a run artifact; delphi-cycle prove already green there (40758279842) | Proof verdict PASS |
| 3 | Consumer repoint: temporal-mcp config documented as per-engagement (no standing target); ops docs updated (`TEMPORAL-SELF-HOST.md` → historical record at teardown); #2028 living record notes the new home | Docs PR merged |
| 4 | Teardown: disable + remove `temporal-selfhost`/`temporal-relay` units, retire the keepalive cron (goal-owned — main/Delphi lane executes or delegates), DB + backups archived into the repo record before the workspace copy goes | Stages 1–3 green; owner-visible report first |

## Address of record

Named by the temporal-integration lane (2026-10-28), as the N5
brief's amended substrate target requires:

- **Surface:** GitHub Actions in this repo — workflows
  `temporal-engagement.yml` (general engagements + §6 proof) and
  `delphi-cycle.yml` (Delphi cycle proof), dispatched from the
  Actions tab or the API. That workflow surface IS the
  GitHub-reachable address; there is no standing host address,
  by design.
- **In-engagement address:** `localhost:7233`, namespace
  `default`, on the job's ephemeral dev server — the same
  coordinates every client/worker already defaults to.
- **Consumers:** read results from run artifacts + repo records,
  not from a live endpoint. temporal-mcp is used per-engagement
  (point its target at the engagement's server while it runs);
  its old standing `selfhost` target retires with stage 4.

## Progress

- Stage 1: LANDED (PR #2193, merged 0a648c8ade).
- Stage 2: **PASSED** — `temporal-engagement` dispatch run
  40759800247 completed success: §6 kill-resume verdict PASS +
  N5 §5 prove PASS against the in-job server, receipts in the
  run artifact. (delphi-cycle dispatch 40758279842 had already
  proven §5 the same way.)
- Stage 3: LANDED (PR #2197, merged faca838af8) — address of
  record named above; consumer docs repointed
  (TEMPORAL-DELPHI-CYCLE.md, TEMPORAL-MCP.md).
- Stage 4: **EXECUTED BY EVENTS, formalized by this record
  (2026-10-28).** Sequence, honestly: the hard gate held while it
  mattered — the VM instance stayed up through stages 2–3 and the
  replacement home was proven first (§6 + §5, above). After stage
  3 landed, a VM replacement wiped `/etc` (units
  `temporal-selfhost`/`temporal-relay` verified not-found +
  inactive, 15:33 PDT) and the `temporal-selfhost-keepalive` cron
  stands **disabled** (verified: enabled=false, last run
  2026-10-28 12:43 PDT, succeeded) — so nothing will resurrect
  the instance, and this lane did NOT reinstall it: reinstalling
  would re-extend VM hosting against the ruling. DB archived by
  record: `temporal.db` (983,040 B, integrity ok, sha256
  `529c7f4154c9…`) + snapshot `backups/temporal-20261028.db`
  (720,896 B, sha256 `3d4761dace57…`) remain on the workspace
  disk as runtime data (never repo content, by design). The
  Actions engagement surface is the operational home; dispatch
  either workflow to run Temporal work.
