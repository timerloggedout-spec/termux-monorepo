# Plugin Integration Priority — 2026-09-22

This is the implementation ordering companion to `PLUGIN-CONNECTOR-CAPABILITY-MATRIX.md`.

## P0 — evidence, governance, and execution backbone

| Surface | Repository role | First integration |
|---|---|---|
| GitHub | system of record | PR/issue/check/artifact/commit evidence |
| Linear | planning/change context | bounded issue/project synchronization |
| Context7 | current dependency knowledge | version-aware implementation research |
| Firecrawl | controlled external research | reproducible page extraction/monitoring |
| OpenAI Platform | credential/setup boundary | explicit API-key setup/target documentation |
| Plugin Management | connector governance | permission/availability review |
| Neon / Supabase | durable evidence/state | structured experiment/evidence storage |
| Vercel / Render / DigitalOcean | deploy/runtime observation | build/deploy/runtime receipts |
| Sprites / Remote Desktop Commander | execution parity | isolated or authorized-machine reproduction |

**Acceptance:** each P0 integration gets an owner, contract, permission boundary, deterministic fixture, runtime evidence, and rollback/failure classification.

## P1 — high-leverage production multipliers

- MotherDuck / ClickHouse / Hex — analytical evidence plane.
- Airtable / Notion / GitBook / Mintlify — operational/documentation synchronization.
- Figma / Lucid / Magic Patterns — design-to-implementation traceability.
- Resend / Sent / Quo / Automations — controlled notification lanes.
- Consensus / Scite / SciSpace / Hugging Face / Exa / Tavily — research evidence lane.
- Replit / Lovable / Base44 / ShipStatic — rapid build/deploy reproduction surfaces.
- Cloudinary / Descript / Higgsfield — media production/evidence artifacts.

## P2 — demand-driven specialist activation

Activate only for a concrete task cohort:

Ahrefs, Klaviyo, Typeform, Tally, Todoist, Wispr Flow, Dovetail Regulatory, Midpage Legal Research, Courtroom5, Inductive, Sixtyfour Intelligence, Stocktwits, Tessie, AutoMotion, AllTrails, onX Offroad, idealista, Newegg, Trocafone, Product Hunt, Hot100 AI, Softonic, Soracom Knowledge, and other domain-specific surfaces in the matrix.

## Integration pattern

Use one adapter contract per capability boundary, not one adapter per provider method:

`provider → normalized event/input → repository-owned contract → evidence → downstream consumers`

Prefer provider-neutral schemas. Keep raw provider payloads out of canonical evidence unless explicitly required and sanitized.

## Anti-duplication rule

Before adding a connector:

1. Check the repository connector registry.
2. Check existing workflows/actions/skills.
3. Check the capability matrix.
4. Identify the current owner of the capability.
5. Prefer the existing first-party/native boundary.
6. Add a new provider only when it adds measurable capability, coverage, or evidence quality.

## Promotion loop

`OBSERVE → CHOOSE → ACT → VERIFY → RECORD → REPEAT`

For repository changes compose with:

`RECON → PLAN/MEASURE → ACT → COMMIT → WAIT → WATCH → VALIDATE → RE-FETCH → COMPARE → CLASSIFY → RECORD`

No provider becomes “production integrated” from documentation alone.
