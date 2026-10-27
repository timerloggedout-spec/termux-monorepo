# Agent-Era Forge & Versioning Comparison — Entire/Trails, Anthropic Scion/Antique, Cloudflare Artifacts vs the fleet's GitHub matrices

**Compiled:** 2026-10-26 (MVT/DoE/Telemetry research lane, [MUSEai] main-lane assignment).
**Status:** research note + posture recommendation. Not a lane: see §5 for why, and for the revisit triggers.
**Question put to this lane:** where do the new agent-era git/versioning systems sit against our existing matrices — the Integration Mesh Matrix, the reviewer JIT / reviewer-metrics system, the peer-review orchestrator + review lanes (Laya/Kev/Jev), and Provenance/HindSight weighting (3L0 / Moneyball / MVT / DoE)?

## 1. Subjects, verified from primary sources

### 1.1 Entire — the forge with Trails (launched 2026-10-26)

Source: Entire's own launch post, "Entire Launches an Independent Git Forge for Agent-Human Collaboration" (entire.com, 2026-10-26); GeekWire coverage same day.

- Entire was founded by Nat Friedman (former GitHub CEO); $60M seed closed February 2026. Its first releases were repo mirroring and the open-source Entire CLI, which captures agent sessions (prompts, transcripts, files touched, tool calls, token usage) as Checkpoints tied to commits. The forge itself was unveiled 2026-10-26 under CEO Thomas Dohmke (also a former GitHub CEO).
- **Trails** replace pull requests: a heads-up display where customized evals are **scored by agents on every push**. Per-trail token spend is displayed. When all evals are satisfied, the change can merge without a human reading the code. Teams can still require human sign-off or passing tests before merge. Agents can address findings in a loop; all Trail data is exposed through the web UI and the open-source CLI.
- **Hosting:** a new Git-compatible source control server; pushes "up to 89x faster than GitHub" (vendor claim, not independently measured). Private repositories hosted natively in US / EU / India / Australia regions. **Public repositories and self-hosted Git nodes are upcoming features, not available at launch** — this repo is public, so it could not move today even if it wanted to.
- **CI is not GitHub Actions.** CI runs through Buildkite and Depot partnerships; Actions workflows migrate via Buildkite's `bk pipeline convert` or Depot CI (which runs Actions-format workflows).
- **Continuous Memory:** agent sessions sync into the repository and stay searchable to agents — a codebase graph plus an "agentic brain" over past sessions/prompts; vendor claims up to 71% token savings.
- Access: "available to every developer today" (private repos). Pricing was not stated in the launch post.

### 1.2 Anthropic Scion + Antique — yes, the other one was Anthropic (2026-10-13)

Source: Anthropic engineering blog, "Redesigning source control at Anthropic" (2026-10-13), as reported by DevOps.com, The Pragmatic Engineer (with team follow-up), and others.

- **Scion** is a version control system Anthropic built in-house and migrated its internal monorepo onto, off Git, in five months (seven engineers). The unit of work is a **changeset**, recorded in a write-ahead log; metadata in Google Spanner, blobs in content-addressed cloud storage; server and client in Rust. Client-server by design: clients are assumed always online, keep bounded local caches, and get sparse/virtualized checkouts; the server answers history/blame/merge queries by API.
- **Antique** is the companion code review and code-management platform (Go + React). It supports **semantic constraints on approvals** — comment-only changes are treated differently from sensitive logical changes — and humans still review every change, but examine intent rather than reading every line.
- Why: merged changes rose from ~2,500/day (May 2026) to **over 30,000/day** (September 2026), attributed to Claude agents; main-branch history ~100 GB; ~25M CI checkouts/day. Reported results (vendor figures): source-control time per change request 34 min → 3.7 min; CI checkouts ~8.8x faster; supporting infrastructure ~200x smaller than the Git-mirror fleet it replaced.
- **Scion is not a product.** Closed source; Anthropic states it is not a general-purpose Git replacement and will not be released. Anthropic says it will share the architecture with GitHub, GitLab, and open-source maintainers instead.
- Name caution: unrelated to Google's "SCION" agent-orchestration testbed, which uses Git worktrees.

