# Infrastructure Registry Design

**Status:** design proposal; not a runtime contract  
**Tracking:** [Issue #1654](https://github.com/timerloggedout-spec/termux-monorepo/issues/1654)  
**Proposed logical name:** Infrastructure, Dependency & Reconciliation Registry (IDRR)  
**Core invariant:** *index and reconcile existing authorities; do not replace them.*

## 1. Purpose

Provide a stable, evidence-backed relationship model for infrastructure used by `termux-monorepo`: what exists, what depends on what, which source is authoritative for each fact, what has actually been observed, how fresh that observation is, and where configuration and observed state disagree.

The registry should make the existing management cockpit more navigable and useful without becoming a new database, scheduler, poller, router, secret store, telemetry ledger, or policy engine.

This document proposes a design boundary and staged path. It does not claim that all infrastructure has been inventoried or that the schema below is already implemented.

## 2. Architectural boundary

```text
 Existing authoritative sources
 GitHub/Git/Actions · provider manifests · quota registry
 deployment/config manifests · documented APIs · approved observers
                         |
                         v
              Read-only source adapters
                         |
                         v
          Normalize identity + relationships
                         |
                         v
           Provenance-bound observations
                         |
                         v
             Reconciliation classifier
                         |
             +-----------+-----------+
             |                       |
             v                       v
       Safe cockpit view       Findings/evidence
       derived projection       with source pointers
```

**Authority rule:** source systems remain authoritative for their own facts. IDRR may index references, normalize identity, compare sources, and publish derived findings. If a projection conflicts with its source, re-fetch the source and regenerate the projection.

**No parallel control plane:** the first slice is read-only. It does not mutate provider configuration, rotate credentials, change model routing, dispatch jobs, promote deployments, or automatically repair infrastructure.

## 3. Existing contracts to compose

The initial reconnaissance identified these relevant sources. This is a starting map, not a complete infrastructure inventory.

| Concern | Existing authority / contract | IDRR responsibility |
|---|---|---|
| Provider identity and capabilities | [Provider Capability Registry](../schemas/provider-capabilities.md) | Reference canonical provider IDs; do not infer live readiness from static flags |
| Provider catalog/adapters | [Provider Batch Implementation](../ops/PROVIDER-BATCH-IMPLEMENTATION.md) | Link provider family, exact model/catalog evidence, and adapter status without inflating counts |
| Provider availability | [provider-availability workflow](../../.github/workflows/provider-availability.yml) | Consume bounded observation results; preserve credential-presence/catalog/inference distinctions |
| Quota and entitlement metadata | [Quota Registry](../ops/QUOTA-REGISTRY.md), `ops/quota/registry.json` | Link quota service IDs and observation references; do not copy private readings into public projections |
| Provider quota metadata | [Provider Quota Managers](../ops/PROVIDER-QUOTA-MANAGERS.md), `ops/quota/provider-managers.json` | Reference static family metadata and passive-parser capability; never call a parser “live validated” by existence alone |
| Routing topology | [Routing & Orchestration Map](../ops/ROUTING-ORCHESTRATION-MAP.md) | Link runtime/component relationships without becoming the routing authority |
| Execution evidence | [Evidence Projection Surface](../ops/EVIDENCE-PROJECTION-SURFACE.md) | Reference run/artifact/SHA evidence; do not create a second event ledger |
| Provenance rules | [BIUDL Execution and Provenance](../ops/BIUDL-EXECUTION-AND-PROVENANCE.md) | Preserve source identity, attribution confidence, and separate COMMITTED / EXECUTED / VALIDATED / PROMOTED states |

Before adding any new field, the implementation must check whether an existing source already owns it. Where two sources legitimately describe different aspects of the same entity, retain both facts with their scopes instead of forcing a false single winner.

## 4. Entity and identity model

Use stable, namespaced IDs that survive display-name changes. IDs are identifiers, not secrets and not claims of live existence.

| Entity type | Illustrative ID | Minimum meaning |
|---|---|---|
| Repository | `github.repo:timerloggedout-spec/termux-monorepo` | Repository identity and canonical URL |
| Workflow | `github.workflow:termux-monorepo/provider-availability.yml` | Repository-scoped workflow identity |
| Service/component | `component:termux-monorepo/model-router` | Deployable or logical component |
| Provider family | `provider:openrouter` | Provider organization/API family |
| Runtime/deployment | `runtime:mcp-hub:production` | Named runtime target, with environment scope |
| Environment | `environment:github-actions:ubuntu-latest` | Execution environment or runner class |
| Resource | `resource:github.actions.cache` | Resource/service identifier, preferably reused from its owning registry |
| Capability | `capability:provider.catalog.read` | Precisely scoped behavior, not broad “healthy” status |
| Credential reference | `credential-ref:github-actions:OPENROUTER_API_KEY` | Name/reference only; never the value |
| Evidence source | `evidence:github.actions.run` | System that can authoritatively report a defined fact |
| Observation | `observation:<source-id>:<run-id>:<attempt>` | One immutable, scoped observation |
| Finding | `finding:<rule-id>:<subject-id>:<evidence-set-id>` | Derived reconciliation result with evidence pointers |

These examples are proposed conventions, not assertions that every corresponding entity is presently configured.

### Identity rules

1. Prefer an upstream stable identifier; otherwise use a documented namespace + canonical locator.
2. Keep human-readable names, aliases, URLs, and labels as mutable attributes, not primary identity.
3. Record alias resolution explicitly. Do not merge entities solely because display names look similar.
4. Retire IDs with a status and superseding ID; do not reuse retired IDs or erase historical references.
5. Keep environment and tenant/account scope explicit where it materially changes the fact.
6. A missing entity reference is an unresolved relationship, not permission to invent a record.

## 5. Relationship model

Use a small, typed edge vocabulary. Every edge has a source, target, relationship type, provenance, and validity scope.

| Relationship | Meaning |
|---|---|
| `depends_on` | Target is a prerequisite for source |
| `runs_on` | Component/workflow executes in a runtime or environment |
| `exposes` | Component exposes an endpoint or capability |
| `observes` | Collector/evidence source can observe a named signal |
| `authenticates_via` | Component references a credential mechanism (never the credential value) |
| `produces_evidence_for` | Workflow/source emits evidence about a subject or claim |
| `consumes` | Component uses a resource, provider, artifact, or capability |
| `configured_by` | A named manifest or settings source describes desired configuration |
| `supersedes` | New identity/version replaces an older one without deleting history |

Do not create a dependency edge from mere co-occurrence. Record evidence for inferred relationships and keep inference confidence distinct from direct configuration evidence.

## 6. Authority and observation semantics

Each fact/observation must declare what kind of truth it represents:

- **configured** — declared in a manifest or settings source;
- **documented** — stated by an authoritative public contract or documentation;
- **observed** — returned by a specific source at a recorded time and scope;
- **derived** — computed from cited input records by a versioned rule;
- **asserted** — supplied by an operator or analyst and not independently verified.

An authority map must be field-specific. A source can be authoritative for configured workflow contents but not for a running deployment; a provider catalog can be authoritative for listed model IDs but not for account entitlement or successful inference.

### Observation envelope (proposed)

```json
{
  "schema": "idrr.observation.v1",
  "observation_id": "observation:github.actions.run:123456:1",
  "subject_id": "github.workflow:termux-monorepo/provider-availability.yml",
  "signal": "catalog_reachability",
  "value": "success",
  "state_class": "observed",
  "source_id": "evidence:github.actions.run",
  "source_ref": "https://github.com/timerloggedout-spec/termux-monorepo/actions/runs/123456",
  "observed_at": "2026-10-25T00:00:00Z",
  "scope": {
    "repository": "timerloggedout-spec/termux-monorepo",
    "run_id": "123456",
    "attempt": 1
  },
  "subject_version": "sha:<observed-commit-sha>",
  "confidence": "direct",
  "status": "observed"
}
```

This is illustrative only. Do not emit fabricated timestamps, run IDs, SHAs, or values in real records. The schema and exact enums require review and fixture-backed validation before implementation.

### State vocabulary

At minimum, distinguish:

- `observed`, `documented_only`, `configured_only`;
- `unknown`, `stale`, `inaccessible`, `error`;
- `conflicting`, `unsupported`, `not_applicable`.

A missing value is never silently converted to zero, healthy, absent, or success. Every freshness policy must be signal-specific and documented; no global TTL should be invented for all sources.

## 7. Preserve operational signal distinctions

These pairs are not equivalent and must not be collapsed in the registry or UI:

| Evidence A | Does not prove |
|---|---|
| Secret name is configured / credential-presence boolean is true | Authentication succeeds or the credential is valid |
| Provider catalog endpoint is reachable | Model inference works, entitlement exists, or quota remains |
| Provider adapter exists | The exact model was invoked successfully |
| Quota limit is documented | Current remaining balance or reset state |
| Workflow is queued/running | Successful completion |
| Workflow/job conclusion is success | Intended end-to-end effect is correct |
| Artifact exists | Artifact contents satisfy the consuming contract |
| Static capability flag is true | Capability is currently available in a specific account/runtime |

The existing provider-availability workflow explicitly treats credential presence and catalog reachability as separate signals and does not claim inference success. IDRR must preserve that boundary.

## 8. Credential and data-protection boundary

IDRR is not a secret scanner output dump or secret inventory of values.

Allowed only where appropriate to the consuming surface:
- credential *reference/name*;
- owning secret manager / environment scope;
- configured-presence boolean from an authorized observation;
- access-check state when the source explicitly supports it;
- timestamp, source, and scope for the observation.

Never include:
- secret values, tokens, cookies, private keys, authorization headers, or raw credential payloads;
- arbitrary provider responses or tool payloads;
- private quota balances, account-specific routing weights, or private hashes in public projections;
- hashes of low-entropy secret material that could enable verification attacks.

Sanitize at the producer boundary, use explicit allowlists, and validate public projections against a closed schema. Private observations must remain in their authorized evidence plane; a dashboard should receive a safe projection, not raw records.

## 9. Reconciliation model

A reconciliation run compares a bounded subject set across explicit authorities. It should emit findings, not silently “fix” state.

Proposed finding fields:

- `finding_id`, `rule_id`, `subject_id`;
- `classification` (e.g. `consistent`, `missing_reference`, `conflict`, `stale_observation`, `unobserved`, `unsupported_claim`);
- `severity` and rationale;
- evidence observation IDs / source refs;
- `evaluated_at`, rule version, source freshness and scope;
- recommended next action and whether that action is read-only or mutating;
- resolution state and superseding finding link, preserving history.

A “consistent” result is permitted only when all required sources for that rule are present, fresh enough for that signal, in compatible scopes, and semantically comparable. Otherwise report unknown/insufficient evidence rather than green.

The first implementation should generate read-only findings only. Remediation and runtime admission are explicitly out of scope.

## 10. Consumer projections

Different consumers require different disclosure boundaries:

1. **Private operator view:** may reference authorized internal observations, while still excluding secret material.
2. **Public dashboard/artifact:** closed allowlist of safe metadata, no private quota readings, account identifiers, raw payloads, or sensitive hashes.
3. **Machine reconciliation input:** schema-versioned normalized records with explicit source IDs and bounded fields.
4. **Evidence links:** point to immutable run/artifact/SHA references; do not copy large raw payloads into the registry.

A projection is derived and rebuildable. It is never the authoritative place to edit the underlying provider, quota, workflow, or deployment configuration.

## 11. Phased implementation

### Phase 0 — Authority inventory (this design stage)

- Inventory existing registries, manifests, workflows, schemas, and observation artifacts.
- Produce a field-level source-of-truth matrix and identify overlaps/gaps.
- Record unknown/inaccessible surfaces as such; do not fill them with guesses.

**Exit evidence:** reviewed inventory with links, authority/scope, observation method, and known gaps.

### Phase 1 — Contract and fixtures

- Define JSON Schema (or the repo's established schema format) for entity references, edges, observations, and findings.
- Use closed schemas and explicit enums; reject secret-shaped/unapproved fields.
- Add fixtures for duplicate IDs, alias ambiguity, unresolved edges, conflicting authorities, stale/missing/inaccessible evidence, scope mismatch, malformed timestamps, and private-field leakage.

**Exit evidence:** deterministic validator and focused tests; no live polling.

### Phase 2 — Read-only adapters/index

- Adapt existing registries and already-produced artifacts.
- Do not add a new polling schedule or vendor API calls for the registry.
- Preserve source SHA/version, observed time, scope, and limitations.

**Exit evidence:** deterministic normalized snapshot plus provenance receipt.

### Phase 3 — Reconciliation findings

- Compare only fields with an explicit authority rule and compatible evidence.
- Emit bounded findings and safe projections.
- Re-fetch source evidence before classifying a mismatch as resolved.

**Exit evidence:** fixtures demonstrate classifications and no false “healthy” result from missing evidence.

### Phase 4 — Cockpit/visualization

- Render entity relationships, freshness, authority, dependencies, and findings.
- Reuse the repository's existing diagram and dashboard automation where it fits.
- Keep generated visuals derived from source manifests/data and preserve machine-readable source.

**Exit evidence:** visualization links back to authoritative sources and never masks unknown/stale/conflicting states.

### Separate future decision — enforcement

Any write action, automatic repair, runtime admission, or routing influence requires its own scope, threat model, permissions, failure policy, tests, and promotion decision. It is not implicitly authorized by this design.

## 12. Initial test matrix

| Case | Expected classification / behavior |
|---|---|
| Duplicate canonical entity ID | Reject or report identity conflict; never silently merge |
| Alias points to two entities | `conflicting`; require explicit disambiguation |
| Edge references unknown target | `missing_reference`; do not synthesize target |
| Configured secret name, no authorized observation | Presence/auth state remains unknown |
| Catalog succeeds, inference untested | Catalog reachable; inference unknown |
| Observation outside freshness window | `stale_observation`, not healthy |
| Sources disagree but use different scopes | `conflicting` or `incomparable_scope`, not arbitrary precedence |
| Source unavailable | `inaccessible` / `unknown`, not absent |
| Missing quota counter | Unknown, not zero |
| Public projection includes unapproved field | Schema validation fails closed |
| Workflow passes but intended effect unverified | Workflow success observed; effect remains unverified |
| Reconciliation result is regenerated | Deterministic result for same normalized inputs and rule version |

## 13. Decisions required before implementation

- Which existing registry/manifest sources are in the initial inventory cohort?
- Which schema/validation conventions should be reused for entity/edge records?
- Which read-only artifact or generated projection should be the first consumer?
- What per-signal freshness policies already exist and can be referenced?
- Which fields may cross from private observations to public artifacts?

These are explicit design decisions, not reasons to invent defaults.

## 14. Acceptance checklist

- [ ] Field-level source-of-truth matrix reviewed.
- [ ] No duplicate poller, scheduler, database, telemetry ledger, router, or secret store introduced.
- [ ] Identity, alias, relationship, authority, freshness, scope, and state semantics specified.
- [ ] Secret and public/private projection boundaries testable.
- [ ] Closed schema and fixtures pass for known and adversarial cases.
- [ ] Read-only adapters reuse existing sources and produce provenance receipts.
- [ ] Reconciliation distinguishes unknown/conflict/stale/error from healthy.
- [ ] Current-head checks and review evidence recorded before promotion.

## Related contracts

- [Provider Capability Registry](../schemas/provider-capabilities.md)
- [Provider Batch Implementation](../ops/PROVIDER-BATCH-IMPLEMENTATION.md)
- [Provider Quota Managers](../ops/PROVIDER-QUOTA-MANAGERS.md)
- [Quota Registry](../ops/QUOTA-REGISTRY.md)
- [Routing & Orchestration Map](../ops/ROUTING-ORCHESTRATION-MAP.md)
- [Evidence Projection Surface](../ops/EVIDENCE-PROJECTION-SURFACE.md)
- [BIUDL Execution and Provenance](../ops/BIUDL-EXECUTION-AND-PROVENANCE.md)


## 15. Required capability coverage: CMDB plus reconciliation

The CMDB framing is the umbrella inventory and relationship model. “IDRR” is an optional name for the reconciliation capability, not a mandate to create a second database or competing system of record. The design must explicitly cover all five capability areas below; current coverage is architectural, not proof that each registry is implemented.

| Capability area | Required inventory / behavior | Existing evidence to reuse first | Initial gap / validation question |
|---|---|---|---|
| **Service & Dependency Catalog** | Canonical references for APIs, services, projects, deployments, workflows, data stores, owners, environments, and typed dependencies | Provider capability registry; provider batch implementation; routing/orchestration map; workflow definitions; evidence projection; repository and skill inventories | Build a field-level source-of-truth matrix and enumerate actual repository paths before asserting completeness |
| **Conflict Matrix / Resource Ownership Registry** | Identify duplicate provisioning, competing writers, ownership ambiguity, incompatible configuration, overlapping project/research lanes, shared-resource collisions, and resource contention | Workflow writer/concurrency configuration; repository/project manifests; quota/resource registries; integration mesh and campaign taxonomies; existing governance/ownership docs | Add explicit owner, writer, scope, collision key, evidence, severity, and disposition only where sources support them; report unknown ownership as unknown |
| **Service Health & SLO Registry** | Keep upstream status separate from our own reachability checks, latency, availability objectives, incident history, and last-known-good observations | Provider-availability workflow; existing SLO/freshness/incident documents where present; Actions runs, artifacts, and evidence projection | Inventory existing signals and per-signal freshness policies; do not invent SLO targets or treat a successful probe as end-to-end health |
| **Secrets & Configuration Inventory** | Record credential references/names, owning secret manager or configuration authority, requiredness, consumers, scope, rotation requirements, and verification state—never secret values | Provider credential-name metadata; quota registry/poller; workflow secret references; existing credential-name inventory and secret-safe evidence contracts | Separate declared reference, authorized presence observation, authentication test, rotation policy, and expiry evidence; absent observation is not proof of absence |
| **Configuration Reconciliation & Drift Ledger** | Compare desired configuration with scoped observed reality; preserve diffs, provenance, affected owner, severity, recommended correction, disposition, and resolution evidence | Existing reconciliation workflows, BIUDL provenance, runtime observations, manifests, generated registries, and immutable workflow/artifact references | Determine whether an existing ledger already owns each finding class; consume it rather than creating a parallel event/history store |

### Cross-cutting entity fields

Where supported by the source, normalize: stable ID; entity type; canonical locator; display name/aliases; owning team/person or unknown; environment/tenant scope; authoritative source and source version; configured/documented/observed/derived/asserted truth class; observation time and freshness policy; dependencies/consumers/writers; lifecycle state; sensitivity/projection class; and evidence references. Do not require every source to provide every field. Missing values remain explicit unknowns.

### Conflict and ownership semantics

A conflict record should identify the subject/resource, competing claims or writers, each claim's authority and scope, evidence references, impact, confidence, owner/disposition, and last checked time. Detecting two references is not by itself proof of duplicate provisioning; distinguish confirmed collisions from candidates and inferred overlap. The registry reports and links evidence; it does not terminate writers, change permissions, or delete resources in the first slice.

### Health, SLO, and last-known-good semantics

Keep these distinct: upstream-declared status; our reachability observation; authenticated request; capability-specific test; end-to-end success; and business outcome. An SLO is a policy/objective with a defined service, measurement method, window, target, exclusions, and owner—not merely a latency field. Last-known-good must carry timestamp, scope, source/version, and age, and must not mask newer failure, inaccessible source, or stale evidence.

### Credential/configuration lifecycle

Track only safe metadata: reference/name, consumer, owning configuration system, environment scope, required/optional status, rotation interval or policy reference, last rotation/verification evidence when authorized, and status such as declared, presence_observed, auth_verified, rotation_due, unknown, or inaccessible. Never ingest values, tokens, cookies, private keys, authorization headers, or hashes of low-entropy secrets. A reference existing does not prove presence, validity, successful authentication, least privilege, or rotation compliance.

## 16. Inventory sweep: repositories, skills, research lanes, and toolkits

Phase 0 must be a real repository census, not a hand-picked list of obvious infrastructure files. Start from tracked files and existing machine-readable inventories; classify each result as canonical source, generated projection, reference-only, experimental/research, external dependency, or unknown. Preserve source URL/SHA, branch/ref, observed-at time, and the limits of each sweep. Do not infer “complete” from code-search results alone.

The first sweep must include, at minimum:

- **Infrastructure and operations:** ops/, ops/quota/, provider registries/manifests, deployment/configuration files, .github/workflows/, schemas, scripts that poll or write state, freshness/SLO/incident docs, and all reconciliation/evidence workflows.
- **Skills as managed assets:** .agents/skills/**/SKILL.md, .github/skills/**/SKILL.md, SKILLS.md, CLAUDE.md, docs/ops/SKILLS-INVENTORY.md, and relevant skill manifests, pins, test/fixture directories, and source/upstream references. Check that the inventory reflects actual tracked skill directories; do not treat local mirrors as canonical where repository policy says otherwise.
- **Approxination:** .agents/skills/approxination-lane/SKILL.md, docs/ops/APPROXINATION-LANE.md, docs/evaluations/approxination/COHORT.md, and docs/proposals/active/approxination-integration/. The current lane document says the skill/cohort are live and the gitlink pin is optional backlog (APPROX-005); preserve that status and verify the exact pin/evidence rather than claiming the external benchmark is vendored.
- **AntiGravityCLI / Google Antigravity:** inspect existing tracking record [issue #1497](https://github.com/timerloggedout-spec/termux-monorepo/issues/1497), any associated PRs, source references, skills, agent/hook/permission integrations, and import/pin proposals. Treat issue text as a research proposal unless source code, merged records, or run evidence establish implementation. A code search with no result is not proof that no associated PR or external resource exists.
- **Awesome lists and external skill catalogs:** locate existing curation/ingestion tasks and canonical indexes (including any awesome-list handoff); record upstream repository, license, exact commit/tag, imported paths, provenance, trust review, and update mechanism. Do not copy entire lists or silently turn a reference into an enabled dependency.
- **Reverse-engineering toolkit:** reconcile docs/ops/WEB-ADAPTER-FOUNDRY.md, docs/ops/WEB-REVERSE-ENGINEERING-CAMPAIGN.md, ops/web_adapter_foundry/ machine registries, .agents/skills/web-adapter-foundry/SKILL.md, tests, and docs/repositories/browser-lane-imports.json. Preserve the existing taxonomy's single-primary-placement rule and cross-membership facets; do not create duplicate catalog entries for Foundry/browser-lane overlaps.
- **Other resource catalogs:** integration mesh, device pull queue, repository observatory, context-relationship indexes, tool/command registries, and other tracked resource directories discovered by the census.

### Sweep deliverable

Produce a source-backed inventory table with: canonical path/URL; resource class; entity types represented; source owner/authority; update mechanism; stable identity; relationships/dependencies; observed/configured/documented status; freshness/evidence; secrets/privacy class; overlaps/conflicts; and unresolved questions. Include excluded and inaccessible surfaces with reasons. Record counts and the exact ref/SHA for reproducibility. The first sweep is a baseline snapshot, not a claim of exhaustiveness until a tracked-file census and reconciliation against relevant indexes are complete.

## 17. Compounding implementation priorities (P0–P4)

Prioritize the lowest-risk work that improves every later phase. These are proposed sequence gates, not claims of existing implementation.

| Priority | Deliverable | Why it compounds | Exit evidence / guardrail |
|---|---|---|---|
| **P0 — Reconnaissance and authority map** | Reproducible tracked-file/source sweep; field-level source-of-truth matrix; owners, writers, scopes, existing registries, skills, and evidence lanes | Prevents duplicate registries and establishes the actual boundary | Inventory cites exact paths and source refs/SHA; overlaps and unknowns recorded; current authorities reviewed |
| **P1 — Canonical CMDB model and fixtures** | Stable entity IDs, typed relationships, ownership/scope, source provenance, sensitivity labels, closed schema, adversarial fixtures | Gives every catalog and reconciliation lane a common contract | Deterministic validation covers duplicate IDs, aliases, unresolved edges, scope mismatch, unknown owner, secret leakage, and provenance |
| **P2 — Read-only projections and conflict/drift findings** | Normalize existing manifests and observations; derive resource collision candidates and desired-vs-observed differences | Creates useful operational visibility without new writers or pollers | Rebuildable snapshot and receipt; deterministic classifications; every finding links evidence; no automatic remediation |
| **P3 — Health/SLO and credential lifecycle views** | Integrate existing probes, latency/availability evidence, incident history, last-known-good, credential references and rotation/verification metadata | Adds time-sensitive operational value once identity and provenance are stable | Per-signal freshness and SLO source defined; auth vs reachability distinguished; private/public projection tests pass |
| **P4 — Cockpit integration and governed action proposals** | Navigable graph, ownership/conflict queues, health/drift views, action recommendations and audit links; separately scoped future write workflows only if justified | Turns inventory into a management cockpit without silently becoming a control plane | Unknown/stale/conflicting states remain visible; read-only default; any mutation requires separate permissions, threat model, tests, rollback, approval, and promotion decision |

**Compounding order:** P0 → P1 → P2 → P3 → P4. Do not start with a dashboard, new poller, new database, automatic repair, or broad vendor integration before P0/P1 establish that it is necessary.

## 18. Expanded acceptance checklist

- [ ] All five capability areas in §15 are covered or explicitly marked as an evidence-backed gap.
- [ ] P0 sweep includes operations, skills, Approxination, Antigravity/issue #1497, awesome-list intake, reverse-engineering toolkit, and other discovered resource catalogs.
- [ ] Field-level source-of-truth matrix distinguishes source authority from freshness and observed state.
- [ ] Conflict findings distinguish confirmed collisions from candidates/inferences and include owner/disposition.
- [ ] Health/SLO semantics separate upstream status, reachability, capability checks, end-to-end outcomes, and last-known-good age.
- [ ] Credential/config inventory contains references and safe lifecycle metadata only, never values or secret-derived hashes.
- [ ] Drift ledger reuses existing reconciliation/evidence ownership where available and preserves history/provenance.
- [ ] P0–P4 exit evidence is defined and promotion remains separate from design/commit/check success.


## 19. P0 baseline artifact and current evidence boundary

The first tracked-path census and field-level source map are recorded in [Infrastructure CMDB P0 Inventory Baseline](INFRASTRUCTURE-CMDB-P0-INVENTORY.md). It records the master tree SHA, tracked-path counts, initial authority map, scope limits, and unresolved work. It is a baseline snapshot—not P0 completion and not a complete semantic inventory.

The baseline found existing assets for skills, provider/quota metadata, credential-name inventory, integration mesh, reconciliation workflows, evidence provenance, relationship graph, repository observatory, research resources, and the Web Adapter Foundry. These are candidates to compose, not a reason to duplicate them.

Repository archaeology also surfaced:
- [Issue #1497](https://github.com/timerloggedout-spec/termux-monorepo/issues/1497) for AntigravityCLI research/provisioning.
- [PR #1514](https://github.com/timerloggedout-spec/termux-monorepo/pull/1514), whose description calls the Antigravity pilot partial and says “DO NOT MERGE”; its base is reported as `master-staging`, so it must not be presented as a merged `master` capability without checking current PR state and refs.
- [Issue #1450](https://github.com/timerloggedout-spec/termux-monorepo/issues/1450) referencing an awesome decision-models catalog.
- [PR #1612](https://github.com/timerloggedout-spec/termux-monorepo/pull/1612), whose description records two free-LLM catalogs as discovery-only / reference-only and explicitly ineligible for runtime use.

These results demonstrate why the inventory must include issues and PRs as evidence surfaces alongside tracked paths. They do not establish that all external skill catalogs, awesome lists, or Antigravity integrations are installed, canonical, or production-ready.

**Next gate:** finish source/PR state verification and field-level authority reconciliation; only then design a canonical entity/relationship schema and fixtures. Do not implement a second ledger, new poller, or write path before the P0 exit criteria in the baseline are met.
