# Connector ability map and quota ledger (recon 2026-11-18)

Connectors change often, and some names are shared by several servers. Route by family, not by name. Re-verify before relying on any row.

## 1. Duplicate-name and multi-server families (route carefully)

| Family | Servers (tool count) | Use | State (2026-11-18) |
|---|---|---|---|
| GitHub | GitHub (GitHub_CoPilot_MCP, ~45) | Reads, search, issues, PRs | Reads OK. Branch create returns 403 (Contents write missing). |
| GitHub | Composio GitHub (via COMPOSIO_*) | Branches, commits, workflow files | ACTIVE under timerloggedout-spec. Commits and workflow-scope writes verified. Use for writes. |
| Cloudflare | cloudflare (API; docs, search, execute, whoami, 4) | Full Cloudflare API | Authenticated as timerloggedout@gmail.com. Use for API work. |
| Cloudflare | Cloudflare Developer Platform (bindings; 23) | Workers, KV, D1, R2 | Connected server is marked deprecated. R2 not enabled. |
| Wrike | Wrike (18) | Tasks, folders, approvals | connect_incomplete. Finish OAuth. |
| Wrike | Wrike-4768ea14 (31) | Items, requestforms, approvals | Not checked. Likely the newer server. |
| Airtable | Airtable (57) | Bases, records, automations | Reads OK. 0 bases. |
| Airtable | HyperAgent_AirTable (10) | Agent threads and approvals | Unrelated to Airtable data. |
| Ahrefs | Ahrefs (159) | SEO data, Brand Radar, GSC | Free plan. See quota. |
| Upstash | upstash (76) | Redis, Vector, QStash, Box, Blob | Not checked. |
| Grafana | Grafana Cloud (134) | Dashboards, alerts, Loki, Prometheus | 1 alert rule, healthy. |
| Vercel | Vercel (256) | Deploys, domains, sandboxes, flags | Hobby team. 4 projects, none from this repo. |
| Netlify | Netlify (14) | Deploys, extensions | Not checked. |
| Make | Make (116) | Scenarios, hooks, data stores | 1 org, 1 team, 0 scenarios. |
| monday | monday.com (107) | Boards, items, docs, workflows | Not rechecked since Oct 19. |
| Canva | Canva (45) | Designs, exports, brand templates | Not checked. |
| Adobe | Adobe (109) | PDF, image, Express, Firefly | Not checked. |
| Notion | Notion (78) | Pages, databases, search, sessions | Reads OK. Writes approved and working. |
| Linear | Linear (70) | Issues, projects, documents | Reads OK. 59 bot triage issues. |
| Lucid | Lucid (35) | Diagrams, mind maps, docs | Writes verified. |
| Miro | Miro (46) | Boards, canvas, spaces | Read verified. |
| Figma | Figma (44) | use_figma, create_new_file, screenshots | Writes verified. Starter quota tight. |
| Framer | Framer (8) | Projects, exec, screenshots | Writes verified. |
| Mintlify | Mintlify (44) | Docs pages, deploys, workflows | Deploy queued (commit 5972cd2). |
| Supabase | Supabase (36) | Projects, SQL, migrations, advisors | Writes verified. Project lane-state. |
| Neon | Neon (141) | Projects, branches, SQL | Reads OK. lane-events active. |
| Render | Render (50) | Services, deploys, logs | Reads OK. Services in use. |
| Sentry | Sentry (74) | Issues, events, traces | Reads OK. Clean in 30 days. |
| Todoist | Todoist (49) | Tasks, comments, projects | Writes verified. |
| Hugging Face | Hugging Face (11) | Hub repos, Spaces, jobs | Private dataset. PRO needed for preview. |
| ElevenLabs | ElevenLabs (222) | Voice, speech, flows | Auth not completed. Reconnect. |
| Elicit | Elicit (43) | Research agents, reports | API access denied on current plan. |
| Scite | Scite (35) | Literature checks, citations | Plan inactive, allowance 0. |
| OpenSEO | OpenSEO (87) | SEO research, GSC, GA | 500 credits left. |
| Ubersuggest | Ubersuggest (61) | Keywords, projects, audits | Free plan. See quota. |
| Semrush | Semrush (19) | Domain and keyword analytics | Not checked. |
| Composio | Composio (12) | Meta-router to other apps | GitHub connection ACTIVE. |

