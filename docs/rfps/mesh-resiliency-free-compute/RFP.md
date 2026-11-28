# Independent RFP: Mesh-Resilient Free Compute and Workload Rotation

**Lane:** `planning:mesh-resiliency`  
**Tracking issue:** [#1622](https://github.com/timerloggedout-spec/termux-monorepo/issues/1622)  
**Status:** Research expanded; provider scoring and selection remain pending  
**Version:** 0.1.0  
**Last updated:** 2026-11-23  
**Owner boundary:** Independent of the hackathon Delphi Oracle RFP, PR #1620, Hex, and any AWS account signup.

## 1. Executive intent

Choose a resilient, portable, evidence-backed compute plan for `termux-monorepo` that makes the best use of genuinely available free quotas and promotional credits across multiple providers. The target is the best **workload-to-provider allocation and recovery policy**, rather than the biggest advertised free VM, under changing quotas, service limits, failure domains, and account eligibility.

The result must explain:
- which workload belongs on which execution surface and why;
- what is truly free, conditional, promotional, expired, or unknown;
- how work is rotated or failed over without thrashing, duplicate side effects, or data loss;
- how the system behaves when a provider, quota, region, credential, or free offer disappears;
- what evidence is required before any real deployment.

This document records an RFP and research plan. Provider selection, eligibility confirmation, awards, and provisioning authorization remain separate decisions.

## 2. Separate-lane contract

This RFP lives under `docs/rfps/mesh-resiliency-free-compute/` and is tracked by issue #1622.

Scope boundaries:
- ownership by the hackathon Delphi RFP;
- inclusion in the Delphi Oracle MVP/Gantt implementation PR;
- dependency on Hex access or human collaborator ballots;
- authorization for AWS signup, infrastructure provisioning, payment setup, or credit spend.

Other lanes may link to this RFP as a dependency. Each lane preserves separate requirements, status, scoring, and decision records.

## 3. Objectives and measurable outcomes

1. **Availability:** tolerate a provider/region/runtime outage for eligible workloads, with declared recovery objectives.
2. **Quota efficiency:** allocate work using current quota evidence, reset windows, usage observations, and account-specific eligibility where available.
3. **Cost safety:** prevent accidental paid use through explicit spend ceilings, provider-specific guardrails, and fail-closed behavior when pricing is uncertain.
4. **Portability:** minimize provider-specific assumptions; package workloads with reproducible build/runtime contracts and explicit state boundaries.
5. **Recovery correctness:** make retries idempotent where possible; record leases, checkpoints, outputs, and duplicate-suppression keys.
6. **Operational simplicity:** favor low-maintenance designs over a fragile “free tier arbitrage” mesh.
7. **Auditability:** retain source URLs, retrieval timestamps, exact terms, evidence freshness, uncertainty, and decision rationale.

Provisional targets to validate with workload owners:
- control plane remains usable if any one optional compute provider is unavailable;
- queued, retryable jobs can be rescheduled without losing their canonical job record;
- every provider switch remains subject to budget, security, and eligibility gates;
- every allocation decision is explainable from a versioned policy and evidence snapshot;
- a missing or expired quota signal remains unknown until a fresh observation establishes capacity.

## 4. Workload profiles to inventory

Classify actual repository workloads before provider scoring. Evaluate portability and long-running suitability independently for each workflow.

| Profile | Examples | Runtime shape | State / side effects | Likely execution class |
|---|---|---|---|---|
| CI and tests | lint, unit/regression tests, smoke suites | bounded, ephemeral | artifact and logs; repo writes must be gated | hosted CI or ephemeral runner |
| Historical backfill | paginated API collection and graph rebuild | long/batch, checkpointable | cursor, manifest, immutable receipts | checkpointed worker |
| Research/benchmark | provider comparisons, bounded experiments | batch, quota-sensitive | source receipts, results, costs | disposable worker |
| API/control service | small control endpoints and dispatch | low-latency, persistent availability | durable job/control state | always-on or managed service |
| Artifact/data service | receipts, manifests, compact indexes | storage/network-sensitive | durability and backup required | managed data/storage plane |
| Interactive development | shell, debugging, exploratory work | human-session, bursty | developer workspace | dev environment, production failover excluded |

For every profile record: CPU architecture/features, memory, disk and persistence, network/egress, runtime, max execution duration, concurrency, secrets scope, required inbound connectivity, durability, RPO/RTO, data sensitivity, and whether work is safe to retry.

## 5. Candidate provider and service classes

This is an **unranked research shortlist**. Candidate inclusion records a discovery lead; current free status and suitability require fresh evidence.

### A. General-purpose VM / instance
- Oracle Cloud Infrastructure Always Free — https://www.oracle.com/cloud/free/
- Google Cloud Free Program / free usage — https://cloud.google.com/free
- AWS Free Tier — https://aws.amazon.com/free/
- Microsoft Azure free account / free services — https://azure.microsoft.com/free/

### B. Managed container / application runtimes
- Google Cloud Run — https://cloud.google.com/run/pricing
- Azure Container Apps — https://azure.microsoft.com/pricing/details/container-apps/
- Cloudflare Workers — https://developers.cloudflare.com/workers/platform/pricing/
- Deno Deploy — https://deno.com/deploy/pricing
- Koyeb — https://www.koyeb.com/pricing
- Render — https://render.com/pricing
- Fly.io — https://fly.io/docs/about/pricing/
- DigitalOcean App Platform — https://www.digitalocean.com/pricing/app-platform

### C. Repository-native / CI and scheduling surfaces
- GitHub Actions — https://docs.github.com/en/billing/managing-billing-for-your-products/about-billing-for-github-actions
- GitHub-hosted runner limits and usage policies must be evaluated against the actual repository plan and workload.
- Existing Termux/Android and local/self-hosted runners may be useful for development or controlled workers, and require separate independence and availability evidence before production placement.

Provider names above are discovery leads. For each candidate, verify the exact product and plan; VM, container, serverless, CI, and storage products serve distinct workload classes.

### D. Extended utilization and adjunct surfaces — 2026-11-23

A dated official-source supplement expands the shortlist with six additional surfaces:

- [SnapDeploy](./EXTENDED-UTILIZATION-OPTIONS-2026-11-23.md#snapdeploy) — sleeping containers with a shared monthly hour budget.
- [Leapcell Hobby](./EXTENDED-UTILIZATION-OPTIONS-2026-11-23.md#leapcell) — bounded serverless invocations and GB-hour quota.
- [Appwrite Free](./EXTENDED-UTILIZATION-OPTIONS-2026-11-23.md#appwrite) — backend functions with a seven-day inactivity pause.
- [alwaysdata Free](./EXTENDED-UTILIZATION-OPTIONS-2026-11-23.md#alwaysdata) — restricted personal website hosting.
- [Back4app Containers](./EXTENDED-UTILIZATION-OPTIONS-2026-11-23.md#back4app-containers) — Docker preview capacity with conflicting URL-lifetime evidence.
- [zrok Free](./EXTENDED-UTILIZATION-OPTIONS-2026-11-23.md#zrok) — network-sharing capacity, separate from compute.

The supplement also records Codespaces and Cloudflare as existing account-backed surfaces, and reconciles the Render image-backed repository path. The supplement's account observations remain timestamped and distinct from published entitlements.

## 6. Evidence protocol

Each provider claim must have an evidence row with:
- provider and exact product/plan;
- official source URL and source title;
- retrieval timestamp (UTC);
- source publication/update date, if stated;
- region and account eligibility constraints;
- quota unit, quantity, reset period, and whether shared across products/projects;
- expiry and post-trial behavior;
- CPU/RAM/architecture/runtime/duration constraints;
- storage, egress, public networking, and persistence limits;
- sleep/suspend/cold-start behavior;
- required payment method and overage behavior;
- cancellation/teardown semantics;
- confidence classification: `verified`, `conditional`, `estimate`, `unknown`, or `expired`;
- raw evidence excerpt or structured facts, captured within provider terms;
- next recheck date and evidence owner.

Prefer official pricing, quota, product-limit, and terms pages. Secondary sources may identify leads but cannot alone establish current eligibility or cost. Confirm account-specific credits directly; public marketing pages provide entitlement context.

### Evidence freshness
- Recheck volatile pricing, free-tier, and quota claims immediately before a decision or experiment.
- Store observation time separately from source publication time.
- Expired or inaccessible evidence becomes `unknown`; prior free status remains historical.
- Preserve historical snapshots so quota/terms changes can be analyzed.

## 7. Scoring rubric (version 1)

Score each criterion 0–5 with written evidence and confidence. Compute a total after weights are agreed and published; preserve uncertainty and avoid false precision.

| Criterion | What a high score means | Initial weight |
|---|---|---:|
| Workload fit | Meets runtime, CPU/RAM, duration, storage, network requirements | 20% |
| Resilience contribution | Adds an independent failure domain and usable recovery path | 20% |
| Free/quota value | Useful verified capacity after constraints, reset, expiry, egress, and overage risk | 15% |
| Portability | Standard OCI/container or simple runtime contract; low migration friction | 10% |
| State and data safety | Supports required durability, backups, checkpoints, and idempotency | 10% |
| Operations burden | Low setup, maintenance, monitoring, and credential complexity | 10% |
| Security and governance | Least privilege, secret isolation, audit, region/data fit | 10% |
| Exit/lock-in | Clear teardown/export and low switching cost | 5% |

Weights are a provisional proposal requiring review. Report per-criterion scores, uncertainty ranges, and disqualifiers. Preserve hard disqualifiers independently of every free-tier score.

### Hard disqualifiers
- unclear or uncontrolled paid overage;
- absence of a safe cap or billable-usage guard;
- incompatible runtime or data-residency requirement;
- required state cannot be recovered;
- terms or eligibility cannot be verified sufficiently for the intended use;
- a provider is only nominally independent but shares a critical dependency with the primary path.

## 8. Mesh topology and control-plane principles

Separate the **control plane** from the **execution pool**.

- Canonical job identity, desired state, leases, checkpoints, policy versions, and receipts live in a durable, provider-neutral record.
- Workers are replaceable executors. They receive bounded, least-privilege work envelopes and return structured receipts.
- Provider adapters implement capabilities and limits; canonical job truth remains in the provider-neutral record.
- Scheduling decisions are deterministic from a versioned policy plus timestamped quota/health observations.
- Health, quota, and credential failures are separate signals. A provider can be healthy but quota-exhausted; a quota can exist while an account is ineligible.
- Provider diversity must be measured across actual failure domains (identity, region, network, storage, control plane, and billing account), rather than brand-name count.
- Keep critical secrets out of artifacts, job payloads, logs, and the canonical evidence ledger.

Prioritize existing repository-native options and measured durability requirements before evaluating a new external control-plane service.

## 9. Rotation and allocation policy to evaluate

Compare at least these policies on identical synthetic fixtures and, only after approval, bounded real workloads:

1. **Static primary + fallback:** lowest operational complexity; fail over only on classified failure.
2. **Quota-aware weighted rotation:** allocate within verified remaining budget, workload fit, and reset windows.
3. **Capability-first placement:** choose only providers satisfying runtime, duration, state, and security requirements.
4. **Health-aware rendezvous/consistent hashing:** limit unnecessary movement and avoid fleet-wide churn.
5. **Deadline/priority-aware queueing:** reserve scarce capacity for critical jobs; defer noncritical research when quotas are low.
6. **Diversity-constrained placement:** avoid placing primary and fallback on the same effective failure domain.
7. **Cooldown/backoff circuit breaker:** suppress rapid retries after provider failures and use jittered retry windows.
8. **Human-approved escalation:** pause rather than switch to paid capacity, weaken security, or exceed policy.

The scheduler must distinguish:
- retryable vs non-retryable failures;
- provider outage vs quota exhaustion vs auth/eligibility failure;
- safe-to-retry jobs vs side-effecting jobs requiring idempotency or human review;
- temporary capacity loss vs end-of-free-offer/credit expiry;
- actual remaining quota vs stale/estimated quota.

### Anti-thrashing rules
- minimum dwell time or stability window before non-emergency rebalancing;
- hysteresis thresholds for switching;
- per-provider and global retry budgets;
- exponential backoff with jitter;
- per-job attempt caps and duplicate suppression;
- explicit cooldown reason and next-eligible timestamp;
- require corroborating health observations before non-emergency rotation.

## 10. Failure and abuse scenarios

The experiment matrix must cover:
- provider API/control plane outage;
- region outage;
- account suspended or verification required;
- quota exhausted or reset time changed;
- free offer expires or product terms change;
- stale quota observation;
- network partition and partial completion;
- worker dies after side effect but before receipt;
- duplicate dispatch / lease expiry race;
- state store unavailable or corrupted;
- artifact upload failure;
- credential revoked or rotated;
- image/runtime architecture mismatch;
- unexpectedly billable operation;
- failover provider shares a hidden critical dependency.

For each: expected detection, safe behavior, recovery, data loss/duplication risk, receipt fields, and manual intervention threshold.

## 11. Experiment plan and gates

### Gate 0 — scope and workload inventory
Produce measured workload profiles from current workflows and identify which are safe to relocate. Provider scoring begins after requirements are established.

### Gate 1 — source-backed provider matrix
Collect official evidence for at least three materially different execution classes and at least two independent VM/instance candidates. Mark unsupported fields unknown. Account signup remains outside this gate.

### Gate 2 — offline policy simulation
Build fixtures for quota resets, expired evidence, provider outages, shared failure domains, duplicate work, and budget limits. Compare candidate policies with deterministic replay. Report decision correctness, unnecessary switches, failed jobs, duplicated side effects, recovery time estimates, and quota overrun attempts.

### Gate 3 — sandbox experiment design
Specify a bounded sandbox test with cost ceiling, data boundaries, teardown checklist, and stop conditions. Run after code is deploy-ready and owner approval covers the account/provider scope.

### Gate 4 — controlled pilot
Only after explicit approval: use synthetic/non-sensitive work, low quotas, spending protections, least-privilege credentials, and an independently verifiable teardown receipt.

### Gate 5 — recommendation
Publish a decision record with chosen topology, rejected alternatives, score/uncertainty, costs, failure evidence, portability plan, rollback, and re-evaluation triggers.

## 12. Security, cost, and operational guardrails

- Planning phase covers repository research and public documentation; cloud calls, account creation, payment setup, and resource provisioning require a separate approved phase.
- Paid fallback requires explicit owner approval.
- Default to fail-closed when price, quota, eligibility, or identity is unknown.
- Separate provider credentials; least privilege; secret values stay out of source and artifacts.
- Explicit per-provider and global budgets, alerts, usage sampling, and kill switch before pilot.
- Teardown must enumerate resources and independently verify their deletion/termination.
- Sensitive repository contents and production secrets require separate review and approval before any experiment.
- Describe a public free-tier offer as account-eligible only after account-specific eligibility evidence exists.

## 13. Required deliverables

1. Workload inventory and capability requirements.
2. Evidence-backed provider matrix and timestamped source ledger.
3. Versioned scoring rubric and explicit disqualifiers.
4. Mesh topology alternatives and failure-domain map.
5. Rotation/allocation policy specification.
6. Deterministic fixture corpus and offline simulation report.
7. Bounded pilot plan with cost/security/teardown gates.
8. Final decision record and operational runbook.
9. Recheck schedule for quota/terms drift.

## 14. Initial decision questions

- Which workloads need persistent availability versus merely eventual completion?
- Which canonical state is already durable and provider-neutral?
- What are the actual concurrency, memory, architecture, duration, storage, and egress profiles of current workflows?
- Which services provide genuinely independent failure domains?
- Is rotation needed for quota conservation, resiliency, or both? These objectives may conflict.
- Which free offers require payment details or carry overage risk?
- What is the minimum viable mesh that improves resilience without creating more operational failure modes than it removes?

## 15. Status ledger

| Work item | Status | Exit evidence |
|---|---|---|
| Separate planning lane claimed | complete | issue #1622 |
| Standalone RFP draft | in progress | this committed file, reviewed and refined |
| Workload inventory | pending | workflow-derived profile table with source references |
| Official provider evidence collection | in progress | dated six-provider supplement; broader matrix pending |
| Weight/rubric approval | pending | versioned rubric decision |
| Offline scheduler simulation | pending | fixtures, tests, deterministic report |
| Pilot authorization | blocked by design until code ready | explicit owner approval and cost/security gate |
| Provider selection | pending | decision record based on evidence |

## 16. Change control

Update this RFP through reviewable commits. Any scoring-weight change must state why and preserve the prior version. Provider terms and quota snapshots are append-only observations; preserve historical versions. A recommendation is valid only for the workload profile, evidence timestamps, and policy version it evaluated.
