# SWARM — Optimizations ∧ Implementation Assurance

`[MUSEai]@{role:{optimizations-assurance}}` ∘ mission 2026-10-31 (owner via Contribution Desk) ∘ evidence = PAT-API firsthand @master `a113a6203675` 2026-10-31T17:07Z ∧ workflow files @same head. Notation #320/#1734: claim ⇒ evidence; ∅ evidence ⇒ `NOT_ESTABLISHED`.

## 0. Registry correction

Mission brief {157 records, 108 distinct, model 88} = STALE ⇒ firsthand `ops/quota/registry.json` @`a113a620`: **161 records, 110 distinct providers, model lane 91 records / 89 distinct**. Use 161/110/91/89 ∀ downstream counts.

## 1. Census — dispatch surfaces (CORRECTED 2026-10-31T17:2xZ; 2 independent PAT-API reads agree)

> **ERRATA:** the first-published version of this table carried WRONG run totals + last-green dates (e.g. Jules 81, Gemini dispatch 91, DeepAgent "4 runs, 3 failure") — superseded in full by this section. Conclusions that survive are marked ✓-kept; withdrawn claims are named. Correction filed openly per verify-before-claim discipline.

Method note: comment-triggered workflows accumulate a run per comment (mostly `skipped` by their own gates) ∴ raw totals ≠ dispatch counts. `40000` = API total_count cap (exact = NOT_ESTABLISHED).