### 1.3 Cloudflare Artifacts — Git for agent state (open beta 2026-10-01)

Source: Cloudflare blog, "We want you to build the next Git platform on Cloudflare" (2026-10-01) and the Artifacts announcement coverage.

- A Git-compatible repository store driven programmatically from Cloudflare Workers (create / get / fork via bindings, short-lived access tokens). Cloudflare's guidance is **one repo per unit of autonomous work** — repo-per-agent instead of many agents contending on one branch.
- Positioned as version control for **agent state/memory**, not as a code-review or forge replacement; the merge-back layer is explicitly left open (Cloudflare ran a public contest for it).
- Open beta on the **Workers Paid** plan. Pricing: 10,000 operations + 1 GB storage included monthly, then $0.15 / 1,000 operations and $0.50 / GB-month; each repo capped at 1 GB. Repository events can trigger workflows (e.g. reviews); usage metrics are queryable for dashboards.
- This fleet already operates Cloudflare (the device pull-queue Worker + D1), so Artifacts is the only one of the three subjects deployable here today without a new vendor relationship.

## 2. The incumbent position this is compared against

The fleet's review and coordination system is GitHub-native and already measured:

- **Coordination plane:** GitHub issues/PRs/comments are the invocation and coordination surface for every lane ([MUSEai] comments, target-brief intake, Jules sessions sourced from this repo). The credential inventory of record is Issue #184; the Integration Mesh Matrix censuses the app surface from the live API.
- **Review plane:** the peer-review orchestrator dispatches provider reviewers per PR context; reviewer settings are JIT-adapted and measured by the reviewer-metrics collector (provider × context map, refreshed via PR #1634). On the current 150-PR map: **CodeRabbit delivery is 0.173** (23 of 133 required cycles), **35% of cycles end in provider cooldown**, median delivery latency ~473s, and bot-authored PRs run 0-for-10 (CodeRabbit seat declined by owner decision; bot PRs proceed without it). The measured bottleneck is **reviewer delivery** — providers not showing up — not diff readability, push speed, or merge mechanics.
- **Weighting plane:** Provenance/HindSight is the attribution layer being initialized for 3L0 / Moneyball / MVT / DoE weighting. Fleet rule: weights come from firsthand-measured delivery, never from vendor-reported scores.

## 3. Comparison on the fleet's axes

| Axis | Entire / Trails | Anthropic Scion / Antique | Cloudflare Artifacts | Fleet incumbent (GitHub + orchestrator/JIT) |
|---|---|---|---|---|
| What it replaces | The pull request (review + merge UX) | Git itself, plus the review surface | The shared-branch assumption for agent work | — |
| Evaluation model | Agent-scored evals per push; merge when evals pass; optional human sign-off / test gates | Human review of every change, intent-first, with semantic approval constraints | None (no review model; events can trigger external review) | Delivered peer reviews (human + provider bots) gated by repo checks; measured per provider × context |
| Telemetry emitted | Eval scores, per-trail token spend, session traces (Continuous Memory); exposed via web UI + open-source CLI | Internal only; nothing emitted to anyone else | Repo operation metrics (ops, pulls, pushes, errors) via dashboard/API | Run/check/comment evidence on GitHub; reviewer-metrics map; HindSight/Provenance records |
| Feedable into MVT/DoE weighting? | Scores: **no** (vendor-side, unmeasured — violates firsthand-counts rule). CLI-exported data (incl. token spend): potentially, after own measurement | No (closed, internal) | Metrics are operational, not evaluative; could feed capacity/quota lanes, not review weighting | Native — the weighting is computed from this telemetry |
| Sign-off gates | Configurable: human sign-off or passing tests can be required | Humans review every change (semantic constraints) | N/A (storage layer) | Repo gate + smoke checks; approval/merge remain the PR's own gates |
| Fit with this repo | **Poor today:** public repos not yet supported; CI must leave Actions (Buildkite/Depot); coordination plane (issues, comments, Jules sourcing, mesh poll, ~205 workflows) is GitHub-native | None — not available at any price | **Complementary:** agent-state versioning alongside GitHub, on a vendor the fleet already runs | — |
| Migration cost / lock-in | Forge move = control-plane move: hosting, review, CI, and coordination all change at once; young vendor, launch-day surface | N/A | Low: additive, per-lane, Git-compatible remotes; beta + 1 GB repo caps bound the shape | — |
| Access today | Live for private repos; public repos upcoming | Never (internal, closed) | Open beta, Workers Paid plan | Live |

## 4. Findings

- **F1 — Trails productizes a layer the fleet already built, one level down.** Agent-eval scoring with loop-back findings is the peer-review orchestrator + JIT metrics concept, moved into the forge. Moving would trade a measured, self-owned system (with known delivery rates per provider and context) for vendor evals whose scoring is neither inspectable nor measured by us. The fleet's problem is that reviewers don't deliver (0.173, cooldown-bound); Trails changes who reads the diff, not whether the evaluation arrives or what it is worth in 3L0 terms.
- **F2 — The genuinely new telemetry class is per-change agent cost.** Trails display token spend per change, and Entire's Checkpoints/Continuous Memory treat the agent session (idea, trace, outcome) as a first-class artifact. That is the closest external analogue to what HindSight/Provenance are being built to capture, and the CLI half of it works on ordinary GitHub repos today. If anything from Entire ever feeds MVT/DoE, it is this export surface — measured by us, not their scores.
- **F3 — Scion is a scaling data point and a design validation, not an option.** It cannot be adopted, piloted, or bought. Its value here: (a) an existence proof that agent merge volume breaks human-era VCS assumptions at ~30k merges/day — three orders of magnitude past this fleet's volume, so GitHub remains correctly sized for us; (b) Antique's semantic approval constraints independently validate the fleet's JIT direction (context-classed review requirements instead of one-size settings). The only channel through which Scion could ever reach this repo is Anthropic's promised architecture-sharing with GitHub/GitLab — watch GitHub's agent-era VCS work, not Scion itself.
- **F4 — Artifacts answers a different question.** Repo-per-agent state versioning complements the forge; it does not compete with it. Its natural comparison set in this fleet is the agent-state lanes (device pull-queue, session stores), and it is the only subject with a pilot shape available today. Beta status, the Workers Paid requirement, 1 GB repo caps, and the deliberately unsolved merge-back layer keep it there.
- **F5 — A forge move is a control-plane move, and the cost lands on coordination, not review.** Issues, comments-as-invocation, the #184 credential inventory, the mesh poll, quota lanes, Jules sourcing, and ~205 Actions workflows all presume GitHub. Entire additionally requires leaving Actions for Buildkite/Depot. That total cost is being weighed against a review-UX gain aimed at a bottleneck our own metrics say is elsewhere (provider delivery/cooldown).

## 5. Posture recommendation

**Watch.** No pilot, no adoption — both remain owner decisions, and on current evidence neither is warranted:

- **Entire (forge):** watch. Revisit triggers: public-repository support ships; a GitHub Actions story exists; the CLI's eval/token telemetry export proves stable enough to measure. If a future pilot is ever scoped, scope it to the **CLI/Checkpoints telemetry on this GitHub repo** (F2), not to a forge migration.
- **Anthropic Scion/Antique:** note-only. Closed and internal by the vendor's own statement; recorded here so the lane never has to re-identify it.
- **Cloudflare Artifacts:** watch, with the only live pilot shape of the three (agent-state lanes, existing Cloudflare account) — pilot decision is the owner's.

**Why notes and not a living lane:** two of the three subjects are inaccessible (one permanently, one until public repos ship) and the third is a beta storage layer with no evaluative telemetry — there is no recurring measurable surface yet on which MVT/DoE comparison entries could be kept current. If any revisit trigger fires, this note is the baseline the lane gets created from.

## Sources

- Entire launch post, entire.com, 2026-10-26: https://entire.com/news/entire-launches-an-independent-git-forge-for-agent-human-collaboration
- GeekWire, "Former GitHub CEO launches rival platform built for AI coding agents", 2026-10-26: https://www.geekwire.com/2026/former-github-ceo-launches-rival-platform-built-for-ai-coding-agents/
- Anthropic engineering blog, "Redesigning source control at Anthropic", 2026-10-13 (as reported): https://devops.com/anthropic-builds-its-own-source-control-after-ai-agents-outgrow-git ; The Pragmatic Engineer, The Pulse (team follow-up on Scion/Antique internals): https://newsletter.pragmaticengineer.com/p/the-pulse-anthropic-builds-its-own
- Cloudflare blog, "We want you to build the next Git platform on Cloudflare", 2026-10-01: https://blog.cloudflare.com/next-git-platform-on-cloudflare/
- Fleet figures: docs/ops/generated/reviewer-metrics.json (150-PR map, landed via PR #1634); docs/ops/INTEGRATION-MESH-MATRIX.md; docs/ops/REVIEWER-JIT-DESIGN.md.

## 6. Addendum (2026-10-26) — incumbent-platform telemetry: Copilot usage metrics API (`totals_by_client`)

[MUSEai]@{role:{copilot-metrics-lane}} — added under the main lane's MVT/DoE/Moneyball telemetry comparison assignment. Companion entry: `copilot-usage-metrics-api` in `config/agent_stack_integrations.json` (status HOLD).

**What changed.** GitHub changelog, 2026-10-23 ("Usage metrics API adds usage from tools like OpenCode"): the Copilot usage metrics API now counts model usage server-side from tools outside the IDE — OpenCode, Claude Code, Codex, Copilot CLI, cloud agent, code review, VS Code, JetBrains — closing the editor-telemetry gap that left such usage missing from `totals_by_ide`. A new `totals_by_client` array ships in the enterprise, organization, enterprise-user, and organization-user reports, 1-day and 28-day (in 28-day reports it appears inside each `day_totals`). Each entry carries `client`, `request_count` (successful model calls — **not prompts**; one prompt can trigger several calls), `session_count`, `token_usage` (prompt tokens, output tokens, average per request), and `totals_by_model` with `model_selection_mode` (`user_selected` / `auto` / `product_selected`; code-review and cloud-agent requests report `product_selected`, code-review models report `unknown`; unrecognized clients group under `other`). Access: enterprise owners and billing managers, organization owners, or a custom role granting `View Copilot Metrics`; the Copilot usage metrics policy must be enabled. Client labels come from the integration ID each request sends — GitHub's own wording: a best-effort grouping, **not a verified identity**. The change is additive; the array is empty when there is no usage to report. This is model-traffic counting, distinct from agent-app activity (jobs started by agent apps).

**Why it is compared here.** Provenance/HindSight attribute *delivered work* for 3L0 / Moneyball / MVT / DoE weighting. `totals_by_client` attributes the *model traffic behind the work* — which agent client, how many requests/sessions/tokens, which models, who selected them. That is the per-change agent-cost signal class flagged in F2, arriving from the incumbent platform rather than a challenger forge, and it is the first Copilot metrics surface that can see this fleet's actual agent clients (Claude Code, Codex, Copilot CLI) at all.

**Applicability — tested live 2026-10-26 via the PAT helper. Verdict: NOT APPLICABLE to this account today.**
- Personal account `timerloggedout-spec`: plan `free`; the API defines no personal-account report scope.
- Both organizations (Research-Astute, search-astute-ly): `GET /orgs/{org}/copilot/billing` returns `seat_breakdown` total **0** with seat management `unconfigured`; `GET /orgs/{org}/copilot/metrics` returns **404** for both. No Copilot seats exist in either org, so there is no usage for the reports to contain.
- What is **not** blocking: access role — `timerloggedout-spec` is admin of both orgs, satisfying the organization-owner leg. The installed "GitHub Copilot for Linear" app is an integration app, not Copilot seats, and confers no metrics access.

**Feedable into MVT/DoE weighting?** No signal exists today. If a fleet org ever holds Copilot Business/Enterprise seats with the usage-metrics policy enabled, the reports enter as a **cost/activity input only — never a score**: request/token volume measures traffic, not delivered value; client attribution is best-effort; server-side counts say nothing about outcomes. That is the discipline §3 and F1 applied to Trails scores, and the telemetry audit's rule that an absent metric is never read as zero work. **Revisit trigger:** the first Copilot seat purchase in any fleet org — re-test the report endpoints then.
