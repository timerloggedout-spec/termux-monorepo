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