| surface | workflow id | runs total | verified anchor | dispatchable TODAY ∅owner-UI |
|---|---|---|---|---|
| Jules issue-label | 327570452 | 38338 all-events; event=issues subset 333 | issues ✓ 2026-10-31T05:32Z run 41173021506; latest issues run ✗ 2026-10-31T16:51Z 41221671137 | ✓-kept (owner-actor issue/label) |
| Jules PR handoff | 355288036 | 26752 | PR runs `action_required` (sample 41222975782) = B1 | ✗ gate-bound on bot/fork PRs |
| Jules review-auto | 326843961 | 40000 (cap) | ✓ issue_comment 2026-10-31T17:06:49Z run 41222921464 ⇒ live today | △ via issue_comment; PR route gate-bound |
| Gemini dispatch | 327943478 | 40000 (cap) | PR runs `action_required` = B1; file triggers {PR, issues, issue_comment}, ∅ workflow_dispatch ✓-kept | ✓ via issues/issue_comment only |
| Gemini invoke / triage | 327943479 / 327943482 | 0 direct | structural: `workflow_call` only (runs attribute to caller; agrees 2026-10-27 census) | indirect |
| Gemini review | 327943481 | 26 | last 2026-08-20 ✗ push ⇒ STALE (agrees 2026-10-27 census) | ✗ stale |
| DeepSeek CI | 330577935 | 40000 (cap) | PR runs `action_required` = B1 | △ workflow_dispatch path only |
| DeepSeek termux-agent | 367231371 | 32894 | head = skipped issue_comment noise; workflow_dispatch last-✓ = NOT_ESTABLISHED (earlier 2026-10-20 claim WITHDRAWN) | △ workflow_dispatch defined in file; success unproven in corrected census |
| DeepAgent (`deepagent-task.yml` only) | 373901223 | **0 runs ever** | never dispatched ⇒ THIS FILE unproven (earlier "3 failure" claim WITHDRAWN; §4 A3 rewritten). File added 2026-10-03 (commit d41bd73877, sole commit for path) | △ trigger exists, unproven |
| **DeepAgent via DeepCLI Agent Bridge** (`deepcli-agent-bridge.yml`) — OWNER CORRECTION 2026-10-31, verified by this lane | 371692445 | 158 total; **28 runs before 2026-10-06** | **✓ successes pre-Oct-6: runs #17–#28 (first ✓ #17 2026-10-04T16:22Z 37216522300; #21 success 37247626949 cited on #1128; last pre-Oct-6 ✓ #28 schedule 2026-10-05T22:06Z 37380309487)**; latest run #158 ✓ 2026-10-23T16:44Z, quiet since. Caveat: #1128 comment records run #21 reached bridge admission with device status "unknown" ⇒ did NOT attempt SSH/DeepAgent execution — bridge-level ✓ established; end-to-end device execution from that run = NOT_ESTABLISHED | ✓ historically (bridge route); current liveness △ (∅ runs since 2026-10-23) |
| provider-batch (OpenRouter free ∧ batch families) | 390191855 | 234 | latest-100: 49 ✓ / 50 ✗; last ✓ 2026-10-28T14:53Z 40710434190; latest ✗ 2026-10-31T06:55Z 41178501775 (#2672) | △ dispatchable; contracts red ⇒ observe blocked (#2672) |
| provider-command-dispatch (CodeRabbit/Devin/Qodo fix lanes) | 339005236 | **1 run ever** | ✓ workflow_dispatch 2026-10-18T22:08Z run 39170909023 | ✓ workflow_dispatch (single proof) |

Repo-wide @first census: `status=action_required` total_count **2500** (API value; treated as floor, exact tail NOT_ESTABLISHED) ∧ queued=3 ∧ in_progress=4 ∴ gate pile ≫ live queue.

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
- **A3 issue #2735 (CORRECTED ×2):** DeepAgent `deepagent-task.yml` = **0 runs ever** — first-dispatch smoke owed for THAT FILE. DeepAgent itself is proven via DeepCLI Agent Bridge (pre-Oct-6 successes, table above); open questions = bridge quiet since 2026-10-23 ∧ which surface is canonical for new DeepAgent dispatches.
- **A4 tracked, ∅ new issue:** #2672 contracts fix ⇒ on green, re-run provider-batch observe ∧ verify Firecrawl harvest lands.
- **A5 standing:** weekly census refresh (this table) via GitHub Workflow surface when a repo automation home is assigned; VM = sandbox only, ∅ local cron.

## 5. Dispatchable TODAY (summary, corrected)

✓ Jules issue-label · Gemini via issue/comment · provider-command-dispatch workflow_dispatch (1 proof)
△ DeepSeek CI workflow_dispatch-only · DeepSeek termux-agent workflow_dispatch (unproven ✓) · provider-batch (B2) · DeepAgent (0 runs, A3)
✗ ∀ PR-event provider reactions (B1, owner-UI) · Gemini review (stale, 2026-08-20)

## 6. Desk input 2026-10-31 — #2732 dispatch_policy ∧ DeepSeek reroute (verified by this lane)

- **#2732 OPEN** (desk self-upgrade, dispatched ↦ Gemini): `gemini-dispatch` run on `issues` event = **SUCCESS run 41223286134** (2026-10-31T17:11:07Z, read firsthand by this lane) ⇒ Gemini issues route carries a named success anchor; deliverable PR off #2732 = NOT_ESTABLISHED yet (API search: ∅ PR), desk reviews on landing.
- **Spec'd (∅ landed until #2732 PR merges):** desk-feed gains `dispatch_policy` {mode: auto|manual, per-role ordered routes (feature_build/fix/review/invoke), `selected` overrides, rotation rule} ∧ desk.html per-role provider `<select>` (intake-issue link carries choice; page mutates nothing).
- **DeepSeek route order (spec'd in #2732, applies to this lane's map NOW as routing intent):** (1) **OpenRouter cloud FIRST** for invoke/review — model `deepseek/deepseek-r1:free`, catalog `scripts/openrouter_free_catalog.py`, `OPENROUTER_API_KEY` provisioned, runs in GitHub Actions = device-free; (2) Termux webWrapper (`deepseek-ci` cookies/webWrapper + `DEEPSEEK_AGENT_URL`) demoted ⇒ **fallback-only, `device_dependent=true`**.
- **Credential constraint (owner correction 2026-10-24, memory-verified):** `DEEPSEEK_API_KEY` = a route-named **GitHub PAT** (one GitHub-access route for DeepSeek CLI Termux agents), ¬ a DeepSeek-issued key ⇒ ∅ "official DeepSeek API" route exists until a real DeepSeek key is provisioned. Names declare family; ∅ official-API claims in any dispatch record.
- Census impact: §1 DeepSeek termux-agent row's route = fallback-only effective this spec; OpenRouter route joins the swarm set as cloud invoke/review surface (provider-batch Actions precedent).
