# Delphic Observatory — versioned showcase

Static, dependency-free research showcase.

- Entry: `index.html`
- Version contract: `VERSION.json`
- Release notes: `CHANGELOG.md`
- Version policy: semantic versioning; increment patch for corrections, minor for additive research capabilities, major for incompatible contracts.
- Source PR: #5216
- Tribute presentation: `apps/tribute-dashboard/delphic-graph.html`, versioned by the shared dashboard manifest and linked from the nested algorithm-labs menu.
- `site/delphic-observatory/` remains a standalone source showcase; it is not assigned a competing repository-level GitHub Pages publisher.

The site is a read-only research projection. It must not be used as a source of live operational status or production authority.


The research artifact is versioned through `VERSION.json` and `CHANGELOG.md`. The public Tribute route is published by the existing Tribute dashboard deployment pipeline; no second Pages publisher is configured.


Latest release: **0.2.0** adds the DoE × MoneyBall configured-instance task-pool integration.
