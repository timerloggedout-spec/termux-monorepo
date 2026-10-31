# SWARM — Optimizations ∧ Implementation Assurance

`[MUSEai]@{role:{optimizations-assurance}}` ∘ mission 2026-10-31 (owner via Contribution Desk) ∘ evidence = PAT-API firsthand @master `a113a6203675` 2026-10-31T17:07Z ∧ workflow files @same head. Notation #320/#1734: claim ⇒ evidence; ∅ evidence ⇒ `NOT_ESTABLISHED`.

## 0. Registry correction

Mission brief {157 records, 108 distinct, model 88} = STALE ⇒ firsthand `ops/quota/registry.json` @`a113a620`: **161 records, 110 distinct providers, model lane 91 records / 89 distinct**. Use 161/110/91/89 ∀ downstream counts.

## 1. Census — dispatch surfaces (runs total / last success in latest-20 sample / gate state)

| surface | workflow id | runs | last ✓ | triggers @file | dispatchable TODAY ∅owner-UI |
|---|---|---|---|---|---|
| Jules issue-label | 327570452 `agent-jules-on-issues.yml` | 81 | 2026-10-31T16:52Z ✓ | issues[labeled], issue_comment | ✓ (owner-actor issue/label) |
| Jules PR handoff | 355288036 `agent-pr-jules-handoff.yml` | 1169 | 2026-10-24 | PR events | ✗ gate-bound on bot/fork PRs |
| Jules review-auto | 326843961 `agent-review-auto-jules.yml` | 162 | 2026-10-22 | PR events | ✗ gate-bound |
| Gemini dispatch | 327943478 `gemini-dispatch.yml` | 91 | 2026-10-30 | PR, issues, issue_comment; ∅ workflow_dispatch | ✓ via issues/issue_comment only |
| Gemini invoke | 327943479 `gemini-invoke.yml` | 1627 | 2026-10-29 | workflow_call only | indirect (caller-dependent) |
| Gemini review | 327943481 `gemini-review.yml` | 4685 | ∅ in latest-20 | workflow_call | ✗ action_required-dominated |
| Gemini triage | 327943482 `gemini-triage.yml` | 2969 | 2026-10-27 | workflow_call | indirect |
| DeepSeek CI | 330577935 `deepseek-ci.yml` | 1700 | ∅ in latest-20 | PR, issue_comment, workflow_dispatch | △ workflow_dispatch path only; PR/comment = gate |
| DeepSeek termux-agent | 367231371 `deepseek-termux-agent.yml` | 14 | 2026-10-20 ✓ workflow_dispatch | issue_comment, issues[assigned], PR[assigned], workflow_dispatch | ✓ workflow_dispatch (DEEPSEEK_AGENT_URL route) |
| DeepAgent | 373901223 `deepagent-task.yml` | 4 | ∅ — 3 failure + 1 action_required | workflow_dispatch | △ dispatchable, own-failure (triage owed, §4 A3) |
| provider-batch (OpenRouter free ∧ batch families) | 390191855 `provider-batch.yml` | 32 | 2026-10-28 | workflow_dispatch | △ dispatchable; contracts red ⇒ observe blocked (#2672) |
| provider-command-dispatch (CodeRabbit/Devin/Qodo fix lanes) | 339005236 `provider-command-dispatch.yml` | 12 | 2026-10-18 | workflow_dispatch only | ✓ workflow_dispatch |

Repo-wide @census: `status=action_required` total_count **2500** (API value; treated as floor, exact tail NOT_ESTABLISHED) ∧ queued=3 ∧ in_progress=4 ∴ gate pile ≫ live queue.

## 2. Blockers (established)

- **B1 ∀ provider reactions on bot/fork PR events ⇒ `action_required`** (pending_deployments=[], ∅ environment keys) ⇒ clears ONLY via owner UI per-run approve ∨ fork-PR approval-policy change. ∅ workaround attempted; escalation = owner-UI item-of-record.
- **B2 #2672 provider-batch contracts red on master** ⇒ observe job skipped/blocked (run 41178501775 evidence in #2672). Fix lane ≠ this lane; this lane tracks ∧ verifies.

## 3. Swarm rules (optimization core)

1. **Rotation:** ∅ provider takes 2 consecutive dispatches for same entry (desk rule). Dispatch comment MUST name {provider, session/run id, entry, prior provider} ⇒ rotation auditable from GitHub alone.
2. **Parallel fan-out:** independent entries ⇒ simultaneous distinct providers: Jules(issue-label) ∥ Gemini(issues/issue_comment) ∥ DeepSeek(workflow_dispatch) ∥ provider-batch(inference families) ∥ command-dispatch(fix lanes, partitioned by PR head). Serial single-provider queues = anti-pattern.
3. **Gate-lawful routes only:** workflow_dispatch ∨ owner-actor issue/comment triggers. ∅ reliance on fork/bot PR-event reactions until B1 owner decision lands.
4. **Quota parallelism:** per-provider quota reconciles before its own dispatch; one provider exhausted ⇒ rotate, ¬ stall swarm (provider-neutral early layer precedent, #1441 correction).
5. **Assurance gate ∀ landed work:** provider+session named per PR ∧ tests/gates read firsthand ∧ merge oracle = PR# ∈ master-history scan ∧ landed content verified. Claim ∅ evidence ⇒ `NOT_ESTABLISHED`, reported as such.

## 4. First actions

- **A1 ✓ this doc** — census + plan of record.
- **A2 issue (filed with this PR):** add `workflow_dispatch` trigger to `gemini-dispatch.yml` ⇒ Gemini joins dispatchable set directly, bypassing B1 lawfully. Small ops change; author = provider lane, this lane verifies run evidence.
- **A3 issue (filed with this PR):** DeepAgent `deepagent-task.yml` 3/4 workflow_dispatch failures — triage root cause; surface currently dispatchable-but-red.
- **A4 tracked, ∅ new issue:** #2672 contracts fix ⇒ on green, re-run provider-batch observe ∧ verify Firecrawl harvest lands.
- **A5 standing:** weekly census refresh (this table) via GitHub Workflow surface when a repo automation home is assigned; VM = sandbox only, ∅ local cron.

## 5. Dispatchable TODAY (summary)

✓ Jules issue-label · Gemini via issue/comment · DeepSeek termux-agent workflow_dispatch · provider-command-dispatch workflow_dispatch
△ DeepSeek CI workflow_dispatch-only · provider-batch (B2) · DeepAgent (A3)
✗ ∀ PR-event provider reactions (B1, owner-UI)
