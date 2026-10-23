# INTEGRATION MESH MATRIX — every GitHub-listed integration for `timerloggedout-spec`, mapped

**Compiled:** 2026-10-21 ~10:00 PDT. **Amended same day (second pass):** census v2. **Refreshed 2026-10-22 (third pass):** secrets 31→33, PRs 1,292→1,327, issues 193→206, workflows 192→195 — all live figures re-taken; see #1505. **Refreshed 2026-10-22 (fourth pass, ~09:48 PDT):** PRs 1,327→1,330, workflows 195→196 (+1 "Research and paper accounting validation"), issues steady at 206 — see #1505. **Refreshed 2026-10-22 (fifth pass, ~15:48 PDT):** secrets 33→37 (+4: 2 Cloudflare deploy, 2 device-queue), workflows 196→198, variables 2→3 (+`DEVICE_QUEUE_URL`), PRs 1,330→1,342, issues 206→207 — see #1505. **Refreshed 2026-10-23 (sixth pass, ~09:48 PDT):** github-advanced-security first check suites in the 30-head window (5 suites, CodeQL, on `547f54e7`), workflows 200→201 (+`operator-variable-provision`), secrets steady at 37 names, PRs 1,358→1,362, issues steady at 213 — see #1505. **Refreshed 2026-10-23 (seventh pass, ~15:48 PDT):** secrets 37→38 (+`VANTAGE_PAT_GH_SECRETS` — Vantage cost-report lane), workflows 201→205 (+4 verified new files: `vantage-cost-report`, `operator-wake`, `delphi-intake`, `target-intake`), PRs 1,362→1,374, issues 213→220 — see #1505.
(full pagination, no samples — 1,342 PRs, 207 issues, 2,000 comments, check suites
across 30 master heads, submitted reviews in two labeled frames) + the installations
probe (stored-token exercise from inside Actions, Issue #184 comment 6321665538),
which retrieved the org installation records in §5A. **Scope:** the GitHub account `timerloggedout-spec`,
its two orgs, and `timerloggedout-spec/termux-monorepo` as the hub repo.
**Companion docs:** `TOOLING-REACH-MAP.md` (reach paths across all agent surfaces),
`docs/ops/ACTIONS-WORKFLOWS-MATRIX.md` (workflow layer), Issue #184 (credential
authorizations & last-used evidence).
**Refreshed 2026-10-22:** §4B added — the owner's firsthand Installed GitHub Apps
list (OWNER-UI screenshot, A–H portion) reconciled against §4/§5, incl. the four
"Permission updates requested" flags; §9 I8 + §10 + closing list updated to match.
This matrix is the **integration** inventory; Issue #184 remains the **credential**
inventory of record — the Settings app lists are app integrations, not credentials.

## Evidence classes — read this first

Every row carries one of these. Do not merge them; they are different GitHub objects.

| Class | Source | Vintage |
|---|---|---|
| **LIVE-API** | Firsthand REST census via the owner PAT (`custom.github-pat`), 2026-10-22, fifth pass, fully paginated: check suites across the 30 most recent master heads, 2,000 newest issue comments, **all 1,342 PRs** (authors), submitted reviews in two frames (150 most recently *updated* PRs; 150 most recently *created* PRs), 300 newest deployments, hooks/secrets/environments/workflows/org-installations listings | 2026-10-22 |
| **PROBE** | Installations probe workflow run 39639440245 (2026-10-21): exercised the stored GitHub tokens from inside Actions against `/user/installations` and `/orgs/{org}/installations`; results posted to Issue #184 (comment 6321665538). Token values never printed | 2026-10-21 |
| **#184** | Issue #184 — the owner's paste of GitHub's own Settings → Credentials pages (Authorized OAuth Apps, Authorized GitHub Apps, PATs, SSH keys) with GitHub's last-used labels | 2026-08-13 snapshot |
| **OWNER-UI** | Owner-firsthand screenshot of Settings → Applications → **Installed GitHub Apps** (github.com/settings/installations), visible **A–H portion only** — 24 apps; the list continues past Hex and the remainder was not captured. Transcribed + reconciled on Issue #184 (comment 6335646953) | 2026-10-22 |
| **REPO** | Files/config on master (`.github/connectors/`, `.coderabbit.yaml`, `dependabot.yml`, agent roster) | current master |
| **MAP** | `TOOLING-REACH-MAP.md` cross-surface facts (Muse connectors, Jules-side MCPs) | 2026-10-20/21 |

