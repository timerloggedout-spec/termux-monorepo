# Repository-Subject Evaluation Profile

**Profile:** `repository-subject-evaluation/v1`  
**Subject:** `timerloggedout-spec/termux-monorepo`  
**State:** profile implementation in review; no certification is claimed.

## 1. Purpose

Evaluate the repository as a standalone software/system artifact. The evaluation is about the repository's own engineering properties and evidence—not about ChatGPT acting as a human aide, nor about a human operator's performance.

The resulting dossier is portable and revision-pinned. It is designed to support independent technical assessment and, where applicable, a separate external certification decision.

## 2. Subject identity

Every report MUST identify:

- canonical repository name and visibility;
- immutable 40-character commit SHA (and tree SHA when available);
- evaluated ref and default branch;
- evaluation profile/schema version;
- evaluation window and evaluator identity/role;
- source snapshot and evidence inventory.

A moving branch name alone is insufficient subject identity.

## 3. Evaluation dimensions

| Dimension | What is evaluated | Example evidence |
|---|---|---|
| Architecture and design integrity | Explicit boundaries, ownership, contracts, dependency direction, supersession | Architecture specs, dependency maps, ADRs, source inspection |
| Functional correctness | Required behavior and negative/failure behavior | Unit/integration tests, reproducible fixtures, issue reproductions |
| Security and privacy | Threat boundaries, secrets handling, permissions, data minimization | Security tests, permission manifests, secret-scan receipts |
| Build and reproducibility | Deterministic builds, pinned inputs, clean rebuilds | Build logs, lockfiles, artifact digests |
| Portability | Supported environments and honest limits | Termux/Android, Linux, architecture-specific smoke evidence |
| Operational reliability | Recovery, retries, idempotency, observability, failure classification | Workflow runs, jobs/steps, logs, artifacts, incident records |
| Documentation and maintainability | Navigation, consistency, versioning, change traceability | Documentation checks, schema validation, review records |
| Provenance and governance | Attribution confidence, review authority, promotion evidence | Commit/PR/run IDs, source refs, dual-gate receipts |

The evaluator MUST select criteria relevant to the declared certification target. This profile does not prescribe a universal numeric score or allow a weighted score to conceal a failed mandatory control.

## 4. Verdict semantics

- `PASS`: acceptance criterion met with sufficient direct evidence.
- `FAIL`: criterion not met or a reproducible defect is established.
- `PARTIAL`: some requirements met, with named unmet requirements.
- `UNKNOWN`: evidence absent, stale, conflicting, or insufficient.
- `NOT_APPLICABLE`: criterion excluded with a recorded rationale.

Overall evaluation outcome is `PASS`, `CONDITIONAL`, `FAIL`, or `UNKNOWN`. Mandatory-control failures cannot be averaged away.

## 5. Evidence rules

1. Pin every evaluation to an immutable repository revision.
2. Prefer direct evidence: source paths/lines, test output, workflow run/job/step IDs, artifact digests, and signed or otherwise authoritative external records.
3. Distinguish repository facts, owner assertions, evaluator judgments, and external authority decisions.
4. Preserve failed, cancelled, skipped, and unavailable attempts; do not rewrite them as success.
5. A successful CI job is evidence of that job's checks, not automatic proof of every system-level claim.
6. Missing evidence is `UNKNOWN`, not zero, not PASS, and not proof of absence.
7. Record tool/version/environment and collection time for reproducibility.
8. Keep secrets, credentials, raw prompts, private session stores, and restricted data out of the dossier.

## 6. Evaluation procedure

```text
REGISTER SUBJECT + PROFILE
        ↓
FREEZE REVISION / BASELINE
        ↓
SELECT CRITERIA + ACCEPTANCE RULES
        ↓
COLLECT EVIDENCE (AEF / DoE / ATES / CI)
        ↓
INDEPENDENT EVALUATION
        ↓
CLASSIFY GAPS + LIMITATIONS
        ↓
ISSUE INTERNAL EVALUATION REPORT
        ↓
OPTIONAL EXTERNAL PROGRAM MAPPING
        ↓
EXTERNAL CERTIFIER DECISION (separate authority)
```

For comparative treatments, use the canonical DoE experiment record and AEF. This profile is the repository-subject report format, not a second experiment ledger.

## 7. Certification boundary

The report has two independent outcomes:

- **Internal technical evaluation:** what the evidence establishes about the pinned repository revision.
- **External certification disposition:** not submitted, submitted, pending, certified, rejected, or not applicable, with authority and evidence reference.

The internal evaluation MUST NOT claim external certification. An external program's published eligibility, terms, assessment integrity, and evidence requirements must be identified by exact program/version before asserting that a particular activity is in scope or out of scope.

The owner-supplied statement that this is a repository-subject experiment, rather than a human-assistance service, is recorded as a scope assertion. It does not override any provider/platform terms or authorize use of restricted exam, account, or assessment flows.

## 8. Reduced-steering operating mode

The lane is optimized for standalone engineering work:

- The operator supplies the subject, intended outcome, and consequential authorization.
- The agent performs bounded RECON, implementation, validation, and evidence recording without repeatedly asking for stylistic direction.
- Unknowns are preserved explicitly; the agent does not invent authority, credentials, certification status, or test results.
- External submissions, protected assessments, paid actions, credential changes, destructive Git operations, and production promotion follow their existing authority gates.

## 9. Canonical integrations

- [Agent Evaluation Framework](../../architecture/AGENT-EVALUATION-FRAMEWORK.md)
- [Blind Agent Selection & Evaluation](../../architecture/AGENT-SELECTION-BLIND-EVALUATION.md)
- [DoE Family](../../ops/DOE-FAMILY.md)
- [BIUDL execution and provenance](../../ops/BIUDL-EXECUTION-AND-PROVENANCE.md)
- [Repository gates](../../ARCHW1Z-GATE.md)
- [Proposal process](../../proposals/PROCESS.md)
- [Agentic permissions](../../proposals/AGENTIC-PERMISSIONS.md)

## 10. Current status

This is a new profile/template under review. No live repository-wide certification assessment has been run by this change. No external program has been identified, and no external certification is claimed.
