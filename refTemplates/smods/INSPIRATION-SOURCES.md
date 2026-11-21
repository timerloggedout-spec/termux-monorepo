# Cited Inspiration Sources — Release Integrity + Acceptance Evidence

**Lane:** `refTemplates/smods/`  
**Disposition:** metadata-only research references; candidate patterns for CEEL-006  
**Work item:** `CCEL-006` — FOSS template inspiration, benefit compounding, and evolutionary reuse  
**Reviewed:** 2026-11-21

This file records external sources that inform repository-native evaluation, provenance, and release-assurance work. These records are citations and research inputs. They are not runtime dependencies, adopted implementations, or live gitlinks.

## Source register

| Source | Primary citation | Companion evidence | Disposition |
|---|---|---|---|
| Notary — GitLab Transcend showcase | https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/43637140/showcase | README describes signed canonical receipts, a tamper-evident ledger, human approval over exact commit/receipt/image digests, and an independent 14-check verifier. | **Pattern candidate** — integrity witness and release-approval design |
| ShipProof — GitLab Transcend showcase | https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/40623268/showcase | Feature MR: https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/40623268/showcase/-/merge_requests/62 | **Pattern candidate** — independent acceptance missions, exact-revision evidence, post-deploy replay, and production monitoring |
| Unresolved Transcend showcase candidate | https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/43452298/showcase | Public page and README retrieval returned cache-miss errors during review on 2026-11-21. | **Unverified / pending recon** — citation retained; content and fit remain unassessed |

## Evidence boundary

### Notary

The retrieved project README describes an assisted-autonomy release gate: agents propose, CI re-runs checks, a canonical receipt is signed, receipts are chained in a ledger, and a human approval binds to the exact commit and receipt hash. It documents an offline verifier with 14 checks and test cases for approval scope, signer identity, replay, expiry, self-approval, and freeze behavior.

The same README records material limits: the protected approval-tag flow had a dry-run but no actual release seal; agent-claim schema conformance was not yet wired into CI; software keys were used; the verifier itself remained a trust boundary; and the monitor script was not a deployed-service monitor. The source files for the verifier, receipt, and ledger were not independently inspected in this review. Treat implementation details as README-reported claims pending source-level replication.

### ShipProof

The retrieved MR diff adds cart-quantity behavior and Playwright tests, and changes the README to describe the broader ShipProof workflow. The README describes issue-derived acceptance missions, frozen browser/HTTP checks against an exact candidate revision, criterion-level outcomes (`PROVEN`, `BROKEN`, `UNVERIFIED`), evidence archives, post-deployment replay before traffic promotion, and a separate production monitor.

The MR diff substantiates the cart feature and its tests; it does not establish that every described workflow, trigger, Cloud Run deployment, or monitor was live. The project landing page and base README were archived/read-only, and the base README was a generic showcase template. Treat the ShipProof architecture as documented design evidence until the workflows and runtime are independently reproduced.

### Unresolved candidate

The showcase at `43452298` could not be retrieved during this review. Preserve the URL as a discovery lead and assign no capability claims or score until its README, source, and execution evidence are available.

## Patterns worth testing in this repository

1. **Integrity witness (Notary-inspired):** canonicalize the evidence envelope; bind receipt to repository, exact commit, workflow run, artifact digests, signer, and policy version; verify independently; retain stable reason codes for invalid or missing evidence.
2. **Behavioral witness (ShipProof-inspired):** derive acceptance missions from explicit issue criteria; freeze mission definitions and target revision; run independent browser/API checks; preserve criterion-level evidence and three-valued outcomes.
3. **Temporal witness (repository-native composition):** retain observed time, tested revision, supersession links, and replay identity so historical backfills distinguish current truth from what was knowable at execution time.
4. **Separated verdict axes:** evaluate behavior, provenance, integrity, temporal freshness, and attribution independently; let the existing policy reducer determine disposition.
5. **Human authority:** preserve explicit human approval for consequential release actions; bind approval to immutable evidence identity.

## 3L0 / CEEL integration hypothesis

Compose these as independent evidence adapters, not competing control planes:

- `AcceptanceWitness` consumes frozen mission results and emits behavioral evidence.
- `IntegrityWitness` consumes canonical receipts and emits signature, digest, and ledger verification evidence.
- `ProvenanceWitness` resolves actor, workflow, commit, and artifact lineage from existing provenance telemetry.
- `TemporalWitness` reconciles observed time, backfills, replay, and supersession.
- Existing classifiers consume these records; an overall decision remains a separate policy reduction.

Proposed outcome axes:

| Axis | Example states |
|---|---|
| Behavior | `PROVEN` / `BROKEN` / `UNVERIFIED` |
| Provenance | `VERIFIED` / `PARTIAL` / `UNKNOWN` |
| Integrity | `VALID` / `TAMPERED` / `INVALID` |
| Temporal | `CURRENT` / `STALE` / `HISTORICAL` |
| Attribution | `HUMAN` / `AGENT` / `AUTOMATION` / `UNKNOWN` |

These names are a research proposal for comparison against existing repository contracts; they do not assert that these exact schemas or classifiers already exist.

## DoE seed

| Factor | Treatments | Primary measures |
|---|---|---|
| Evidence integrity | CI artifact; digest manifest; signed receipt; signed receipt + append-only ledger + offline verifier | Tamper detection, reproducibility, verification cost |
| Acceptance independence | Developer tests; generated independent missions; frozen post-deploy replay | Missed defects, false positives, criterion coverage, detection latency |
| Temporal reconstruction | Current-state snapshot; event-time history; history + signed receipts | Attribution accuracy, temporal consistency, replay reproducibility |
| Release policy | Conventional CI; exact-SHA evidence gate; exact-SHA + integrity witness; candidate deployment + replay | Escaped defects, false blocks, recovery time, operational cost |

Run each treatment against the repository-native baseline with shared cohort identity, immutable run evidence, uncertainty reporting, and maintenance/security cost accounting. Promote only independently reproduced improvements through the existing dual-gate and proposal lifecycle.

## Admission and follow-up

- Keep all three showcase citations metadata-only in this register.
- Create a custom fork and a live `smods/` gitlink only after source inspection, license review, adaptation scope, immutable pin, compatibility evidence, and dual-gate validation.
- Re-fetch the unresolved showcase before assigning a tier or extracting patterns.
- Compare the proposed witness axes with existing provenance telemetry, ATES, Temporal Hindsight Witness, Repo-Replay, and classifier contracts before introducing new types.
- Preserve the distinction between source-reported claims, directly inspected code, executed tests, and independently reproduced results.

## Citation links

- Notary showcase: https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/43637140/showcase
- ShipProof showcase: https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/40623268/showcase
- ShipProof feature MR !62: https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/40623268/showcase/-/merge_requests/62
- Unresolved showcase: https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/43452298/showcase
