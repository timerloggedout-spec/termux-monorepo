# Integration Registry — termux-monorepo

**Registry:** [registry.json](registry.json)
**Contract:** [ADAPTER-CONTRACT.md](ADAPTER-CONTRACT.md)
**Status vocabulary:** see the design document linked from [Integration Intelligence](README.md).

## Prioritized portfolio

| Integration | Priority | Current evidence | Repository adapter | Intended role |
|---|---:|---|---|---|
| Superpowers | P0 | Skill installed in current assistant session | Repository-local skill available in master | Engineering methodology |
| API Impact Mapper | P0 | Connector tools exposed in current session | Implemented (advisory; CI validation pending) | API evolution and PR impact analysis |
| Domino Data Lab | P1 | No live connector tools exposed in this session; skill docs are available in assistant environment | Planned | Reproducible ML/research operations |
| EmpirioLabs AI | P1 | Connector tools exposed in current session | Planned | Model/agent research and benchmarking |
| tldraw | P1 | Connector tools exposed in current session | Planned | Visual architecture and research collaboration |
| Cache Stats | P1 | Skill installed in current assistant environment; no live telemetry tool exposed here | Planned | Local prompt-cache/context efficiency evidence |
| Alloy | P2 | Connector tools exposed in current session | Planned | Robotics/edge mission and device evidence |
| Klaviyo | P3 | Connector tools exposed in current session | Planned | Consent-based research/release communications |
| Context.dev | P0 | Connector tools exposed in current session | Offline normalizer implemented; runtime API wiring pending | Attributed web research and evidence retrieval |
| Context7 | P0 | Documentation tools exposed in current session | Offline normalizer implemented; runtime API wiring pending | Version-aware library documentation |
| Mintlify | P1 | Documentation tools exposed in current session | Planned | Branch-scoped docs authoring and controlled publishing |
| Smart Model Router | P1 | Named by operator; no matching session tool exposed | Not started; reconcile with existing router | Model selection policy and evaluation |
| HAPI MCP Registry | P1 | Registry metadata tools exposed in current session | Offline normalizer implemented; server admission remains blocked | MCP discovery, versioning, and provenance |
| Sprites | P1 | Isolated environment tools exposed in current session | Planned | Reproducible sandboxed development and validation |

"Exposed in current session" is deliberately session-scoped. It does not establish availability in GitHub Actions, Termux, local development, another user's account, or production.

## Priority rationale

1. **P0 — Superpowers:** improves the quality and repeatability of every engineering task; must be discoverable before new provider adapters are built.
2. **P0 — API Impact Mapper:** high-leverage PR review lane for API changes, consumer compatibility, tests, and documentation. The initial adapter is advisory and SHA-bound; the ChatGPT connector is not callable directly from Actions.
3. **P1 — Domino + EmpirioLabs:** strengthen reproducible experiments and model/provider selection; integrate only through pinned manifests, evidence, and cost controls.
4. **P1 — tldraw + Cache Stats:** improve system understanding and measure agent efficiency without replacing canonical source or ATES/WTCV.
5. **P2 — Alloy:** valuable but specialized; isolate robotics/edge evidence from general software operations.
6. **P3 — Klaviyo:** defer until an explicit opt-in communications use case exists.
7. **P0 — Context.dev + Context7:** high-leverage research and implementation references; keep outputs attributed, versioned, and subordinate to repository tests.
8. **P1 — Mintlify + HAPI + Sprites:** documentation publishing, MCP discovery, and isolated execution are useful only with branch, trust, network, and promotion boundaries.
9. **P1 — Smart Model Router:** reconcile with the existing provider-routing architecture before implementation to avoid a duplicate control plane.

## Registry maintenance

- Update `registry.json` and this catalog in the same PR.
- Keep session capability observations dated and qualified.
- Never use a single `integrated: true` flag; distinguish discovery, session availability, adapter implementation, validation, and promotion.
- Add a new integration only with an owner, intended use, source evidence, security boundary, and exit criteria.
- Retire entries by recording a terminal/deprecated state and migration evidence; do not erase history.


## Agent toolchain expansion

The six additional tools and their evidence boundaries are specified in [Agent Toolchain Portfolio](AGENT-TOOLCHAIN-PORTFOLIO.md). The machine-readable entries live in `registry.json`; this document remains the canonical human-readable catalog.