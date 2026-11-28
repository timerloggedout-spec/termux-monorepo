# Mesh Extended Utilization Implementation Plan

> **For agentic workers:** Execute this plan task-by-task with TDD for behavior changes and deterministic documentation validation for documentation-only changes.

**Goal:** Expand the mesh-resiliency RFP with six freshly researched utilization surfaces, reconcile the existing Render wiring, and record the next evidence-led priority investigations.

**Architecture:** Keep the existing mesh RFP and provider evidence matrix authoritative. Add one dated evidence dossier for six candidate surfaces and the existing Codespaces/Cloudflare/GitLab/Render lanes. Update the deployment-lane SSOT to distinguish repository wiring from provider-account validation.

**Tech Stack:** Markdown, GitHub repository contents API, official provider documentation, existing quota registry and deployment records.

**Spec:** `docs/rfps/mesh-resiliency-free-compute/RFP.md`, tracked by issue #1622.

## Global Constraints

- Keep public entitlements separate from account balances and current availability.
- Record official source URLs and observation date (2026-11-23).
- Keep unknown, disputed, and account-specific facts explicitly unknown.
- Keep research separate from provisioning, paid spend, credentials, production deployment, and runtime admission.
- Preserve the existing GitHub/Actions control plane and provider-neutral ledger.
- Render's repository wiring is distinct from live service/account verification.
- Use the existing Loopy-derived six-step feedback semantics and native adaptive WAIT; keep one scheduler and one telemetry ledger.

## Review Focus

- SnapDeploy's idle wake behavior and ephemeral-filesystem boundary.
- Leapcell's included quota versus metered overage and serverless-only free shape.
- Appwrite's seven-day inactivity pause and function runtime limits.
- alwaysdata's free-plan service/profit restrictions.
- Back4app's 60-minute preview URL and free auto-deploy restrictions.
- zrok's network-sharing role versus actual compute capacity.

---

### Task 1: Record six extended utilization candidates

**Files:**
- Create: `docs/rfps/mesh-resiliency-free-compute/EXTENDED-UTILIZATION-OPTIONS-2026-11-23.md`
- Modify: `docs/rfps/mesh-resiliency-free-compute/RFP.md`
- Modify: `docs/rfps/mesh-resiliency-free-compute/PROVIDER-EVIDENCE-MATRIX.md`

**Interfaces:**
- Consumes: existing RFP workload profiles and evidence schema.
- Produces: dated official-source dossier and six additional candidate rows, unranked; research-only.

- [x] Add SnapDeploy, Leapcell, Appwrite, alwaysdata, Back4app Containers, and zrok with official evidence, fit, constraints, uncertainty, and next validation.
- [x] Add Codespaces and Cloudflare as existing mesh surfaces with owner/usage states.
- [x] Preserve the RFP's provider selection pending and research-only provisioning boundary.

### Task 2: Reconcile Render deployment wiring

**Files:**
- Modify: `docs/DEPLOYMENT-LANES.md`
- Reference: `ops/render-image/README.md`
- Reference: `.github/workflows/readme-extractor-image.yml`
- Reference: `scripts/quota_poll.py`

- [x] Record the GitHub Actions → GHCR image → Render image-backed service path.
- [x] Distinguish repository evidence from Render account/service state.
- [x] Preserve the separate Vercel, Pages, and Render lane boundaries.

### Task 3: Validate and publish

- [x] Check Markdown table structure, local anchors, source URLs, and evidence dates.
- [x] Review the PR diff and compare its base with current master.
- [x] Open focused PR #5807 linked to issue #1622.
- [ ] Re-fetch checks against the immutable PR head SHA and record terminal states.

**Review Focus / acceptance:** Six candidate surfaces are added; Render's repository wiring is accurately recorded; Codespaces/Cloudflare remain distinct from new providers; unknowns remain explicit; account and production state remain unchanged.


## Execution ledger — 2026-11-23

- **Loop source:** repository `docs/ops/CONTINUOUS-IMPROVEMENT-POLICY.md` and `.agents/skills/adaptive-wait/SKILL.md`; Loopy six-step cycle adapted to the native WAIT contract. Root `LOOPS.md` is absent; the published Loop Library host is unspecified in the supplied skill, so catalog duplication review remains pending.
- **Task 1:** complete. Six provider candidates, official-source evidence, workload fit, limits, and priority tests are recorded in the RFP supplement and evidence matrix.
- **Task 2:** complete. Render's GHCR image-backed README path is reconciled as REPO-WIRED / PROVIDER HEALTH PENDING.
- **Cloudflare:** read-only account inventory and GraphQL Analytics activity confirmed; exact usage counts remain in private oversight. Billing Read remains required for financial usage. Queues inventory is empty; R2 activation remains owner-gated.
- **Codespaces:** owner HOLD dated 2026-10-27 preserved; allocation remains 0% with 100% reserve.
- **Quota ledger:** active registry remains 172 unique adopted-service records. Candidate-only entitlements remain in the RFP matrix until account approval and service adoption. Public quota snapshots remain identical.
- **Validation:** JSON parsing passed; registry IDs are unique; six provider rows and all six RFP anchors resolve; Markdown table column counts pass; positive-form scan passed across the new/updated RFP, provider matrix, deployment SSOT, and plan.
- **PR:** #5807; head `fc2742910888f809c244d419a58b118bea07db8b`. Current check sample: Vercel `build-rate-limit` failure; Devin Review pending; repository workflows queued/pending/cancelled. Reviews: none recorded. Branch is two generated commits behind master; compared paths are separate from this PR's changed files.
- **WAIT state:** approval-required for Render workspace selection; pending for repository workflow terminal states. Provider signup, paid resource creation, R2 activation, Queue provisioning, and production deployment remain owner-gated.
