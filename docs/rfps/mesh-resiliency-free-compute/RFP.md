# Independent RFP: Mesh-Resilient Free Compute and Workload Rotation

**Lane:** `planning:mesh-resiliency`  
**Tracking issue:** [#1622](https://github.com/timerloggedout-spec/termux-monorepo/issues/1622)  
**Status:** Planning claimed; research not yet completed  
**Version:** 0.1.0  
**Last updated:** 2026-10-24  
**Owner boundary:** Independent of the hackathon Delphi Oracle RFP, PR #1620, Hex, and any AWS account signup.

## 1. Executive intent

Choose a resilient, portable, evidence-backed compute plan for `termux-monorepo` that makes the best use of genuinely available free quotas and promotional credits across multiple providers. The target is not “the biggest advertised free VM.” It is the best **workload-to-provider allocation and recovery policy** under changing quotas, service limits, failure domains, and account eligibility.

The result must explain:
- which workload belongs on which execution surface and why;
- what is truly free, conditional, promotional, expired, or unknown;
- how work is rotated or failed over without thrashing, duplicate side effects, or data loss;
- how the system behaves when a provider, quota, region, credential, or free offer disappears;
- what evidence is required before any real deployment.

No provider is selected by this document. This is an RFP and research plan, not a claim of eligibility, an award, or an authorization to provision resources.

## 2. Separate-lane contract

This RFP lives under `docs/rfps/mesh-resiliency-free-compute/` and is tracked by issue #1622.

It is **not**:
- a subtask or deliverable owned by the hackathon Delphi RFP;
- part of the Delphi Oracle MVP/Gantt implementation PR;
- blocked on Hex access or human collaborator ballots;
- authorization to sign up for AWS, provision infrastructure, enter payment details, or spend credits.

Other lanes may link to this RFP as a dependency. They must not absorb its requirements, status, scoring, or decision records into their own completion claims.

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
- no provider switch is allowed to bypass budget, security, or eligibility gates;
- every allocation decision is explainable from a versioned policy and evidence snapshot;
- a missing/expired quota signal never becomes an assumption of free capacity.

## 4. Workload profiles to inventory

Before provider scoring, classify actual repository workloads. Do not infer that all workflows are portable or suitable for long-running instances.

| Profile | Examples | Runtime shape | State / side effects | Likely execution class |
|---|---|---|---|---|
| CI and tests | lint, unit/regression tests, smoke suites | bounded, ephemeral | artifact and logs; repo writes must be gated | hosted CI or ephemeral runner |
| Historical backfill | paginated API collection and graph rebuild | long/batch, checkpointable | cursor, manifest, immutable receipts | checkpointed worker |
| Research/benchmark | provider comparisons, bounded experiments | batch, quota-sensitive | source receipts, results, costs | disposable worker |
| API/control service | small control endpoints and dispatch | low-latency, persistent availability | durable job/control state | always-on or managed service |
| Artifact/data service | receipts, manifests, compact indexes | storage/network-sensitive | durability and backup required | managed data/storage plane |
| Interactive development | shell, debugging, exploratory work | human-session, bursty | developer workspace | dev environment, not production failover |

For every profile record: CPU architecture/features, memory, disk and persistence, network/egress, runtime, max execution duration, concurrency, secrets scope, required inbound connectivity, durability, RPO/RTO, data sensitivity, and whether work is safe to retry.

## 5. Candidate provider and service classes

This is a **research shortlist**, not a ranking. Candidate inclusion does not imply a currently free offering.

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
- Existing Termux/Android and local/self-hosted runners may be useful for development or controlled workers, but are not assumed to be independent, continuously available production infrastructure.

Provider names above are discovery leads. For each candidate, verify the exact product and plan; VM, container, serverless, CI, and storage products are not interchangeable.

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

Prefer official pricing, quota, product-limit, and terms pages. Secondary sources may identify leads but cannot alone establish current eligibility or cost. Never infer account-specific credits from public marketing pages.

### Evidence freshness
- Recheck volatile pricing, free-tier, and quota claims immediately before a decision or experiment.
- Store observation time separately from source publication time.
- Expired or inaccessible evidence becomes `unknown`, not “still free.”
- Preserve historical snapshots so quota/terms changes can be analyzed.

## 7. Scoring rubric (version 1)

Score each criterion 0–5 with written evidence and confidence. Do not compute a total until weights are agreed and published; avoid false precision.

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

Weights are a proposal for review, not a predeclared scientific truth. Report per-criterion scores, uncertainty ranges, and disqualifiers. Do not let a high free-tier score offset a failed security, durability, or cost-safety gate.

### Hard disqualifiers
- unclear or uncontrolled paid overage;
- no safe way to cap or prevent billable usage;
- incompatible runtime or data-residency requirement;
- required state cannot be recovered;
- terms or eligibility cannot be verified sufficiently for the intended use;
- a provider is only nominally independent but shares a critical dependency with the primary path.

## 8. Mesh topology and control-plane principles

Separate the **control plane** from the **execution pool**.

- Canonical job identity, desired state, leases, checkpoints, policy versions, and receipts live in a durable, provider-neutral record.
- Workers are replaceable executors. They receive bounded, least-privilege work envelopes and return structured receipts.
- Provider adapters implement capabilities and limits; they do not own canonical job truth.
- Scheduling decisions are deterministic from a versioned policy plus timestamped quota/health observations.
- Health, quota, and credential failures are separate signals. A provider can be healthy but quota-exhausted; a quota can exist while an account is ineligible.
- Provider diversity must be measured across actual failure domains (identity, region, network, storage, control plane, and billing account), not just brand names.
- Critical secrets are never copied into artifacts, job payloads, logs, or the canonical evidence ledger.

Do not require a new external control-plane service until the current repository-native options and durability needs are measured.

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
- no rotation based only on a single transient health probe.

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
Produce measured workload profiles from current workflows and identify which are safe to relocate. No provider scores before requirements exist.

### Gate 1 — source-backed provider matrix
Collect official evidence for at least three materially different execution classes and at least two independent VM/instance candidates. Mark unsupported fields unknown. No account signup required.

### Gate 2 — offline policy simulation
Build fixtures for quota resets, expired evidence, provider outages, shared failure domains, duplicate work, and budget limits. Compare candidate policies with deterministic replay. Report decision correctness, unnecessary switches, failed jobs, duplicated side effects, recovery time estimates, and quota overrun attempts.

### Gate 3 — sandbox experiment design
Specify a bounded, no-production test with cost ceiling, data boundaries, teardown checklist, and stop conditions. Do not run until code is deploy-ready and the owner explicitly approves the account/provider scope.

### Gate 4 — controlled pilot
Only after explicit approval: use synthetic/non-sensitive work, low quotas, spending protections, no broad credentials, and an independently verifiable teardown receipt.

### Gate 5 — recommendation
Publish a decision record with chosen topology, rejected alternatives, score/uncertainty, costs, failure evidence, portability plan, rollback, and re-evaluation triggers.

## 12. Security, cost, and operational guardrails

- No cloud calls, account creation, payment setup, or resource provisioning in the planning phase.
- No paid fallback without explicit owner approval.
- Default to fail-closed when price, quota, eligibility, or identity is unknown.
- Separate provider credentials; least privilege; no long-lived secrets in source or artifacts.
- Explicit per-provider and global budgets, alerts, usage sampling, and kill switch before pilot.
- Teardown must enumerate resources and independently verify their deletion/termination.
- No sensitive repo contents or production secrets in experiments unless separately reviewed and approved.
- Never describe a public free-tier offer as account-eligible until that account's eligibility is actually verified.

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
| Official provider evidence collection | pending | timestamped evidence ledger |
| Weight/rubric approval | pending | versioned rubric decision |
| Offline scheduler simulation | pending | fixtures, tests, deterministic report |
| Pilot authorization | blocked by design until code ready | explicit owner approval and cost/security gate |
| Provider selection | not started | decision record based on evidence |

## 16. Change control

Update this RFP through reviewable commits. Any scoring-weight change must state why and preserve the prior version. Provider terms and quota snapshots are append-only observations; do not silently rewrite history. A recommendation is valid only for the workload profile, evidence timestamps, and policy version it evaluated.
