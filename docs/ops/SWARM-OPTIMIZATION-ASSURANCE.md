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
| DeepSeek termux-agent | 367231371 | 32894 | **workflow_dispatch subset EXHAUSTIVE (2 reads agree): 20 runs, 18 ✓ / 2 ✗, 2026-09-25→10-05; last ✓ 2026-10-05T10:35Z run 37297514722** ⇒ route PROVEN when device lives. Desk-relayed "last ✓ 2026-10-20" date = NOT_ESTABLISHED (∅ dispatch success after 2026-10-05 in the exhaustive subset; other-event successes are buried in 32k comment-noise runs, unconfirmed). Route works-when-device-lives ∧ owner's device-availability objection ⇒ #2732 reroute (OpenRouter primary, this route fallback-only) — BOTH facts stand (§6) | △ workflow_dispatch proven historically; device-dependent ⇒ fallback per #2732 |
| DeepAgent (`deepagent-task.yml` only) | 373901223 | **0 runs ever** | never dispatched ⇒ THIS FILE unproven (earlier "3 failure" claim WITHDRAWN; §4 A3 rewritten). File added 2026-10-03 (commit d41bd73877, sole commit for path) | △ trigger exists, unproven |
| **DeepAgent via DeepCLI Agent Bridge** (`deepcli-agent-bridge.yml`) — OWNER CORRECTION 2026-10-31, verified by this lane | 371692445 | 158 total; **28 runs before 2026-10-06** | **✓ successes pre-Oct-6: runs #17–#28 (first ✓ #17 2026-10-04T16:22Z 37216522300; #21 success 37247626949 cited on #1128; last pre-Oct-6 ✓ #28 schedule 2026-10-05T22:06Z 37380309487)**; latest run #158 ✓ 2026-10-23T16:44Z, quiet since. Caveat: #1128 comment records run #21 reached bridge admission with device status "unknown" ⇒ did NOT attempt SSH/DeepAgent execution — bridge-level ✓ established; end-to-end device execution from that run = NOT_ESTABLISHED | ✓ historically (bridge route); current liveness △ (∅ runs since 2026-10-23) |
| provider-batch (OpenRouter free ∧ batch families) | 390191855 | 234 | latest-100: 49 ✓ / 50 ✗; last ✓ 2026-10-28T14:53Z 40710434190; latest ✗ 2026-10-31T06:55Z 41178501775 (#2672) | △ dispatchable; contracts red ⇒ observe blocked (#2672) |
| provider-command-dispatch (CodeRabbit/Devin/Qodo fix lanes) | 339005236 | **1 run ever** | ✓ workflow_dispatch 2026-10-18T22:08Z run 39170909023 | ✓ workflow_dispatch (single proof) |

Repo-wide: `status=action_required` — **RULING 2026-10-31 (§9): "2500" WITHDRAWN as a total.** 2500 = endpoint CAP: unbounded query returns 2500 (×2 reads) ∧ the ≥2026-10-30 subrange ALONE also returns 2500, while <2026-10-24 returns 166 ⇒ true total **≥2666, exact = NOT_ESTABLISHED**. queued=3 ∧ in_progress=4 @first census (uncorrected leg).

## 2. Blockers (established)

- **B1 (MECHANISM CORRECTED 2026-10-31, desk owner-challenged ∧ re-verified by this lane): ¬ fork-approval.** Mechanism = **GitHub `GITHUB_TOKEN` anti-recursion rule**: events created by `GITHUB_TOKEN` don't start new runs; the run parks at `action_required` awaiting a human "Approve and run workflows" (workflow_dispatch/repository_dispatch exempt). Evidence: run **41221418258** — actor ∧ triggering_actor = `github-actions[bot]`, jobs=0, pending_deployments=[]; its PR **#2167 author = owner, head fork=false** ⇒ fork policy cannot explain it. **PAT/App-token PR events are UNAFFECTED**: PR #2635 (author `google-labs-jules[bot]`) head carries 38 check-runs, 11 ✓. Per-run UI approval drains STOCK only.
  - **FIX CLASS F1 (optimization list):** migrate PR-creating/pushing workflows off `GITHUB_TOKEN` ↦ PAT/App token (fleet Apps + PAT routes already exist), ∨ chain follow-ups via `workflow_dispatch` ⇒ drains the 2500 pile's INFLOW at source. Census shorthand "bot/fork PR gate" elsewhere in this doc = read as this mechanism.
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
✗ PR-event reactions to GITHUB_TOKEN-created events (B1; fix class F1, ¬ per-run approval) · Gemini review (stale, 2026-08-20)

## 6. Desk input 2026-10-31 — #2732 dispatch_policy ∧ DeepSeek reroute (verified by this lane)

- **#2732 OPEN** (desk self-upgrade, dispatched ↦ Gemini): `gemini-dispatch` run on `issues` event = **SUCCESS run 41223286134** (2026-10-31T17:11:07Z, read firsthand by this lane) ⇒ Gemini issues route carries a named success anchor; deliverable PR off #2732 = NOT_ESTABLISHED yet (API search: ∅ PR), desk reviews on landing.
- **Spec'd (∅ landed until #2732 PR merges):** desk-feed gains `dispatch_policy` {mode: auto|manual, per-role ordered routes (feature_build/fix/review/invoke), `selected` overrides, rotation rule} ∧ desk.html per-role provider `<select>` (intake-issue link carries choice; page mutates nothing).
- **DeepSeek route order (spec'd in #2732, applies to this lane's map NOW as routing intent):** (1) **OpenRouter cloud FIRST** for invoke/review — model `deepseek/deepseek-r1:free`, catalog `scripts/openrouter_free_catalog.py`, `OPENROUTER_API_KEY` provisioned, runs in GitHub Actions = device-free; (2) Termux webWrapper (`deepseek-ci` cookies/webWrapper + `DEEPSEEK_AGENT_URL`) demoted ⇒ **fallback-only, `device_dependent=true`**.
- **Credential constraint (owner correction 2026-10-24, memory-verified):** `DEEPSEEK_API_KEY` = a route-named **GitHub PAT** (one GitHub-access route for DeepSeek CLI Termux agents), ¬ a DeepSeek-issued key ⇒ ∅ "official DeepSeek API" route exists until a real DeepSeek key is provisioned. Names declare family; ∅ official-API claims in any dispatch record.
- Census impact: §1 DeepSeek termux-agent row's route = fallback-only effective this spec; OpenRouter route joins the swarm set as cloud invoke/review surface (provider-batch Actions precedent).

## 7. Desk cross-check 2026-10-31 — DeepSeek termux-agent (verified by this lane)

Desk acceptance of census noted. Cross-check pair kept together in-plan: (a) termux-agent route **works when the device lives** — exhaustive workflow_dispatch subset = 20 runs / 18 ✓ (2026-09-25→10-05, last ✓ run 37297514722); (b) that proof **predates the owner's device-availability objection**, and the desk's answer is the #2732 reroute (OpenRouter primary, webWrapper fallback-flagged `device_dependent=true`). Date correction vs desk relay: last-✓ = **2026-10-05**, ¬ 2026-10-20 (see §1 row).

## 8. B1 correction record (2026-10-31)

Original plan text named B1 a "fork-PR approval gate" — WRONG mechanism (the pending_deployments=[] observation was real; the fork inference was not). Corrected per desk challenge + this lane's firsthand re-verification (run 41221418258, PR #2167 fork=false/owner-authored, PR #2635 App-token check-runs ✓). Fix class F1 added to §2/§3 scope: token migration ∨ workflow_dispatch chaining for PR-creating/pushing workflows.

## 9. Ruling — the "2500 action_required" figure (2026-10-31, desk query)

Desk flagged the figure appeared in neither the withdrawn nor survives list. Ruled here: **UNVERIFIED as a total; WITHDRAWN.** Evidence (PAT-API, this lane, 2026-10-31): unbounded `status=action_required` ⇒ total_count 2500 on two reads; `created>=2026-10-30` alone ⇒ 2500; `created>=2026-10-24` ⇒ 2500; `created<2026-10-24` ⇒ 166. A subrange saturating the same value as the whole proves a cap, not a count. Correct statement for any relay: **action_required pile ≥2666 (166 pre-2026-10-24 + ≥2500 since), exact total NOT_ESTABLISHED.** Any owner summary that relayed "2500" as the total carries this correction.

## 10. Owner direction 2026-10-31 — tokens in Secrets ∧ Swarm AppID confer (via desk)

- Owner: "Those tokens are already in SECRETS && you can mint as necessary. Maybe make the Swarms an AppID?" ⇒ **F1 needs ∅ new provisioning to start**: stored PAT secrets (OPERATOR_GITHUB_TOKEN class, names-only) are usable TODAY for workflow PR events.
- **Confer OPENED** desk ↦ AppID process lane: proposed Swarm App perms {contents, pull_requests, issues, actions: write; checks: write; termux-monorepo only} ∧ custody question for in-Actions minting (PEM-in-Secrets — fleet precedent: Collector minting fix, secret-name pattern `TERMUX_FLEET_COLLECTOR_PRIVATE_KEY` + app-id var — vs local-only custody vs interim PAT secrets). Identity design = AppID lane's surface; their answer routes ↦ desk ∧ this lane. This lane takes ∅ identity-design position.
- App-token advantage (evidence): installation tokens trigger downstream runs — Publisher self-publish PR #2417 precedent ∧ PR #2635 check-runs (§8).
- **F1 PILOT FILED #2750:** `delphi-ledger-feed-collect.yml` (default-token env L30-31 → `git push -f` L74 + `gh pr create` L75 on `delphi-ledger-feed/refresh`, the pile's sample branch family) — swap push/PR-create token ↦ stored PAT secret; this lane verifies inflow Δ on landing.

## 11. AppID confer ANSWER 2026-10-31 — Termux Fleet Swarm package READY (owner GO pending)

- **AGREE ∧ package ready** (AppID lane 7075f9c0): **Termux Fleet Swarm**, slug `termux-fleet-swarm`, fleet app #6, own 5000/h bucket, termux-monorepo only.
- Perms **TRIMMED** vs desk proposal: {contents:write, pull_requests:write, issues:write, actions:write, metadata:read} — **checks:write ✗** (∅ swarm workflow posts check runs; checks = Gate's class; amendment flow exists if ever needed).
- Minting = **SEC-03 pattern**: Actions secret `TERMUX_FLEET_SWARM_PRIVATE_KEY` + `APP_ID`/`CLIENT_ID` vars; in-workflow mint via `create-github-app-token` with **numeric app-id** (lesson of record from Collector fix: the action takes app-id, ¬ client-id); local 0600 PEM = master custody (SEC-02 Collector precedent, mint-probe ✓).
- **Scope honesty (recorded verbatim in effect):** un-parks ONLY swarm-token events going forward; the action_required STOCK (≥2666, §9) stays owner-UI per-run; other bots' PRs unaffected.
- **Provisioning ≠ distribution: the per-workflow mint-step ADOPTION WAVE = THIS LANE's ownership once the app is live** (first family = #2750 pilot). Sole owner residual = ONE sudo-mode tap at create; AppID lane fires on owner GO with ⚠️ pre-warning first. Desk has relayed ↦ owner for GO. Status here: AWAITING OWNER GO (∅ action by this lane until live + installation evidence lands).
