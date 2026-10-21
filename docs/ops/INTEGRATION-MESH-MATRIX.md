# INTEGRATION MESH MATRIX — every GitHub-listed integration for `timerloggedout-spec`, mapped

**Compiled:** 2026-10-21 ~10:00 PDT. **Scope:** the GitHub account `timerloggedout-spec`,
its two orgs, and `timerloggedout-spec/termux-monorepo` as the hub repo.
**Companion docs:** `TOOLING-REACH-MAP.md` (reach paths across all agent surfaces),
`docs/ops/ACTIONS-WORKFLOWS-MATRIX.md` (workflow layer), Issue #184 (credential
authorizations & last-used evidence).

## Evidence classes — read this first

Every row carries one of these. Do not merge them; they are different GitHub objects.

| Class | Source | Vintage |
|---|---|---|
| **LIVE-API** | Firsthand REST census via the owner PAT (`custom.github-pat`), 2026-10-21: check suites on the 5 most recent master heads, 400 newest issue comments, submitted reviews on the 50 most recently updated PRs, 300 newest deployments, hooks/secrets/environments/workflows listings | 2026-10-21 |
| **#184** | Issue #184 — the owner's paste of GitHub's own Settings → Credentials pages (Authorized OAuth Apps, Authorized GitHub Apps, PATs, SSH keys) with GitHub's last-used labels | 2026-08-13 snapshot |
| **REPO** | Files/config on master (`.github/connectors/`, `.coderabbit.yaml`, `dependabot.yml`, agent roster) | current master |
| **MAP** | `TOOLING-REACH-MAP.md` cross-surface facts (Muse connectors, Jules-side MCPs) | 2026-10-20/21 |

