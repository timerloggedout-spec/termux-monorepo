# Integration Registry: termux-monorepo

**Machine-readable source:** [registry.json](registry.json)  
**Portfolio audit:** [INTEGRATION-PORTFOLIO.md](INTEGRATION-PORTFOLIO.md)  
**Adapter contract:** [ADAPTER-CONTRACT.md](ADAPTER-CONTRACT.md)  
**Event schema:** [integration-event.schema.json](schemas/integration-event.schema.json)

## Prioritized portfolio

| Integration | Priority | Session evidence | Repository adapter / integration state | Intended role |
|---|---:|---|---|---|
| Superpowers | P0 | Skill installed in this session and repository-local skill exists | Native skill implemented | Engineering methodology |
| API Impact Mapper | P0 | Connector tools exposed; a SHA-bound advisory PR lane exists | Planned; PR #4019 advisory lane remains proposed pending validation | API evolution and PR impact analysis |
| Context7 | P0 | Documentation tools exposed | Planned | Version-aware upstream documentation |
| Mintlify | P0 | Authenticated deployment and repository source verified | Native repository integration | Published developer documentation |
| Agent Ready | P0 | Live site scan completed | Planned remediation work | Agent readability and protocol audit |
| AI Task Brief Builder | P0 | Brief extraction tool exposed | Planned | Evidence-based task requirements |
| Devin AI / DEVINdeepWiki | P1 | User reports secret provisioned; no successful indexing run verified in this session | Indexing controller/workflow implemented | Private branch-level wiki indexing |
| DeepWiki.com | P1 | Public page verified; indexed source ref is stale | Structure-harvest workflow implemented; refresh campaign open | Public generated wiki discovery |
| Mermaid Chart | P1 | Account authenticated; no saved diagrams | Planned | Architecture visualization |
| Engram | P1 | Connector available; no project memory written in this audit | Planned | Opt-in long-term context |
| Context.dev | P1 | Search/scrape and usage tools available | Planned | Attributed web research and extraction |
| Consensus | P1 | Academic search/fetch tools exposed | Planned | Peer-reviewed research |
| Opscotch | P1 | Root guidance retrieved | Planned | Constrained workflow runtime |
| Temporal | P1 | Developer skill installed; server access not established | Existing adapter proposal requires reconciliation | Durable workflow orchestration |
| SiteTriage | P1 | Diagnostic tools exposed | Planned | Read-only DNS/TLS/HTTP diagnostics |
| Product Design | P1 | Skill installed; Work Mode required for full workflow | Planned | UX research, audit, prototyping |
| Flow AI Collaboration | P1 | Workspace tools exposed; no records modified | Planned | Team work-item projection |
| TinyFish | P1 | Search/fetch/browser tools exposed; no browser mutation run | Planned | Bounded browser workflows |
| Manus | P1 | Research/task tools exposed; no task dispatched | Planned | Delegated research and execution |
| Ahrefs | P2 | Tool exposed; account call returned Insufficient plan | Blocked by plan | SEO and site research |
| Soracom Knowledge | P2 | Documentation tools exposed | Planned | IoT/vendor documentation |
| Inductive Bio | P2 | Public LogD and pKa model catalog retrieved | Planned | Molecular-property research |
| Google Calendar | P2 | Calendar tools exposed; no calendar data accessed | Planned | Optional milestone scheduling |
| Precise Special Functions | P2 | High-precision computation tools exposed | Planned | Scientific computation |
| Sixtyfour Intelligence | P2 | Entity/company research tools exposed; not exercised | Planned | Scoped company/vendor intelligence |
| WorkOS | P2 | Authenticated login, but no dashboard account exists | Provisioning blocked | Identity and access management |
| Domino Data Lab | P1 | No live connector exposed; installed skill documentation exists | Planned | Reproducible ML/research operations |
| EmpirioLabs AI | P1 | Connector tools exposed in this session | Planned | Model and agent research/benchmarking |
| tldraw | P1 | Connector namespace and repository skill guidance available | Planned | Visual architecture and research collaboration |
| Cache Stats | P1 | Skill installed; no live telemetry tool exposed | Planned | Local prompt-cache/context efficiency evidence |
| Alloy | P2 | Mission/device and Mesh Storage tools exposed | Planned | Robotics/edge mission and device evidence |
| Klaviyo | P3 | Connector tools exposed in this session | Planned; deferred pending explicit consent-based use case | Consent-based research/release communications |

## Priority rationale

- **P0:** documentation integrity, version-aware source retrieval, and requirements quality compound across nearly every repository change.
- **P1:** research, orchestration, collaboration, design, and browser workflows can improve delivery when their evidence, cost, and write boundaries are explicit.
- **P2:** specialized, plan-blocked, or identity-sensitive capabilities should remain optional until a concrete consumer and validated access path exist.

## Capability vocabulary

Do not collapse these states into a single `integrated: true` flag:

- `discovered`: provider or external surface identified from evidence.
- `tool_connected_in_session`: a connector tool is exposed in this assistant session.
- `skill_installed_in_session`: a skill is available in this assistant environment.
- `not_exposed_in_session`: no matching tool was found in this session; this does not prove the provider lacks an integration.
- `repo_adapter_planned`: adapter is specified but not implemented.
- `repo_adapter_implemented`: repository code exists; this does not prove successful runtime execution.
- `validated`: end-to-end evidence confirms behavior on a pinned revision.
- `promoted`: explicitly accepted into the production lane under repository policy.

A connector being exposed does not establish account authorization, paid-plan entitlement, GitHub Actions availability, Termux availability, or production readiness.

## Registry maintenance

- Update `registry.json` and this catalog in the same PR.
- Keep session capability observations dated and qualified.
- Preserve the event schema and adapter contract as canonical shared interfaces.
- Record user-reported provisioning as reported, not verified.
- Keep secret names in approved configuration docs only; never record secret values.
- Retire entries by recording a terminal/deprecated state and migration evidence; do not erase history.
