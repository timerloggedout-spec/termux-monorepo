# Delphic Observatory — versioned showcase

Static, dependency-free research showcase.

- Entry: `index.html`
- Version contract: `VERSION.json`
- Release notes: `CHANGELOG.md`
- Version policy: semantic versioning; increment patch for corrections, minor for additive research capabilities, major for incompatible contracts.
- Source PR: #5216
- Hosting: Vercel Git-linked project / static root directory `site/delphic-observatory`.

The site is a read-only research projection. It must not be used as a source of live operational status or production authority.


The public showcase is versioned through `VERSION.json` and `CHANGELOG.md`. Deployment workflow: `.github/workflows/delphic-observatory-pages.yml`. GitHub Pages must be enabled for the repository before first publication.


Latest release: **0.2.0** adds the DoE × MoneyBall configured-instance task-pool integration.
