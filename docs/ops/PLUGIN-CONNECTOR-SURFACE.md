# Plugin Connector Surface — Live Handoff Registry

**Repository:** `timerloggedout-spec/termux-monorepo`  
**Branch:** `ops/plugin-connector-parity-20260922`  
**Snapshot:** 2026-09-23  
**Live surface:** **86 providers / 1,960 MCP connector actions**

## Who to ask

**Primary:** Plugin Connector Steward.  
**Repository coordination:** GitHub PR/issue in `timerloggedout-spec/termux-monorepo`.  
**Planning/integration anchor:** Linear **TER-15**.  
**Canonical skill:** `.agents/skills/plugin-connector-parity/SKILL.md`.  
**Capability matrix:** `docs/ops/PLUGIN-CONNECTOR-CAPABILITY-MATRIX.md`.  
**Priority/initialization ledger:** `docs/ops/PLUGIN-INTEGRATION-PRIORITY.md`.

When asking for connector work, include:

1. provider;
2. exact capability/action;
3. intended repository workflow;
4. required authorization/plan;
5. whether the operation is read-only or mutating;
6. expected evidence/receipt;
7. rollback or failure condition.

## Status semantics

- **EXPOSED** — the connector is callable in this runtime.
- **AUTHORIZED/OBSERVED** — live provider calls succeeded and evidence was observed.
- **EXPOSED/UNRESOLVED** — callable surface exists, but required resource/account binding is not resolved.
- **EXPOSED/BLOCKED** — callable surface exists but a provider-side entitlement/constraint prevents use.
- **EXCLUDED** — intentionally not active in this runtime.

Exposure is not integration. A provider becomes repository-integrated only after an explicit contract, workflow/skill binding, validation evidence, and recorded ownership exist.

## Provider registry

