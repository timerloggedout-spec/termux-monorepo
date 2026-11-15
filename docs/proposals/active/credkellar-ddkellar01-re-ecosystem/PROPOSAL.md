# CredKellar / ddkellar01 reverse-engineering ecosystem — RFP & QUE proposal

**Status:** Proposed; research intake and source verification required  
**Date:** 2026-11-15  
**Lane:** Reverse Engineering Toolkits / Research-Astute → RFP → QUE  
**Primary registry:** `ops/reverse_engineering/taxonomy.json` (`re-taxonomy/v1`)  
**Proposal ID:** `cred-kellar-re-ecosystem-2026-11`

## 1. Executive decision

Establish a provenance-aware research and integration lane for the public projects and container images associated with the Docker Hub profile `credkellar` and its linked GitHub identity `ddkellar01`. Evaluate the named projects **Sandbox-API** and **Hack-Dhe-Net** first, then inventory the wider `ddkellar01` GitHub surface and the linked Docker Hub profile's repositories.

The intended outcome is not a bulk import. It is a repeatable funnel that turns externally discovered repositories/images into:
1. an identity- and provenance-resolved source record;
2. a reproducible capability/security assessment;
3. a taxonomy placement proposal;
4. a QUE-ranked, dependency-aware task only after evidence is sufficient; and
5. a controlled adoption decision (reference, adapt, import selected code, or pin as a dependency).

**Recommended decision:** approve a metadata-first research tranche, with Sandbox-API and Hack-Dhe-Net as priority candidates. Keep all source code and container execution out of scope until provenance, license, source-to-image correspondence, and isolation requirements pass their gates.

## 2. Identity and source resolution

Treat these as distinct identifiers until evidence links them:

| Identity / locator | Current evidence | Interpretation |
|---|---|---|
| Docker Hub namespace `credkellar` | Public Docker Hub profile and image pages exist | Container publisher namespace; not proof of GitHub ownership |
| Docker Hub profile's linked GitHub | Profile links to `https://github.com/ddkellar01` | Strong discovery lead for GitHub inventory; relationship still needs account-level confirmation |
| GitHub `credkellar` | Earlier GitHub connector repository lookups for the two named repositories returned 404 | Not found through that connector at lookup time; not proof of nonexistence or non-ownership |
| GitHub `ddkellar01` | Linked profile identity; repository inventory not yet fully enumerated | Include in all repository searches and provenance resolution |
| `credkellar/Sandbox-API`, `credkellar/Hack-Dhe-Net` | Docker metadata points to GitHub clone URLs under `credkellar`; connector lookups returned 404 | Source owner/path discrepancy to resolve before code adoption |

Do not merge identity records based on matching display names. Record GitHub numeric account IDs, canonical repository URLs, Docker Hub namespace/repository identifiers, image digests, publisher links, and dated observations when independently available. Do not infer that `credkellar` == `ddkellar01`.

## 3. Evidence baseline — facts, claims, and unknowns

### 3.1 Named priority candidates

| Candidate | Publicly observed metadata | Publisher-described capability (unverified) | Critical unknowns |
|---|---|---|---|
| `credkellar/sandbox-api` | Docker Hub page exists; page reported approx. 508.7 MB image and digest prefix `sha256:99fdb236a…`; page showed approx. 7.6K pulls and recent update at time of inspection | “Safely detonate files across PC, mobile, and cloud environments with AI-driven threat reports” | Canonical source repo; source/image correspondence; actual detonation isolation; network egress controls; sample retention; data handling; supported formats; auth model; API contract; license; reproducible build |
| `credkellar/hack-dhe-net` | Docker Hub page exists; page reported approx. 48.6 MB image and recent update | Publisher README describes an authorized-scope pentest lab, Python 3.12 standard library, scope registry gate before network packets, connect scans/banner/service detection, TLS, directory discovery, offline CVE cross-reference, CVSS 3.1 scoring, topology/trust mapping, logs, and offline fixtures | Canonical GitHub source; source/image correspondence; test reproducibility; network safety; scope enforcement under redirects/DNS/IP changes; license; dependency and vulnerability state |

