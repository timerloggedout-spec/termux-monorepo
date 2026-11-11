# QDesk Pipeline Review RFP — Observatory, Delphi and DoE Evolution

**Proposal ID:** `qdesk-observatory-delphi-doe`  
**Status:** submitted for Delphi review; implementation authorization remains gated by the award and repository protections  
**Priority requested:** P0 architecture review, P1 implementation  
**Owning review lane:** QDesk → Delphi Oracle  
**Implementation lane:** QDesk pipeline / termux-monorepo  
**Related canonical systems:** Delphi Oracle RFP gate, DoE family, Dreambeans candidate pool, ForeSight Evidence Spine, HindSight, ICM, Temporal, provider/quota registry, Observatory surfaces map.

## 1. Executive request

Commission an evidence-led review and bounded implementation of a unified QDesk pipeline that turns an accepted RFP into a reproducible, reviewable and continuously improving implementation cycle.

The pipeline shall:

1. accept a QDesk work request and classify its scope, risk, dependencies and evidence;
2. generate or normalize an RFP using the existing Oracle Method proposal generator;
3. submit the RFP through the existing `delphi:rfp` gate and preserve the blind panel, sourced Oracle facts, cost veto, signed ledger and award semantics;
4. convert an accepted award into a versioned DoE design and candidate-pool generation request;
5. evaluate Dreambeans / method-version candidates using documented fit, novelty, feasibility, evidence, risk and validation criteria;
6. generate bounded implementation work packets, not unreviewed production mutations;
7. execute implementation through approved QDesk / GitHub / Temporal / Actions lanes;
8. validate output with independent tests, provenance and outcome receipts;
9. update the DoE pool with candidate lineage, culls, cherry-picks, propagation and negative results;
10. expose the entire lifecycle in existing Observatory and Delphi surfaces.

This is an extension of existing systems. It must not create a parallel Delphi gate, second RFP feed, duplicate evidence ledger, competing scheduler, replacement provider registry, or independent dashboard truth.

## 2. Problem and opportunity

The repository already has a functioning Delphi RFP gate, a Delphi RFP feed/collector, segmentation rules, an Oracle Method generator, DoE campaign governance, a 40-dimension DoE Questions Matrix, method-version candidate inventory, evolutionary replay and an Observatory/surface integration map.

The opportunity is to close the hand-off gaps between these components:

- intake and proposal generation;
- RFP award and implementation task creation;
- candidate-pool census and selection;
- design registration and actual execution;
- implementation evidence and outcome feedback;
- pool evolution and next-generation propagation;
- cross-surface visibility and provenance.

A high gate score is not implementation approval. A generated proposal is not a ballot. A replay win is not a production result. A candidate title is not evidence of candidate fitness. These distinctions remain mandatory.

## 3. Existing contracts to reuse

| Existing contract / implementation | Required treatment |
|---|---|
| `docs/ops/DELPHI-ORACLE-RFP-GATE.md` | Extend through its issue/event interface; do not fork scoring, panel or award logic |
| `docs/ops/DELPHI-LANE-CONTRACT.md` | Use approved events and signed award comments |
| `docs/ops/DELPHI-RFP-FEED.md` + `scripts/delphi/rfp_flood_feed.py` | Preserve one feed and one collector; add fields additively only after versioned schema review |
| `docs/ops/DELPHI-RFP-SEGMENTATION.md` | Keep silo/block boundaries and no cross-silo score leakage |
| `scripts/delphi/generate_proposal.py` | Extend deterministic, evidence-resolving generation; no hidden model calls or invented facts |
| `docs/ops/DOE-FAMILY.md` | DoE remains DESIGN OF EXPERIMENTS; MVT is one family member |
| `docs/ops/DOE-QUESTIONS-MATRIX.md` | Reference numbered dimensions; amendments are versioned, never silently renumbered |
| `docs/ops/DOE-DREAMBEANS-POOL.md` | Preserve source-card identity, MD5 duplicate flags and title-level triage uncertainty |
| `docs/ops/DOE-METHODS-EPOCH-2026-11-03.md` | Distinguish implemented methods from candidates and design-only methods |
| `docs/ops/FORESIGHT-EVIDENCE-SPINE.md` | Reuse resource/item/lane identity, evidence status, horizon, hashes and append-oriented corrections |
| `docs/ops/UNIFIED-PROVIDER-OBSERVABILITY-INDEX.md` | Observatory is a projection over canonical sources, not a replacement store |
| `scripts/agent_evolution/replay_simulator.py` | Replay only data/policy candidates; no generated code execution in replay |
| `docs/ops/AGENT-MONIKERS.md` | Preserve identity, role, provider, model and GitHub actor distinctions |

## 4. Functional scope

### 4.1 QDesk intake and trigger

Support explicit manual dispatch and approved repository events. Normalize each request into an immutable intake envelope:

