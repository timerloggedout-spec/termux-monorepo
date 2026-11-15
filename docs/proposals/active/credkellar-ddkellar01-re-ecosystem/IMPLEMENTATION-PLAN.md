# CredKellar / ddkellar01 RFP Implementation Plan

> **For agentic workers:** execute only after QUE admission and the relevant safety gates. Checkboxes track work; proposal status is not execution evidence.

**Goal:** Produce a complete, provenance-resolved and safety-reviewed inventory of the CredKellar Docker Hub ecosystem and linked `ddkellar01` GitHub repositories, then route justified integrations through the existing RE taxonomy and QUE machinery.

**Architecture:** Metadata-first candidate discovery feeds one normalized evidence inventory. Identity resolution and source-to-image verification precede static review; offline/contained testing precedes adoption decisions. Existing RE taxonomy, QDesk, RFP/Delphi and QUE remain authoritative.

**Tech Stack:** GitHub/Docker Hub public metadata; repository-native JSON/Markdown; Python standard library for deterministic validation; existing GitHub Actions and QUE intake. No new runtime dependencies in tranche 0.

**Spec:** `docs/proposals/active/credkellar-ddkellar01-re-ecosystem/PROPOSAL.md`

## Global Constraints

- No unknown sample execution on Termux, workstation, or shared CI.
- No third-party network scanning; only explicit authorized scope and synthetic lab targets.
- No image pulls until provenance, size and resource gates pass; do not pull the reported 4.4 GB malware sandbox image to Termux.
- No credentials, tokens, cookies, keys, private URLs or sample content in Git.
- No taxonomy v1 mutation without validated `re-taxonomy` intake and review.
- No new QUE, scheduler, ranker, source registry, quota ledger or evidence ledger.
- Every claim is labelled OBSERVED, PUBLISHER-CLAIMED, INFERRED, REPRODUCED, CONTRADICTED or UNKNOWN.
- A Docker namespace, GitHub handle, display name or README is not proof of common ownership.
- Default adoption path is reference/adapt; submodule only for a reviewed, pinned dependency required by the build.

## Review Focus

1. **Identity collision / aliasing:** `credkellar` and `ddkellar01` may not be the same principal; assert unresolved until corroborated.
2. **Source-image mismatch:** tags may be mutable and images may not correspond to claimed source; use immutable digest and build provenance.
3. **Network-scope bypass:** DNS changes, redirects, IPv6, encoded IPs and alternate target forms must not escape authorization.
4. **Unsafe sample processing:** archives, malformed files and active content can attack the analyzer; dynamic work remains blocked absent independent containment review.
5. **Incomplete inventory:** profile pagination and GitHub search limits can silently omit repositories; preserve per-page counts, cursors and completeness status.

---

### Task 1: Establish immutable discovery inventory

**Files:**
- Create: `ops/reverse_engineering/candidates/credkellar-ddkellar01.json`
- Create: `docs/proposals/active/credkellar-ddkellar01-re-ecosystem/PROPOSAL.md`

**Interfaces:**
- Consumes: public GitHub and Docker Hub metadata, dated observation records.
- Produces: candidate records with canonical identity, source URLs, evidence labels, status and unresolved questions.

- [ ] Capture all pages of Docker Hub `credkellar` profile and public repository metadata.
- [ ] Enumerate GitHub public repos for `credkellar` and `ddkellar01`; record exact account/repo identifiers.
- [ ] Record each observation timestamp, page/cursor, URL and immutable digest or commit SHA where available.
- [ ] Verify that every discovered item appears once in the normalized inventory; classify duplicate names and mirrors.
- [ ] Mark census completeness explicitly; do not represent the known 90-profile count as inspected until all pages are captured.

**Verification:** JSON parses; candidate IDs unique; every URL is canonical; every item has evidence label and status.

### Task 2: Resolve priority source provenance

**Files:**
- Update: `ops/reverse_engineering/candidates/credkellar-ddkellar01.json`
- Create: `docs/proposals/active/credkellar-ddkellar01-re-ecosystem/provenance-report.md`

**Interfaces:**
- Consumes: Task 1 inventory.
- Produces: source-to-image map for Sandbox-API and Hack-Dhe-Net.

- [ ] Resolve `credkellar/Sandbox-API` and `credkellar/Hack-Dhe-Net` against both GitHub handles.
- [ ] Record exact repo existence, owner ID, default branch, commit SHA, license, releases and archive state.
- [ ] Read Docker image config/labels/OCI annotations, tags and immutable digests through metadata-only paths.
- [ ] Compare source commit and image build metadata; assign VERIFIED/PARTIAL/UNVERIFIED/CONTRADICTED.
- [ ] Capture SBOM/signature/attestation evidence if published; absence is recorded, not inferred away.
- [ ] Resolve discrepancy between Docker Hub linked GitHub identity `ddkellar01` and source URLs under `credkellar`.

**Verification:** each priority image has a provenance status and explicit evidence supporting that status; no README-only verification.

### Task 3: Static architecture, capability and overlap review

**Files:**
- Create: `docs/proposals/active/credkellar-ddkellar01-re-ecosystem/capability-matrix.md`
- Create: `docs/proposals/active/credkellar-ddkellar01-re-ecosystem/threat-model.md`