The Docker Hub pages and their descriptions are evidence of what was published, not proof that the software behaves as described. The README claims must be independently tested. In particular, the Hack-Dhe-Net “scope gate” is a claim to verify with adversarial tests, not a control to trust.

### 3.2 Additional Docker Hub candidates to inventory

The following public Docker Hub results surfaced during discovery. These are **candidate leads**, not accepted integrations:

- `credkellar/diffre-lab` — binary diff/static RE; described PE/ELF/Mach-O header analysis, firmware signatures, strings/entropy, Mermaid call graphs; source URL reported as `credkellar/DiffRE-Lab`.
- `credkellar/php-vuln-re` — PHP static-vulnerability research lab; publisher describes synthetic samples, source-to-sink/taint mapping, obfuscation and framework fingerprinting.
- `credkellar/malware-research-hub` — publisher description claims a large encrypted sample/family collection; high-risk data provenance and sample-handling review required.
- `credkellar/malware-sandbox-suite` — large image (reported approx. 4.41 GB); do not pull to Termux; investigate only metadata and source manifests first.
- `credkellar/mon-ultra-matrix` and `credkellar/monad-ultra-infinite-matrix` — EVM/ABI/contract-analysis and composite RE ecosystem claims; deduplicate their claimed constituent repositories/images before any adoption.
- `credkellar/a-c-d-matrix-force` — publisher describes network analysis, CVE-RE, footprint masking, Sandbox-API and honeypot components; assess dual-use and component provenance carefully.
- `credkellar/q6g-1tb` — publisher description says some merged images have no public source repositories; source transparency must be treated as unresolved.
- `credkellar/reflashx-exploit-bomb` — source attribution surfaced under a different GitHub owner (`kimanicollier44-cmyk`); record as a provenance anomaly, not as a CredKellar-owned source.
- Other surfaced names include `commit`, `intuition`, `ultra-compiler`, `deconstruction`, `connectionx`, `kellar-ecosystem`, `guardrailx`, `cve-re`, `netx`, `sysadmin-footprint-mask`, `quantum-brutal-force`, and `lte-6g`. Confirm exact current names and metadata during the complete profile census.

The linked Docker Hub profile advertised 90 repositories over three pages at the time of inspection. This proposal does **not** claim that all 90 were inspected. Complete all pages, preserve pagination/census evidence, and distinguish owned, starred, mirrored, and merely published/linked objects where the platform exposes those distinctions.

## 4. Why this belongs in the existing RE taxonomy

The repository already has a validated, polyhierarchical reverse-engineering registry:
- machine source: `ops/reverse_engineering/taxonomy.json`;
- validator/query CLI: `ops/reverse_engineering/taxonomy.py`;
- operator guide: `docs/ops/REVERSE-ENGINEERING-TAXONOMY.md`;
- intake templates and validator contract: `docs/ops/RE-TAXONOMY-TEMPLATES.md`;
- taxonomy v1 includes target, method, objective, format, environment, architecture, evidence and tool-role axes; workflow stages are `acquire → identify → extract → analyze-static → observe-dynamic → validate → document`.

Current v1 has malware analysis as a work family and tool roles including extractor, emulator, capture and instrumentation, but does not explicitly model a sandbox execution boundary, network assessment/scanning, vulnerability assessment, or assessment orchestration as tool roles. Do **not** silently mutate v1 or invent a duplicate taxonomy. The RFP should test whether these are genuinely missing concepts or can be represented by current nodes/axes; then submit a separate v2 vocabulary proposal through the existing `re-taxonomy` intake.

### Proposed taxonomy review (not yet accepted)

| Candidate concept | Proposed treatment | Rationale / caveat |
|---|---|---|
| Sandbox execution boundary | Consider a new tool-role or explicit execution-environment node | A sandbox is a control boundary/environment, not automatically a tool. Model boundary properties separately from a product name |
| Network assessment | Consider `network-assessment` category/work family and scanner role | Keep authorized assessment distinct from exploitation |
| Vulnerability assessment | Consider a role or work family | Distinguish static code analysis, CVE correlation, configuration assessment and active probing |
| Assessment orchestration | Consider tool role only if multiple tools/steps are orchestrated | Do not make “orchestrator” a generic label for any CLI |
| EVM bytecode / smart contracts | Evaluate adding format/target vocabulary or a sibling registry | Avoid misclassifying EVM bytecode as JVM/CLR; confirm need and cross-links |
| Malware sample corpus | Model as evidence/data collection with custody and handling metadata, not as a tool | Encrypted samples do not establish lawful provenance or safe handling |