Two different GitHub lists exist and this matrix keeps them separate:
**Authorized** apps (user granted the app account access — the #184 lists) vs
**Installed/Active** apps (installed on the account/repos and actually emitting
checks/reviews/comments — the LIVE-API census). An app can be in either list
without the other (§5 is exactly that gap). The Settings → Installations UI
is the union view: its API route stays a **proven boundary** (fleet credential
rule, 2026-10-21 — this fleet's owner-controlled GitHub access runs through
the PAT helper, `/user/installations` refuses PATs (403) by GitHub's design,
and no browser sign-in route is used for GitHub access), but the **Installed
tab's A–H portion is now evidenced owner-firsthand** (§4B, OWNER-UI
2026-10-22); the remainder past H and the per-app repository scope remain
NOT ESTABLISHED (closing list). §3/§4 + §4B + §5 together are the standing
answer — an evidence-based reconstruction, not a placeholder.
**Live floor, recounted 2026-10-23:** ≥30 distinct apps are active on the hub
repo alone (25 check-suite apps across 30 master heads — +Buildkite ~03:00 PDT, +github-advanced-security ~04:05 PDT — + ECC, Qodo, Codex, Jules, Dependabot). The #184 counts (31 OAuth / 38 GitHub Apps)
are the **Aug-13 floor, not current totals** — the owner states the account
now has way more than 38 GitHub Apps, and the account-level total (677 repos
+ 2 orgs) is NOT ESTABLISHED via API. **Reconciled 2026-10-22:** 38 Aug-13
authorized GitHub Apps + 8 installed-only newcomers visible in §4B's A–H
window = **46 distinct GitHub App names evidenced** across sources; the true
total is larger (the Installed list continues past H). The org slice of the
installations picture *was* retrieved live — see §5A.

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

### 2b. Repository Actions secrets — termux-monorepo (LIVE-API, 38 names)

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
| Cloudflare | `CLOUDFLARE_ACCOUNT_ID`, `CLOUDFLARE_API_TOKEN` |
| Device queue | `DEVICE_QUEUE_PRODUCER_TOKEN_ACTIONS`, `DEVICE_QUEUE_DEVICE_TOKEN_PRIMARY` |
| Termux device MCP | `TERMUX_MCP_KNOWN_HOSTS`, `TERMUX_MCP_SSH_PRIVATE_KEY` |
| Cost reporting | `VANTAGE_PAT_GH_SECRETS` |

### 2c. Every other secret store — enumerated; all empty except the 7 repo Codespaces secrets listed here (LIVE-API, 2026-10-22)

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
| Repo Actions variables | 3 — `TERMUX_MCP_ENDPOINT` (Pinggy tunnel to the device MCP, refreshed 2026-10-22), `TERMUX_MCP_ENDPOINT_UPDATED_AT`, `DEVICE_QUEUE_URL` |