| Provider | Actions | State | Initialization / validation |
|---|---:|---|---|
| `AI_Task_Brief_Builder` | 3 | EXPOSED | Plugin Connector Steward → repo maintainers; use TER-15 for coordination |
| `API_Impact_Mapper` | 3 | EXPOSED | Plugin Connector Steward → repo maintainers; use TER-15 for coordination |
| `Agent_Ready` | 2 | EXPOSED | Plugin Connector Steward → repo maintainers; use TER-15 for coordination |
| `Ahrefs` | 135 | EXPOSED | Plugin Connector Steward → repo maintainers; use TER-15 for coordination |
| `Airtable` | 47 | AUTHORIZED/OBSERVED | Plugin Connector Steward → repo maintainers; use TER-15 for coordination |
| `AllTrails` | 6 | EXPOSED | Plugin Connector Steward → repo maintainers; use TER-15 for coordination |
| `All_Tide_Times` | 1 | EXPOSED | Plugin Connector Steward → repo maintainers; use TER-15 for coordination |
| `Alloy` | 20 | EXPOSED | Plugin Connector Steward → repo maintainers; use TER-15 for coordination |
| `AnyBarcodeScanner` | 1 | EXPOSED | Plugin Connector Steward → repo maintainers; use TER-15 for coordination |
| `AutoMotion` | 3 | EXPOSED | Plugin Connector Steward → repo maintainers; use TER-15 for coordination |
| `Automations` | 7 | EXPOSED | Plugin Connector Steward → repo maintainers; use TER-15 for coordination |
| `Base44` | 19 | AUTHORIZED/OBSERVED | Plugin Connector Steward → repo maintainers; use TER-15 for coordination |
| `ClickHouse` | 17 | EXPOSED | Plugin Connector Steward → repo maintainers; use TER-15 for coordination |
| `Cloudinary` | 23 | EXPOSED | Plugin Connector Steward → repo maintainers; use TER-15 for coordination |
| `Consensus` | 2 | EXPOSED | Plugin Connector Steward → repo maintainers; use TER-15 for coordination |
| `Context7` | 2 | EXPOSED | Plugin Connector Steward → repo maintainers; use TER-15 for coordination |
| `Context_dev` | 37 | EXPOSED | Plugin Connector Steward → repo maintainers; use TER-15 for coordination |
| `Convex` | 4 | EXPOSED | Plugin Connector Steward → repo maintainers; use TER-15 for coordination |
| `Courtroom5` | 3 | EXPOSED | Plugin Connector Steward → repo maintainers; use TER-15 for coordination |
| `Descript` | 8 | EXPOSED | Plugin Connector Steward → repo maintainers; use TER-15 for coordination |
| `DigitalOcean` | 54 | AUTHORIZED/BLOCKED | Plugin Connector Steward → repo maintainers; use TER-15 for coordination |
| `Dovetail_Regulatory` | 37 | EXPOSED | Plugin Connector Steward → repo maintainers; use TER-15 for coordination |
| `Dropbox` | 24 | EXPOSED | Plugin Connector Steward → repo maintainers; use TER-15 for coordination |
| `Endurance_Planner` | 15 | EXPOSED | Plugin Connector Steward → repo maintainers; use TER-15 for coordination |
| `Engram` | 8 | EXPOSED | Plugin Connector Steward → repo maintainers; use TER-15 for coordination |
| `Exa` | 2 | EXPOSED | Plugin Connector Steward → repo maintainers; use TER-15 for coordination |
| `Figma` | 41 | AUTHORIZED/OBSERVED | Plugin Connector Steward → repo maintainers; use TER-15 for coordination |
| `Firecrawl` | 25 | EXPOSED | Plugin Connector Steward → repo maintainers; use TER-15 for coordination |
| `GitBook` | 9 | EXPOSED | Plugin Connector Steward → repo maintainers; use TER-15 for coordination |
| `GitHub` | 89 | AUTHORIZED/OBSERVED | Plugin Connector Steward → repo maintainers; use TER-15 for coordination |
| `Graffiticode` | 7 | EXPOSED | Plugin Connector Steward → repo maintainers; use TER-15 for coordination |
| `Grow_My_Website` | 3 | EXPOSED | Plugin Connector Steward → repo maintainers; use TER-15 for coordination |
| `HAPI_MCP_Registry` | 3 | EXPOSED | Plugin Connector Steward → repo maintainers; use TER-15 for coordination |
| `Hercules` | 7 | EXPOSED | Plugin Connector Steward → repo maintainers; use TER-15 for coordination |
| `Hex` | 4 | EXPOSED/BLOCKED | Plugin Connector Steward → repo maintainers; use TER-15 for coordination |
| `Higgsfield` | 77 | EXPOSED | Plugin Connector Steward → repo maintainers; use TER-15 for coordination |
| `Hot100_ai` | 6 | EXPOSED | Plugin Connector Steward → repo maintainers; use TER-15 for coordination |
| `Hugging_Face` | 9 | AUTHORIZED/OBSERVED | Plugin Connector Steward → repo maintainers; use TER-15 for coordination |
| `Inductive` | 2 | EXPOSED | Plugin Connector Steward → repo maintainers; use TER-15 for coordination |
| `Klaviyo` | 264 | EXPOSED | Plugin Connector Steward → repo maintainers; use TER-15 for coordination |
| `Linear` | 74 | AUTHORIZED/OBSERVED | Plugin Connector Steward → repo maintainers; use TER-15 for coordination |
| `LinkedIn` | 1 | EXPOSED | Plugin Connector Steward → repo maintainers; use TER-15 for coordination |
| `Lovable` | 40 | AUTHORIZED/OBSERVED | Plugin Connector Steward → repo maintainers; use TER-15 for coordination |
| `Lucid` | 35 | EXPOSED | Plugin Connector Steward → repo maintainers; use TER-15 for coordination |
| `Magic_Patterns` | 23 | EXPOSED | Plugin Connector Steward → repo maintainers; use TER-15 for coordination |
| `Mermaid_Chart` | 2 | EXPOSED | Plugin Connector Steward → repo maintainers; use TER-15 for coordination |
| `Midpage_Legal_Research` | 5 | EXPOSED | Plugin Connector Steward → repo maintainers; use TER-15 for coordination |
| `Mintlify_MCP` | 19 | EXPOSED | Plugin Connector Steward → repo maintainers; use TER-15 for coordination |
| `Mobbin` | 3 | EXPOSED | Plugin Connector Steward → repo maintainers; use TER-15 for coordination |
| `Neon` | 106 | EXPOSED/UNRESOLVED | Plugin Connector Steward → repo maintainers; use TER-15 for coordination |
| `Newegg` | 6 | EXPOSED | Plugin Connector Steward → repo maintainers; use TER-15 for coordination |
| `Notion` | 25 | EXPOSED | Plugin Connector Steward → repo maintainers; use TER-15 for coordination |
| `OpenAI_Platform` | 3 | EXPOSED | Plugin Connector Steward → repo maintainers; use TER-15 for coordination |
| `Opscotch` | 44 | EXPOSED | Plugin Connector Steward → repo maintainers; use TER-15 for coordination |
| `Parallel_Search` | 2 | EXPOSED | Plugin Connector Steward → repo maintainers; use TER-15 for coordination |
| `Plugin_Management` | 6 | EXPOSED | Plugin Connector Steward → repo maintainers; use TER-15 for coordination |
| `Product_Hunt` | 7 | EXPOSED | Plugin Connector Steward → repo maintainers; use TER-15 for coordination |
| `Promocodes_com` | 2 | EXPOSED | Plugin Connector Steward → repo maintainers; use TER-15 for coordination |
| `Quo` | 15 | EXPOSED | Plugin Connector Steward → repo maintainers; use TER-15 for coordination |
| `Real_Random` | 2 | EXPOSED | Plugin Connector Steward → repo maintainers; use TER-15 for coordination |
| `Render` | 22 | AUTHORIZED/OBSERVED | Plugin Connector Steward → repo maintainers; use TER-15 for coordination |
| `Replit` | 8 | AUTHORIZED/OBSERVED | Plugin Connector Steward → repo maintainers; use TER-15 for coordination |
| `Resend` | 106 | EXPOSED | Plugin Connector Steward → repo maintainers; use TER-15 for coordination |
| `SciSpace` | 2 | EXPOSED | Plugin Connector Steward → repo maintainers; use TER-15 for coordination |
| `Scite` | 34 | EXPOSED | Plugin Connector Steward → repo maintainers; use TER-15 for coordination |
| `Sent` | 19 | EXPOSED | Plugin Connector Steward → repo maintainers; use TER-15 for coordination |
| `ShipStatic` | 15 | EXPOSED | Plugin Connector Steward → repo maintainers; use TER-15 for coordination |
| `SiteTriage` | 7 | EXPOSED | Plugin Connector Steward → repo maintainers; use TER-15 for coordination |
| `Sixtyfour_Intelligence` | 26 | EXPOSED | Plugin Connector Steward → repo maintainers; use TER-15 for coordination |
| `Softonic` | 5 | EXPOSED | Plugin Connector Steward → repo maintainers; use TER-15 for coordination |
| `Soracom_Knowledge` | 3 | EXPOSED | Plugin Connector Steward → repo maintainers; use TER-15 for coordination |
| `Sprites` | 24 | AUTHORIZED/OBSERVED | Plugin Connector Steward → repo maintainers; use TER-15 for coordination |
| `Stocktwits` | 13 | EXPOSED | Plugin Connector Steward → repo maintainers; use TER-15 for coordination |
| `Supabase` | 28 | AUTHORIZED/OBSERVED | Plugin Connector Steward → repo maintainers; use TER-15 for coordination |
| `Tally` | 25 | EXPOSED | Plugin Connector Steward → repo maintainers; use TER-15 for coordination |
| `Tavily` | 5 | EXPOSED | Plugin Connector Steward → repo maintainers; use TER-15 for coordination |
| `Tessie` | 8 | EXPOSED | Plugin Connector Steward → repo maintainers; use TER-15 for coordination |
| `Todoist` | 47 | EXPOSED | Plugin Connector Steward → repo maintainers; use TER-15 for coordination |
| `Trocafone` | 2 | EXPOSED | Plugin Connector Steward → repo maintainers; use TER-15 for coordination |
| `Typeform` | 61 | EXPOSED | Plugin Connector Steward → repo maintainers; use TER-15 for coordination |
| `Vercel` | 24 | AUTHORIZED/OBSERVED | Plugin Connector Steward → repo maintainers; use TER-15 for coordination |
| `Wispr_Flow` | 14 | EXPOSED | Plugin Connector Steward → repo maintainers; use TER-15 for coordination |
| `Wolfram` | 3 | EXPOSED | Plugin Connector Steward → repo maintainers; use TER-15 for coordination |
| `WorkOS` | 4 | EXPOSED | Plugin Connector Steward → repo maintainers; use TER-15 for coordination |
| `idealista` | 4 | EXPOSED | Plugin Connector Steward → repo maintainers; use TER-15 for coordination |
| `onX_Offroad` | 2 | EXPOSED | Plugin Connector Steward → repo maintainers; use TER-15 for coordination |