- request_id, parent_request_id, created_at, updated_at;
- source issue/PR/document refs and source SHAs;
- requested outcome, scope, constraints and acceptance criteria;
- owner lane, responsible role and display moniker;
- risk class, permission class and spend class;
- evidence refs and unresolved gaps;
- idempotency key and correlation IDs;
- lifecycle state and state-transition receipt.

Trigger behavior must be idempotent. Duplicate events must reconcile to one request, one RFP, one campaign identity and one work-packet identity per logical unit. Burst handling must coalesce concurrent work and preserve a guaranteed final post-burst sweep. A filing that arrives after an active sweep captures its input set must be picked up by the next sweep; cancellation of an intermediate/final tick must not silently drop the pending sweep.

### 4.2 RFP and Delphi review

Generate an RFP package containing MANIFEST, ITEMS, RFP and PROVENANCE using the existing Oracle Method generator. Every factual claim must resolve to an evidence item; unresolved claims are explicitly marked UNVERIFIED / OPEN.

File or update one `delphi:rfp` issue per review unit. Preserve the existing blind panel and signed ledger. The gate must paginate through every page of open `delphi:rfp` issues (not only the first 100) on each reconciliation sweep. The approved disposition must be bound to a canonical SHA-256 of the complete proposal package, including architecture, acceptance criteria and referenced immutable artifacts; any content change invalidates the prior approval and requires re-review. The consumer must verify the exact proposal hash against the signed review record before it consumes an award. Never manufacture ballots, provider inference, external endorsement or consensus.

A Delphi award controls review disposition only. It does not authorize credentials, paid calls, merges, deploys, external account creation, data deletion or production traffic.

### 4.3 DoE campaign and pool generator

Create a versioned, reproducible candidate-selection and experiment-design layer over the existing Dreambeans pool and DoE family.

Candidate record fields should include:

- candidate_id, source_card_ref, source_hash, title and normalized concept;
- duplicate_group and duplicate disposition (flag only; no destructive dedupe);
- triage class and triage confidence;
- fit dimensions, evidence refs and evidence status;
- domain transfer risk / prohibited-transfer flags;
- candidate version, parent candidate and generation;
- experiment campaign, block/stratum and treatment assignment;
- implementation cost estimate and quota/capacity requirements;
- validation plan, independent oracle and exit criteria;
- decision state, reason, reviewer and receipt refs.

Pool generation must be deterministic for a pinned input census, config, seed and generator version. Every generation retains the incumbent and all candidates, including when a new candidate improves the observed score; promotion creates a new generation and never overwrites or deletes the incumbent. It must support:

- full-factorial and Taguchi L9 where appropriate and supported;
- blocked/randomized assignment where the design calls for it;
- baseline/control/variant membership;
- complementary exploration cohorts;
- explicit sample-size and power/precision limitations;
- SRM / assignment-integrity checks;
- uncertainty and dispersion reporting;
- sequential stopping only when predeclared;
- preserve-negative-results behavior;
- candidate culling, cherry-pick and propagation with lineage.

Do not call a title-level census a reviewed candidate. Do not treat repeated runs on one task as independent task replication. Do not claim statistical significance when the design cannot support it.

### 4.4 Bounded self-implementation

After an eligible award and required authorization, create implementation work packets with:

- exact scope and non-goals;
- pinned base SHA;
- target files and interface contracts;
- tests and fixtures;
- security / permission boundary;
- provider and quota eligibility;
- rollback plan;
- expected artifacts and provenance receipt.

The implementation agent may propose and commit changes on a review branch when repository permissions allow. It must not merge, deploy, provision paid resources, rotate credentials or widen permissions without the corresponding gate. Failed or incomplete attempts remain recorded.

### 4.5 Verification and evolutionary feedback

Require separate evidence for:

1. execution completion;
2. task outcome;
3. correctness;
4. integration;
5. regression;
6. resource/cost outcome;
7. provenance integrity;
8. independent review.

Only verified outcomes may influence fitness, role weights or promotion. Replay-only scores are candidate evidence, not online proof. Keep the incumbent and all candidates. A negative result is a retained result, not a discarded failure.

### 4.6 Observatory surfaces

Extend existing surfaces and feeds rather than replacing them. Provide linked views for:

- QDesk intake queue and lifecycle;
- RFP status, criteria, questions, panel response and signed outcome;
- DoE campaign, factor matrix, strata, allocation and run status;
- candidate pool census, lineage, duplicate groups, triage and selection;
- implementation packets, PRs, tests and approvals;
- provider/model/quota freshness and admission;
- provenance, telemetry, Temporal/Actions correlation and evidence gaps;
- generation comparisons, culls, cherry-picks and propagated methods.

The UI must render unknown, stale, unobserved, blocked and NOT_ESTABLISHED as distinct states. No blank-as-zero behavior.