**Interfaces:**
- Consumes: Task 2 source-provenance report and readable source trees.
- Produces: module map, API/CLI contract summary, threat model and fleet overlap decisions.

- [ ] Inspect Sandbox-API upload, detonation, isolation, storage, retention, report and deletion paths.
- [ ] Inspect Hack-Dhe-Net scope parsing, DNS/IP handling, redirects, connect logic, rate limits and offline fixture behavior.
- [ ] Compare against existing Ghidra, Binwalk, QEMU, Frida, mitmproxy, apk-xref, RE taxonomy and fleet security workflows.
- [ ] Separate unique capabilities from repackaged upstream tools, wrappers and duplicate products.
- [ ] Record maintenance cost, dependency footprint, platform compatibility and Termux suitability.

**Verification:** every matrix cell cites a source file/line or is marked UNKNOWN; all claims retain their evidence class.

### Task 4: Offline tests and containment design

**Files:**
- Create: `docs/proposals/active/credkellar-ddkellar01-re-ecosystem/verification-plan.md`
- Optional later: dedicated tests/fixtures only after code is admitted.

**Interfaces:**
- Consumes: Task 3 threat model.
- Produces: deterministic offline tests and a separately reviewed dynamic-test protocol.

- [ ] Hack-Dhe-Net: synthetic loopback targets only; test CIDR boundaries, DNS changes, redirects, IPv4/IPv6, malformed input, timeout/rate ceilings and scope rejection before socket creation.
- [ ] Sandbox-API: inert synthetic files only; verify API auth, isolation claims, egress denial, resource limits, retention and deletion.
- [ ] Do not run active samples; require isolated disposable microVM/sandbox with no host mounts and deny-by-default network before any dynamic sample work.
- [ ] Capture fixture hashes, environment image digest, exact command, exit code, logs and independent reviewer.
- [ ] Define stop conditions for containment escape, uncontrolled egress, credential exposure, sample retention uncertainty or resource exhaustion.

**Verification:** all dynamic actions are separately authorized; offline test suite is deterministic and reproducible.

### Task 5: Taxonomy v2 intake proposal

**Files:**
- Create: `docs/proposals/active/credkellar-ddkellar01-re-ecosystem/taxonomy-v2-candidate.md`
- If justified, submit existing `re-taxonomy` issue form.

**Interfaces:**
- Consumes: Tasks 3–4.
- Produces: candidate node records conforming to current intake validator.

- [ ] Decide whether sandbox boundary, network assessment, vulnerability assessment, orchestration and EVM bytecode require new concepts.
- [ ] Prefer existing axes/nodes when semantically sufficient; do not add tool roles for environmental controls.
- [ ] Ensure each tool node has `tool_role`, parents resolve, tags use exact axis vocabulary and toolchain stages preserve order.
- [ ] Submit through existing `re-taxonomy` intake and obtain toolkit-lane review.
- [ ] Do not edit canonical taxonomy directly as part of discovery.

**Verification:** `scripts/reverse_engineering/re_taxonomy_intake.py` accepts the proposed record against current default-branch taxonomy.

### Task 6: QUE admission, ranking and execution handoff

**Files:**
- Create/update: canonical QUE issue(s), using existing project-task filing and dispatch stamp contract.
- Update: proposal status only when QUE receipts support it.

**Interfaces:**
- Consumes: approved RFP tranche, evidence artifacts, dependency map.
- Produces: admitted, ranked and claimable QUE tasks with explicit done evidence.

- [ ] Split tasks at independently verifiable boundaries: census, provenance, static review, offline verification, taxonomy intake, adoption.
- [ ] Reuse #5283 ranking and #5286 claim/resolution; do not duplicate their machinery.
- [ ] Apply dependency edges: provenance before static source claims; threat model before dynamic verification; taxonomy review before registry promotion.
- [ ] Every task specifies owner lane, tier, acceptance criteria, stop conditions, evidence URLs and completion receipt.
- [ ] Preserve proposal/research/implementation/verification/promotion states separately.
- [ ] Reconcile with #5389 RFP→Delphi→DoE lifecycle where formal adjudication or experiment design is warranted.

**Verification:** QUE task is visible in canonical intake, has valid dispatch metadata, dependencies resolve and no execution is claimed before a claim/receipt exists.

### Task 7: Adoption decision and follow-through

**Files:**
- Create: `docs/proposals/active/credkellar-ddkellar01-re-ecosystem/adoption-decisions.md`

- [ ] Assign each candidate one disposition: ADOPT, ADAPT, REFERENCE, DEFER or REJECT.
- [ ] State license, provenance, security, maintenance, platform and capability rationale.
- [ ] For imports, use minimal function-level extraction with tests and attribution.
- [ ] For submodules, pin immutable reviewed commit and justify why reference/adapt is insufficient.
- [ ] For container use, pin digest and document build/provenance and runtime constraints.
- [ ] Require independent review before promotion.

**Verification:** every candidate has a recorded decision and all accepted items have an owner, tests, rollback path and maintenance plan.

---

## Commit and review cadence

- Commit each independently useful proposal artifact; do not batch unrelated changes.
- Rebase/update from current `master` before each promotion attempt; never force-push.
- Run JSON parsing, schema/validator tests, `git diff --check`, focused tests and current-head CI before claiming readiness.
- Open a PR for review; do not merge automatically.
- Preserve this branch/worktree for PR feedback.