## Current blockers / boundaries

- **MotherDuck:** intentionally excluded after uninstall; do not claim it is active or silently relabel another provider as MotherDuck.
- **Hex:** currently blocked by Team/Enterprise MCP entitlement.
- **Neon:** connector exists, but project binding still needs a project ID.
- **DigitalOcean:** authenticated, but the account reports its Droplet ceiling is reached.
- **Figma:** authenticated on a Starter/View seat; write/read assumptions must respect the seat/plan limits. fileciteturn111file0L5-L8
- **Other EXPOSED providers:** require a live provider call before being promoted to AUTHORIZED/OBSERVED.

## Provider action samples

The machine-readable companion contains up to 12 live action names per provider: `.github/connectors/runtime-surface.json`.

## Integration contract

Every provider that becomes active for repository automation follows:

`EXPOSED → CONNECTED → AUTHORIZED → OBSERVED → ADAPTED → INTEGRATED → VALIDATED`

and:

`RECON → PLAN/MEASURE → ACT → COMMIT → WAIT → WATCH → VALIDATE → RE-FETCH → COMPARE → CLASSIFY → RECORD`

Mutating operations require explicit task intent and should be bounded, reversible where practical, and accompanied by a receipt.

## No dead-end handoffs

A collaborator should never need to guess where connector work belongs:

- **“Can this connector do X?”** → Plugin Connector Steward + this registry.
- **“Is it authorized?”** → run/inspect the provider's live identity/metadata operation.
- **“How should it integrate?”** → capability matrix + priority ledger + TER-15.
- **“Did the repository change?”** → GitHub commit/PR/check evidence.
- **“Can it ship?”** → repository gates + provider-specific validation receipt.
