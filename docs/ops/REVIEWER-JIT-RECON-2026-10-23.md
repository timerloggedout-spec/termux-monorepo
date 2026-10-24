# Reviewer Settings JIT — Recon

**Scope:** timerloggedout-spec/termux-monorepo @ master, read live via the PAT helper on 2026-10-23 (~23:25–23:40 PDT). Recon only — no writes made.
**Directive being fed:** "CodeRabbitAI && others settings .yaml required to be JIT adapted to each context & mapped with performance metrics."
**Method:** full recursive tree (8,626 blobs, not truncated), contents reads of every reviewer-named file, Actions variables API, check-runs API, PR #1607 comments/reviews as the worked example, CodeRabbit vendor docs (docs.coderabbit.ai/reference/configuration, fetched 2026-10-23). Anything not read live is marked NOT ESTABLISHED.

---

## 1. Inventory — reviewer/provider settings surfaces

### 1.1 CodeRabbit — the only vendor settings file in the repo

| Surface | Detail |
|---|---|
| `.coderabbit.yaml` (repo root, 612 B) | **What it controls:** `reviews.profile: assertive`; `high_level_summary: true`; `request_changes_workflow: true`; `review_status: false`; `auto_review{enabled, drafts: true, auto_incremental_review: true, base_branches: [master, master-staging, feature/skyhook, deep_core/feat/reverse_engineered_deepseek_wasm_gh-worflows]}`; `finishing_touches.autofix.enabled: true`; `auto_apply_labels: true`; `chat.auto_reply: true`. Header pins the vendor schema (`coderabbit.ai/integrations/schema.v2.json`). |
| Static or context-sensitive? | **Static file, read by the CodeRabbit app at review time.** It contains no per-PR/per-author/per-path variation today: no `path_filters`, no `path_instructions`, no `auto_approvals`, no label/author gating — all unused (vendor-documented, see §4.1). The only in-file context axes the vendor offers are path globs, base-branch regexes, labels, and author-team/path approval overrides. |
| Consumer | The CodeRabbit GitHub App (`coderabbitai[bot]`) — external; nothing in-repo parses this file. |

### 1.2 The orchestrator — the actual control plane (`.github/workflows/peer-review-orchestrator.yml`, 37,512 B)

Single job `collect-peer-responses`, inline github-script JS. Triggers: `pull_request_target[opened, synchronize, ready_for_review, reopened]`, `issue_comment[created]`, `pull_request_review[submitted]`.

- **Provider registry is in code**, two maps:
  - logins → provider: `coderabbitai[bot]`→coderabbit, `qodo-code-review[bot]`→qodo, `devin-ai-integration[bot]`→devin, `aikido-security[bot]`→aikido, `sentry-io[bot]`→sentry, `copilot-pull-request-reviewer[bot]`→copilot.
  - check-app slugs for delivery evidence: same six providers.
