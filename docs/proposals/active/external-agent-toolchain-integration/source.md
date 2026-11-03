# External Agent Toolchain — RECON and Integration Design

**Tracking issue:** [#4008](https://github.com/timerloggedout-spec/termux-monorepo/issues/4008)  
**Parent architecture:** [Infrastructure Registry Design](../../../architecture/INFRASTRUCTURE-REGISTRY-DESIGN.md)  
**Related authorities:** [Integration Mesh Matrix](../../../ops/INTEGRATION-MESH-MATRIX.md), [MCP risk split](../mcp-hub-risk-split/ITEMS.md), [Model Selection Market](../model-selection-market/ITEMS.md)

## 1. Purpose

Map the requested agent/developer tools into the existing Termux Monorepo ecosystem with clear ownership, evidence, trust boundaries, and consumers. Compose existing capabilities into the management cockpit and development lifecycle without introducing a second control plane.

This proposal begins with read-only discovery and architecture. It does not claim that ChatGPT-connected tools are already wired into repository runtime, CI, or production.

## 2. Existing repository architecture to reuse

| Existing authority | What it owns | Integration rule |
|---|---|---|
| GitHub repository, branches, PRs, Actions | Source, review, workflow and CI truth | Keep code and promotion authority here |
| CMDB / IDRR design (#1654, landed #1678) | Identity, dependencies, ownership, observations, reconciliation | Index existing authorities; do not become a new database or scheduler |
| Integration Mesh Matrix + poll | GitHub app/integration census and poll evidence | Consume current evidence; distinguish app installation from credentials and runtime use |
| ICM system map | Bounded navigation to authoritative source cards | Add a focused card only through ICM maintenance |
| Skills inventory and tracked skills | Skill discovery and repository skill inventory | Reconcile rather than duplicate skills |
| Model Selection Market | Task selection/evaluation contracts and routing evidence | Do not add a competing router or mutate production weights |
| mcp-hub / hub_mcp split | Public read-only vs controlled device-mutating capability boundary | Registry discovery never grants execution or permission |
| Mintlify/docs lane | Documentation authoring/publishing environment | Publish only approved, validated docs |

The CMDB design preserves source authority and treats its projection as derived. Its P0 inventory and P1 authority/writer matrix are historical/partial evidence products, not proof of a complete live inventory. Refreshes must be bound to exact source refs and SHAs.

## 3. Tool capability and evidence matrix

This is a **session-surface inventory**, not a claim of repository deployment. Availability means a corresponding connector or skill is present in this ChatGPT work context. Repository wiring, credentials, live endpoint access, production use, and outcomes require separate evidence.

| Tool | Capability in current work context | Intended monorepo use | Evidence state | Boundary / validation |
|---|---|---|---|---|
| Context.dev | Connected research and source/page extraction tools are available | Gather source-backed integration facts and preserve URLs, timestamps, and extracted evidence | Session tool surface available; repo wiring/runtime not established | External research is input, not repository authority; cite and re-fetch decisive claims |
| Context7 | Connected library/framework documentation lookup is available | Resolve version-specific library APIs during implementation | Session tool surface available; repo wiring/runtime not established | Pin library/version and verify against project lockfiles and tests |
| Mintlify | Connected documentation platform tools are available | Maintain/publish approved developer documentation | Session tool surface available; site/repo mapping and publish permissions not established | Draft/review/build/publish are distinct states; no unreviewed publication |
| Smart Model Router | Installed skill describes a local Windows task-routing application and optional preview | Optional task-specific model recommendation for separate Codex tasks | Skill available; Windows runtime, account model availability, and repo integration not established | Does not change this conversation's model; unavailable selections must fail closed |
| HAPI MCP Registry | Connected MCP registry discovery tools are available | Discover candidate MCP servers and metadata for review | Session tool surface available; registry-to-repo synchronization not established | Discovery is not trust, permission grant, install, or admission |
| API Impact Mapper | Connected analysis tools accept supplied API-change material | Classify API changes and map consumers, tests, and docs | Session tool surface available; CI/repo automation not established | Analysis is an input; repository tests/review decide acceptance |
| Superpowers | Installed workflow skills include brainstorming and writing-plans | Standardize design, planning, implementation, review, and debugging workflow | Skills available and relevant skills read in this session; repo skill synchronization not established | Must obey repository governance, proposal scope, and human-only permission boundaries |
| Sprites | Connected isolated cloud-environment tools are available | Disposable/isolated experiments, reproducible environments, checkpoints | Session tool surface available; repo integration and deployment authority not established | Environment isolation is not authorization to access secrets or deploy |

### Evidence vocabulary

- **session-surface-available** — a connector or skill is present in this ChatGPT work context.
- **repo-wired** — tracked repository code/config explicitly consumes the tool, verified at a commit SHA.
- **authorized** — required account/installation/permission is evidenced for the exact scope; no secret value is recorded.
- **runtime-verified** — a bounded operation completed with a run ID, timestamp, source ref, and outcome.
- **outcome-verified** — intended consumer behavior was independently checked.
- **documented-only**, **blocked**, **stale**, **unknown**, and **not-applicable** remain distinct states.

No row above should be promoted beyond session-surface availability without the corresponding evidence.

## 4. Logical workflow

Task/change request → repository governance + proposal item → task classification → research / code / API-change lane → Context.dev, Context7, HAPI, or API Impact Mapper as appropriate → optional Smart Model Router + Superpowers workflow → isolated execution with Sprites where appropriate → tests + repository gates + source-owner review → GitHub PR/commit/Actions evidence → approved documentation through Mintlify/docs lane → CMDB/IDRR and ICM derived references.

This is a proposed routing model, not a current runtime topology. GitHub CI and existing repository governance remain authoritative. Tool selection and documentation retrieval cannot bypass review or validation.

## 5. Trust boundaries

1. **Discovery:** HAPI and other catalogs provide candidates and metadata only. Each server still requires source inspection, permission review, provenance, and scoped risk assessment.
2. **Research:** Context.dev and Context7 provide evidence/reference material. They do not override repository source, pinned versions, lockfiles, or test results.
3. **Model selection:** Smart Model Router is an optional local application for separately submitted tasks. It does not change the active ChatGPT conversation model or authorize paid inference.
4. **Workflow:** Superpowers improves process discipline; it does not override CLAUDE.md, proposal acceptance, consensus, or the dual gates.
5. **Execution:** Sprites can isolate experiments. Secret access, network egress, persistence, and deployment must be explicitly scoped and evidenced.
6. **Publication:** Mintlify publishing is a consequential external action; approved source, preview/build validation, target site, and publish authorization must be established independently.
7. **API impact:** API Impact Mapper is an analysis aid; its output is not a substitute for compile/test/consumer verification or reviewer acceptance.

## 6. Phasing

### Phase 0 — evidence inventory and authority mapping

Complete EATI-001 and EATI-002. Reconcile tool capabilities against existing repo surfaces and classify each claim. Do not add a new service, database, poller, workflow, or secret.

### Phase 1 — metadata contract and fixture validation

Complete EATI-003 with a schema/fixture-only design. Test duplicate identity, alias collisions, missing sources, stale observations, conflicting authority, secret-shaped fields, and unsupported readiness inference. No live polling.

### Phase 2 — separate tool lanes

Complete EATI-004 through EATI-007 as independently reviewable design packages. Runtime work requires separate accepted items and exact permission/validation contracts.

### Phase 3 — measured pilots

Only after review and acceptance, select one bounded read-only pilot. Capture input scope, exact source refs, execution evidence, output, limitations, and outcome. Compare against the existing workflow before broader adoption.

## 7. Non-goals and safety

- No new database, graph engine, scheduler, poller, router, telemetry ledger, or policy engine.
- No secret values, raw tokens, private balances, browser profiles, or reversible secret hashes in public artifacts.
- No credential provisioning/rotation, external account changes, paid inference, silent fallback, routing/admission mutation, deployment, or automatic remediation.
- No MCP server installation or exposure based solely on registry presence.
- No production readiness claim from connector availability, documentation, a successful build, or a catalog response alone.

## 8. Acceptance criteria

- Each named tool has a bounded capability, source/owner, intended consumer, trust boundary, evidence class, and verification method.
- Each fact maps to an existing authority or is explicitly marked as a proposed contract.
- Connected tools, repo wiring, authorization, runtime success, outcome success, and publication are separate.
- Initial metadata design is read-only and uses no new polling cadence or external dependency.
- Fixtures reject sensitive fields and unsupported state promotion.
- Independent runtime integrations are split into separate accepted work items before implementation.
- Future code changes cite exact item IDs and pass repository-required gates.