Other connected families not listed above (not checked yet): Klaviyo, Apollo, AgentMail, AgentPhone, ThunderPhone, Calendly, Dropbox, Google Drive/Gmail/Calendar/Docs/Sheets, Expo, Context7, Jam, Bitly, Circleback, CircleCI, Boltz, Tally, DeepL, Stewdio, Replit, Lovable, Base44, Macaly, Webflow, v0, Magic Patterns, animatedwebs, Mobbin, Quartr, Supermetrics, Windsor, Open Targets, Amass, PopHIVE, MAIA, Consensus, SciSpace, PubMed, bioRxiv, ChEMBL, Lacuna, Clinical Trials, alphaXiv, Exa, Parallel Search, Firecrawl, TinyFish, AWS MCP, AWS Marketplace, Wolfram, tldraw, Three.js, Atlassian, Prefect, MongoDB Atlas, MotherDuck, Termux Desktop Commander (offline intermittently since Oct).

## 2. Quota ledger

| Connector | Limit | Used or remaining | Reset | Action |
|---|---|---|---|---|
| Figma (Starter) | 20 MCP tool calls per month | Low. Batch Figma work. | Monthly | Batch every change into one call. |
| Figma (Starter) | 3 files | 2 of 3 used (test file plus one more) | Plan | Delete unused drafts before creating more. |
| Figma (Starter) | AI credits | 0 of 500 monthly, 0 of 150 daily | Monthly, daily | None used. |
| OpenSEO | Credits | 500 remaining | Per plan | Confirm with the user before any batch over 2,000. |
| Ubersuggest (free) | Keywords | 0 of 25 | Plan | Stay within 25. |
| Ubersuggest (free) | Reports | 0 of 3 | Plan | Save reports only when needed. |
| Ubersuggest (free) | Monthly keyword metric updates | 0 of 10 | Monthly | Use sparingly. |
| Ubersuggest (free) | AIW words | 0 of 2000 | Plan | Unused. |
| Ahrefs (free) | API units (key) | 0 of 200,000 used | 2026-11-23 | Free for demo queries. Paid plan needed for real data. |
| Scite | Plan allowance | 0. Plan inactive. Pay-as-you-go not available. | Monthly | Upgrade needed (user decision). |
| Elicit | API access | Denied. Pro or above needed. | Plan | Upgrade needed (user decision). |
| ElevenLabs | Credits | Unknown. Auth not completed. | Monthly | Reconnect, then read account_get_usage. |
| Hugging Face | Private dataset preview | PRO needed. | Plan | Spend decision. |
| Vercel (Hobby) | Build rate limit | Hit in Oct. | Daily | Keep the build count low. |
| Render (free) | Services and pipeline minutes | 6 services. | Monthly | Keep services owned and in use. |
| Linear | Usage limit | Sync logged a usage-limit error in the past. | Plan | Confirm current usage. |
| Desktop Commander | Device | Termux intermittent since Oct. | n/a | Skip unless online. |

## 3. Batch performance rules

- GitHub: use GITHUB_COMMIT_MULTIPLE_FILES (Composio) for any change touching more than one file. One commit, one call.
- Composio: COMPOSIO_MULTI_EXECUTE_TOOL can carry several tool calls in one request. Use it for independent reads, such as several paths at once.
- Figma: one use_figma call per board or change set. Each call uses the monthly quota.
- Framer: one exec per build stage (gather, build, then one screenshot).
- Lucid: create the whole mind map in one call (up to 1000 nodes).
- Supabase: execute_sql accepts multi-statement batches. Use one call per logical change.
- Todoist: add-tasks and add-comments take arrays. Batch them.
- Notion: notion-create-pages takes an array of pages in one call.

## 4. Known gaps

- The Cloudflare API connector (cloudflare) is live. An earlier note said its replacement was missing, and that was wrong.
- GitHub connector writes still fail (403). Composio GitHub is the write path.
- Expo has no EAS projectId in this repo.