- **Trigger commands** (OPERATOR posts them as comments): coderabbit `@coderabbitai full review`, qodo `/agentic_review`, devin `/devin review`. Aikido/Sentry/Copilot have **no command configured** — tracked for evidence only.
- **Policy inputs are repo variables with in-code defaults** (env block): `PEER_REQUIRED_PROVIDERS` (default `coderabbit`), `PEER_ENFORCE_PROVIDER_COMPLETION` (default `false` — pending evidence is advisory), `OPERATOR_EXECUTOR_LOGINS` (default repo owner), `OPERATOR_ALLOWED_ACTIONS` (default `coderabbit:trigger_review,qodo:trigger_review,devin:trigger_review`), `PEER_STATE_PUBLISHER_LOGINS` (default repo owner). Plus hardcoded `MAX_WAIT_SEC=1`, `POLL_SEC=5` (event-driven snapshots, not a waiting loop).
- **LIVE FINDING — the variable layer is unused:** the Actions variables API returns exactly **3 repo variables** (`DEVICE_QUEUE_URL`, `TERMUX_MCP_ENDPOINT`, `TERMUX_MCP_ENDPOINT_UPDATED_AT`). Every one of the five orchestrator variables returns 404 — **none is set**. All orchestrator policy today is the in-code defaults. Setting one is a JIT lever that needs no commit (see §4).
- **Already context-sensitive (landed 2026-10-23, PR #1628):** the collect step fetches the PR, detects bot authors (`user.type === 'Bot'` or `[bot]` login), and drops `coderabbit` from the *effective* required set, recording `not_required_bot_authored_pr` in the state comment; the OPERATOR request step consumes the effective set. This is the fleet's first JIT adaptation and the pattern to generalize.
- **State publication:** one SHA-bound comment per cycle (marker `<!-- agent-peer-response-state:v2 -->`), updated in place, carrying `cycle_id` (`pr-<n>-<sha12>`), `head_sha`, `cycle_started_at`, `state`, `ready`, `required_providers` (effective), `enforce_provider_completion`, per-provider delivery lines with evidence URLs and cooldown detail, and pending/operator-control lines.
- **Downstream consumers of that state:** the same workflow's "Dispatch verified second pass" step (fires `gemini-after-peers.yml` only when `state=responses_collected && ready=true`), and `gemini-after-peers.yml` itself, which re-reads the state comment and refuses to run unless the contract holds.
- **Cooldown parsing:** regex set over provider comments/reviews/review-comments — `review limit reached | review rate limited | action not completed | couldn't start this review | next (included) review (will be) available in <duration>` → provider state `provider_cooldown` with the parsed retry window.
- **Delivery definition (per provider, per SHA, within the cycle):** a review-comment or review by the provider's bot login bound to `head_sha` and not matching the non-review-notice patterns, or a completed+success check run whose `app.slug` matches the provider — with the operator-acknowledgement rule for checkbox-control providers.

### 1.3 Gemini lane (second pass + standalone) — settings live in workflows + a shared action

| Surface | Detail |
|---|---|
| `.github/workflows/gemini-after-peers.yml` (11,140 B) | `workflow_dispatch` only, inputs `pr_number`/`head_sha`/`cycle_id`; verifies the orchestrator state contract (§1.2), then routes through the model router and posts the second-pass review. Static gating, context = the verified cycle inputs. |
| `.github/workflows/gemini-review.yml` (7,373 B) | Standalone review entry; same model-router path; skips with a posted reason when the router says skip. |
| `.github/workflows/gemini-dispatch.yml` (8,730 B) | Event dispatcher (`pull_request`, `issue_comment`, `pull_request_review_comment`, `pull_request_review`) classifying commands into triage/review/invoke jobs; skips forks and drafts on PR events. Context-sensitive by event type and command — the lane's own JIT-ish routing. |
| `.github/workflows/gemini-triage.yml`, `gemini-invoke.yml`, `gemini-interactions-smoke.yml` | Sibling lanes in the same family (present in tree; contents not read in this recon — NOT ESTABLISHED beyond existence). |
| `.github/actions/model-router/action.yml` (composite, 4,094 B) | **The Gemini lane's real settings surface:** picks provider+model per role (`triage|review|invoke`) from a live catalog feed + which provider keys exist (omni/openrouter/felo/gemini presence inputs), with a versioned capacity cache (`/tmp/model-router`) and explicit outputs `provider, model, skip, reason, decision, decision_summary, catalog_state, routing_mode`. Already evidence-driven/context-sensitive by design. |
| `.github/actions/gemini-quota-gate/action.yml` | Quota gate action in the same family (existence verified; internals NOT ESTABLISHED in this recon). |
| `GEMINI.md` (repo root) | Context/instructions file for Gemini CLI agentic CI ("Context for Gemini CLI (agentic CI/CD)", hard rules incl. gate names) — a prompt-settings surface, static. |
| Quota substrate | `ops/quota/registry.json`, `ops/quota/provider-managers.json` (schema `provider-quota-managers/v1`, per-family status/reset/signals — self-described as an *offline registry of documented passive observations*, not an entitlement source), `scripts/provider_quota_service.py` + siblings. This is where Gemini/provider quota state is modeled for reconcile-before-dispatch. |

### 1.4 CellCog — advisory reviewer lane

`.github/workflows/cellcog-review.yml` (8,740 B): triggers on `pull_request` + `workflow_dispatch`; self-described "independent, ADVISORY (non-blocking) lane — modeled on deepseek-ci.yml"; builds a prompt from the PR diff and calls the CellCog API (key via secret, name only). **One variable-driven knob:** `CELLCOG_CHAT_TIER: ${{ vars.CELLCOG_CHAT_TIER || 'max' }}` — the variable is **not set** (not among the 3 repo variables), so it runs on the `max` default. No vendor config file in repo.

### 1.5 ECC Tools — app + repo-side ops lane

| Surface | Detail |
|---|---|
| `.claude/ecc-tools.json` (8,179 B) | `generatedBy: "ecc-tools"` (generated 2026-09-01 in-file): ECC profile/component selection — `profiles{requested, recommended, effective}` + aliases, `tier`, requested/selected/tier-filtered component and package lists, `referenceSetReadiness` (score 0/7 in-file). **Consumer is the external ECC Tools app**; code search finds no in-repo reader (only an evaluation artifact mentions the filename). Static snapshot — its `generatedAt` shows it is regenerated by the app, not hand-maintained. |
| `.github/workflows/agent-ecc-tools-ops.yml` (30,369 B) | The repo-side control lane: schedule `23 6,18 * * *` + dispatch modes (`sweep-prs`, `issue`), **6h debounce** on the PR-audit job, **12h debounce** in sweep, sweep cap 50 PRs, batched single comment per PR with overflow behavior, and the **check-run mirror step** (landed PR #1491): ECC's comment-only audit outcomes are re-published as evidence-only check runs at each swept PR's current head SHA. ECC itself has no checks permission (vendor design) — the mirror is how ECC evidence enters the check-run surface. |

### 1.6 Feedback consumer — `agent-review-auto-jules.yml` (15,436 B)

Not a settings surface but part of the loop JIT design must respect: triggers on `pull_request_review` / `pull_request_review_comment` / `issue_comment` from **bot reviewers** (coderabbit, qodo, devin, copilot named in its `if:` conditions), non-`approved` states, and routes substantive feedback to Jules for disposition. Provider-owned control checkboxes are explicitly excluded (those stay in the orchestrator's operator path).

### 1.7 Adjacent / non-review

- `.github/workflows/dependency-review-advisory.yml` — path-filtered (lockfile/manifest globs) advisory dependency review; path-context-sensitive by trigger design.
- `.devin/wiki.json` (3,388 B) + `reconcile-devin-wiki-access.yml` — Devin **wiki** access config/reconciliation, **not** PR review settings.
- `.coderabbit.yaml` is the **only** vendor reviewer config file in the entire tree. Tree scans for `qodo`, `copilot`, `aikido`, `sentry` config filenames return **zero** files: Qodo, Devin (review), Copilot, Aikido, and Sentry have **no repo-side settings files** — they exist only as entries in the orchestrator's login/check-app maps (§1.2) and the auto-jules conditions (§1.6).
- Sweep evidence store: `docs/ops/generated/sweep-ledger/` — **1,171 files** in tree (per-PR sweep receipts, JSON).
- Repo scale context: 180 workflow files under `.github/workflows/`.

---

## 2. Context signals available at review time

| Signal | Available today? | Where |
|---|---|---|
| PR author login + type (Bot/User) | **Yes — already consumed** | Orchestrator collect fetches the PR (`pr.user`) and uses it for the bot exemption (PR #1628). |
| Head SHA / cycle identity | **Yes** | `cycle_id = pr-<n>-<sha12>`, `head_sha`, `cycle_started_at` in every state comment. |
| Draft / fork status | **Yes** | Orchestrator skips drafts and forks (`out_of_scope_pr`); gemini-dispatch also gates on both. |
| Provider cooldown state | **Yes** | Parsed from provider notices into state comments (`provider_cooldown` + retry window). |
| Orchestrator cycle state (pending/ready/per-provider state) | **Yes** | State comment fields + provider lines; consumed by gemini-after-peers. |
| Changed files / paths | **Plumbing exists, not captured in state** | Orchestrator does not fetch the file list; the PR files API is already used elsewhere in the fleet, and CodeRabbit's own `path_filters`/`path_instructions` + dependency-review's `paths:` triggers prove path context is actionable. Would need a new fetch in collect + new state fields. |
| Change type (docs/code/workflow/config/tests) | **Not captured** | Derivable from changed-file paths; no current surface records it. NOT ESTABLISHED anywhere in the review path. |
| PR size (additions/deletions/files count) | **Not captured in state** | Present on the PR object the orchestrator already fetches (`additions`, `deletions`, `changed_files` fields) — zero new API cost, just not recorded. |
| Labels | **Not captured in state** | Present on the fetched PR object; CodeRabbit can also gate on labels vendor-side (§4.1). Not currently read by the orchestrator. |
| Base branch | **Partially** | CodeRabbit config enumerates 4 base branches; orchestrator doesn't record base ref in state. PR object carries it. |
| Review history on the PR (prior cycles, re-review count) | **Partially** | Prior state comments persist per cycle (one comment per cycle_id), so cycle history is reconstructable from the comment thread; no surface aggregates it. |
| Provider quota state | **Separate lane** | `ops/quota/*` + quota service model provider quota; the orchestrator itself only sees cooldown notices, not quota balances. Joining the two is new plumbing. |

**Worked example (live, PR #1607, Jules-authored):** 24 comments — ecc-tools[bot] 12, owner 4, github-actions[bot] 3, coderabbitai[bot] 3, jules 1, blocksorg[bot] 1; **0 reviews**. The state comment for cycle `pr-1607-a7609cd0d1c0` (cycle_started_at 2026-10-23T23:37:01Z — *before* PR #1628 merged) still shows `required_providers: coderabbit`, `state: awaiting_provider_response`, `ready: false`; CodeRabbit's own comment is the "Review skipped — authored by a bot without [an assigned seat]" notice. This is the before-picture the exemption fixes on the next cycle, and a ready-made labeled sample for metrics work.

---

## 3. Performance metrics — what exists / is collectible per provider

### 3.1 The metrics map shape

Join key available today: **provider × PR × head SHA × cycle** (from state comments), extensible to **provider × context × metric** once §2's uncaptured context (author class, paths, size, labels) is recorded per cycle.

| Metric | Source today | Status |
|---|---|---|
| Delivery latency (cycle start → provider delivery) | State comment `cycle_started_at` + evidence timestamps (review `submitted_at`, review-comment `created_at`, check-run `completed_at`) via the reviews / review-comments / check-runs APIs the orchestrator already calls | **Collectible now** — every input is already fetched during collect; nothing persists the delta. |
| Delivery success / skip / cooldown per cycle | State comment `state`, per-provider lines, `pending`; CodeRabbit skip is itself a comment artifact ("Review skipped", seen live on #1607) | **Collectible now** from comment census per provider login. |
| Cooldown frequency + parsed retry windows | State comments (`provider_cooldown` + detail) | **Collectible now.** |
| Approvals vs changes-requested vs comment-only | Reviews API `state` per provider login | **Collectible now** (orchestrator fetches all reviews per cycle). On #1607: 0 reviews from anyone — a data point, not an anecdote, once aggregated. |
| Comment volume per provider per PR (noise proxy) | Issue-comments API grouped by bot login | **Collectible now.** #1607 sample: ECC 12 comments vs CodeRabbit 3 vs 0 reviews — volume and delivery are wildly decoupled per provider. |
| Actionable-vs-noise ratio | Review-comment threads + resolution state; agent-review-auto-jules dispositions (it already classifies bot feedback as substantive vs control noise) | **Partially** — thread resolution is API-visible; "actionable" labeling exists implicitly in the auto-jules lane's behavior but is NOT ESTABLISHED as a stored metric. |
| Re-review count per PR | Distinct `cycle_id`s per PR in the comment thread | **Collectible now.** |
| Quota burn per provider | `ops/quota/registry.json` + `provider-managers.json` + `scripts/provider_quota_service.py` (documented caps/cooldowns/resets per family); CodeRabbit cooldown notices are the burn signal visible in the review path | **Partially** — registry is documented-observation grade, not live balances (its own contract says so). |
| ECC audit outcomes | ECC comments + the check-run mirror (one evidence check run per kind per swept PR head) + `docs/ops/generated/sweep-ledger/*.json` (1,171 receipts) | **Exists in-repo.** |
| Actions-side cost/latency of the review lanes themselves | `ops/github-telemetry/` (config `metric-policy.yaml` = `actions-perf-v1`: queue/runtime/wall latency definitions, failure-conclusion rules, 7/30/90/365-day windows, dimensions workflow×job×branch×event×runner×conclusion) + `ops/github_telemetry/` collector/reducer + `github-telemetry-snapshot.yml`; UI-reconciled CSVs in `docs/ops/generated/actions-metrics-*.csv` | **Exists** — but its dimensions are workflow/job, **not provider**; a provider dimension is the new join. |
| Weighting machinery to consume metrics | `ml/pipelines/moneyball/` (`scorer.py` scores PRs on gates/base/size/tests/age via `weights.py`; `quota_weights.py`), `deepcli/deepcli/observatory/doe.py`, `.github/workflows/agent-mvt-experiment.yml` / `team-mvt.yml` / `hex-moneyball-evidence.yml`, `docs/ops/ATES-ORCHESTRATOR-DOE-MVT.md` | **Exists for PRs/quotas — NOT ESTABLISHED for reviewer providers.** No file found maps provider performance into weights today; that mapping is the design work this recon feeds. |
| HindSight / Provenance telemetry | `agent_telemetry_stream.json` (root), `.github/workflows/deploy-hindsight.yml` / `fly-hindsight-config.yml` / `koyeb-hindsight-deploy.yml`, `docs/ops/sessions/HINDSIGHT.md`, provenance audit lane (`rindig-provenance-audit.yml`, `docs/ops/RINDIG-PROVENANCE-AUDIT.md`) | **Exists as attribution/telemetry substrate**; no reviewer-provider performance schema found in it (NOT ESTABLISHED). |

### 3.2 Raw-data locations (all verified in tree or live API)

1. **Orchestrator state comments** — per PR, per cycle: the single richest provider-performance record (timestamps, states, evidence URLs, cooldowns).
2. **Reviews / review-comments / issue-comments APIs** — per-provider-login census (volume, states, timestamps).
3. **Check runs** — provider app slugs on PR heads (CodeRabbit/Qodo/etc. when they publish checks; ECC only via the repo mirror). Note: master-head commits carry only `github-actions` suites (78/78 on head `a2178ba0` at recon time) — provider check evidence lives on PR heads, not master.
4. **`docs/ops/generated/sweep-ledger/*.json`** — ECC sweep receipts (1,171 files).
5. **`ops/github-telemetry/` + `ops/github_telemetry/`** — Actions performance pipeline with a governed metric policy.
6. **`ops/quota/*`** — provider quota/cap/cooldown registry (27 families; documented-observation grade).

---

## 4. JIT levers per provider — REAL vs speculative

### 4.1 CodeRabbit

**REAL (vendor-documented at docs.coderabbit.ai/reference/configuration, fetched 2026-10-23; schema pinned in the repo file's header):**
- `reviews.profile`: `quiet | chill | assertive` — the single biggest volume/quality knob (repo runs `assertive`).
- `reviews.path_filters` (globs, `!` exclusions) and `reviews.path_instructions` (per-path review guidance) — **path-context adaptation inside the static file**; unused in the repo today.
- `reviews.auto_review`: `enabled`, `drafts`, incremental review on push, **auto-pause after N reviewed commits** (default 5), **title-keyword skips**, **label gating** (positive labels opt in, `!label` excludes), **base_branches as regex**, and an **ignore-authors username list**.
- `reviews.auto_approvals`: automatic approval with **max merge/security risk limits** and **overrides matched by author team and/or changed paths** — genuine author×path context-sensitivity, vendor-side (repo does not use it; repo instead uses `request_changes_workflow`).
- `reviews.pre_merge_checks` (docstring/title/description/linked-issue/custom — `off|warning|error` modes), `reviews.tools.*` toggles (shellcheck, ruff, ast-grep, …), `knowledge_base` learnings, finishing touches incl. autofix.
- **Constraint that shapes the design:** the file is one repo-level file read by the app per review. There is no per-PR config file selection — so *true per-context JIT* for CodeRabbit = (a) exploit the in-file context axes above (paths, labels, base-branch, author overrides), and/or (b) **generated config commits** — a lane that rewrites `.coderabbit.yaml` on master from measured performance (the file is small and the fleet already lands config via PR), and/or (c) orchestrator-side adaptation (§4.6), which is where per-PR context actually lives.

**Speculative / not available:** per-PR dynamic profile switching via API or comment — no such mechanism found in vendor docs (NOT ESTABLISHED). Review-seat assignment for bots is the vendor's answer to bot-authored PRs; the owner declined it (2026-10-23) — not a lever in play.

### 4.2 Gemini lane (after-peers / review / dispatch)

**REAL (repo-verified):**
- **Model-router action** — provider+model selection per role from a live catalog + key availability + capacity cache, with `skip` + `reason` outputs. This is already a JIT engine; its inputs (role, provider availability) are the context axes, and `decision`/`decision_summary` outputs are an audit trail.
- **Orchestrator gating** — whether the second pass runs at all is decided per-PR by peer state (the strongest context lever: don't burn Gemini quota until peers deliver).
- **Quota gate + quota registry** — `gemini-quota-gate` action and `ops/quota/*` reconcile-before-dispatch machinery (provider-neutral direction per the owner's 2026-10-21 correction: per-provider threads, each reconciling its own quota).
- `GEMINI.md` — prompt-context file; editing it changes review behavior repo-wide (static, but a real lever).

### 4.3 CellCog

**REAL (repo-verified):** `CELLCOG_CHAT_TIER` repo variable (currently unset → `max` default) — a no-commit tier lever; the workflow's prompt is built from the PR diff in-workflow, so prompt/shape changes are workflow edits. Advisory-only by design, so the cost of a wrong context call is low.
**NOT ESTABLISHED:** any CellCog-side config file or per-context vendor settings — none in repo, none claimed.

### 4.4 ECC Tools

**REAL (repo-verified):** all levers are repo-side cadence, in `agent-ecc-tools-ops.yml`: sweep schedule (2×/day), 6h/12h debounces, sweep cap, force flag, batched-comment + overflow behavior, and the check-run mirror. `.claude/ecc-tools.json` profile/tier/component selection is **app-generated** — treat as read-only evidence of the app's effective profile, not a hand-edited lever (editing it in-repo has NOT ESTABLISHED effect; the app regenerates it).
**Vendor constraint (verified 2026-10-21, restated in the workflow):** ECC requests no checks permission and is comment-only by design; the mirror step is the sanctioned evidence bridge. No ECC-side JIT config surface exists in-repo.

### 4.5 Qodo / Devin / Copilot / Aikido / Sentry (tracked providers)

**REAL (repo-verified):** orchestrator-side only —
- membership in `PEER_REQUIRED_PROVIDERS` (per-repo variable or default change),
- `OPERATOR_ALLOWED_ACTIONS` membership (whether OPERATOR may trigger them),
- trigger commands for qodo (`/agentic_review`) and devin (`/devin review`) already wired; aikido/sentry/copilot have **no trigger command** and no evidence requirement — they are observe-only entries in the login/check maps.
**NOT ESTABLISHED:** any vendor config file or repo-side settings for these five (tree scan: zero files). Any claim about Qodo `.qodo` configs, Copilot instruction files, etc. would be invention — none exist here, and whether the installed apps would honor repo files was not verified with the vendors in this recon.

### 4.6 The cross-provider JIT layer (where per-context adaptation can actually live)

Repo-verified mechanisms, in increasing order of power:

1. **Repo variables** (no commit, instant): `PEER_REQUIRED_PROVIDERS`, `PEER_ENFORCE_PROVIDER_COMPLETION`, `OPERATOR_ALLOWED_ACTIONS`, `OPERATOR_EXECUTOR_LOGINS`, `PEER_STATE_PUBLISHER_LOGINS`, `CELLCOG_CHAT_TIER`. **All currently unset** — the entire policy layer is dormant and running on defaults. Coarse (repo-global), but the fastest lever that exists.
2. **Orchestrator collect-step logic** (per-PR, per-cycle): the bot-author exemption (PR #1628) proves the pattern — fetch PR → derive context → adjust effective required set → record the decision in the state comment. The same seam can consume author class, labels, size, paths, cooldown history, and measured provider performance, and can record every adaptation in the state comment for audit.
3. **Generated settings commits**: a metrics-driven lane that opens PRs rewriting `.coderabbit.yaml` (profile, path_instructions, label/author gating) or the orchestrator defaults from measured provider×context performance — the only way the *vendor file itself* becomes adaptive, at commit cadence rather than per-PR cadence.
4. **Model-router inputs/outputs** for the Gemini lane: role + availability today; provider-performance weights are a natural additional input (NOT ESTABLISHED as implemented).

---

## 5. Gaps & NOT ESTABLISHED list

- No provider-performance dataset exists today: state comments hold the raw facts per cycle, but nothing aggregates them (no provider×context×metric table anywhere in tree).
- Moneyball/DoE weighting exists for PRs and quotas; **no reviewer-provider weighting** found.
- `gemini-triage.yml`, `gemini-invoke.yml`, `gemini-quota-gate/action.yml` internals not read in this recon.
- Whether CodeRabbit reads `.coderabbit.yaml` from the default branch vs the PR base at review time — vendor behavior not pinned down in the fetched docs pages (matters for how fast a generated config commit takes effect on in-flight PRs).
- Vendor-side settings held in each app's own dashboard (CodeRabbit org settings, Qodo, Devin, Copilot, Aikido, Sentry) are invisible to the PAT and were not inspected — per fleet rules they are owner-UI items of record, not blockers.
- ECC's `.claude/ecc-tools.json` regeneration cadence/trigger: NOT ESTABLISHED (in-file `generatedAt` 2026-09-01 only).

## 6. Recon bottom line

- **Inventory:** 1 vendor settings file (`.coderabbit.yaml`), 1 control-plane workflow (orchestrator) with a dormant 5-variable policy layer, a 4-surface Gemini lane (3 workflows + model-router + quota gate + `GEMINI.md`), CellCog (1 workflow, 1 unset variable), ECC (1 app-generated profile file + 1 ops workflow), 1 feedback consumer (auto-jules), 5 tracked-but-configless providers (qodo/devin/copilot/aikido/sentry).
- **Strongest JIT lever per provider:** CodeRabbit → orchestrator-side effective-required-set + in-file path/label/author axes (the file alone can't do per-PR); Gemini → model-router + peer-state gating (already JIT-shaped); CellCog → `CELLCOG_CHAT_TIER` variable; ECC → ops-workflow cadence knobs (debounce/cap/schedule); tracked five → required-set / allowed-actions membership.
- **Metrics source to build on:** orchestrator **state comments** (provider × PR × SHA × cycle, with timestamps, states, evidence URLs, cooldowns) joined with the reviews/comments APIs for volume and verdicts, ECC's sweep ledger + check mirror, and `ops/github-telemetry`'s governed metric policy for the Actions-cost dimension. The join key and the audit trail already exist; what's missing is only the aggregation and the weighting map.