**Reading:** the mesh's *secret stores* are 100% repo-scoped today (the
account-level PATs in §2a and the SSH key in §5B are separate account
surfaces, not secret stores). The orgs and
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
| Qodo.ai | qodo-ai | Never | via Qodo Code Review App (§5) | OAuth twin; the App in §5 is the working surface |
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
| BlocksOrg | BlocksOrg | Never | **Active** — check suites on 30/30 master heads, 60/2,000 comments | Slack-assignable agent marketplace. ⚠ Broadest permission set in the mesh (incl. `administration`, org hooks) — breadth noted, not changed (§9 rules) |
| ChatGPT Codex Connector | openai | ≤5 mo | **Active, low volume** — 80/2,000 comments | Codex review lane (peer set, opt-in per orchestrator) |
| Claude | anthropics | Never | none via App — Claude-authored work lands via owner PAT (MAP §B3) | App dormant; collaborator lane is PAT-based |
| Codacy Production | codacy | Never | **Active** — check suites on 30/30 heads | Code-quality checks |
| coderabbitai | coderabbitai | Never | **Active, primary reviewer** — suites on 30/30 heads, 155/2,000 comments, **83 submitted reviews** (150 most-recently-updated frame: 57 CHANGES_REQUESTED, 6 APPROVED, 19 COMMENTED, 1 DISMISSED); also authored 9 PRs | Required peer reviewer (orchestrator default) |
| Copilot Chat App | github | ≤1 wk | account-level only | Chat surface, no repo footprint |
| Copilot Pull Request Reviewer | github | Never | no submitted reviews in 50-PR sample | Tracked opt-in peer (orchestrator); staged use |
| Copilot SWE Agent | github | ≤2 wk | no PRs authored in sample | Coding-agent lane, unused on hub repo |
| cto.new | Engine-Labs | Never | none | Dormant |
| Cursor | cursor | ≤1 wk | **Active** — check suites on 30/30 heads | Background coding agents. ⚠ `administration` permission |
| Devin.ai Integration | usacognition | Never | **Active, top submitted reviewer** — suites on 30/30 heads, **147 submitted reviews** (150 most-recently-updated frame, all COMMENTED; 92 on PR #143 alone); authored 2 PRs | Review+fix lane. ⚠ Org-admin/repo-creation permissions |
| ECC Tools | ECC-Tools | Never | **Active, comment-lane only** — **915 of the 2,000 newest issue comments (46%, top actor)**, **zero check runs**. Mechanism established via `GET /apps/ecc-tools`: the vendor app's own configuration requests only contents/issues/pull_requests write + metadata read — **it carries no Checks permission at all** (contrast coderabbitai checks:write, qodo checks:read), so no installation-owner approval exists or is pending; only the vendor can add it | Agent-harness audits (6 kinds). Repo-side fix = Actions mirror, PR #1491 (§9 I1) |
| Factory Droid | Factory-AI | Never | none | Dormant coding agent |
| Gitar Bot | gitarcode | ≤5 mo | **Active** — suites on 30/30 heads, 42/2,000 comments | Review + validated-fix lane |
| GitHub Codespaces | github | Never | 3 codespaces exist (§1) | Off-device compute lane (§9 C2) |
| Google Labs Jules | google-labs-code | ≤1 wk | **Active, primary coding agent** — **284 of all 1,342 PRs authored**, 240 contributions, 6/2,000 comments | Bolt ⚡ lane; Muse steers via `custom.jules` no-HITL (MAP §B1) |
| Graphite App | withgraphite | ≤1 wk | **Active** — suites on 30/30 heads | Stacked-PR lane |
| Grok (by xAI) | xai-org | ≤1 wk | none via App — Grok works in its own app, lands via owner PAT (MAP §B5) | App is a sign-in grant; work lane is PAT-based |
| HackerOne Code | PullRequestInc | Never | none | Dormant security review |
| Happy Coder App | slopus | Never | none | Dormant |
| Kilo Code Bot | Kilo-Org | Never | **Active** — suites on 30/30 heads | Review/agent lane |
| Koyeb | koyeb | Never | none | Dormant deploy vendor |
| Linear | linear | Never | **Active** — repo webhook (all events, last 200 OK), `LINEAR_API_KEY`, feedback→subtasks workflow | PM spine of the mesh |
| Linear Code | linear | Never | none distinct | Dormant sibling |
| lovable.dev | GPT-Engineer-App | Never | none on GitHub; Muse-side Lovable connector connected (MAP) | App-building lane (Muse side) |
| Manus Connector | manus-ai-team | ≤1 wk | `MANUS_SSH_*` secrets + 1 contribution by `manus` | Manus lane runs over SSH; connector is its GitHub grant |
| Miro | miroapp | Never | none | Dormant whiteboard |
| MistralAI | mistralai | ≤2 wk | **Active** — suites on 30/30 heads | Review lane; `mistral-vibe` contributor (1) |
| Render | renderinc | Never | **Active** — suites on 30/30 heads; also Jules-side integration (MAP §B1) | Preview/deploy lane |
| Sentry | getsentry | Never | **Active** — suites on 30/30 heads | Error-monitoring lane |
| SonarQube Agent | SonarSource | Never | none | Dormant (GHAS/CodeQL cover this lane) |
| SonarQubeCloud | SonarSource | Never | none | Dormant |
| Tembo | tembo | Never | **Active** — suites on 30/30 heads | Agent orchestration; nests Linear/MCP/sub-agents (REPO roster) |
| Travis CI | travis-ci | Never | **Active** — check suites on 30/30 master heads | Legacy CI signal duplicating Actions (§9 I4) |
| Vercel | vercel | Never | **Active, primary deploy** — suites on 30/30 heads, 91/300 deployments, 12/2,000 comments | Deploy lane (quota-capped — §9 I5) |
| Zed Industries | zed-industries | Never | none | Dormant editor grant |

## 4B. Installed GitHub Apps — owner-firsthand (OWNER-UI, 2026-10-22)

The **Installed** tab of Settings → Applications is a different list from the
**Authorized** tab §4 transcribes: an app can be installed without appearing
in the Aug-13 authorized list, and vice versa. The owner captured the
Installed list firsthand on 2026-10-22; the visible portion runs **A–H
(24 apps)** and the list continues past Hex — so the installed total exceeds
24 by an uncounted remainder (NOT ESTABLISHED, closing list). Display names
are GitHub's; slug forms are given where the census uses them.

| App (as listed) | In Aug-13 authorized (§4)? | Live activity (Oct-21 census) | Notes |
|---|---|---|---|
| Aikido PR Checks | No — its sibling Aikido Security is | **Active** — `aikido-pr-checks` check suites on hub heads; Aikido submitted 12 reviews (150-updated frame) | The PR-checks half of Aikido's pair; §4's Aikido Security row is the other half |
| Aikido Security | Yes ("Never") | No direct activity observed | The active Aikido surface is the sibling above |
| AskSolo.ai | Yes | none | Dormant (§9 C6) |
| blacksmith.sh | **No — installed-only** | **Active** — `blacksmith-sh` suites on 30/30 heads (§5) | Also installed on both orgs (§5A) |
| BlocksOrg | Yes | **Active** — suites 30/30, 60/2,000 comments | — |
| ChatGPT Codex Connector | Yes | **Active, low volume** — 80/2,000 comments | — |
| Codacy Production | Yes | **Active** — suites 30/30 | — |
| Codecov | **No — installed-only** | **Active** — suites 30/30 + `CODECOV_TOKEN` (§5); reaches 5 of the 7 cluster repos (§5B) | Also installed on Research-Astute (§5A) |
| coderabbitai | Yes | **Active, primary reviewer** | ⚠ **Permission update requested** — owner-UI item of record (§9 I8) |
| cto.new | Yes | none | Dormant (§9 C6) |
| Cursor | Yes | **Active** — suites 30/30 | ⚠ **Permission update requested** (§9 I8) |
| Devin.ai Integration | Yes | **Active, top submitted reviewer** — 147 reviews (150-updated frame) | ⚠ **Permission update requested** (§9 I8) |
| ECC Tools | Yes | **Active, comment-lane only** — 915/2,000 comments, zero check runs | **No** permission update is flagged for ECC — consistent with §4's mechanism: the vendor app requests no Checks permission in its own configuration, so there is nothing pending to approve. A different state from the four flagged apps |
| endor-labs-github-agenthq | **No — installed-only** | No activity under this name in the census | Possibly the installation behind §5's `launchdarkly-agent` suites (AgentHQ) — identity NOT ESTABLISHED; carried as its own row until a slug-level join exists |
| Factory Droid | Yes | none | ⚠ **Permission update requested** — a dormant app asking for expanded scope is a deliberate-decision item, not a rubber stamp (§9 I8) |
| FalconerAI | **No — installed-only** | none observed | New to the matrix with this screenshot; no GitHub-side activity in the Oct-21 census and no assigned role yet — assign-or-park (§9 C6 pattern) |
| Gitar Bot | Yes | **Active** — suites 30/30, 42/2,000 comments (as `gitar-bot`) | — |
| GitHub Copilot for Linear | **No — installed-only** | none observed on the hub repo | New to the matrix; by name a Copilot↔Linear bridge — no check/comment/review footprint in the census, so any use is off-hub or not yet exercised |
| Google Labs Jules | Yes | **Active, primary coding agent** — authored 279 of 1,292 PRs | Also installed on Research-Astute (§5A) |
| Graphite App | Yes | **Active** — suites 30/30 | — |
| Grok (by xAI) | Yes | none via App | Works in its own app; lands via owner PAT (§4) |
| HackerOne Code | Yes | none | Dormant (§9 C6) |
| Hark | **No — installed-only** | **Active** — `hark` suites on hub heads; reaches 4 of the 7 cluster repos (§5B) | The App is one face of the Hark agent surface (MAP §B7) |
| Hex - GitHub sync | **No — installed-only** | none observed | New to the matrix. Distinct from the "Hex" in the `HEX_ALSO_USEDBY_CELLCOG` secret name (§2b/§8) — that is a CellCog-side reference; no join between the two is established |

**Reconciliation:** the 8 installed-only names in just the A–H window
(Aikido PR Checks, blacksmith.sh, Codecov, endor-labs-github-agenthq,
FalconerAI, GitHub Copilot for Linear, Hark, Hex - GitHub sync) bring the
evidenced GitHub App total to **46 distinct names** (38 Aug-13 authorized +
8). The installed list's remainder past H is expected to add more of §5's
actives (LaunchDarkly, Mintlify, Pulumi, Qodo sort past H) — stated as an
expectation, not a count.

**Permission updates requested (4):** coderabbitai, Cursor, Devin.ai
Integration, Factory Droid show "Permission updates requested" in Settings.
Approving an update is an owner-UI act; the four are recorded here as
owner-UI items of record (§9 I8) so the state is not lost — they do not block
any fleet work, and no chat will park on them.

## 5. Installed & active but NOT in the #184 authorized lists (LIVE-API)

These prove installation/activity in October that the August authorization
snapshot cannot show — the strongest argument for the §10 polling.
Cross-checked against §4B (2026-10-22): Blacksmith, Codecov and Hark now also
carry firsthand installation evidence there; this section holds their
activity evidence. The remaining §5 apps sort past §4B's A–H window, so their
absence from the screenshot portion is expected, not contradictory.

| App | Slug / owner | Evidence | Role |
|---|---|---|---|
| GitHub Actions | `github-actions` / github | **970 check suites across 30 master heads** (320 success / 534 skipped / 112 cancelled / 4 failure); 1,299 contributions | The execution substrate (201 workflows, §6) |
| GitHub Pages | `github-pages` / github | suites + 48/300 deployments | Docs/site deploy |
| Mintlify | `mintlify` / mintlify | suites + **161/300 deployments** (all `staging` = docs previews) | Docs platform; biggest deployment producer |
| Qodo Code Review | `qodo-code-review` / qodo-ai | 41/2,000 comments + reviews | Peer reviewer (orchestrator tracked opt-in) |
| GitHub Advanced Security | `github-advanced-security` / github | **NEW 2026-10-23** — 5 check suites in the 30-head window (4 success / 1 neutral, CodeQL; first seen 2026-10-23 ~04:05 PDT on `547f54e7`); submitted reviews in sample | Code scanning lane |
| Blacksmith.sh | `blacksmith-sh` / useblacksmith | suites on 30/30 heads | Hosted Actions runners (speed/cost lane) |
| Buildkite | `buildkite` / buildkite | **NEW 2026-10-23** — 2 check suites in the 30-head window (1 success, 1 failure; first seen 2026-10-23 ~02:59 PDT) + new repo webhook (id 702058218, all events, last 200 OK) | External CI lane — arrived with no repo-side workflow; who set it up NOT ESTABLISHED from API evidence |
| Codecov | `codecov` / codecov | suites on 30/30 heads + `CODECOV_TOKEN` secret | Coverage lane |
| Hark | `hark` / Adcock-AGI-Inc | suites on 30/30 heads | Agent surface (MAP §B7); its GitHub App is one of its connections |
| LaunchDarkly agent | `launchdarkly-agent` / launchdarkly | suites on 30/30 heads | AgentHQ flag/agent-task lane — no visible task use yet (§9 C6) |
| Pulumi | `pulumi` / pulumi | suites on 30/30 heads | IaC lane |
| Dependabot | `dependabot` / github | 3 contributions; `dependabot.yml` present; Dependabot secrets 0; automated security fixes **disabled** | Dependency lane, partially wired (§9 I6) |

## 5A. Org installations — retrieved live (LIVE-API + PROBE cross-verified)

`GET /orgs/{org}/installations` answers both chat-side (owner PAT) and from
inside Actions with the stored classic admin tokens — identical results from
four independent credentials. All installations are `repository_selection: all`,
none suspended.

| Org | App | Installed | Permission keys (non-none) |
|---|---|---|---|
| Research-Astute | google-labs-jules | 2026-08-05 | actions, administration, artifact_metadata, checks, contents, deployments, issues, members, pull_requests, security_events, workflows |
| Research-Astute | render | 2026-08-10 | actions, checks, contents, deployments, environments, issues, pull_requests, repository_hooks, statuses, vulnerability_alerts, workflows |
| Research-Astute | manus-connector | 2026-08-20 | actions, administration, attestations, contents, dependabot_secrets, environments, issues, organization_projects, organization_personal_access_token_requests, pull_requests, repository_custom_properties, repository_projects, workflows |
| Research-Astute | mintlify | 2026-08-22 | checks, contents, deployments, issues, pull_requests |
| Research-Astute | blacksmith-sh | 2026-08-25 | actions, checks, contents, issues, members, organization_self_hosted_runners, pull_requests, workflows |
| Research-Astute | codecov | 2026-09-24 | administration, checks, contents, issues, members, pull_requests, statuses |
| search-astute-ly | manus-connector | 2026-08-20 | (same as Research-Astute) |
| search-astute-ly | mintlify | 2026-08-22 | checks, contents, deployments, issues, pull_requests |
| search-astute-ly | blacksmith-sh | 2026-08-25 | actions, checks, contents, issues, members, organization_self_hosted_runners, pull_requests, workflows |

**Token capability matrix (PROBE receipts, run 39639440245):**

| Token | Class | `GET /user` | `/user/installations` | `/orgs/{org}/installations` |
|---|---|---|---|---|
| `OPERATOR_GITHUB_TOKEN` | Classic, full-admin scopes | 200 | 403 (app-authorized token required) | **200** |
| `OPERATOR_TOKEN` | Classic, full-admin scopes | 200 | 403 | **200** |
| `RECON_INTEL_GITHUB_WRITE_TOKEN` | Classic, full-admin minus delete:packages | 200 | 403 | **200** |
| `ARCHWIZ_GITHUB_TOKEN` | Fine-grained | 200 | 403 (not accessible by PAT) | 404 |
| `MUSE_ADMIN_GH` (chat-side) | Classic, near-full admin | 200 | 403 | **200** |
| Workflow `GITHUB_TOKEN` (control) | Installation token | 403 | 403 | 403 |

**Established boundary (with receipts, not assumption):** the *personal
account's* installation list is refused to every credential class the fleet
holds — GitHub reserves it to access tokens authorized to a GitHub App. The
org slice above is fully enumerable and now enumerated; the personal slice is
reconstructed from activity (§4/§5). `GH_PAT`, named as a stored secret in
#184's comments (2026-09-24), is **not** in the live 37-name repo secret list —
the name has drifted or moved since September; recorded as a names-drift
finding, not used by the probe.

## 5B. The personal account itself — `timerloggedout-spec` (LIVE-API, census v3)

The personal-account counterpart to §5A, derived two ways: direct identity
endpoints, and a **cross-repo check-suite census** — head commits of the 60
most recently pushed personal repos. An app's suite on a repo's head proves
the app receives and acts on events for that repo; the pattern across repos
shows the apps' *effective reach*. (The installation *records* for the
personal account remain behind the §5A proven boundary; this section is
activity evidence, labeled as such.)

