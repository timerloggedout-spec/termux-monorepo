# Adaptive Dynamic Awareness

**Purpose:** make cadence decisions responsive to evidence across collaborators, VM jobs, repository workflows, and quota-bound execution lanes.

**Canonical mode:** `Dynamic`. Dynamic is a decision policy, not a fixed interval such as 45m, 1h, or 2h. A controller derives each lane's next due time from current evidence and records the decision.

## Fast distinction: schedule vs timeout vs window

Read these fields as separate dimensions:

| Field | Meaning | Example |
|---|---|---|
| `schedule` | When the scheduler admits a run | `daily @ 05:52:19 PT` |
| `timeout_secs` | Maximum execution duration for one run | `7200s = 2h` |
| `cron:timing-window` metadata | Declared timing window / operating hint | `3600s = 1h` |
| `observed_at` / `next_due_at` | Actual observation and computed next decision | Timestamped receipt |

A 2h timeout does not mean a 2h recurrence. A 45m timing window does not establish a 45m recurrence. Treat a cadence as changed only after the live scheduler read-back confirms its effective schedule and next-run time.

## Dynamic decision inputs

Evaluate each lane independently under one registry-owned cadence controller:

- Source state: current source SHA, local mirror freshness, prior watermark, and changed paths.
- Work state: last run, duration, exit status, queue depth, dependency state, and material output delta.
- Capacity: authoritative quota/headroom, API rate limits, runner/VM pressure, and provider availability.
- Freshness: age of the last successful evidence and the consequence of delayed refresh.
- Coordination: other producers, shared inputs, and downstream consumer deadlines.

## Decision contract

For each lane, choose and receipt one action:

- **RUN** — new source state, stale evidence, or a downstream dependency makes work useful.
- **SKIP_UNCHANGED** — source and relevant inputs match the prior watermark; emit a compact skip receipt.
- **BACKOFF** — evidence remains current while capacity or execution pressure is elevated.
- **RETRY** — the next attempt has a changed input or an evidence-backed recovery condition.
- **EXPEDITE** — a material source change or freshness risk justifies earlier execution.

Record the effective policy version, decision, reason, observed inputs, next due time, lane identity, source SHA, prior watermark, run identity, quota evidence, duration, and output location. Keep each producer's execution receipt, result, consumer, and encryption state distinct.

## Cross-surface propagation and read-back

A cadence change is complete only when all of these agree:

1. One canonical unified-registry entry records `Dynamic` and the policy inputs.
2. The VM scheduler reads back the accepted mode, effective next-run time, and job identity.
3. The corresponding repository workflow/config surface reads back the same registry decision.
4. Each producer emits its own run or skip receipt with a comparable watermark.
5. At least 24h of receipts demonstrate coordinated decisions across the participating lanes.

Use the owning request / unified-registry route to change cadence. Verify live scheduler state after the request; chat status, a committed backup descriptor, and a successful dispatch are supporting evidence rather than scheduler read-back.

## Current RECON lesson — BRR × repo-export-sync

The 2026-11-23 published descriptors showed two independent daily schedules:

- `repo-export-sync`: 03:40:44 user-local, `timeout_secs: 3600`.
- `vm-brr-delta`: 05:52:19 America/Los_Angeles, `timeout_secs: 7200`.

Their `cron:timing-window` tags were 7200s and 3600s respectively. These values describe separate metadata and execution dimensions; neither proves a 45m or 2h recurrence. The observed export and BRR artifact timestamps also belonged to separate producer windows.

The owner directive selects `Dynamic` for the relationship. Keep repo export and BRR as separate lanes under shared cadence decisions and comparable watermarks. BRR continues to require local-Git ancestry, fetch-before-use, its regression suites, and its 300-second pass budget. A GraphQL-only inventory remains a distinct method and receipt.

## Security / CTF learning cohort

The agent-team architecture already recognizes CTF and security evaluation cohorts as Scout populations. A cohort assignment is a learning and evaluation route; execution authority comes from the specific lab's rules and written scope.

Preferred progression and reference set:

- [OverTheWire Bandit](https://overthewire.org/wargames/bandit/) — beginner Linux, shell, SSH, and command-line foundations.
- [PicoCTF](https://picoctf.org/) and [pwn.college](https://pwn.college/) — structured CTF learning and systems/security exercises.
- [PortSwigger Web Security Academy](https://portswigger.net/web-security) — web security labs and guided practice.
- [OffSec PEN-200](https://www.offsec.com/courses/pen-200/) — structured penetration-testing preparation and OSCP/OSCP+ pathway.

Operate against explicitly authorized CTF/lab targets, local intentionally vulnerable environments, or written-scope assessment assets. Keep target allowlists, time windows, permitted techniques, rate limits, evidence handling, and stop conditions with each exercise. Route findings into remediation and defensive regression tests.

For OffSec certification exams, follow the current official exam guide. The OSCP+ guide prohibits AI chatbots during the exam and reporting phase; exam work remains the learner's independent performance.

## Collaborator discovery

- Primary entry: `CLAUDE.md`.
- Skill index: `docs/ops/SKILLS-INVENTORY.md`.
- Execution behavior: `.agents/skills/adaptive-wait/SKILL.md` and `.agents/skills/adaptive-feedback-cycle/SKILL.md`.
- Team/security cohort context: `docs/architecture/AGENT-TEAM-CONTROL-PLANE.md`.
- Session learning log: `docs/ops/sessions/LEARNINGS.md`.
