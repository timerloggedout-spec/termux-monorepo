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


## Plugin-directory validation

The live plugin directory was checked against the P0 lanes. It confirms installed/available surfaces including GitHub, Linear, Notion, Lovable, Neon, Supabase, Airtable, Replit, Vercel, OpenAI Developers, Scite, Hugging Face, and Exa. It also exposes additional candidates not currently connected in this session, including Datadog, Railway, Asana, Webflow, ClickUp, SharePoint, and meeting/document surfaces.

**Production observability candidate:** Datadog is currently available for connection but is not connected in this session. It was surfaced for the observability lane; connecting it remains a user action. Do not mark the P0 observability lane integrated until a live authorized call and repository evidence path exist.


## Connector exclusion — MotherDuck

MotherDuck is intentionally **not active** in the current connector runtime. The connector was uninstalled after an unresolved connection issue. This is an explicit environment decision, not evidence that the provider itself is unavailable or defective.

Current state:

- **Runtime exposure:** absent
- **Authorization:** not testable
- **Repository adapter:** not required while the connector is absent
- **Fallback analytical surfaces:** ClickHouse, Hex, Neon, Supabase, Airtable
- **Re-entry condition:** reconnect/reinstall MotherDuck, then run read-only authorization and metadata probes before restoring it to an active integration lane

Do not silently substitute another provider and label it MotherDuck-compatible. Analytical workflows should target the repository-owned normalized evidence contract so the provider can be swapped without changing downstream consumers.


## Live initialization ledger — 2026-09-23

| Lane | State | Next bounded action |
|---|---|---|
| GitHub | AUTHORIZED / OBSERVED | reconcile PR #762 |
| Linear | AUTHORIZED / OBSERVED | use TER-15 as integration anchor; avoid duplicate source-of-truth state |
| Context7 / Firecrawl | EXPOSED | activate for concrete dependency/research tasks |
| OpenAI Platform / Plugin Management | EXPOSED | keep credential setup explicit; use governance probes |
| Vercel | AUTHORIZED / OBSERVED | preserve deployment evidence; investigate rate limits separately |
| Render | AUTHORIZED / OBSERVED | use existing services; no duplicates |
| DigitalOcean | AUTHORIZED / BLOCKED | maintenance before new Droplets |
| Sprites | AUTHORIZED / OBSERVED | create only for concrete isolated execution |
| Neon | EXPOSED / UNRESOLVED | resolve project ID, then read-only metadata probe |
| Supabase | AUTHORIZED / OBSERVED | no project creation without concrete data requirement |
| Airtable | AUTHORIZED / OBSERVED | structured evidence experiments only |
| Hex | EXPOSED / BLOCKED | use authorized analytical alternatives |
| Figma | AUTHORIZED / OBSERVED | read/inspection unless write entitlement established |
| Hugging Face | AUTHORIZED / OBSERVED | research/model retrieval when task-relevant |
| Lovable / Replit | AUTHORIZED / OBSERVED | bounded reproduction/build; GitHub remains canonical |
| MotherDuck | EXCLUDED | no silent substitution |
