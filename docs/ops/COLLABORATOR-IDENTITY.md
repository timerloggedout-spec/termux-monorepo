# Collaborator Identity — canonical contract

**Status:** active schema and migration contract  
**Schema:** `collaborator-identity/v1`  
**Companion SSOT:** [COLLABORATOR-MONIKERS.md](COLLABORATOR-MONIKERS.md)  
**Individual records:** [`docs/collaborators/`](../collaborators/)

## 1. Identity model

A collaborator is represented by a stable collaborator ID and an individually maintained `{name}.md` profile. The profile records the collaborator's declared role, display name, moniker, source-backed platform capabilities, and independently revisioned persona and execution surfaces.

The identity chain keeps these dimensions distinct:

| Dimension | Meaning | Canonical source |
|---|---|---|
| Collaborator | Stable internal subject ID | `docs/collaborators/{name}.md` |
| Name | Human-readable collaborator name | Individual profile |
| Moniker | Display call-sign, scoped to its namespace | `COLLABORATOR-MONIKERS.md` |
| Role | Work function with its own revision | Individual profile / role registry |
| Platform trigger | Callable platform syntax, when verified | Platform workflow or adapter |
| GitHub actor | Authenticated GitHub login / App actor | GitHub event evidence |
| Git author | Commit author metadata | Commit object |
| Provider / model / adapter | Execution provenance | Run receipt / provider configuration |
| Persona | Voice, soul, identity, role instructions | Individual persona files, when present |
| Execution | Collaborator entrypoint, skills, tools, permissions | Named instruction and skill files |

Each dimension carries its own evidence and revision. A display name or moniker identifies a collaboration surface; authenticated actor and commit evidence establish authorship.

## 2. Individual collaborator records

Create one file per collaborator:

`docs/collaborators/{collaborator-name}.md`

Use a stable lowercase slug derived from the collaborator's canonical display name. Maintain each profile independently. The directory index links to the individual records; the index itself carries no duplicated profile payload.

Required profile sections:

1. **Identity** — stable ID, display name, moniker, profile revision, lifecycle state.
2. **Role** — role ID, role revision, responsibilities, boundaries.
3. **Invocation** — verified platform trigger or adapter reference, with evidence and current status.
4. **Persona** — separate paths, revisions, and SHA-256 fingerprints for `VOICE.md`, `SOUL.md`, `IDENTITY.md`, and `ROLE.md`, when those files exist.
5. **Execution** — named instruction entrypoint, skill-set revision, tool-set revision, and permission profile revision.
6. **Provenance** — source namespace, export record IDs, repository commit, and observation timestamp.
7. **Collision review** — namespace, candidate, disposition, reviewer, and review timestamp.
8. **Privacy** — classification, retention boundary, and approved public metadata.

A field with absent evidence is recorded as `NOT_ESTABLISHED` or `null` according to the schema. Profile authors preserve the difference between unknown, unavailable, retired, and explicitly withheld.

## 3. Persona and execution revisioning

Persona files are optional, independently revisioned resources:

- `VOICE.md` — communication style and expression.
- `SOUL.md` — behavioural principles and stable values.
- `IDENTITY.md` — collaborator identity and continuity.
- `ROLE.md` — role-specific responsibilities and authority.

Execution files are independently revisioned:

- `CLAUDE.md`, `GEMINI-CLI.md`, `CODEX.md`, or another collaborator-named entrypoint.
- Skill manifests and skill content.
- Tool/connector manifests and capability declarations.
- Permission profiles and workflow bindings.

A profile records a SHA-256 digest and source revision for each resource. The profile's aggregate `configuration_fingerprint` is computed from a canonical, sorted manifest of resource IDs, revisions, and digests. A resource update creates a new profile revision and a new fingerprint; historical revisions remain addressable by repository commit.

## 4. Moniker and collision policy

Monikers are display labels scoped to a declared namespace. Platform triggers, GitHub actors, provider names, model IDs, registration aliases, and anonymous profile labels remain separate identity dimensions.

Collision review records:

- `namespace`
- `candidate`
- `normalized_candidate`
- `collision_scope`
- `matched_identity_id` (opaque internal ID, where access permits)
- `disposition` (`clear`, `collision`, `reserved`, `retired`, `unresolved`)
- `evidence_ref`
- `reviewed_at`
- `reviewer_id`

The registry preserves historical monikers and graduation events. Live triggers remain attached to their verified platform adapters. Display monikers remain non-callable unless a workflow explicitly registers them as an alias.

## 5. Muse side-chat exports and discovery metadata

Muse side-chat clones enter the existing Provenance pipeline as message exports under `muse-side-chat/<date>/`. Each source record retains its source namespace, native conversation/message identifiers, timestamps, source actor label, and classifier stamps.

The privacy-safe discovery vocabulary is maintained in [COLLABORATOR-MONIKERS.md](COLLABORATOR-MONIKERS.md):

`moniker`, `collision`, `marketing`, `naming`, `anon`, `4n0nSEC`, `4n∅N`, `4n∅nSEC`, `profiles`.

Ingest stores matched terms as versioned labels. Search metadata supports retrieval, SEO taxonomy, naming analysis, and collision review. Source excerpts and profile payloads remain within the access-controlled export store. Public surfaces publish aggregate counts and opaque references.

Anonymous profile records use opaque IDs and per-source namespaces. Cross-platform linkage requires a separately authorized private mapping. Public collaborator records contain approved display metadata and source citations; they carry no joined platform-handle/profile table.

## 6. DoE / DSPy treatment identity

Every designed or observational run records the immutable collaborator configuration used by that run:

| Field | Meaning |
|---|---|
| `collaborator_id` | Stable collaborator subject |
| `moniker` | Display moniker at execution time |
| `role_id` / `role_revision` | Role and its revision |
| `profile_revision` | Collaborator profile revision |
| `persona_fingerprint` | Canonical persona resource digest |
| `execution_fingerprint` | Instruction / skills / tools / permissions digest |
| `configuration_fingerprint` | Aggregate collaborator configuration digest |
| `source_record_refs` | Opaque provenance record references |
| `model_id` / `provider` / `adapter` | Execution route evidence |

Unknown values remain null. Run records preserve the historical treatment even when the collaborator profile changes later. DSPy remains a consideration/evaluation lane and does not mutate production routing weights.

## 7. Privacy and public publishing

Public profile pages contain approved display name, moniker, role summary, public evidence links, and revision fingerprints. Private source exports contain transcript text and source-level profile metadata under the source store's access policy.

The 4n0n boundary uses independent per-platform aliases and opaque profile references. Public SEO labels are topic tags; they are not identity joins. Secret values, credentials, session stores, browser profiles, and raw private chat payloads stay outside this repository.

## 8. Migration rule

Treat every `AGENTS.md` import, alias, link, workflow input, skill reference, and contributor instruction as a migration target. Route each collaborator to its own named file. Keep repository-wide governance in the canonical root governance entry and shared process documents. Preserve historical records as historical evidence while updating all active navigation and executable imports.

The canonical collaborator documents are:

- `docs/ops/COLLABORATOR-IDENTITY.md`
- `docs/ops/COLLABORATOR-MONIKERS.md`
- `docs/collaborators/{name}.md` (one file per collaborator)