## 5. Objectives and success measures

### Objectives
1. Resolve the `credkellar` ↔ `ddkellar01` identity and repository-source discrepancy with durable evidence.
2. Enumerate all relevant public GitHub repositories for both handles and all pages of the linked Docker Hub profile.
3. Map repository source, image tags/digests, build provenance, licenses, release history, dependencies and documentation.
4. Verify advertised capabilities without running unknown binaries or samples on the host.
5. Compare candidates against existing RE tools and fleet capabilities to prevent duplicate integrations.
6. Produce a ranked adoption decision and QUE implementation plan with explicit owners, dependencies, acceptance tests and stop conditions.
7. Improve the RE taxonomy only through validated intake and review.

### Success measures
- 100% of pages in the Docker profile census accounted for, with timestamp and pagination evidence.
- Both GitHub handles searched; every discovered repository classified as owned/linked/fork/mirror/unknown.
- Every Docker candidate has immutable digest(s), observed update date, source URL status, license status and image-size metadata where available.
- Every accepted source-to-image mapping supported by a build recipe, attestation, reproducible build, or explicitly downgraded confidence.
- No external candidate enters the production taxonomy or toolchain without a passing intake validator and human review.
- Every QUE task carries acceptance criteria and machine-verifiable done evidence.
- No unknown sample execution, credential exposure, host networking, or unbounded resource consumption.

## 6. Work packages / RFP requirements

### WP0 — Identity and provenance census (P0)
- Query GitHub for `credkellar` and `ddkellar01`; resolve user/org identity, public repositories, forks, archived state, default branch, license, topics, releases, latest commit and source links.
- Query Docker Hub profile `credkellar` across all pages; collect repository name, description, last update, pull count, tags, immutable digests and image sizes.
- Preserve raw source URLs, capture time, pagination cursor/page, and normalized records.
- Classify identity relationships: confirmed-linked, likely-linked, unrelated, unresolved. Only confirmed evidence permits a canonical owner alias.

**Acceptance:** complete census with explicit counts and zero silently dropped pages; discrepancy register for every source path that does not resolve.

### WP1 — Source and supply-chain verification (P0)
- Resolve the GitHub source for Sandbox-API and Hack-Dhe-Net, including the possible `credkellar` vs `ddkellar01` owner mismatch.
- Compare Docker image labels, OCI annotations, build metadata, commit SHA, SBOM, signatures/attestations and source manifests.
- Inspect licenses and notices; classify absent/ambiguous license as no-adoption until clarified.
- Inventory dependencies and known vulnerabilities; distinguish publisher claims from independently observed facts.
- Record whether images are reproducibly built from public source.

**Acceptance:** source provenance status for each image: VERIFIED, PARTIAL, UNVERIFIED, or CONTRADICTED; immutable digest recorded; no “verified” label based solely on README or profile links.

### WP2 — Static capability and architecture review (P1)
- Review source tree, API contracts, CLI entrypoints, modules, data flow, storage, network behavior, permissions, secrets handling, logging and telemetry.
- Produce architecture map and component-level comparison against current fleet tools.
- Identify reusable algorithms/contracts versus duplicated product surfaces.
- Review Sandbox-API upload, detonation, orchestration, report and deletion semantics.
- Review Hack-Dhe-Net scope registry, target parsing, DNS resolution, redirects, CIDR/IP normalization, connect behavior, timeout/retry limits and offline CVE data.

**Acceptance:** source-backed component inventory, capability matrix, threat model, and duplication map.

