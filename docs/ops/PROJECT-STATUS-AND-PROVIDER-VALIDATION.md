# Project Status, Provider Validation, and MuseAI Alignment

**Observation date:** 2026-10-21 UTC  
**Repository:** `timerloggedout-spec/termux-monorepo`  
**Canonical branch:** `master`  
**Baseline SHA observed:** `4d316727df0a46bedc2edaaf3b72f96f5d9117e2`  
**Purpose:** Current collaboration hand-off. This document separates live observations, existing implementation, unresolved verification, and next actions. It supersedes no technical contract; update it when new evidence is collected.

## Executive status

1. The current repository is substantially newer than the historical conversation snapshots. Use the current `master` tree and live run evidence as authority.
2. Historical PR [#523](https://github.com/timerloggedout-spec/termux-monorepo/pull/523) is **closed and unmerged** at head `69c33cf5fd1938db444f94ee4386aebc12bda445`. Do not merge it or treat its old branch as current. Reconcile any still-needed changes against present-day `master`.
3. Provider health, catalog availability, credential presence, account entitlement, and successful inference are separate claims. A green workflow or successful catalog poll is not proof of inference.
4. MuseAI is not identified in repository code/issue/PR searches performed for this hand-off. The available GitHub connector does not expose the user's personal token last-used audit or authorized-app management surfaces. Therefore this review **cannot establish which PAT MuseAI is using, prove that it is using one, or change MuseAI's account-side permissions**.
5. Continue the evidence-first cycle: `RECON → PLAN → IMPLEMENT → COMMIT → WAIT → WATCH → VALIDATE → RE-FETCH → COMPARE → RECORD → REPEAT`. Never equate queued with success, configured with healthy, or committed with promoted.

## Live repository observations

- GitHub repository metadata reports `master` as the default branch and administrative/push permissions for the connected identity.
- The latest fetched master commit was `4d316727df0a46bedc2edaaf3b72f96f5d9117e2`, a Sweep Accountability receipt commit.
- At observation time, the newest fetched Actions records included multiple `lane events recorder` runs in `queued` state and `Actions Run Watcher — incident notification` runs with `skipped` conclusions. These observations are not provider-health evidence.
- The latest historical corpus status document in master contains a manifest observation dated 2026-08-19 with `next_start_page = 2`. It is stale relative to this status date and must be re-fetched from the current manifest before any completion claim or continuation dispatch.
- The prior integration ledger `docs/ops/SHE-INTEGRATION-FINDINGS.md` remains useful architecture context, but its status tables include historical observations and must not be read as current runtime proof.

## Provider validation matrix

### Existing implementation

The current master branch contains:
- `.github/workflows/provider-availability.yml`: scheduled every six hours, with manual strict mode. Its contract distinguishes configured credentials and catalog probes from inference; it does not perform routine inference.
- `.github/workflows/provider-batch.yml`: contract tests on relevant changes and trusted manual diagnostic/smoke inputs. Inference smoke defaults off and is deliberately bounded.
- `.github/workflows/continuous-evaluation.yml`: catalog-driven evaluation and experiment artifacts; evaluation is not an automatic routing/adoption gate.
- `.github/workflows/openrouter-free-catalog-sync.yml`: public catalog snapshot and drift evidence; it does not create a PR or activate a route.
- `scripts/provider_model_catalog.py`: provider/model catalog collection and normalized access/pricing evidence. Its documented policy treats catalog state as evidence, not routing policy.

### Last explicit live inference evidence located

The current `docs/ops/PROVIDER-FREE-INFERENCE.md` references production run [39432211461](https://github.com/timerloggedout-spec/termux-monorepo/actions/runs/39432211461), on commit `9dee06ef18d70f373e961e6d767a051c24814d10`:
- OpenRouter authentication/account metadata and `is_free_tier: true` were observed.
- The exact allowlisted `liquid/lfm-2.5-2.6b:free` route had zero listed price.
- Exactly one bounded synthetic completion was attempted and returned **HTTP 429**.
- The recorded outcome is `inference_ok: false`, `reason: inference_http_429`.
- The cause of the rate limit is not established. No successful completion is claimed.
- Gemini and Felo catalog observations were recorded, but account-specific no-cost entitlement was not established and no inference request was sent to them in that run.

These are concrete observations from run 39432211461, not the newest health signal. Additional current runtime evidence was inspected during this hand-off:

- [Provider availability continuity run 39501175974](https://github.com/timerloggedout-spec/termux-monorepo/actions/runs/39501175974), completed SUCCESS on 2026-10-20 21:32:21Z at SHA `42a72f2b12361dbf1be465a5711f5fd2f41e7c3d`. I inspected its job steps and logs and confirmed the sanitized health artifact was uploaded.
- The provider availability probe reported **OpenRouter: credential present + catalog OK; Felo: credential present + catalog OK; Gemini: credential present + catalog OK but `free_account_unverified`**. It also observed public catalogs for LLM7, ModelScope, and OVHcloud. These checks explicitly reported `inference=false`; they do not prove completion capability or free-tier entitlement.
- The same probe reported many providers as `missing_secret` / unconfigured, including Groq, Hugging Face, Mistral, NVIDIA, Omni, Cohere, and others. This is the Actions environment's observed mapping, not a claim that the user has no account or credentials elsewhere.
- [Provider batch production contracts run 39452118281](https://github.com/timerloggedout-spec/termux-monorepo/actions/runs/39452118281) completed SUCCESS. The contract job and no-inference free-key diagnostics job passed; the optional public-research observation job was skipped.
- [Continuous Team Evaluation run 39524836826](https://github.com/timerloggedout-spec/termux-monorepo/actions/runs/39524836826) completed SUCCESS on 2026-10-21 01:01:22Z at SHA `36d96630027ba2221b7cf65590543c505e6d2adb`. The discover/catalog job and 20 experiment jobs completed and uploaded artifacts, but the matrix intentionally preserves lane-level failures without failing the whole workflow. I inspected representative invocation logs and found mixed live outcomes: `dots-studio/dots-3-note-preview:free` returned HTTP 200; `minimax/minimax-m3.1-flash:free` returned HTTP 200; `google/gemma-4-31b-it:free` returned HTTP 429 (rate limit); `liquid/lfm-2.5-2.6b:free` returned HTTP 504 (transport/upstream error); and Felo `ox-alpha` returned HTTP 403, `This model is disabled`. Thus workflow-level SUCCESS is not equivalent to every candidate succeeding. The successful HTTP 200 samples prove those exact invocations completed in that cohort only; model quality and broader availability require separate evidence.
- [OpenRouter free catalog snapshot run 39464361856](https://github.com/timerloggedout-spec/termux-monorepo/actions/runs/39464361856) completed SUCCESS and uploaded its catalog observation.

The resulting diagnosis is **partially healthy and evidence-backed**, not “all providers working”: catalog continuity is confirmed for the configured OpenRouter/Felo/Gemini paths; one recent team-evaluation cohort completed its invocation steps; Gemini's no-cost entitlement remains unverified; and OpenRouter's separate bounded inference smoke previously returned HTTP 429. No new provider workflow was dispatched during this pass.

### Required validation cadence

For each provider, report independent fields:
- `credential_present` — only that a secret name/value is configured in the workflow environment; never disclose the value.
- `catalog_ok` — a provider catalog request succeeded.
- `auth_ok` — an authorized, non-sensitive authentication check succeeded where supported.
- `entitlement_ok` — the intended account/model is eligible for the claimed plan or no-cost tier, with evidence source and observation time.
- `inference_ok` — only a separately authorized, bounded probe completed successfully.
- `rate_limited`, `billing_blocked`, `policy_blocked`, `network_error`, `unknown` — explicit failure/uncertainty classes; never retry blindly or silently fail over to paid inference.

**Next provider action:** inspect the latest `provider-availability` and `provider-batch` Actions runs, including job steps and sanitized artifacts; dispatch a bounded read-only availability check if needed; use the one-shot free inference smoke only after its explicit account/price guard passes. Record run ID, attempt, SHA, timestamp, provider/model, response class, and artifact/receipt URL. Do not log prompts, secrets, raw sensitive payloads, or account identifiers.

## MuseAI / GitHub PAT alignment

### What is and is not established

- Searches of repository files, PRs, and issues for `MuseAI`/ `MUSEAI` returned no direct integration record.
- Repository commit authorship, comments, or Actions activity under `timerloggedout-spec` cannot reliably distinguish a human from an external agent operating through the same account or credential.
- A historical credential-inventory issue (#184) contains a user-supplied snapshot of personal token names/scopes and authorized applications. It is historical, not a current token audit. Do not infer current token usage from it.
- The available connector cannot inspect or revoke the user's personal access tokens or authorized OAuth/GitHub Apps. No token has been changed by this work.

### Immediate account-side controls

1. In GitHub **Settings → Developer settings → Personal access tokens** and **Applications**, identify the exact credential/application MuseAI is using and check its current last-used evidence, scopes, repository access, and expiration.
2. If the credential is unknown, over-scoped, exposed, or cannot be confidently attributed, revoke it and provision a replacement through MuseAI's supported connection flow. Do not paste PAT values into chat, issues, repository files, workflow logs, or agent prompts.
3. Prefer a dedicated GitHub App or fine-grained PAT scoped only to `timerloggedout-spec/termux-monorepo` and the minimum required permissions. Avoid classic PATs with broad account/organization administration scopes for routine coding work.
4. Keep provider API keys (OpenRouter, Gemini, Felo, etc.) separate from GitHub credentials. A GitHub PAT must not be reused as an inference-provider key.
5. Give MuseAI a narrow contribution contract: work from issues, use a dedicated branch, open a PR, attach tests/evidence, preserve source/run/SHA provenance, and do not push directly to `master`, merge, alter secrets, or change routing/production policy unless separately authorized.
6. Attribute actions using workflow/run/job/step IDs, triggering event, PR/issue, SHA, timestamp, tool/provider telemetry, and declared agent identity. Store confidence and `unknown` where provenance cannot be proven; never infer agent identity from the GitHub username alone.
7. Review recent commits, workflow runs, and app authorizations against the expected MuseAI task list. Investigate unexplained writes and disable/revoke the specific credential if unauthorized activity is found.

### MuseAI acceptance criteria

MuseAI is considered aligned only when:
- the exact authorized integration and credential owner are identified;
- effective permissions are least-privilege and limited to the intended repository/workflow scope;
- direct production-branch writes and unapproved merges are prevented by actual controls, not documentation alone;
- its changes are attributable to an agent/session and immutable commit/run IDs;
- all changes arrive through reviewable PRs with relevant test/check evidence;
- no secret values or sensitive provider payloads enter source, logs, comments, or evidence artifacts.

## Consolidated implementation plan

### P0 — Security and current-state truth
- [ ] Verify MuseAI's exact GitHub connection/credential and current permissions in account settings.
- [ ] Revoke/rotate any exposed or over-scoped token that cannot be trusted; confirm the replacement is least-privilege.
- [ ] Re-fetch current master corpus manifest and current provider workflow runs; replace stale numbers with observed evidence.
- [ ] Inspect the latest provider availability run's jobs, steps, summary, and artifact. Classify each provider independently.

### P1 — Provider execution evidence
- [ ] Run the read-only provider availability check on trusted `master`.
- [ ] Validate provider-specific authentication and entitlement only through supported, non-sensitive checks.
- [ ] Execute a single bounded no-cost inference only after the existing exact-model and account eligibility guards pass.
- [ ] Preserve HTTP 429 and other failures as observations; do not hide them with blind retries, alternate accounts, or paid fallback.
- [ ] Verify OpenRouter catalog, provider-batch contracts, and continuous-evaluation evidence are current-SHA bound.

### P1 — Agent governance and collaboration
- [ ] Document MuseAI's approved scope, allowed branches, PR-only write path, and forbidden secret/merge operations.
- [ ] Reconcile the historical PR #523 changes with current master; recover only still-needed changes as a new focused PR.
- [ ] Add or update tests for agent attribution, least-privilege workflow permissions, and no-secret telemetry.
- [ ] Maintain one status/evidence ledger linking each claim to commit SHA, workflow run/attempt, artifact, and observed time.

### P2 — Complete the operating system
- [ ] Refresh the Historical Corpus from its live manifest and continue only from the canonical checkpoint with validated page advancement.
- [ ] Keep SHE as a projection over evidence, never the authority for execution status.
- [ ] Keep OpenTelemetry/JSONL evidence neutral and exportable; keep Langfuse, Phoenix, and Hex optional adapters.
- [ ] Compare orchestration managers only after outcomes, retries, conflicts, human interventions, provider failures, and attribution confidence are measurable.
- [ ] Close each phase only when the intended effect is re-fetched and validated, not merely when code is committed.

## Promotion and stopping rules

- No merge/promotion is authorized by this document.
- Do not describe the historical corpus as complete until the current canonical manifest has `next_start_page = null` and reconciliation passes.
- Do not describe a provider as working from a catalog poll, configured secret, skipped job, or green wrapper workflow alone.
- Do not claim MuseAI alignment until account-side credential identity and effective permissions have been inspected.
- Preserve failures and cancellations as evidence; rerun only when a diagnosed condition and explicit policy justify it.

## Evidence links

- [Repository](https://github.com/timerloggedout-spec/termux-monorepo)
- [Historical PR #523 — closed, unmerged](https://github.com/timerloggedout-spec/termux-monorepo/pull/523)
- [Historical provider inference evidence — run 39432211461](https://github.com/timerloggedout-spec/termux-monorepo/actions/runs/39432211461)
- [Provider availability workflow source](../../.github/workflows/provider-availability.yml)
- [Provider batch workflow source](../../.github/workflows/provider-batch.yml)
- [Continuous evaluation workflow source](../../.github/workflows/continuous-evaluation.yml)
- [Provider-free inference status](PROVIDER-FREE-INFERENCE.md)
- [Free LLM provider reconciliation](FREE-LLM-PROVIDER-RECON.md)
- [SHE integration findings](SHE-INTEGRATION-FINDINGS.md)
- [Credential authorization inventory issue #184](https://github.com/timerloggedout-spec/termux-monorepo/issues/184)
