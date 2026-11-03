# Integration Registry — termux-monorepo

**Registry:** [registry.json](registry.json)  
**Contract:** [ADAPTER-CONTRACT.md](ADAPTER-CONTRACT.md)  
**Status vocabulary:** see the design document linked from [Integration Intelligence](README.md).

## Prioritized portfolio

| Integration | Priority | Current evidence | Repository adapter | Intended role |
|---|---:|---|---|---|
| Superpowers | P0 | Skill installed in current assistant session | Repository-local skill being added in this branch | Engineering methodology |
| API Impact Mapper | P0 | Connector tools exposed in current session | Planned | API evolution and PR impact analysis |
| Domino Data Lab | P1 | No live connector tools exposed in this session; skill docs are available in assistant environment | Planned | Reproducible ML/research operations |
| EmpirioLabs AI | P1 | Connector tools exposed in current session | Planned | Model/agent research and benchmarking |
| tldraw | P1 | Connector tools exposed in current session | Planned | Visual architecture and research collaboration |
| Cache Stats | P1 | Skill installed in current assistant environment; no live telemetry tool exposed here | Planned | Local prompt-cache/context efficiency evidence |
| Alloy | P2 | Connector tools exposed in current session | Planned | Robotics/edge mission and device evidence |
| Klaviyo | P3 | Connector tools exposed in current session | Planned | Consent-based research/release communications |

"Exposed in current session" is deliberately session-scoped. It does not establish availability in GitHub Actions, Termux, local development, another user's account, or production.

## Priority rationale

1. **P0 — Superpowers:** improves the quality and repeatability of every engineering task; must be discoverable before new provider adapters are built.
2. **P0 — API Impact Mapper:** high-leverage PR guard for API changes, consumer compatibility, tests, and documentation.
3. **P1 — Domino + EmpirioLabs:** strengthen reproducible experiments and model/provider selection; integrate only through pinned manifests, evidence, and cost controls.
4. **P1 — tldraw + Cache Stats:** improve system understanding and measure agent efficiency without replacing canonical source or ATES/WTCV.
5. **P2 — Alloy:** valuable but specialized; isolate robotics/edge evidence from general software operations.
6. **P3 — Klaviyo:** defer until an explicit opt-in communications use case exists.

## Registry maintenance

- Update `registry.json` and this catalog in the same PR.
- Keep session capability observations dated and qualified.
- Never use a single `integrated: true` flag; distinguish discovery, session availability, adapter implementation, validation, and promotion.
- Add a new integration only with an owner, intended use, source evidence, security boundary, and exit criteria.
- Retire entries by recording a terminal/deprecated state and migration evidence; do not erase history.
