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
- Back4app's conflicting free-URL lifetime evidence.
- zrok's network-sharing role versus actual compute capacity.

---

### Task 1: Record six extended utilization candidates

**Files:**
- Create: `docs/rfps/mesh-resiliency-free-compute/EXTENDED-UTILIZATION-OPTIONS-2026-11-23.md`
- Modify: `docs/rfps/mesh-resiliency-free-compute/RFP.md`
- Modify: `docs/rfps/mesh-resiliency-free-compute/PROVIDER-EVIDENCE-MATRIX.md`

**Interfaces:**
- Consumes: existing RFP workload profiles and evidence schema.
- Produces: dated official-source dossier and six additional candidate rows, all unranked and non-authorizing.

- [ ] Add SnapDeploy, Leapcell, Appwrite, alwaysdata, Back4app Containers, and zrok with official evidence, fit, constraints, uncertainty, and next validation.
- [ ] Add Codespaces and Cloudflare as existing mesh surfaces requiring measured usage and lane completion.
- [ ] Preserve the RFP's provider selection pending and research-only provisioning boundary.

### Task 2: Reconcile Render deployment wiring

**Files:**
- Modify: `docs/DEPLOYMENT-LANES.md`
- Reference: `ops/render-image/README.md`
- Reference: `.github/workflows/readme-extractor-image.yml`
- Reference: `scripts/quota_poll.py`

- [ ] Record the GitHub Actions → GHCR image → Render image-backed service path.
- [ ] Distinguish repository evidence from Render account/service state.
- [ ] Preserve the separate Vercel, Pages, and Render lane boundaries.

### Task 3: Validate and publish

- [ ] Check Markdown structure, links, and exact source dates.
- [ ] Verify the diff and current branch base.
- [ ] Open a focused PR linked to issue #1622.
- [ ] Re-fetch checks against the immutable PR head SHA and report terminal states.

**Review Focus / acceptance:** Six candidate surfaces are added; Render's repository wiring is accurately recorded; Codespaces/Cloudflare remain distinct from new providers; unknowns remain explicit; account and production state remain unchanged.