### WP3 — Contained verification and test design (P1)
- Start with static inspection and offline fixtures. Do not detonate real samples.
- If dynamic verification is justified, use an isolated disposable environment with no host mounts, no host network, deny-by-default egress, resource/time quotas, disposable credentials, non-sensitive synthetic fixtures and auditable logs.
- For Sandbox-API, test only inert synthetic fixtures until containment has been independently reviewed. Require explicit sample custody, retention/deletion and egress controls before any real malware sample is considered.
- For Hack-Dhe-Net, use loopback-only or dedicated synthetic lab targets; test scope bypass attempts, DNS rebinding, IPv4/IPv6, redirects, alternate encodings, malformed CIDRs, timeout exhaustion and rate limits.
- Never use the tools against third-party systems without explicit authorization and a defined scope.

**Acceptance:** reproducible test plan and results with environment, fixture hashes, command, exit status, logs, and reviewer. No live third-party scans.

### WP4 — Integration/adoption decision (P2)
Evaluate the staged adoption ladder from issue #336:
1. reference/document only;
2. extract concepts and contracts;
3. adapt selected patterns in fleet-owned code;
4. import a bounded module/function with license and tests;
5. pin an upstream repository as a submodule only when the fleet must build/test that exact reviewed source.

Default to stages 1–3. No bulk vendor, no blind submodule, no giant image pull. Adopt only where the capability is distinct, source is trusted, license permits, maintenance burden is justified, and the fleet has a clear owner.

**Acceptance:** per-candidate decision (adopt/adapt/reference/defer/reject), rationale, risk and follow-up.