**Cross-repo result:** only **10 of 60** repos show any app suites on their
head commits; 3 of those show GitHub Actions only. The full cluster
(19–24 apps) appears on exactly **7 repos**:

| Repo | Apps on head | Notes |
|---|---|---|
| `termux-monorepo` | 24 | The hub (§5/§6) — **+Buildkite this poll** |
| `timerloggedout-spec.github.io` | 24 | The user-site repo carries the same full cluster — **+Buildkite this poll** |
| `gh-aw-mcpg_fork` | 22 | Missing github-pages vs hub |
| `gh-aw_fork` | 22 | Same |
| `agentos_fork` | 20 | |
| `gpt4free_fork` | 20 | |
| `zero` | 19 | |
| `cubicle_fork`, `deepbiology-lab_fork`, `redamon_fork` | 1 each | GitHub Actions only |

Per-app spread across those repos: the core 19 apps (Cursor, Gitar, CodeRabbit,
Mistral, Devin, Vercel, Render, Travis, Sentry, LaunchDarkly, Codacy, Aikido,
BlocksOrg, Tembo, Graphite, Mintlify, Kilo, Pulumi, Blacksmith) appear on all 7
cluster repos; **Codecov on 5, Hark on 4, GitHub Pages on 2** (hub + user-site),
**Buildkite on 2** (hub + user-site — new 2026-10-23).
Reading: the review/deploy app cluster's reach covers all seven cluster
repos, not just the hub — consistent with all-repositories
installations — while Codecov/Hark/Pages act only where their specific
triggers fire. The three other recently pushed repos in the sample
(`cubicle_fork`, `deepbiology-lab_fork`, `redamon_fork`) show GitHub Actions
only and sit outside the cluster; the other 50 repos' heads predate or never
triggered the apps.
**Webhooks:** among the top 15 pushed repos, only the hub has any (§6).

