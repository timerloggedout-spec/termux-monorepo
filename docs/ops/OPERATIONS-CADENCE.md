# Operations Cadence

## Unified clock

The repository uses **UTC as the machine clock** for Actions schedules, telemetry timestamps, and quota-boundary reasoning. Every recurring schedule must declare `timezone: UTC` explicitly.

GitHub documents that scheduled workflows can be delayed during high-load periods, particularly around the start of an hour. Staggering recurring work across non-zero minute offsets reduces self-inflicted bursts; it does not guarantee scheduler latency.

GitHub Actions included usage resets at the start of the applicable billing cycle. The repository records the monthly UTC boundary as the common operational anchor. Provider/account quotas remain observed state and are never inferred from public entitlement alone.

**Calendar-day phases are eliminated** (except pure metrics tracking). Planning uses an abstract concurrent phase lattice instead.

## Arrhythmic × Agile × Broad RECON × Phase Lattice

| Lens | Question | Operating behavior |
|---|---|---|
| Arrhythmic (timing without rhythm) | Where is the rigid pattern we can break? | deliberate non-zero offsets; concurrent phase instances; avoid predictable :00 bursts |
| Agile | What is the smallest useful next increment? | small batch → inspect → adapt |
| Broad RECON | What is the whole situation, considered carefully? | scan queue / SHA / quota / dependencies / writers **plus** starred · forked · following · watched · submodules · proposals registry · debate terms · external concurrent jobs |
| Focused execution | What is the one bounded action after RECON? | one task / one evidence target / one write lease |
| Phase lattice (13 abstract) | Which phases are live right now? | RECON · PLAN · MEASURE · PROPOSAL_SCAN · DEBATE · SWEEP · ACT · COMMIT · WAIT · WATCH · VALIDATE · REFETCH_COMPARE · RECORD_CLASSIFY — multiple instances concurrent/parallel allowed |
| Watch loop | Did execution actually progress? | WAIT → WATCH → VALIDATE → REFETCH → COMPARE → RECORD |

The phase lattice replaces any day-bound planning metaphors. GitHub remains the authoritative technical clock.

## Unified response state machine

```text
RECON (starred/forked/following/watched/submodules + proposals + debate + external jobs)
  → PLAN / MEASURE
  → PROPOSAL_SCAN / DEBATE (when intent is open)
  → SWEEP (repository drift / leases / orphans)
  → ACT → COMMIT
  → WAIT → WATCH → VALIDATE → REFETCH → COMPARE Δ → CLASSIFY → RECORD → REPEAT
```

Queued, running, commented, or “green-looking” metadata is never equivalent to validated execution.

## Issue events

```text
RECEIVE → TRUST_BOUNDARY → DEDUPE → TRIAGE → ROUTE → ACT → WAIT → WATCH → VALIDATE → RECORD
```

Issue/comment bodies are untrusted data. Command-like text is never executable merely because it names an agent.

Issue response workflows should serialize by `github.event.issue.number` and normally preserve an in-progress run rather than canceling useful evidence.

## Pull-request events

```text
RECEIVE → SNAPSHOT_HEAD_SHA → TRUST_BOUNDARY → CHECKS / REVIEW → WRITE_LEASE → ACT → WAIT → WATCH → REFETCH → COMPARE → VALIDATE → RECORD
```

For synchronize events, a new head supersedes stale work for that PR only. It must not cancel work on another PR. Review labels/comments express coordination intent; they are not enforcement by themselves.

## Proposals & Debate mechanics (structured into the process)

Home: `docs/proposals/`  
Registry: `docs/proposals/registry.yaml`  
Process: `docs/proposals/PROCESS.md`  
Consensus tiers: `docs/CONSENSUS.md`

**Prior RECON sequence (research & evaluation layers):**

1. Scan `active/` + `registry.yaml` for status / priority / open items.
2. Scan `DEBATE.md` / Review logs for open terms and structured `VOTE:` entries.
3. Scan starred / forked / following / watched repositories and submodules for external research signals.
4. Evaluate claims under CONSENSUS tiers (Merit → Driver → Light → Quorum → Operator) before any ACT that asserts institutional truth.
5. Automation stays first-class: `validate_registry.py`, `record_vote.py`, `promote_proposal.py`, `proposal-lifecycle.yml`.

Proposals own **intent**. Branches own **measured evidence**. Votes attach to **claims**, never to the mere existence of a branch.

## Repository Sweep operations

First-class SWEEP phase inside the lattice.

Surfaces:

- every workflow under `.github/workflows/**` (timezone, concurrency lease, top-of-hour risk)
- `docs/proposals/active/**` + registry + MANIFEST consistency
- open issue/PR response leases
- external concurrent jobs (other agents’ 2× hourly schedules, free-quota / trial / catalog lanes)

Evidence identity remains: workflow + workflow_run + event + issue/PR + head_sha + observed_at_utc.

## Quota-aware scheduling

1. Use explicit `timezone: UTC`.
2. Prefer staggered minutes such as 07, 13, 17, 27, 37, 47, 53, 57.
3. Avoid `:00` unless a true boundary event requires it.
4. Serialize conflicting writers with concurrency groups.
5. Cancel stale observation work when a newer PR head supersedes it; preserve long-running evidence where cancellation would destroy useful state.
6. Re-observe provider/account quota state after a reset before increasing parallelism.
7. Treat promotional/free capacity as an experiment lane, never a permanent route.
8. Record `observed_at_utc`, provider/model, run/request identity, and available quota/rate-limit evidence.
9. Treat other agents’ concurrent jobs as situational inputs inside RECON, not invisible background.

## Security / taint boundary

**Sources:** issue titles/bodies, issue comments, PR titles/bodies/diffs, event payloads, provider responses.

**Sinks:** shell commands, provider prompts, repository writes, secret-bearing requests.

Validate and normalize before crossing a sink. Fork PR code is untrusted code; secrets must not be exposed merely because a workflow observes a PR.

## Migration

The first rollout remains **advisory** so legacy workflow drift is visible rather than hidden behind a false-green gate.

### Phase 1 — inventory

Audit every workflow for schedules, event triggers, concurrency, and quota-sensitive cadence.

### Phase 2 — align high-impact writers

Prioritize issue/PR agent responders, review/reconciliation writers, provider experiments, merge/promotion observers, and quota-sensitive schedules.

### Phase 3 — enforce

After legacy schedules are migrated or explicitly excepted, switch the audit from advisory to enforcement for workflow changes.

Promotion remains a separate decision. Passing cadence validation never authorizes merge/deployment. Dual-gate (termux-smoke + repo-gate) before promote.

## Evidence identity

Meaningful observations should be traceable to:

```text
workflow + workflow_run + event + issue/PR + head_sha + observed_at_utc
```

This is the cadence counterpart to the repository’s team-orchestration rule: declared routing is not performance evidence until the route actually executes.

## Current operating loop

```text
RECON (considerate + external + proposals) → PLAN/MEASURE → ACT → COMMIT
→ WAIT → WATCH → VALIDATE → RE-FETCH → COMPARE → CLASSIFY → RECORD → REPEAT ➿
```

Build the future now. Arrhythmic. Concurrent. Evidence-led.
