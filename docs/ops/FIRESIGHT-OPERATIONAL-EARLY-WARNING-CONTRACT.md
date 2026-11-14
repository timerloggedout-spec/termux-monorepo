# FireSight operational early-warning contract

**Status:** staged design; implementation follows canonical event/evidence substrate  
**Parent:** [BIUDL Integrated Steering and Evidence Plan](../architecture/BIUDL-INTEGRATED-STEERING-AND-EVIDENCE-PLAN.md)

## 1. Mission and boundary

FireSight detects operational conditions that deserve attention, assigns severity/confidence, links evidence and routes findings for human/operator review. It is an early-warning layer, not a general observability replacement, planning engine, workflow runner, or autonomous repair agent.

Distinct responsibilities:

- **Observatory:** what changed or was observed?
- **FireSight:** what needs attention now?
- **Foresight:** what should be planned next?
- **ChronoMancer:** what verified context should carry forward?
- **Delphi:** what does the evidence justify?
- **HyperForge:** which bounded capability may be selected?
- **Admin Web:** who may authorize and govern an action?

FireSight findings are signals, not execution authority.

## 2. Inputs

Consume canonical repository/GitHub operational evidence, including:
- workflow run/job/step lifecycle and conclusions;
- repo gate and Termux smoke results on exact SHAs;
- artifact existence/digests and validation references;
- PR review/approval and mergeability transitions;
- deployment/release observations;
- action/effect receipts;
- capability and collaborator availability/freshness;
- dependency and approval age;
- feed generation timestamps and declared freshness windows.

Do not scrape or infer private provider quota, secrets, or device state outside authorized evidence sources. The device-offline hold is an explicit availability condition; it must not be misclassified as a product incident or test failure.

## 3. Detection classes

| Class | Example signal | Required qualification |
|---|---|---|
| Gate regression | required gate fails on candidate SHA | exact SHA + named check/run |
| Repeated failure | same workflow/capability fails repeatedly | stable fingerprint and bounded time window |
| Retry storm | repeated attempts without new source/input | attempts, concurrency group and causal linkage |
| Evidence gap | completed operation lacks required artifact/receipt | capability contract and missing reference |
| Stale approval | protected operation references expired/stale approval | approval policy/version and target SHA |
| Dependency degradation | required capability/provider unavailable | timestamped authoritative availability |
| Release drift | integration pin incompatible with component release | manifest/schema compatibility evidence |
| Deployment anomaly | unexpected failed or unhealthy deployment | deployment ID, environment and source SHA |
| Attribution ambiguity | action cannot be tied to a configured actor/instance | missing or conflicting provenance |
| Feed staleness | operational projection exceeds freshness SLO | generated_at, source watermark and policy |

A single cancelled/skipped run, Vercel rate limit classified as non-gating, or intentionally held device test is not automatically an incident. Policy and context matter.

## 4. Finding record

Minimum logical finding:

```yaml
schema_version: "1.0"
finding_id: "fire.<stable-id>"
fingerprint: "<stable-deduplication-key>"
detector:
  id: "<detector-id>"
  version: "<semver>"
  rule_id: "<rule>"
severity: "warning" # info | warning | major | critical
confidence: 0.0
state: "open" # open | acknowledged | mitigated | resolved | false_positive
summary: "<operator-readable statement>"
affected:
  repository: "owner/repo"
  ref: "<ref>"
  sha: "<40-hex SHA or null>"
  entities: []
evidence_refs: []
first_observed_at: "<UTC>"
last_observed_at: "<UTC>"
window:
  start: "<UTC>"
  end: "<UTC>"
owner: null
escalation:
  policy_ref: "<policy>"
  target: null
  due_at: null
related_finding_ids: []
resolution:
  action_ref: null
  validated_by: null
  validated_at: null
```

Confidence must be evidence-derived and bounded [0,1]; unknown confidence remains null rather than a fabricated midpoint. The example numeric value is a schema illustration only.

## 5. Severity and deduplication

Severity considers user/operator impact, blast radius, persistence, security implications and recovery urgency. It is not a raw count threshold alone.

Deduplicate using detector/rule + affected stable entity + normalized failure signature + bounded time window. Preserve repeat observations and first/last-seen times. Reopen a resolved finding only when a new qualifying event occurs; link the new episode.

Escalation targets are resolved from the owning lane and policy, not hardcoded to a presumed person or agent. Critical security/policy incidents follow existing security response policy.

## 6. Actions and prohibited behavior

FireSight may:
- emit a finding with evidence;
- group correlated findings;
- notify/route to an owning issue or review surface;
- recommend a bounded diagnostic;
- track acknowledgement, mitigation and verified resolution.

FireSight may not autonomously:
- modify source code;
- rerun/cancel workflows;
- merge PRs;
- change secrets, permissions or environments;
- publish releases or deploy;
- close/resolve its own finding without independent evidence.

Any future automated remediation must be a separately registered capability, policy-approved, idempotent, reversible where possible, and gated by explicit authorization.

## 7. Feedback loops

- FireSight → Foresight: risk signal, affected dependencies and evidence refs.
- FireSight → Admin Web: operator review queue and escalation.
- FireSight → Admin Graph: finding nodes/edges, state and freshness.
- FireSight → Collaborator Management: availability/reliability evidence, not an automatic quality verdict.
- FireSight → ChronoMancer: verified resolution context only after an issue is resolved and independently validated.

## 8. Acceptance criteria

- Every finding links to immutable evidence and detector/rule version.
- Replaying the same event set yields deterministic fingerprints and equivalent findings.
- Severity/confidence are explainable and preserve uncertainty.
- False positives and mitigations remain auditable.
- Stale or missing feeds are surfaced as data-quality warnings.
- Held/unavailable device work is represented accurately.
- No finding grants execution or promotion authority.
- Resolution requires evidence external to the detector's own assertion.

## 9. Delivery order

1. Event/evidence input adapter and replay fixtures.
2. Deterministic rule engine for gate regression, evidence gaps and stale feeds.
3. Finding schema, ledger integration and deduplication.
4. Routing/acknowledgement and Admin Graph projection.
5. Dependency, retry, attribution and release-drift detectors.
6. Threshold calibration over observed false-positive/false-negative cohorts.
7. Optional remediation proposals only after governance/security review.
