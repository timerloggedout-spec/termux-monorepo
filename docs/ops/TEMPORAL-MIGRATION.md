# Temporal — migration off the VM (owner correction 2026-10-28)

**Ruling.** There is NO Temporal exception to the VM = sandbox-only
rule. The exception relayed 2026-10-27 was main's inference; the
owner rejected it 2026-10-28. Temporal is **REQUIRED as a
capability**; where it runs was never exempted. Under the VM rule
its continuous execution must home on a **GitHub-reachable surface**
— reachable via GitHub Workflows. The current VM systemd instance
(`temporal-selfhost` + `temporal-relay` + the keepalive cron) is a
**migration item**, owned by the temporal-integration lane.

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

## Current state at plan time (2026-10-28)

- VM instance: UP (units active, DB live) — stays up through
  stage 3 by the hard gate above.
- Stage 2 is partially pre-proven: delphi-cycle.yml already runs
  the N5 §5 acceptance — including a SIGKILL-mid-implementation
  resume — against an in-job dev server. The §6 harness run in
  `temporal-engagement.yml` is the remaining stage-2 evidence.
