# Plugin / Connector Capability Matrix

**Snapshot:** 2026-09-22 (ChatGPT tool surface observed in this stewardship session)  
**Repository:** `timerloggedout-spec/termux-monorepo`  
**Purpose:** distinguish *currently exposed* connector/tool capacity from *repository-integrated* capability, and preserve a repeatable parity review.

> **Important:** tool exposure is not proof of account authentication, billing, plan entitlement, provider-side permission, or successful runtime execution. The matrix records what this session can invoke; repository integration must separately record adapter status and runtime evidence.

## 1. Current surface totals

| Surface | Count | Meaning |
|---|---:|---|
| Connector providers | 88 | Distinct `mcp__…` provider surfaces exposed in this session |
| Connector tools | 2,042 | Individual connector actions exposed in this session |
| Total callable tools | 2,052 | Connector + native/internal callable tools visible to the orchestration runtime |
| GitHub installation | verified | `timerloggedout-spec`; repository selection = all |
| GitHub repository permission | admin/maintain/push/etc. | Current connector reports admin-capable access to `timerloggedout-spec/termux-monorepo` |
| GitHub app permission | elevated | App-specific setting reports “Allow all actions” |

**Safety interpretation:** “available” means exposed to the runtime. “connected” means the provider connector is present. “authenticated/authorized” must be established by a provider call. “integrated” means a repository contract, workflow, adapter, test, and evidence path exist.

## 2. Provider inventory

Tool counts are the number of currently exposed actions for the provider in this snapshot.

### Repository / engineering / deployment

| Provider | Tools | Primary capacity |
|---|---:|---|
| GitHub | 89 | repos, files, branches, commits, PRs, reviews, issues, checks, artifacts, workflow jobs/logs |
| Linear | 74 | issues, projects, docs, cycles, releases, comments, reviews, initiatives, customers |
| DigitalOcean | 54 | cloud workspace / droplet lifecycle and inspection |
| Lovable | 40 | app creation, inspection, updates |
| Vercel | 24 | projects, deployments, logs, agent runs, toolbar |
| Render | 22 | services, deploys, logs, metrics, Postgres |
| Base44 | 19 | app/entity/file operations and connectors |
| ShipStatic | 15 | static deployments/domains/DNS |
| GitBook | 9 | documentation spaces/content |
| Replit | 8 | app create/search/inspect/update/publish |
| Hercules | 7 | app/website building |
| Automations | 7 | scheduled/conditional automation |
| Convex | 4 | backend/project operations |
| WorkOS | 4 | workspace/identity operations |
| OpenAI Platform | 3 | API-key setup/targets |
| Graffiticode | 7 | verified task-language operations |
| HAPI MCP Registry | 3 | MCP server discovery/registry |
| Sprites | 24 | isolated cloud compute, files, services, checkpoints |
| Remote Desktop Commander | 30 | authorized-machine files, processes, sessions |
| Context7 | 2 | current library/documentation retrieval |
| Opscotch | 44 | Opscotch knowledge/authoring |
| Mintlify MCP | 19 | documentation search/read/edit/ship |

### Data / analytics / storage

| Provider | Tools | Primary capacity |
|---|---:|---|
| Neon | 113 | Postgres projects, branches, SQL, schema, migrations, diagnostics |
| Airtable | 47 | bases, tables, records, automations, interfaces |
| MotherDuck | 41 | data warehouse/query/visualization |
| Supabase | 28 | Postgres, auth, storage, edge functions, logs |
| ClickHouse | 17 | Cloud services, schemas, SQL, diagnostics |
| Hex | 4 | projects/threads/analysis surface |
| Wolfram | 3 | rigorous computation / Wolfram Language |
| Cloudinary | 23 | media assets, transformations, search, relations |
| Alloy | 20 | mission/device/data-lake analysis |

### Research / web / knowledge

| Provider | Tools | Primary capacity |
|---|---:|---|
| Ahrefs | 135 | SEO, backlinks, rankings, brand/AI visibility, site audit |
| Firecrawl | 25 | scrape/map/crawl/search/research/developer search/monitor |
| Scite | 34 | literature, citations, patents, trials, regulatory/clinical evidence |
| Context_dev | 37 | live web/files and agent-ready retrieval |
| Hugging Face | 9 | models, datasets, papers, Spaces, jobs, docs |
| Tavily | 6 | web search/extract/crawl/map/research |
| Product Hunt | 7 | product/startup discovery |
| Hot100 AI | 6 | AI project/tool/agent discovery |
| Consensus | 2 | peer-reviewed literature search/fetch |
| SciSpace | 2 | academic paper discovery/review |
| Exa | 2 | AI-native web search/fetch |
| Parallel Search | 2 | web search/extraction |
| Agent Ready | 2 | agent/crawler readability scans |
| Grow My Website | 3 | SEO scans/growth/fixes |
| SiteTriage | 7 | DNS/TLS/edge diagnostics |
| Softonic | 5 | software discovery |
| Soracom Knowledge | 3 | official Soracom documentation/API lookup |
| LinkedIn | 1 | professional lookup |
| Midpage Legal Research | 5 | legal research |
| Courtroom5 | 3 | self-represented civil litigation support |
| Dovetail Regulatory | 37 | medtech/regulatory workspace |
| Inductive | 2 | ADMET prediction |
| Sixtyfour Intelligence | 26 | people/company investigation and relationship/risk signals |

### Communication / work management / forms