## 5. Lifecycle and state contract

`RECEIVED → NORMALIZED → EVIDENCE_CHECKED → RFP_GENERATED → DELPHI_PENDING → DELPHI_AWARDED → DESIGN_REGISTERED → POOL_GENERATED → IMPLEMENTATION_READY → IMPLEMENTING → VALIDATING → REVIEW_PENDING → ACCEPTED | REJECTED | HELD → FEEDBACK_RECORDED → NEXT_GENERATION`.

`DELPHI_PARKED` is a holding state, not a path to design registration. A parked request remains parked until its gate-defined recheck condition is met; it then returns to `DELPHI_PENDING` for a fresh decision. It cannot create a design, campaign, work packet or provider call while parked.

Side states: `BLOCKED`, `STALE`, `CANCELLED`, `FAILED`, `RETRYABLE`, `SUPERSEDED`. Transitions must be append-recorded with actor, timestamp, reason, input/output hashes and evidence refs. Invalid transitions fail closed.

## 5.1 Standing DO statements and Memory Palace governance

The pipeline MUST consume the repository's existing **DO Statements** intent class rather than inventing a parallel directive taxonomy.

Canonical implementation:
- `scripts/classifiers/chat_intent.py` — `chat-intent v2`, with `R6-do-statement`.
- `scripts/classifiers/test_chat_intent.py` — regression fixtures for the DO class and precedence rules.
- `docs/ops/DOE-FAMILY.md` — records the owner ruling and DoE versioning/backfill doctrine.
- `docs/ops/DO-PHRASING-FRAMING-FRAMEWORK.md` — action-first request framing and evidence/stop boundaries.

A DO statement is a standing principle/criteria declaration (a durable directive-of-record), not a one-off task, artifact request, question, speculation or aside. Preserve the original statement and its source provenance. The current classifier uses a bounded maxim shape (bare declarative, at least two principle/criteria lexicon hits, at most ten words, no hedge/artifact/action) and returns rule/evidence fields. Its accuracy is NOT_ESTABLISHED until the documented labeled-outcome gate is met (at least 30 labeled outcomes per class, minority at least 10, p<0.05). Therefore classification is a candidate signal, not automatic authority.

A durable DO memory record must include: stable statement ID; exact original text; normalized text (never replacing the original); author/source message ref; observed/captured time; classifier version/rule/evidence; confidence or UNKNOWN; scope and affected lanes; priority; status (ACTIVE, SUPERSEDED, DISPUTED, EXPIRED); effective/review dates where supplied; supersession/conflict links; and provenance refs. No inferred author, scope, priority, expiry or authority. Sensitive content is excluded under existing privacy rules.

The Memory Palace / Method of Loci is a retrieval/indexing metaphor and navigation layer over the existing ICM/HindSight graph, not a second store of truth. Loci must resolve to canonical record IDs and source refs. Retrieval is scope-aware, permission-aware and provenance-preserving. Conflicting DO statements are surfaced with their chronology and authority; they are not silently blended or ranked by recency alone. A DO statement constrains execution but does not itself authorize a protected action, merge, spend, credential change or deployment.

## 5.2 Performance Psychology execution contract

Use the existing `.agents/skills/gemini-performance-psychology/SKILL.md` as an execution-control skill, not as a correctness oracle or a claim about human psychology. The QDesk worker adopts its evidence-bearing loop:

`smallest useful change → validation → feedback → next useful change`

Required behaviors:
- Momentum is a sequencing signal, never a quality signal.
- After every meaningful action, record what changed, evidence gained, what remains unproven and the next useful action.
- Increase workload progressively; HTTP 200 or provider availability is not task success.
- Preserve attempt lineage and change the smallest relevant variable after failure; no unchanged retries.
- Correctness outranks latency unless latency is the registered experiment factor.
- Do not reward green checks, activity, token count, comment count, low latency or provider availability over verified task outcome.
- Use bilateral critique for consequential architecture/security/provider/regression decisions.
- Preserve actor, role, provider/model, prompt version, run/attempt, commit, reviewer and artifact provenance.
- Follow BIUDL: broad objective → useful lane → thin slice → validate → integrate learning → broaden.
- Use explicit outcomes: PASS, FAIL, UNKNOWN, PARTIAL, COOLDOWN, UNAVAILABLE, BLOCKED, REGRESSION.

ATES/WTCV and related throughput measures are observational and diagnostic. They MUST NOT become a scalar merge threshold or substitute for correctness, independent review, acceptance evidence or authorization. Quality remains a separate hard gate.

## 6. Security, cost and governance constraints

