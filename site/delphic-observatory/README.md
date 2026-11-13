# Delphic Observatory

Versioned static UI for the Delphic research and engineering observatory.

- Entry: `index.html`
- Client feed logic: `observatory.js`
- Lane presentation index: `lane-registry.json`
- Version: `VERSION.json`
- Platform contract: `docs/ops/DELPHIC-OBSERVATORY-PLATFORM-MIGRATION.md`
- Vercel project: `delphic-observatory`, Git-linked to `timerloggedout-spec/termux-monorepo`, root `site/delphic-observatory`.
- Render: proposed read-only feed service in root `render.yaml`; requires reviewed Blueprint plan before provisioning.
- GitHub: canonical source, lane architecture, schemas and workflow evidence.

The UI polls public GitHub REST endpoints. It is read-only and subject to upstream rate limits. Render aggregation is opt-in and must pass health and contract checks before use. Never infer success from missing data.

The lane registry is a presentation index; `docs/research/LANE-ARCHITECTURE.md` remains canonical.