| Provider | Tools | Primary capacity |
|---|---:|---|
| Klaviyo | 264 | marketing, profiles, events, campaigns, flows, agents |
| Resend | 106 | transactional email, domains, templates, broadcasts, webhooks |
| Typeform | 64 | forms, contacts, analysis, automations |
| Todoist | 47 | tasks, projects, comments, reminders, workspaces, analytics |
| Notion | 25 | search, pages, databases, comments, files |
| Tally | 25 | form creation/management |
| Dropbox | 24 | files, folders, sharing, revisions, upload/download |
| Sent | 19 | SMS/WhatsApp/RCS, contacts, templates, delivery |
| Quo | 15 | business phone/communications |
| Wispr Flow | 14 | meetings, transcripts, notes, calendar |
| Engram | 8 | long-term memory/search |
| Promocodes.com | 2 | promo-code discovery |
| Real Random | 2 | randomization/shuffling |

### Design / media / creative

| Provider | Tools | Primary capacity |
|---|---:|---|
| Higgsfield | 77 | image/video/creative production |
| Figma | 41 | design files/workflows |
| Lucid | 35 | diagrams/visual collaboration |
| Magic Patterns | 23 | UI/product prototyping |
| Descript | 8 | video/audio editing |
| Mobbin | 3 | UI/UX reference search |

### Specialized operational / commerce / field surfaces

| Provider | Tools | Primary capacity |
|---|---:|---|
| AllTrails | 6 | hiking discovery |
| All Tide Times | 1 | tide information |
| onX Offroad | 2 | off-road trail discovery |
| Endurance Planner | 15 | endurance training analysis |
| Tessie | 8 | Tesla access/control |
| AutoMotion | 3 | automotive diagnosis/service |
| AnyBarcodeScanner | 1 | barcode/product inspection |
| Newegg | 6 | product discovery |
| Trocafone | 2 | pre-owned technology |
| idealista | 4 | property listings |
| Stocktwits | 13 | market/community data |
| Promocodes.com | 2 | shopping promo discovery |

## 3. Native/non-connector surfaces

The runtime also exposes first-class capabilities that are not provider connectors:

- Web search/open/click/find/screenshot and URL navigation.
- Image search and image generation/editing.
- Product, business, restaurant availability, and structured local search.
- GenUI widgets for sports, weather, currency, unit conversion, and time.
- Python analysis and user-visible file/chart generation.
- Container execution and file inspection.
- Safety/account-control surfaces where applicable.
- Project Files search/read/materialize and skill discovery/read.

These are **orchestration primitives**, not repository providers.

## 4. Capability-state model

Use these states instead of a single “integrated” boolean:

`EXPOSED → CONNECTED → AUTHORIZED → OBSERVED → ADAPTED → INTEGRATED → VALIDATED`

- **EXPOSED:** tool/provider exists in the current runtime.
- **CONNECTED:** connector is installed/available.
- **AUTHORIZED:** a live provider operation succeeds under the permitted account/scope.
- **OBSERVED:** runtime behavior/evidence has been captured.
- **ADAPTED:** repository adapter/contract exists.
- **INTEGRATED:** adapter is wired into a real workflow or skill.
- **VALIDATED:** tests + live evidence support the stated contract.

Never promote a state merely because the previous state is present.

## 5. Repository parity boundary

Current repository-native integration registry is intentionally narrower than this live surface. `.github/connectors/integrations.yaml` currently records CodeRabbit, Jules, Devin, Linear, Vercel, and peer-reviewer surfaces. This matrix therefore acts as a **capability inventory**, not a claim that all 88 providers are already integrated.

The existing repository governance also says to reuse first-party/native capabilities before adding overlapping marketplace wrappers and to keep connector capability changes bounded by an ownership and compatibility review.

## 6. Highest-leverage production lanes

1. **GitHub + Linear + Context7 + Firecrawl** — evidence-backed engineering/research loop.
2. **GitHub + Vercel + Render/DigitalOcean + Replit/Lovable** — build → deploy → observe.
3. **Neon/Supabase + MotherDuck/ClickHouse + Hex** — durable data/evidence plane.
4. **OpenAI Platform + Plugin Management** — credential/setup and connector governance.
5. **Figma/Lucid/Magic Patterns + GitHub** — design-to-implementation traceability.
6. **Notion/GitBook/Mintlify + GitHub** — documentation synchronization.
7. **Resend/Sent/Quo + Automations** — controlled external notification lanes.
8. **Consensus/Scite/SciSpace/Hugging Face + Firecrawl/Exa/Tavily** — research/evidence lane.
9. **Sprites/Remote Desktop/DigitalOcean** — reproducible execution and authorized-machine operations.
10. **Domain-specific connectors** — activate only when a task cohort demonstrates demand.

## 7. Review cadence

Repeat this review whenever the connector surface materially changes, and at least once per stewardship cycle that depends on external tools.

Required evidence per review:

- snapshot timestamp;
- provider/tool count;
- connected/authenticated checks for providers actually used;
- repository registry delta;
- new/removed capabilities;
- security/permission delta;
- duplicate/overlapping capability candidates;
- tests and runtime evidence;
- promotion/rollback state.

The review itself is **read-only by default**. Repository changes are an explicit apply action.

## Source notes

This snapshot incorporates the uploaded stewardship/relationship/loop skill material and the live tool surface observed during the 2026-09-22 stewardship session. The attached `termux-mcp-project-steward` skill explicitly requires read-only preflight by default and an apply mode for requested repository writes; the context-relationship skill requires verified/candidate separation and evidence-backed updates; the attached Loopy skill defines bounded Observe → Choose → Act → Verify → Record → Repeat loops with named terminal states.