- No secret values in issues, RFPs, telemetry, artifacts or provenance; secret names only.
- No paid fallback, card-gated service, account hopping or credential provisioning from an RFP award.
- Provider/model inference is disabled unless the existing exact entitlement, fresh quota and independent validation requirements are satisfied. Unknown, stale, incomplete or exhausted quota is an admission denial: no provider call (including a nominally free call) may occur until the authoritative quota evidence is fresh and admission succeeds.
- Provider quotas are capacity constraints, not quality scores.
- Do not let an agent approve its own high-impact changes.
- Keep builder, reviewer and independent verifier roles distinct.
- Never promote based on model preference, prose quality, replay-only scores or unverified telemetry.
- Use least-privilege GitHub permissions and scoped QDesk participant identities.
- Keep workflow concurrency, API budgets, retry ceilings and idempotency explicit.
- All destructive or externally consequential actions require an explicit authorization gate.

## 7. Implementation phases

| Phase | Deliverable | Exit gate |
|---|---|---|
| 0 — Recon & contract freeze | Existing system map, ownership matrix, state/schema delta, gaps register | Independent source/contract review |
| 1 — Intake bridge | QDesk request envelope, idempotency, RFP generator adapter, event trigger | Fixture tests; duplicate/burst tests |
| 2 — Delphi hand-off | RFP filing, existing gate invocation, outcome parser and receipt correlation | Existing gate regression suite + signed ledger verification |
| 3 — DoE pool generator | Deterministic census ingestion, candidate evaluation, design generation, lineage | Golden fixtures, seed determinism, SRM and duplicate checks |
| 4 — Implementation worker | Authorized work packet creation and branch/PR workflow | Permission tests, no auto-merge, reproducible build/test |
| 5 — Observatory | Existing feed projections and navigation | Feed/page parity, stale/unknown tests, accessibility |
| 6 — Evolution | Online outcome ingestion, replay comparisons, bounded cull/cherry-pick/propagation | Independent outcome corroboration and incumbent non-regression |
| 7 — Hardening | failure injection, recovery, audit, docs, runbooks | Full end-to-end test and rollback rehearsal |

## 8. Required deliverables

1. Architecture and threat-model review.
2. Versioned QDesk intake and lifecycle schema.
3. RFP generator integration and provenance receipts.
4. Delphi event/issue hand-off with no duplicate gate.
5. DoE pool generator and candidate-selection contracts.
6. Deterministic fixtures and test suite.
7. Implementation work-packet contract and bounded worker.
8. Observatory feed and UI integration.
9. Operational runbook, failure matrix and rollback procedure.
10. Final independent review with PASS / PASS WITH FINDINGS / HOLD / NO-GO and evidence refs.

## 9. Acceptance criteria

- Existing Delphi gate and feed remain the sole canonical RFP evaluation and feed path.
- A repeated trigger creates no duplicate request, RFP, campaign or work packet.
- All generated proposal claims resolve or are explicitly UNVERIFIED.
- RFP panel votes and awards are sourced verbatim from signed ledger records.
- Pool output is reproducible from pinned inputs and generator version.
- Candidate duplicates are flagged without deletion; domain-risk candidates remain parked until reviewed.
- Design assignment passes SRM and allocation integrity checks.
- Every treatment, candidate, cull, cherry-pick and propagation has lineage.
- No replay-only or title-level data is promoted as a verified outcome.
- Builder and verifier are independently attributable.
- Paid/credentialed/destructive/prod actions remain gated.
- Dashboard projections match canonical feed/ledger records. A documented propagation grace period is bounded per feed contract; during the interval any delta must be explicitly `STALE`/`INCOMPLETE` with observed and expected counts, and after recovery exact parity is required. No feed may remain indefinitely incomplete merely because it publishes a delta.
- All required tests and failure-injection cases pass; residual gaps are named.

## 10. Review questions for Delphi panel

1. Is the integration boundary correctly reusing existing Delphi, DoE, ForeSight, HindSight and Observatory contracts?
2. Which hand-off gap creates the highest operational risk?
3. Is the proposed candidate fitness rubric evidence-based and resistant to title/novelty bias?
4. Which design classes are appropriate for the actual factor types and sample budget?
5. What minimum evidence is required before a candidate can be selected, culled or propagated?
6. Does the proposed lifecycle distinguish admission, authorization, implementation and promotion?
7. Which surfaces should be first-class in the initial Observatory release?
8. What independent verification is required for the first end-to-end run?
9. What should be explicitly deferred to avoid overbuilding?
10. What are the measurable stop/go criteria for each phase?

## 11. Source record and uncertainty

This RFP is grounded in the repository contracts listed above. It does not claim that QDesk currently has a complete participant identity-plane implementation, that every provider is live, that all Dreambeans cards have been fully reviewed, or that autonomous production promotion is available. Those are discovery/validation questions for Phase 0.

**Decision requested:** Delphi review of this bounded integration and implementation plan, followed by a QDesk-owned implementation packet only when the gate and applicable authorization requirements are satisfied.