**Sign-in & identity inventory (direct endpoints, 2026-10-21):**

| Surface | Firsthand result |
|---|---|
| Account email | **1** — primary, verified, public (the account's Gmail address) |
| SSH authentication keys | **1** — `DeepSeek_Account-1_ssh` |
| GPG keys / SSH signing keys | 0 / 0 |
| Social accounts | 1 — generic → `termux-monorepo.vercel.app` |
| 2FA | **On** |
| PATs | §2a — 2 fine-grained + 5 classic (#184) + `MUSE_ADMIN_GH` |
| Authorized OAuth / GitHub Apps (current count) | NOT enumerable via API (§5A boundary) — #184 Aug-13 floor (31 / 38) + **29 distinct apps observed active** across personal repos in this census |
| Login sessions / devices | **Not exposed by any GitHub API** — exists only in the web UI security log; no API record is claimed here |

## 6. Hub-repo wiring (LIVE-API, termux-monorepo)

| Piece | State |
|---|---|
| Webhooks (4) | **Linear** — all events (`*`), last 200 OK · **GitLab mirror** — push+PR → `gitlab.com` project 85129320 mirror/pull, last **400** · **ZenHub** — 12 event types, last **422 misconfigured** · **Buildkite (NEW 2026-10-23)** — all events (`*`), last 200 OK (id 702058218) |
| Workflows | **205 total, 204 active, 1 manually disabled** (+4 since the 2026-10-23 09:48 PDT poll, all verified as live files on master: `vantage-cost-report.yml` (Vantage cost report, created 10:30 PDT), `operator-wake.yml` (Operator wake, 12:21 PDT), `delphi-intake.yml` (Delphi conversational intake, 13:37 PDT), `target-intake.yml` (target intake — T.A.K. input layer, PR #1597, 14:36 PDT); the one disabled workflow is Merge Promotion Queue (disabled_manually); note the API registry total also carries phantom entries for deleted workflow files — 176 workflow files are actually on master; still no repo-side Buildkite workflow — the Buildkite lane is webhook/check-app only). Recent 100 runs: actors `timerloggedout-spec` 62 (owner-attributed — schedule + dispatch surface; which specific token fired each run is NOT ESTABLISHED, see the closing list), vercel[bot] 29, ecc-tools[bot] 9; events workflow_run 40, issue_comment 60 — owner-attributed + Vercel deploy runs dominate this window; CodeRabbit review activity continues in the updated-PR frame, so no lane outage |
| PR / issue totals (v2, fully paginated) | **1,374 PRs** — authors: owner 1,063 (+10 since the 09:48 PDT poll), Jules 288 (+1), CodeRabbit 9, github-actions 5 (+1), Dependabot 3, ECC 3, Devin 2, Tembo 1 · **220 true issues** (owner 198 (+7), github-actions 21, mehvvy 1) · requested-reviewer records sit almost entirely on the owner (10) — the peer bots are triggered by comments/orchestrator, not by review requests |
| Submitted reviews (two frames — keep separate) | *Most-recently-updated 150 PRs:* 35 PRs carry 251 reviews — Devin 139 (all COMMENTED; 92 still on #143), CodeRabbit 66 (42 CHANGES_REQUESTED / 6 APPROVED / 17 COMMENTED / 1 DISMISSED), owner 26 (24 COMMENTED / 2 APPROVED), Aikido 12, GHAS 7, Qodo 1. *Most-recently-created 150 PRs:* 22 PRs carry reviews — CodeRabbit 37 (23 CHANGES_REQUESTED / 10 COMMENTED / 4 APPROVED), owner 18 (all COMMENTED), GHAS 7. Review weight lives on long-lived PRs |
| Comment actors (2,000 newest) | Only **10 distinct actors**: ECC 792 (40%), owner 475, github-actions 263, CodeRabbit 155, Codex 105, BlocksOrg 81, Gitar 54, Qodo 54, Vercel 13, Jules 8 — **bots ≈ 76% of volume** |
| Actions permissions | Enabled, allowed_actions = all, SHA pinning not required. Default workflow permissions = **write**; workflows **can approve PR reviews** (`can_approve_pull_request_reviews: true`) — a real mesh capability: the repo's own automation can act as an approver |
| Deploy keys / autolinks / collaborators | **0 / 0 / owner only** — no deploy-key or autolink integrations exist on the hub repo |
| Pages | Legacy build from `gh-pages` branch, https enforced, `timerloggedout-spec.github.io/termux-monorepo/` |
| Environments | 14 (listed §2c) — deployment targets exist for help-wanted-dash / oversight / mcp-hub / termux-monorepo in Preview + Production pairs |
| Deployments (300 sampled) | Mintlify 153 (staging/docs) · Vercel 96 (Preview/Production per app) · GitHub Pages 51 |
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
| CI / checks | GitHub Actions (201 workflows) | Blacksmith runners, Travis (duplicate signal), Buildkite (new 2026-10-23, external CI — webhook/check-app only), github-advanced-security CodeQL suites (new 2026-10-23, code scanning) | Travis duplication, §9 I4 |
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
| I1 | ECC check runs come from the repo-side mirror, not from any settings approval | ECC is the top bot actor (**915/2,000 comments, 46%**) but publishes **zero** check runs because the vendor app requests **no Checks permission in its own configuration** (`GET /apps/ecc-tools`) — no owner approval exists to give, in any UI. **Done as build, not as an ask — MERGED 2026-10-22 (PR #1491, e6c4d342):** a `Mirror ECC audit outcomes to check runs` **step** folded into the existing `sweep-prs` job of `agent-ecc-tools-ops.yml` (+ `checks: write` on that job only — zero new jobs, zero new executions; trigger accounting per the owner's rule), republishing ECC's own audit conclusions as evidence-only check runs on the existing sweep cadence (06:23/18:23 UTC) | Landed and verified on master (step + `checks: write` present, no standalone job). First execution on the next regular ecc-ops sweep; vendor adding Checks app-side would supersede the mirror |
| I2 | Repair the GitLab mirror webhook (400) | Mirror is the redundancy lane for the whole repo; 3 GitLab secrets exist to support it | Check GitLab project 85129320 mirror state; re-ping hook via API |
| I3 | ZenHub: repair the 422 webhook **or** retire the lane deliberately | Board duplicates Linear (the working spine). A dead webhook firing 12 event types is pure noise | Owner decision; either fix config in ZenHub or remove hook + OAuth in one recorded move |
| I4 | Resolve Travis CI duplication | Travis suites on every master head while Actions is the real CI — double signal, double noise in the gate | Verify whether Travis runs any unique job; if not, park it as a recorded decision (not a silent clearing) |
| I5 | Keep Vercel moves quota-first | Daily deploy cap already tripped once (2026-10-20); Mintlify (161) + Vercel (91) dominate deployment volume | Batching cooldown (vercel-batch-deploy, 6h) + ignore-step guard; no new deploy-producing integrations until cap behaviour is measured |
| I6 | Finish Dependabot wiring | `dependabot.yml` exists, secrets 0, automated security fixes disabled | Enable security fixes; keep Dependabot in the peer-cadence (batched, SHA-bound) |
| I7 | Enforce the review-cadence matrix | 9+ review bots, ECC flooding documented (#1441: 207 comments) | peer-review-orchestrator: required = CodeRabbit; Qodo/Devin/Copilot tracked opt-in; Gemini only after peers (quota save); ECC via its 6h-debounced ops workflow for commands — the App's per-push audits stay, threaded not muted |
| I8 | Disposition the four **permission-update requests** (§4B, OWNER-UI 2026-10-22) | coderabbitai, Cursor, Devin.ai Integration — the three most active review/agent lanes — plus Factory Droid have updates awaiting owner approval in Settings → Installed GitHub Apps; unapproved updates can cap the lanes' newer features at their old permission sets | Owner-UI items of record: approve the three active lanes' updates after reading the requested deltas; read Factory Droid's request deliberately first (dormant app, expanded scope). Recorded here so the state is tracked — not a blocker for any fleet work, and never escalated to a browser session |

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
only), environment/workflow counts, deployment-creator mix. Per the owner
order of 2026-10-22, findings land **on GitHub**: material diffs are posted
as `[MUSEai]` comments on the standing thread (Issue #1505), and when a diff
materially stales this doc the poll opens a doc-refresh PR and merges it
through the repo gates — no staging, no per-step asks. **No change = no
comment, no report.** Snapshots stay in
`~/workspace/github-integration-census/` — never committed (rule 4).

## NOT ESTABLISHED — stated, not filled in

- **Personal-account installation records** (the per-app All vs Select list
  for the user account itself) — the *org* slice is now ESTABLISHED (§5A,
  retrieved live four ways), and the Installed tab's **A–H portion is now
  evidenced owner-firsthand** (§4B, 2026-10-22). What remains NOT
  ESTABLISHED: the Installed list's remainder past H, the per-app All-vs-Select
  repository scope for the personal account, and the API route itself — a
  **proven boundary**: `/user/installations` refused all five credential
  classes the fleet holds (PROBE receipts, §5A) because GitHub reserves it to
  App-authorized tokens. §3+§4+§4B+§5 remain its answer of record. Closed
  item; not a step the owner is asked to perform.
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
