# Source — Agent Routing Orchestrator investigation

## 1. What was asked

The owner asked for a scoping investigation into a multi-model Agent Routing Orchestrator: routing across model providers (OpenRouter, FELO, HuggingFace, and others already in use) to power GitHub Actions Workflow "developer" roles — bots that actually write code and open PRs, not just comment. The specific trigger was the observation that OpenRouter has reportedly only been posting PR comments, not writing code, and the request to determine whether that is a model/role config gap, a permission gap, or a workflow design gap.

## 2. What exists today (verified against live repo state, timerloggedout-spec/termux-monorepo)

### 2.1 Provider routing workflows

`gemini-invoke.yml`, `gemini-review.yml`, `gemini-triage.yml`, and `gemini-after-peers.yml` all implement "Gemini PRIMARY → peer Omni ↔ OpenRouter secondary" routing via a reusable `./.github/actions/model-router` action, with roles named `invoke`, `review`, and `triage` only — there is no `developer`/code-writing role defined anywhere in this routing family. `ox-alpha-smoke.yml` and `team-mvt.yml` route between `openrouter` and `felo` specifically for MVT/experiment lanes (not general dev work). `continuous-evaluation.yml` runs a 4-way provider/lane matrix (openrouter, felo, omni) for evaluation purposes only.

### 2.2 The actual permission gap (root cause, verified not assumed)

Every one of `gemini-invoke.yml` / `gemini-review.yml` / `gemini-triage.yml` declares a top-level `permissions: {}` and then a job-level permissions block of exactly `contents: read, issues: write, pull-requests: write`. The same read-only contents scoping applies to `peer-review-orchestrator.yml`, `provider-command-dispatch.yml`, `agent-continuous-ops.yml`, `repo-gate.yml`, and `proposal-lifecycle.yml`. A repo-wide grep for `contents: write` across all 60+ workflow files found it in only ~14 workflows, almost none of them AI-writer workflows — they are catalog-sync/telemetry/doc-publish jobs (`openrouter-free-catalog-sync.yml`, `publish-wiki.yml`, `context-relationship-*.yml`, `github-telemetry-snapshot.yml`, `docs-branch-index.yml`, `merge-promotion-steward.yml`). The ONE clear precedent for an agent workflow that both writes code and can push/PR is `deepseek-ci.yml`, which explicitly grants `contents: write, pull-requests: write, issues: write, actions: read` at job level and checks out with `persist-credentials: true` using an elevated `OPERATOR_TOKEN` (ARCHWIZ/OPERATOR PAT chain), not the default `GITHUB_TOKEN`.

Conclusion: OpenRouter has not been "posting only comments" because of a model/prompt limitation — it is invoked exclusively inside `invoke`/`review`/`triage` roles whose GitHub Actions job permissions never include `contents: write`. There is no role, workflow, or token path today that lets the OpenRouter-routed peer commit code or open a PR autonomously. This matches `docs/proposals/AGENTIC-PERMISSIONS.md`'s stated minimum checklist ("Contents R/W, Pull requests R/W...") — the checklist exists precisely because most current workflows do not meet it for provider-routed roles. This is a workflow-permission / role-design gap, not a bug in OpenRouter's model behavior, and not a credential outage (`OPENROUTER_API_KEY` presence is checked and used successfully for the comment-producing roles).

### 2.3 HuggingFace

A full code search (`api.github.com/search/code?q=repo:...+huggingface`) and a workflow-file grep for "hugging" found ZERO references to HuggingFace in any `.github/workflows/*.yml`, any provider script (`scripts/model_router.py`, `scripts/provider_model_catalog.py`, `scripts/poll_openrouter_free_catalog.py`), or the `.github/actions/model-router` action. The only HuggingFace mentions in the whole repo are unrelated: a local agent session log path, a CLI doc, `.pi/agent/auth.json`/`settings.json` config stubs, and `docs/schemas/llm-leaderboard-matrix.yaml`. HuggingFace is Tanka-linked for the owner but is NOT wired into this repo's provider routing at all — it should be scoped as "not yet connected," not silently assumed.

## 3. What the referenced skills actually specify (read in full, not inferred from names)

### 3.1 multivariate-doe (.agents/skills/multivariate-doe/SKILL.md)

The factor space is provider × model × prompt × manager × cohort × sequencing. The skill requires stating a hypothesis before treatments, preserving negative/skipped/censored observations, avoiding p-hacking and latency-as-correctness-proxy, and keeping a mandatory experiment record (experiment ID, hypothesis, factor levels, provider/model identity, manager/policy version, task/ref SHA, execution status, correctness/verification notes, promotion/culling decision, uncertainty). This is the actual technical content behind "MVT DOE."

### 3.2 gemini-performance-psychology (.agents/skills/gemini-performance-psychology/SKILL.md)

This is an engineering-control discipline for autonomous dev agents — momentum is a control signal, not a quality signal; progressive challenge follows `catalog → credential presence → request probe → task probe → repeated validation → team admission`; reward hacking must be avoided (never optimize for green checks or comment count over verified task outcome); and explicit development lanes (Builder / Review / Recon / Experiment / Telemetry / Synthesis) exist so Gemini and peer providers — explicitly listing OpenRouter, Felo, DeepSeek, Jules, CodeRabbit, Devin, Qodo, Mistral — don't collide. This is what "Validation Verifications Performance Enhancement" maps to in the actual repo.

### 3.3 evidence-led-monorepo-ops (.agents/skills/evidence-led-monorepo-ops/SKILL.md)

Quoted directly: "Authority > ranking. MoneyBall / 3L0 / leaderboard scores are decision-support only. Hard authority, policy, and human gates always dominate." This is the explicit, already-documented rule that any scoring system built on top of the DOE/psychology skills must obey — it can rank and inform promotion, it cannot itself accept a proposal, merge a PR, or grant permissions. This confirms the owner's own framing (MoneyBall/3L0/Leaderboards) is already a first-class, governed concept in this repo, not something to invent fresh.

## 4. Governance constraints applied to this proposal (docs/proposals/AGENTIC-PERMISSIONS.md, docs/CONSENSUS.md)

Tier 0-2 covers documentation and design items (ARO-1, ARO-2, ARO-4, ARO-5 ledger mechanics); Tier 3 (Quorum: driver + distinct second mind OR Operator) governs this proposal's own acceptance and any P0 disposition; Tier 4 (Operator-only: credential rotation, force-push, history rewrite, branch-protection/App-permission changes) explicitly covers the one action that actually closes the gap — granting `contents: write` to a new or existing OpenRouter-routed workflow and provisioning any new secret/environment for it. This proposal does NOT perform that grant; it designs the workflow and defers the grant to the Operator, consistent with AGENTIC-PERMISSIONS.md's "GitHub App permission gaps" and "Provider API keys" rows under "What still needs YOU (human)."

## 5. Recommendation

Adopt ARO-1..ARO-6 as scoped; do not attempt to flip any workflow's permissions or add secrets as part of this PR; route the actual grant through Operator review per Tier 4, using `deepseek-ci.yml` as the closest working precedent for how a code-writing workflow should be shaped (elevated token, path-scoped triggers, concurrency guards, hard-fail on missing credentials).