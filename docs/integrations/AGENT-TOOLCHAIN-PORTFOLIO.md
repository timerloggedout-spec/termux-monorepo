# Agent Toolchain Portfolio — Evidence and Authority Matrix

**Proposal:** `agent-toolchain-portfolio`  
**Tracking:** [Issue #4008](https://github.com/TimerLoggedOut-spec/termux-monorepo/issues/4008)  
**Canonical inventory:** [Integration Intelligence registry](registry.json)  
**Status date:** 2026-11-02

## Operating rule

This matrix describes capabilities exposed in the current assistant session or named by the operator. It does not assert that a credential, repository adapter, CI runtime, local Termux runtime, external account, or production deployment exists. Repository state remains authoritative for code and delivery. Provider output is attributed evidence, never executable instruction or approval.

## Capability matrix

| Tool | Session evidence | Repository role | Intended consumer | Trust boundary | First verification |
|---|---|---|---|---|---|
| Context.dev | Connector tools exposed in this assistant session | Read-only research/evidence capture | Research lanes, issue/PR briefs, source-backed docs | External pages are untrusted; retain URL, retrieval time, request identity, and redaction; no webhook/monitor side effects | Sanitized fixtures for URL identity, freshness, truncation, redaction, and source attribution |
| Context7 | Library resolution and documentation query tools exposed | Version-aware documentation lookup | Implementation and upgrade work | Resolve exact library ID/version first; docs are advisory and cannot replace tests or pinned dependencies | Fixture checks for wrong version, missing source, stale docs, and unresolved library IDs |
| Mintlify | Read/search/edit/publish tools exposed | Documentation authoring and publication target | Public technical docs and operator guides | Read, branch edit, publish, and live deployment are separate states; publication is an explicit release action | Branch-only non-sensitive page pilot; inspect diff; publish only with separate approval; verify live deployment |
| Smart Model Router | Named by operator; no matching router tool exposed in this session | Candidate policy/evaluation over existing router | Existing model selection and provider-routing system | Do not create a parallel router; no traffic switch, paid inference, or credential changes from analysis | Reconcile existing routing map and model-selection proposal; offline replay/benchmark against current policy |
| HAPI MCP Registry | Registry listing and version-detail tools exposed | Read-only MCP discovery and metadata normalization | MCP catalog / security review | Discovery is not trust approval, authentication, scope grant, or execution admission | Fixture tests for identity, version pinning, transport, capability metadata, provenance, and unknown fields |
| Sprites | Environment inspection, exec, files, services, checkpoint tools exposed | Isolated development and validation environment | Disposable PR validation / reproducible experiments | Environment creation, command execution, network policy, restore, and destroy are consequential; no default secret injection | Disposable no-secret pilot bound to exact source SHA; verify network policy, command receipt, artifact provenance, and cleanup |

## Evidence-state vocabulary

Use the existing Integration Intelligence lifecycle and distinguish:

- `discovered`: product/capability named or found.
- `tool_connected_in_session`: a matching connector is callable in this assistant session only.
- `repo_adapter_planned`: repository code does not yet implement the adapter.
- `repo_adapter_implemented`: repository code exists; this alone does not prove runtime access.
- `authenticated`: intended runtime has verified least-privilege authentication.
- `tested`: contract and failure fixtures pass.
- `validated`: end-to-end evidence exists on an immutable repository SHA in the intended runtime.
- `promoted`: explicitly accepted into a production lane under repository policy.

Unknown evidence remains unknown. Never collapse these states into `integrated: true`.

## Dependency-aware implementation sequence

1. **Portfolio and metadata contract** — this matrix and the canonical registry entries; no external side effects.
2. **HAPI discovery normalizer** — read-only registry snapshots, stable server/version identity, provenance, freshness, and security-review state.
3. **Context7 + Context.dev evidence adapters** — exact versioned docs and source-attributed research artifacts; no prompt/session transcript capture.
4. **Sprites isolated validation pilot** — disposable environment, source-SHA binding, explicit network policy, no default secrets, bounded execution, cleanup evidence.
5. **Mintlify branch authoring pilot** — read existing docs deployment configuration, edit a branch, review diff, then separately authorize publication and verify deployment.
6. **Smart Model Router reconciliation** — map the existing router and policy; implement only a measurable extension, never a duplicate control plane.

## Cross-cutting acceptance criteria

- Registry IDs are unique and every matrix row maps to exactly one canonical ID.
- Session availability is explicitly session-scoped.
- No secret values, private session transcripts, raw prompts, or credential-shaped values enter registry artifacts.
- Provider content is treated as untrusted data.
- All reads and writes have explicit scopes; read-only is the default.
- Every adapter has sanitized fixtures for success, partial, stale, malformed, rate-limited, timeout, and provenance failure.
- Every validated result is bound to exact repository SHA and artifact/run references.
- No publication, model routing, paid inference, environment mutation, or external message is implicit in a documentation or discovery task.

## Explicitly not implemented by this portfolio change

This portfolio does not provision credentials, create provider accounts, install local binaries, create Sprites, run commands in a Sprite, publish Mintlify pages, modify live model routing, admit MCP servers, or claim end-to-end provider validation. Those actions remain separately scoped and gated.