Two different GitHub lists exist and this matrix keeps them separate:
**Authorized** apps (user granted the app account access — the #184 lists) vs
**Installed/Active** apps (installed on the account/repos and actually emitting
checks/reviews/comments — the LIVE-API census). An app can be in either list
without the other (§5 is exactly that gap). The Settings → Installations UI is
the union view; it is **not yet re-read live** (browser sign-in pending at
compile time) — §3/§4 + §5 together are its evidence-based reconstruction.

**Names-only discipline:** secret and token *names* only, never values. Webhook
destinations are hosts only. This follows the standing credential caution:
nothing here proposes a purge, rotation, or revocation — see §9 rules.

---

## 1. Account & identity surface (LIVE-API)

| Fact | Value |
|---|---|
| Account | `timerloggedout-spec` (id 233432881), Free plan, 2FA on, created 2025-09-20 |
| Repos | **677 public** (660 forks, 1 archived), 0 private; hub = `termux-monorepo` (207 open issues+PRs at census) |
| Orgs (role: **admin**) | `Research-Astute` (5 repos, mostly Manus research), `search-astute-ly` (3 repos, incl. 2 enterprise monorepo copies) |
| SSH keys | 1 — `DeepSeek_Account-1_ssh` (matches #184) · GPG keys 0 · SSH signing keys 0 |
| Social link | `termux-monorepo.vercel.app` |
| Codespaces | 3, all Shutdown, all on termux-monorepo (2-core/8 GB + 2× 4-core/16 GB) |
| Packages | GHCR container `termux-readme-extractor` (public, from termux-monorepo) |
| API budget | PAT core 5,000 req/hr (4,493 remaining at census) |

## 2. Tokens & credential stores (names only)

### 2a. Personal access tokens (#184, 2026-08-13, + one live addition)

| Token | Kind | #184 last-used | Notes |
|---|---|---|---|
| `ARCHWIZ_GITHUB_TOKEN` | Fine-grained | Never used | No expiration. Also exists as a repo Actions secret (§2b) — the second admin lane |
| `DeepSeek_account-1` | Fine-grained | ≤2 weeks | **Expired** at #184 snapshot |
| `DEEPSEEK_API_KEY` | Classic | Never used | Full-admin scope set (see #184). Name collides with the DeepSeek *model* key in §2b — different objects, do not cross-wire (repo rule, `.github/connectors/README.md`) |
| `Gh_actions` | Classic | ≤1 week | Full-admin scope set, no expiration |
| `gitlab_cicd-w+org_view` | Classic | ≤1 week | `read:org, repo` only — the narrowest classic token |
| `gitlab_cicd` | Classic | Never used | `repo` scope |
| `timers-full+accessPAT` | Classic | Never used | Full-admin scope set, no expiration |
| `MUSE_ADMIN_GH` | Classic | Live daily | Created 2026-10-20, **post-dates #184**. Muse's only GitHub route (`custom.github-pat`, Secure Vault, no per-call approval cards) |

### 2b. Repository Actions secrets — termux-monorepo (LIVE-API, 31 names)

Grouped by the service each name serves (the mesh's wiring diagram in one table):

| Service lane | Secret names |
|---|---|
| GitHub admin lanes | `OPERATOR_GITHUB_TOKEN`, `ARCHWIZ_GITHUB_TOKEN`, `OPERATOR_TOKEN`, `RECON_INTEL_GITHUB_WRITE_TOKEN` |
| GitLab | `GITLAB_TOKEN`, `GITLAB_ADMIN_TOKEN`, `OPERATOR_GITLAB_TOKEN` |
| Model providers | `DEEPSEEK_API_KEY`, `DEEPSEEK_AGENT_TOKEN`, `DEEPSEEK_AGENT_URL`, `DEEPSEEK_AWS_WAF_TOKEN`, `GEMINI_API_KEY`, `OPENROUTER_API_KEY`, `FELO_AI_API` |
| Agent platforms | `JULES_API_KEY`, `CELLCOG_API_KEY`, `LIKECLAW_A2A_GH_ACTIONS`, `MANUS_SSH_HOST`, `MANUS_SSH_KEY`, `MANUS_SSH_PORT` |
| Telemetry / memory | `HINDSIGHT_API_KEY`, `HINDSIGHT_BANK_ID`, `HINDSIGHT_BASE_URL`, `HINDSIGHT_TENANT_ID`, `HEX_ALSO_USEDBY_CELLCOG` |
| PM / deploy / coverage | `LINEAR_API_KEY`, `VERCEL_TOKEN`, `VERCEL_GITHUB_AND_TANKA`, `FLY_IO_ORG_TOKEN`, `CODECOV_TOKEN` |
| Vault | `TMX_VAULT_AGE_KEY` |

### 2c. Every other secret store — enumerated, all empty (LIVE-API, 2026-10-21)

| Store | Result |
|---|---|
| Repo Dependabot secrets | 0 |
| Repo Codespaces secrets | **7** — `HINDSIGHT_API_KEY`, `HINDSIGHT_API_LLM_API_KEY`, `HINDSIGHT_BANK_ID`, `HINDSIGHT_BASE_URL`, `HINDSIGHT_TENANT_ID`, `OPENROUTER_API_KEY`, `TMX_VAULT_AGE_KEY` |
| Environment secrets × 14 environments | **0 in every environment** (env_Termux-MonoRepo, github-pages, hindsight-prod, Preview ×5, Production ×5, staging) |
| Org Actions secrets (both orgs) | 0 |
| Org Dependabot secrets (both orgs) | 0 |
| Org Codespaces secrets (both orgs) | endpoint 404 (not available on Free orgs) |
| Org Actions variables / org webhooks | 0 / 0 |
| User Codespaces secrets | 0 |
| Repo Actions variables | 2 — `TERMUX_MCP_ENDPOINT` (Pinggy tunnel to the device MCP, refreshed 2026-10-21), `TERMUX_MCP_ENDPOINT_UPDATED_AT` |

**Reading:** the mesh's credentials are 100% repo-scoped today. The orgs and
environments are named structure with nothing behind them yet — that is unused
capacity, addressed in §9 (moves C3/C4), not a defect to fix by moving secrets
around casually.

## 3. Authorized OAuth Apps — 31 (#184, GitHub's list)

Last-used is GitHub's label **as of 2026-08-13**. "Live evidence" is the
2026-10-21 census. *Never used* in August + active in October is normal here —
the repo's heavy automation mostly switched on after the snapshot.

| OAuth App | Owner | #184 last-used | Live evidence (Oct 21) | Mesh role / best use |
|---|---|---|---|---|
| BLACKBOXAI | blackbox-dep | Never | none | Dormant coding assistant — park (§9 D-list) |
| Browserless | browserless | ≤2 wk | none on GitHub | Browser-automation lane; acts off-GitHub |
| ChatGPT Verification | openai | Never | none | Identity verification only |
| Codeit | codeitcodes | Never | none | Dormant |
| coderabbitai | coderabbitai | Never | via the GitHub App (§4) | OAuth twin of the App; App is the working surface |
| Composio | composio-dev | Never | none on GitHub | Tool-router; candidate bridge for agent tool access (§9 C5) |
| Dify | langgenius | Never | none | Dormant workflow/LLM platform |
| Entelligence-AI | Entelligence-AI | Never | none | Dormant |
| Genspark AI | wwwppp0801 | Never | none | Dormant |
| Gitar | gitarcode | ≤5 mo | via the GitHub App (§4) | OAuth twin; App active |
| GitCode | GitCode2024 | Never | none | Dormant |
| GitHub CLI | github | Never | indirect (device/Actions `gh`) | CLI auth lane |
| GitLab.com | gitlabhq | Never | **Live, degraded** — repo mirror webhook last response 400; 3 GitLab token secrets (§2b) | Mirror/redundancy lane — repair (§9 I2) |
| Jam | jamdotdev | Never | none | Dormant bug-report tool |
| Kernel Dashboard | kernel | Never | none | Dormant (browser-agent infra) |
| kilocode.ai | Kilo-Org | Never | via Kilo Code Bot App (§4) | OAuth twin; App active |
| Kimi GitHub Plugin | MoonshotAI | Never | none | Dormant model-vendor plugin |
| Komi Store | kurikomi-labs | ≤4 mo | none on GitHub | Dormant storefront |
| Mino | tinyfish-io | Never | none | Dormant |
| Nous Research (via Privy) | NousResearch | Never | none | Dormant |
| PlanetScale | planetscale | Never | none | DB vendor; no GitHub-side activity — DB lane is Neon/Supabase (§7) |
| PostHog | PostHog | Never | none | Dormant analytics |
| Pulumi Cloud | pulumi | Never | via Pulumi App (§5) | OAuth twin; App active |
| Qodo Git Connect | Codium-ai | Never | via Qodo Code Review App (§5) | OAuth twin; App active |
| Qodo.ai | qodo-ai | Never | via Qodo Code Review App (§5) |
| Replit | replit-integrations | ≤2 wk | Muse-side connector also connected (MAP) | Paired surfaces: Replit apps lane |
| Spck Editor | spck-io | Never | none | Mobile editor; device-side convenience |
| Supermemory login [v3 prod] | Dhravya | Never | none | Dormant memory service |
| Tavily | tavily-ai | Never | none on GitHub | Research/search API; agent-surface lane |
| Tembo | tembo | Never | via Tembo App (§4) | OAuth twin; App active |
| Zenhub | ZenHubIO | ≤1 wk | **Live, broken** — repo webhook 422 misconfigured (§6) | PM board lane — repair or retire deliberately (§9 I3) |

## 4. Authorized GitHub Apps — 38 (#184, GitHub's list)

| GitHub App | Owner | #184 last-used | Live evidence (Oct 21) | Mesh role / best use |
|---|---|---|---|---|
| Aikido Security | AikidoSec | Never | Sibling app `aikido-pr-checks` active (§5) | Security PR checks |
| AskSolo.ai | AskSolo-ai | Never | none | Dormant |
| BlocksOrg | BlocksOrg | Never | **Active** — check suites 5/5 heads, 10/400 comments | Slack-assignable agent marketplace. ⚠ Broadest permission set in the mesh (incl. `administration`, org hooks) — breadth noted, not changed (§9 rules) |
| ChatGPT Codex Connector | openai | ≤5 mo | **Active, low volume** — 14/400 comments | Codex review lane (peer set, opt-in per orchestrator) |
| Claude | anthropics | Never | none via App — Claude-authored work lands via owner PAT (MAP §B3) | App dormant; collaborator lane is PAT-based |
| Codacy Production | codacy | Never | **Active** — check suites 5/5 | Code-quality checks |
| coderabbitai | coderabbitai | Never | **Active, primary reviewer** — suites 5/5, 40/400 comments, 16 submitted reviews / 50 PRs | Required peer reviewer (orchestrator default) |
| Copilot Chat App | github | ≤1 wk | account-level only | Chat surface, no repo footprint |
| Copilot Pull Request Reviewer | github | Never | no submitted reviews in 50-PR sample | Tracked opt-in peer (orchestrator); staged use |
| Copilot SWE Agent | github | ≤2 wk | no PRs authored in sample | Coding-agent lane, unused on hub repo |
| cto.new | Engine-Labs | Never | none | Dormant |
| Cursor | cursor | ≤1 wk | **Active** — check suites 5/5 | Background coding agents. ⚠ `administration` permission |
| Devin.ai Integration | usacognition | Never | **Active, top submitted reviewer** — suites 5/5, **124 submitted reviews / 50 PRs** | Review+fix lane. ⚠ Org-admin/repo-creation permissions |
| ECC Tools | ECC-Tools | Never | **Active, comment-lane only** — 151/400 comments (top bot actor), **zero check runs**: Checks publication denied (app owner must enable Checks: read/write + installation owner must approve the permission update). Owner-UI fix dispatched 2026-10-21, result pending at compile time | Agent-harness audits. Fix = §9 I1 |
| Factory Droid | Factory-AI | Never | none | Dormant coding agent |
| Gitar Bot | gitarcode | ≤5 mo | **Active** — suites 5/5, 10/400 comments | Review + validated-fix lane |
| GitHub Codespaces | github | Never | 3 codespaces exist (§1) | Off-device compute lane (§9 C2) |
| Google Labs Jules | google-labs-code | ≤1 wk | **Active, primary coding agent** — 33 PRs authored in sample, 239 contributions | Bolt ⚡ lane; Muse steers via `custom.jules` no-HITL (MAP §B1) |
| Graphite App | withgraphite | ≤1 wk | **Active** — suites 5/5 | Stacked-PR lane |
| Grok (by xAI) | xai-org | ≤1 wk | none via App — Grok works in its own app, lands via owner PAT (MAP §B5) | App is a sign-in grant; work lane is PAT-based |
| HackerOne Code | PullRequestInc | Never | none | Dormant security review |
| Happy Coder App | slopus | Never | none | Dormant |
| Kilo Code Bot | Kilo-Org | Never | **Active** — suites 5/5 | Review/agent lane |
| Koyeb | koyeb | Never | none | Dormant deploy vendor |
| Linear | linear | Never | **Active** — repo webhook (all events, last 200 OK), `LINEAR_API_KEY`, feedback→subtasks workflow | PM spine of the mesh |
| Linear Code | linear | Never | none distinct | Dormant sibling |
| lovable.dev | GPT-Engineer-App | Never | none on GitHub; Muse-side Lovable connector connected (MAP) | App-building lane (Muse side) |
| Manus Connector | manus-ai-team | ≤1 wk | `MANUS_SSH_*` secrets + 1 contribution by `manus` | Manus lane runs over SSH; connector is its GitHub grant |
| Miro | miroapp | Never | none | Dormant whiteboard |
| MistralAI | mistralai | ≤2 wk | **Active** — suites 5/5 | Review lane; `mistral-vibe` contributor (1) |
| Render | renderinc | Never | **Active** — suites 5/5; also Jules-side integration (MAP §B1) | Preview/deploy lane |
| Sentry | getsentry | Never | **Active** — suites 5/5 | Error-monitoring lane |
| SonarQube Agent | SonarSource | Never | none | Dormant (GHAS/CodeQL cover this lane) |
| SonarQubeCloud | SonarSource | Never | none | Dormant |
| Tembo | tembo | Never | **Active** — suites 5/5 | Agent orchestration; nests Linear/MCP/sub-agents (REPO roster) |
| Travis CI | travis-ci | Never | **Active** — check suites on 5/5 master heads | Legacy CI signal duplicating Actions (§9 I4) |
| Vercel | vercel | Never | **Active, primary deploy** — suites 5/5, 76/300 deployments, 6/400 comments | Deploy lane (quota-capped — §9 I5) |
| Zed Industries | zed-industries | Never | none | Dormant editor grant |

## 5. Installed & active but NOT in the #184 authorized lists (LIVE-API)

These prove installation/activity in October that the August authorization
snapshot cannot show — the strongest argument for the §10 polling.

| App | Slug / owner | Evidence | Role |
|---|---|---|---|
| GitHub Actions | `github-actions` / github | 127 check suites across 5 heads; 1,238 contributions | The execution substrate (192 workflows, §6) |
| GitHub Pages | `github-pages` / github | suites + 38/300 deployments | Docs/site deploy |
| Mintlify | `mintlify` / mintlify | suites + **186/300 deployments** (all `staging` = docs previews) | Docs platform; biggest deployment producer |
| Qodo Code Review | `qodo-code-review` / qodo-ai | 10/400 comments + reviews | Peer reviewer (orchestrator tracked opt-in) |
| GitHub Advanced Security | `github-advanced-security` / github | submitted reviews in sample; check runs on PR heads | Code scanning lane |
| Blacksmith.sh | `blacksmith-sh` / useblacksmith | suites 5/5 | Hosted Actions runners (speed/cost lane) |
| Codecov | `codecov` / codecov | suites 5/5 + `CODECOV_TOKEN` secret | Coverage lane |
| Hark | `hark` / Adcock-AGI-Inc | suites 5/5 | Agent surface (MAP §B7); its GitHub App is one of its connections |
| LaunchDarkly agent | `launchdarkly-agent` / launchdarkly | suites 5/5 | AgentHQ flag/agent-task lane — no visible task use yet (§9 C6) |
| Pulumi | `pulumi` / pulumi | suites 5/5 | IaC lane |
| Dependabot | `dependabot` / github | 3 contributions; `dependabot.yml` present; Dependabot secrets 0; automated security fixes **disabled** | Dependency lane, partially wired (§9 I6) |

## 6. Hub-repo wiring (LIVE-API, termux-monorepo)

| Piece | State |
|---|---|
| Webhooks (3) | **Linear** — all events (`*`), last 200 OK · **GitLab mirror** — push+PR → `gitlab.com` project 85129320 mirror/pull, last **400** · **ZenHub** — 12 event types, last **422 misconfigured** |
| Workflows | **192 total, 191 active.** Recent 100 runs: actors all `timerloggedout-spec` (PAT-fired surface); events workflow_run 40, push 22, issue_comment 22, issues 12 |
| Environments | 14 (listed §2c) — deployment targets exist for help-wanted-dash / oversight / mcp-hub / termux-monorepo in Preview + Production pairs |
| Deployments (300 sampled) | Mintlify 186 (staging/docs) · Vercel 76 (Preview/Production per app) · GitHub Pages 38 |
| Branch governance | Ruleset `master-no-rewind` **active** (deletion + non-fast-forward blocked). Classic branch protection on master: **none** (404) — the repo gate + ruleset carry governance instead |
| Vulnerability alerts | endpoint live (204) · Automated security fixes **disabled** |
| Root config signals | `.coderabbit.yaml` (assertive, auto-review+autofix on), `.devin/`, `.Jules/`, `.claude/`, `.codex/`, `.github/dependabot.yml`, `docs.json` (Mintlify), `vercel.json` lane via apps |

## 7. Cross-surface mesh (MAP — the GitHub lists are only one face)

| Surface | Its integration set | Reach |
|---|---|---|
| Muse (this agent) | 63 system connectors on disk, **20 confirmed connected** (Google Workspace, Dropbox, Notion, Todoist, Vercel, Figma, Linear, Canva, Zoom, Meta, Lovable, Klaviyo, Replit, Tailscale…) + **2 custom** (`custom.github-pat`, `custom.jules`) + 54 skills | Directly promptable; system connectors card-gated on writes, custom connectors are not |
| Jules | Own MCPs: **Linear, v0, Render, Neon** connected (Neon verified 2026-10-20 23:35 PDT); **Supabase still open**; Stitch, Tinybird available-not-connected | Prompt Jules; Muse steers via `custom.jules` |
| Model providers (repo) | **27 quota families** on master (aion, cerebras, cloudflare, cohere, felo, gemini, groq, huggingface, kilo, llm7, mistral, modelscope, nvidia, ollama, omni, openrouter, ovhcloud, sambanova, siliconflow, zai, requesty, routeway, sealion, typhoon, unorouter, xfyun, xkiro); passive adapters implemented for groq, huggingface, ollama, openrouter, sambanova, siliconflow | Inference only — never platform tooling (MAP §C master rule) |
| Hark / Manus / Grok / Claude / ChatGPT | Own surfaces, own connections (Hark's set not enumerated Muse-side) | Work lands via owner PAT; Provenance/HindSight is the attribution layer |

## 8. Utility map — who does what job in the mesh

| Job | Primary | Peers / backup | Saturated? |
|---|---|---|---|
| Coding (write code) | Jules (Bolt ⚡) | Cursor, Devin, Copilot SWE (unused), Kilo, Factory (dormant) | No — one primary, rest review-weighted |
| PR review | CodeRabbit (required) | Devin (top volume), Qodo, Gitar, ECC (comments), Codex, Copilot Reviewer, Mistral, Aikido, Codacy | **Yes — 9+ reviewers/PR** → cadence problem, §9 I7 |
| CI / checks | GitHub Actions (192 workflows) | Blacksmith runners, Travis (duplicate signal) | Travis duplication, §9 I4 |
| Deploy / preview | Vercel (apps) | Render (previews), Mintlify (docs), Pages, Fly.io (token only), Koyeb (dormant) | Vercel daily cap is the binding constraint, §9 I5 |
| PM / planning | Linear (webhook + API + Jules MCP + Muse connector — 4 faces, one spine) | ZenHub (broken), GitHub Projects (enabled, unused visibly) | ZenHub decision, §9 I3 |
| Memory / telemetry | HindSight (secrets ×5, env `hindsight-prod`) | Hex (via CellCog secret), Supermemory (dormant) | OK |
| Comms / A2A | GitHub comments as trigger surface (16 issue_comment workflows) | LikeClaw A2A secret, Tembo orchestration, BlocksOrg via Slack | Watch trigger-burn |
| Research | Tavily, Browserless, FELO, provider families | Composio (bridge candidate) | OK |
| Security | GHAS + Aikido + CodeQL workflows | SonarQube ×2 (dormant), HackerOne (dormant) | One lane is enough; park rest |

## 9. Capacity maximization plan

**Standing rules (owner, already in force — this plan obeys them):**
(1) Never clear/disable bot participation to solve volume — thread it through
quota-aware cadence. (2) No credential purge/rotation/revocation without
redundancy + owner clone/archive + dependency evaluation. (3) Names-only for
all credential work. (4) Poller output is never committed (commits burn
Vercel/Render quota) — census snapshots live in the workspace, this doc is
hand-refreshed. (5) Provider-neutral early dispatch layer; per-provider
parallel quota threads, each reconciling its own cap before its own dispatch.

**Immediate (owner-actionable this week):**

| # | Move | Why / evidence | Route |
|---|---|---|---|
| I1 | Approve ECC Tools' Checks permission update | ECC is the top bot actor (151/400 comments) but publishes **zero** check runs; every audit comment ends with the denial notice | Owner UI: Settings → Installations → ECC Tools (dispatched 2026-10-21; verify before recording fixed) |
| I2 | Repair the GitLab mirror webhook (400) | Mirror is the redundancy lane for the whole repo; 3 GitLab secrets exist to support it | Check GitLab project 85129320 mirror state; re-ping hook via API |
| I3 | ZenHub: repair the 422 webhook **or** retire the lane deliberately | Board duplicates Linear (the working spine). A dead webhook firing 12 event types is pure noise | Owner decision; either fix config in ZenHub or remove hook + OAuth in one recorded move |
| I4 | Resolve Travis CI duplication | Travis suites on every master head while Actions is the real CI — double signal, double noise in the gate | Verify whether Travis runs any unique job; if not, park it as a recorded decision (not a silent clearing) |
| I5 | Keep Vercel moves quota-first | Daily deploy cap already tripped once (2026-10-20); Mintlify (186) + Vercel (76) dominate deployment volume | Batching cooldown (vercel-batch-deploy, 6h) + ignore-step guard; no new deploy-producing integrations until cap behaviour is measured |
| I6 | Finish Dependabot wiring | `dependabot.yml` exists, secrets 0, automated security fixes disabled | Enable security fixes; keep Dependabot in the peer-cadence (batched, SHA-bound) |
| I7 | Enforce the review-cadence matrix | 9+ review bots, ECC flooding documented (#1441: 207 comments) | peer-review-orchestrator: required = CodeRabbit; Qodo/Devin/Copilot tracked opt-in; Gemini only after peers (quota save); ECC via its 6h-debounced ops workflow for commands — the App's per-push audits stay, threaded not muted |

**Capacity unlocks (build next):**

| # | Move | Unlock |
|---|---|---|
| C1 | Finish Jules ↔ Supabase (last open Jules MCP) | Completes Jules' DB pair (Neon done); Stitch + Tinybird after, same pattern |
| C2 | Use the 3 Codespaces + 7 Codespaces secrets as the heavy-build lane | Offloads BLU B160V; prebuilds stay owner-gated per CE-001 |
| C3 | Org-level shared secrets for `Research-Astute` / `search-astute-ly` when their repos start Actions work | Today org stores are empty structure; replicate only the shared telemetry/inference names (HindSight, OpenRouter) — owner-approved credential move, names-first |
| C4 | Put environment secrets behind the 14 existing environments **only when** a deploy actually needs env-scoped credentials | Environments are currently pure structure; don't pre-fill |
| C5 | Evaluate Composio as the standard bridge before adding any new one-off OAuth grants | 31 OAuth grants is the sprawl metric; new capability should arrive through one router where possible |
| C6 | Assign-or-park the dormant set in one owner pass: AskSolo, cto.new, Factory Droid, Happy Coder, Koyeb, Miro, Zed, SonarQube ×2, HackerOne, BLACKBOX, Dify, Entelligence, GitCode, Jam, Kernel, Mino, Nous, Komi, Spck, ChatGPT Verification, Linear Code, Copilot Chat | "Park" = recorded dormant in this matrix with a named job-if-woken. **Not** revocation — rule (2) governs any later removal |

## 10. Active polling

A 6-hourly census poll (`github-integration-matrix-poll`, alongside
`jules-census-6h`) re-runs the LIVE-API census and diffs it against the previous
workspace snapshot: new/removed check-apps on master heads, bot-actor changes,
hook health (last response codes), secret-name additions/removals (names
only), environment/workflow counts, deployment-creator mix. Changes are
reported; **no change = no report**. Snapshots stay in
`~/workspace/github-integration-census/` — never committed (rule 4). This doc
is refreshed by hand from a poll diff, with the vintage line updated.

## NOT ESTABLISHED — stated, not filled in

- **Settings → Installations union list** (which apps are installed on which
  repos, All vs Select) — needs the owner's signed-in browser session; the
  2026-10-21 browser attempt stalled at GitHub's login page (session not
  established). §3+§4+§5 reconstruct it from evidence; the UI read remains
  the one open verification.
- **#184 vintage risk:** last-used labels are 2026-08-13. Anything marked
  "Never" there may have activated since (several did — §4). Treat #184 as
  the authorization *floor*, the LIVE-API census as current *activity*.
- **Token-to-workflow dependency map** for the 7 PATs (which token each
  workflow actually uses is in workflow YAML + §2b secret names, not yet
  joined 1:1).
- **Hark's own connection set** (user-enabled, not enumerated Muse-side).
- **Org-repo integrations** (hooks/secrets above are org-level stores; the 8
  org repos' own hooks/apps were not censused — hub repo first by design).

*End of matrix. Update rule: refresh from a poll diff or a fresh #184-style
owner paste; never edit a row from memory alone.*