### WP5 — Taxonomy and QUE handoff (P2)
- Submit taxonomy additions through the existing `re-taxonomy` intake; no direct registry edits by the discovery collector.
- File QUE tasks only for work packages with clear acceptance criteria and dependencies.
- Reuse existing QUE task-plane ranking (#5283), auto-claim/resolution (#5286), QDesk intake and RFP→Delphi→DoE pipeline (#5389) where applicable.
- Do not create a second queue, scheduler, source registry, ranking algorithm or evidence ledger.

**Acceptance:** all tasks admitted through canonical QUE with tier, dependency, claim state and completion receipt; proposals remain proposals until their owning gates accept them.

## 7. Security, safety and legal controls

- **Authorization:** network assessment only against explicit owned/authorized lab targets; scope is machine-readable and checked before any packet is emitted.
- **Sandbox:** no unknown sample execution on the Termux host, developer workstation or shared CI runner. Use a separately reviewed isolation boundary.
- **Egress:** default deny. Any allowlist must be narrow, documented and testable; DNS/IP changes and redirects must not escape scope.
- **Credentials:** never commit tokens, passwords, cookies, private keys, API secrets, registry credentials or sample-bearing URLs. Store names/secret references only.
- **Samples:** no real malware corpus download, extraction or detonation in this proposal tranche. Track sample hashes and lawful provenance only if later authorized.
- **Images:** metadata-only first. Do not pull `malware-sandbox-suite` (~4.4 GB reported) or other large images onto Termux. Sandbox-API was reported ~508.7 MB; even that is not a reason to pull before source/provenance review.
- **Licensing:** no source import until license and notice obligations are established.
- **Dual use:** describe capabilities neutrally; prioritize defensive analysis, authorized testing and offline research. Any feature that materially enables unauthorized access, stealth, evasion or exploitation is a separate review gate and may be excluded.
- **Evidence:** preserve observed vs inferred vs publisher-claimed states; source evidence must have URL, timestamp and digest/commit where available.

## 8. Proposed delivery sequence and dependencies

| Sequence | Work | Priority | Dependency | Deliverable |
|---|---|---:|---|---|
| 0 | Create RFP + QUE intake record | P0 | None | This proposal, QUE issue |
| 1 | Identity + complete profile census | P0 | WP0 access | Machine-readable inventory + discrepancy report |
| 2 | Resolve Sandbox-API / Hack-Dhe-Net source | P0 | WP0 | Source provenance records |
| 3 | Static review + capability map | P1 | WP1 | Architecture, threat model, overlap matrix |
| 4 | Offline/contained verification | P1 | WP2 + security approval | Test evidence pack |
| 5 | Wider repo/image triage | P1/P2 | WP0 | Ranked candidate matrix |
| 6 | Taxonomy v2 proposal | P2 | WP2 findings | Validated `re-taxonomy` intake record |
| 7 | Adoption decision + integration tasks | P2 | WP3/WP4 | QUE-approved work items |

Parallel lanes after WP0:
- Lane A: GitHub account/repository identity census.
- Lane B: Docker Hub profile/image metadata census.
- Lane C: source-to-image provenance for Sandbox-API and Hack-Dhe-Net.
- Lane D: current taxonomy and fleet capability overlap analysis.

The lanes merge at a single evidence reconciliation checkpoint; no lane may independently promote a candidate.

## 9. RFP response format

Respondents/research agents must provide:
1. source identity and exact canonical URLs;
2. observation timestamp and evidence references;
3. repository and image digest mapping;
4. license and supply-chain status;
5. architecture/capability map;
6. threat model and abuse cases;
7. static and offline test results;
8. dynamic test plan and explicit containment prerequisites, if applicable;
9. overlap with existing fleet tools;
10. taxonomy placement recommendation;
11. adoption recommendation and maintenance estimate;
12. unresolved questions and stop conditions.

Use evidence labels consistently:
- **OBSERVED** — directly retrieved or tested.
- **PUBLISHER-CLAIMED** — description/README statement not independently tested.
- **INFERRED** — reasoned from available evidence.
- **REPRODUCED** — independently reproduced under a recorded environment.
- **CONTRADICTED** — evidence conflicts with the claim.
- **UNKNOWN** — not established.

## 10. Governance and decision rights

- RFP owner: Reverse Engineering Toolkits / Research-Astute lane.
- QUE: canonical admission, dependency ordering, prioritization, claim and execution receipts.
- Taxonomy owner: reverse-engineering-toolkits lane; registry changes only via validated intake/review.
- Security reviewer: independent review of sandbox, network scope, sample handling and supply-chain risk.
- Integration owner: named only when the task is admitted and an authorized seat claims it.
- Human owner: approves any transition from research to source import, real-sample execution, external network activity, or production adoption.

## 11. QUE admission record

The initial research-only task is filed as [QUE issue #5457](https://github.com/timerloggedout-spec/termux-monorepo/issues/5457). It uses the existing `issue-dispatch/v1` project-task route at tier 3. This filing is an intake/admission request, not a claim that the task has been ranked, claimed, executed or completed. Reconcile the actual QUE feed/claim receipts before reporting execution state.

## 12. Current decision requested

Approve WP0 and WP1 as the initial research tranche. Keep WP2–WP5 staged behind their dependencies. The RFP is not an approval to run images, detonate files, scan external networks, create credentials, or import code. Those require separate evidence and authorization.

## 13. Source register

- Docker Hub profile: https://hub.docker.com/u/credkellar
- Docker Hub Sandbox-API: https://hub.docker.com/r/credkellar/sandbox-api
- Docker Hub Hack-Dhe-Net: https://hub.docker.com/r/credkellar/hack-dhe-net
- GitHub identity linked from Docker profile: https://github.com/ddkellar01
- Claimed Sandbox-API source: https://github.com/credkellar/Sandbox-API
- Claimed Hack-Dhe-Net source: https://github.com/credkellar/Hack-Dhe-Net
- Claimed DiffRE-Lab source: https://github.com/credkellar/DiffRE-Lab
- Existing RE taxonomy: https://github.com/timerloggedout-spec/termux-monorepo/blob/master/ops/reverse_engineering/taxonomy.json
- Existing taxonomy guide: https://github.com/timerloggedout-spec/termux-monorepo/blob/master/docs/ops/REVERSE-ENGINEERING-TAXONOMY.md
- Existing adoption ladder: https://github.com/timerloggedout-spec/termux-monorepo/issues/336
- QUE task-plane prioritization: https://github.com/timerloggedout-spec/termux-monorepo/issues/5283
- QUE auto-claim/resolution: https://github.com/timerloggedout-spec/termux-monorepo/issues/5286
- QUE RFP→Delphi→DoE lifecycle: https://github.com/timerloggedout-spec/termux-monorepo/issues/5389

---
*This is a research proposal and intake artifact. It intentionally does not assert source ownership, code quality, runtime safety, or capability verification beyond the evidence stated above.*
