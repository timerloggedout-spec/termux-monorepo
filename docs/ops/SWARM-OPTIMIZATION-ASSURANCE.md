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

- **B1 (MECHANISM CORRECTED 2026-10-31, desk owner-challenged ∧ re-verified by this lane): ¬ fork-approval.** Mechanism = **GitHub `GITHUB_TOKEN` anti-recursion rule**: events created by `GITHUB_TOKEN` don't start new runs; the run parks at `action_required` awaiting a human "Approve and run workflows" (workflow_dispatch/repository_dispatch exempt). Evidence: run **41221418258** (Gemini Dispatch, branch reviewer-metrics/refresh) — actor ∧ triggering_actor = `github-actions[bot]`, jobs=0, pending_deployments=[]; its PR **#2167 author = owner, head fork=false** ⇒ fork policy cannot explain it. **PAT/App-token PR events are UNAFFECTED**: PR #2635 (author `google-labs-jules[bot]`) head carries 38 check-runs, **26 ✓** (6 skipped/5 cancelled/1 neutral; count corrected 2026-10-31, ×2 reads). Per-run UI approval drains STOCK only.
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
- **DeepSeek route order (spec'd in #2732, applies to this lane's map NOW as routing intent):** (1) **OpenRouter cloud FIRST** for invoke/review — model `deepseek/deepseek-r1:free`, catalog `scripts/openrouter_free_catalog.py`, `OPENROUTER_API_KEY` provisioned, runs in GitHub Actions = device-free; (2) Termux webWrapper (`deepseek-ci` cookies/webWrapper + `DEEPSEEK_AGENT_URL`), `device_dependent=true`. **OWNER CORRECTION 2026-10-31: "fallback-only" as a RANK is rejected — the DeepSeek termux-agent route is PROVEN (dispatch subset exhaustive: 18 ✓ / 2 ✗, §7); `device_dependent` is an availability flag only, ¬ a capability demotion. The order above is the desk's #2732 routing intent for device-free invoke/review, nothing more.** **AMENDMENT 2026-10-31 (#2732 amendment #3, owner order; desk comments 6553097467 + 6553122306): the literal model pin above is SUPERSEDED — DeepSeek-class roles resolve at dispatch via the live catalog/router (`scripts/openrouter_free_catalog.py` + `scripts/model_router.py`), ¬ a pinned literal; route availability = catalog ∧ probe planes (balance per openrouter-paid-value-probe / bracket snapshot; at amendment time the paid balance read $0.00 ∧ the former pin was delisted, so the route carried availability "unfunded" ∧ auto mode is barred from selecting unavailable routes; revival = owner top-up/model ruling).**
- **Credential constraint (owner correction 2026-10-24, memory-verified):** `DEEPSEEK_API_KEY` = a route-named **GitHub PAT** (one GitHub-access route for DeepSeek CLI Termux agents), ¬ a DeepSeek-issued key ⇒ ∅ "official DeepSeek API" route exists until a real DeepSeek key is provisioned. Names declare family; ∅ official-API claims in any dispatch record.
- Census impact: §1 DeepSeek termux-agent row's route carries the `device_dependent` availability flag (rank unchanged — proven route, see correction above); OpenRouter route joins the swarm set as cloud invoke/review surface (provider-batch Actions precedent).

## 7. Desk cross-check 2026-10-31 — DeepSeek termux-agent (verified by this lane)

Desk acceptance of census noted. Cross-check pair kept together in-plan: (a) termux-agent route **works when the device lives** — exhaustive workflow_dispatch subset = 20 runs / 18 ✓ (2026-09-25→10-05, last ✓ run 37297514722); (b) that proof **predates the owner's device-availability objection**, and the desk's answer is the #2732 reroute (OpenRouter primary for desk invoke/review as routing intent; webWrapper carries the `device_dependent=true` availability flag — flag only, ¬ rank, per the §6 owner correction). Date correction vs desk relay: last-✓ = **2026-10-05**, ¬ 2026-10-20 (see §1 row).

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

## 12. Errata — run attribution + #2635 count (2026-10-31)

(1) Run 41221418258 = Gemini Dispatch on `reviewer-metrics/refresh` (¬ delphi family, as an earlier relay implied); the delphi-ledger-feed/refresh family's own parked sample = run 41222975817 (DeepSeek CI, bot actor, jobs=0) — #2750 corrected on-issue. (2) PR #2635 head check-runs: 38 total = 26 ✓ / 6 skipped / 5 cancelled / 1 neutral (earlier "11 ✓" was a partial count).

## 13. Swarm LIVE + F1 pilot VERIFIED (2026-10-31)

Owner GO 2026-10-31 16:53 PT (via desk) with FINAL perms = original six incl. checks:write (restored; supersedes the §11 trimmed set — Tribute-lane interaction). **Termux Fleet Swarm LIVE**: App ID 5560920, slug `termux-fleet-swarm`, bot user id 350898559, installation 177357774 (termux-monorepo only); Actions var `TERMUX_FLEET_SWARM_APP_ID`=5560920 + secret `TERMUX_FLEET_SWARM_PRIVATE_KEY` provisioned (names verified firsthand by this lane). Record PR #2761 merged `36c986c39fdb` — created ∧ merged BY the swarm token (merge commit author = termux-fleet-swarm[bot], verified); custody `custom.github-app-swarm/CONNECTOR.md`, record `ops/github-apps/swarm-pilot/`.

**F1 PILOT (#2750) VERIFIED**: adoption PR #2763 merged `74bb10917ea8` (exists + ancestry + landed mint verified) — delphi-ledger-feed-collect mints the Swarm token for checkout/push/`gh pr create`; reads stay on the default token; mint failure fails loudly (∅ silent fallback). Proof run 41255317900 (workflow_dispatch): success, refresh pushed @63448889c153 (author swarm bot) ⇒ **14 pull_request runs fired with triggering_actor = termux-fleet-swarm[bot]**: repo gate 41255373530 SUCCESS, DeepSeek CI 41255373385 started (vs parked sample 41222975817 jobs=0), 34 check-runs on the head; second cycle @e5c801bff5af likewise un-parked. Nuances: refresh PR = pre-existing #2263 (default-token-authored 2026-10-28, parked since; swarm force-push un-parked it via synchronize; gate-green, delphi lane to land); one non-gate check failure (collect-peer-responses). Verification comment on #2750 (6550976032). Family 2 proceeds by action_required inflow share.

## 14. F1 adoption wave — census, family 2 VERIFIED, family 3 landed (2026-10-31)

**Inflow census** (most-recent 400 action_required runs, by head_branch): delphi-ledger-feed/refresh 239 · reviewer-metrics/refresh 144 · delphi-rfp-feed/refresh 17 — only 24 distinct head SHAs; each parked push parks ~17 downstream runs. The recent inflow is these THREE families only.

**Family 2 — reviewer-metrics-collect VERIFIED** (with a disclosed failed first attempt): #2770 put the Swarm mint before the refresh step + a remote set-url swap; proof cycle 41256400832 committed as the swarm bot yet pushes STILL parked (head fd14530ac7f0: triggering_actor github-actions[bot]). LESSON: **git push authenticates with the credential actions/checkout persisted (extraheader), which outranks remote-URL tokens — commit author ≠ push actor; mint must precede checkout and checkout must take the Swarm `token:`**. Fix #2777 merged `fc6ac05c3741` ⇒ swarm push @6605913281 fired 26 downstream runs, ALL triggering_actor = termux-fleet-swarm[bot], repo gate SUCCESS, action_required = 0.

**Family 3 — delphi-rfp-feed-collect LANDED** (#2775 merged `9ef9adad262f`, family-1 shape); proof PENDING a rate window: 3 dispatches died at the fetch step (pre-push) — rfp_flood_fetch.py hard-fails on shared-token 403/429 (no defer discipline, unlike ledger_fetch.py); the workflow's own history documents this class (2026-10-29). NOT a swarm regression (fetch auth untouched). Bounded watcher set for the first swarm-triggered downstream run; verification posts on #2750 when a natural cycle clears the window.

**Wave state**: sampled inflow families 3/3 adopted; new parked inflow from these branches should fall to ~0 (re-sample after family-3 proof). The ≥2666 stock stays owner-UI per §11 scope.

## §15 — Widened rotation (provider-utilization fix, owner 2026-11-01)

Owner ruling (via main, 2026-11-01, 2nd widening order): the 4-lane dispatch funnel {Jules, Gemini, DeepSeek, command-dispatch} vs the 89-provider bench is REJECTED — "USE THEM ∀". Rules now in force for this lane's dispatches: (1) every already-triggered/wired provider surface in the Provider Index is a real dispatch arm in the rotation — ∅ default-to-Jules/Gemini; (2) selection = task-fit across the full bench, provider + reason stamped per dispatch; (3) wired-but-unproven surfaces get bounded, DoE-stamped PROOF dispatches instead of permanent inference-only exile; (4) live-state reported to main + manager.

**Arm inventory (evidence-graded, census 2026-11-01 ~11:19Z firsthand):** triggered-today {Jules issues/handoff · Gemini dispatch (monorepo + repo-story transplant) · DeepSeek CI · Qodo (review) · CodeRabbit (review)} · wired-not-today {DeepAgent bridge (last ✓ 2026-10-23) · deepagent-task (0 runs → proof below) · provider-command-dispatch (1 run ever, fix/polish only) · DeepSeek termux-agent device route (dispatch-proven 18✓/2✗, dormant since 2026-10-05)} · Devin triggered-today NOT_ESTABLISHED in sample · provider-batch = probe arm, DEGRADED (see proof 2).

**Proof dispatch 1 — DeepAgent (deepagent-task):** first run ever, 41301564332 SUCCESS (workflow level), 2026-11-01T11:21:56Z; smoke input PR #3052; device steps skipped (reachable=false ⇒ device execution NOT_ESTABLISHED). Stamped on #2735 (comment 6557267123).

**Proof dispatch 2 — provider-batch operational check:** run 41301473553 (workflow_dispatch, check_operational_providers=true) completed FAILURE with the evidence in the job split: contracts job failed (pre-existing #2672 red) ⇒ operational_providers + all observation jobs SKIPPED (gated on contracts). FINDING: the batch bench arm cannot produce capability evidence until the contracts job is green — the gate, not the providers, is the blocker. Fix path = #2672 (meta-lane #2758 class); on green, re-run this dispatch to harvest per-provider operational evidence (cohere/sambanova/zai/llm7/routeway/unorouter/siliconflow).

**Rotation going forward:** task-fit selection across the arms above + bench invoke surfaces as their proof lands; the old funnel survives only as 4 arms among the set, with no default. Every dispatch from this lane carries the provider + reason stamp.

## §16 — Inference surface at scale + net-new wiring wave (2026-11-01)

**Contracts unblocked:** #2672 gate chain (#3126/#3128/#3130/#3138) ⇒ provider-batch contracts GREEN (run 41308987754 = first operational_providers execution ever); Desk-held harvest re-fire 41315737003 SUCCESS (Firecrawl keyless route's first completed execution).

**Inference batch final classes** (ledger #3141, Actions evidence only): INVOKE OK {cohere ×3 models, sealion ×2, baseten} · funded-out @ completion {zai 429, llm7 402, routeway 402, siliconflow 402, huggingface 402 (inference-scoped fleet token; credits exhausted)} · capacity {sambanova 429} · no-credential in Actions secrets {cerebras, kilo, mistral, modelscope, ovhcloud, requesty, typhoon, xfyun} · egress/edge 403 from Actions {groq, xkiro, aion} · catalog/serving skew {nvidia 0/5 served, gemini flagship 404} · consent-gated {unorouter: per-upstream web consent, catalog 324} · no reviewed chat endpoint {felo, omni}.

**Endpoint floor progression (CI counts only; owner rule: MUST BE ACTIONS):** 5,337 (fix-seat public census #3175) → 7,046 (#3189: CI base 6,441 + 893 − routeway dedupe 288) → 7,219 (+deepinfra 173) → 7,317 (+novita 98) → 7,322 (+friendli 5) → **7,342 (+baseten 20)**. groq/aion = uncountable from Actions (egress 403 on catalogs); VM-vantage counts rejected + retracted in the open. Unorouter catalog drift 330→324 noted (churn, no floor move).

**Net-new wiring wave** (provisioning lands ⇒ same-day full-web wiring: provider_extensions + extension catalogs + invoke/batch workflows + quota registry/managers/mappings + regenerated coverage + quota.txt; contracts green per PR): deepinfra PR #3208 (catalog 173, invoke 402 balance) · novita PR #3214 (catalog 98, invoke 403 $0) · friendli PR #3224 (catalog 5, invoke 403 Tier 0) · baseten PR #3235 (catalog 20, **invoke 200 ✓ gpt-oss-120b**; free credits finite ⇒ burn-aware). Pattern note: API-created PRs need close→reopen to spawn gates (QAC-009 class).

**Entry build arms state (2026-11-01 16:00Z):** Jules DOWN (sessions created 3 / completed 0 / errored 3, provider-side) · Gemini CLI OUT (interactions smoke failing) · DeepSeek device tunnel DOWN (runs green, agent never invoked — tunnel-unresolved skip at Start) · **command-dispatch = sole live entry arm**. webWrapper wave held at builder layer (route datum, not campaign verdicts). Repo-Story build held on Gemini capacity return.

## §17 — Owner fact: fleet has no credit card (2026-11-01)

Owner fact (2026-11-01, via provisioning): the fleet has **∅ credit card**. All "owner top-up item" framings in §16 and earlier records are RETIRED. Card-gated = closed class: no-key {nebius, together, cerebras, anthropic/openai, WABA}; funded-out PERMANENT (absent a card existing) {huggingface, deepinfra, novita, friendli, zai, llm7, routeway, siliconflow} — their catalogs still count toward the floor; completions never clear. All "re-fire on top-up" commitments are void. Live completion routes are free-tier/free-credit only: baseten (credits finite), cohere, sealion proven; unorouter remains consent-gated (free action, not card).

## §18 — WebWrapper campaign scope note (owner, via main, 2026-11-01)

Possible future ww scope, recorded for the campaign record (a scope note, not a dispatch): **chat interaction + additional DeepWiki refreshes** — i.e., when the ww cloud/account targets recover (Jules-gated), DeepWiki refresh beyond Devin's built-in cadence is a named candidate task class for the campaign. The wiki's standing dependency remains the Devin API (`DEVIN_API_KEY`). No dispatch is authorized by this note; the wave remains held at the builder layer until a Jules probe session completes.

**Promotion (owner, via main, 2026-11-01): the DeepWiki leg is now a REQUIREMENT, not a scope candidate.** DeepWiki.com requires continuous automated refresh + update, and it has no documented indexing-write endpoint (the public MCP is read-only) ⇒ the refresh path is webWrapper UI interaction, additional to Devin's API automation — which is separately provisioning-gated (`DEVIN_API_KEY` / ORG_ID / EFFORT absent; register PR #3323). Execution stays Jules-gated like the rest of the wave (held at the builder layer until a probe session completes). Import of DeepWiki.com material to our own surfaces belongs to the repo-org tree's design leg (mcp.deepwiki.com read tools); coordinate via main if the legs touch.

**Prep wired (2026-11-01):** the refresh leg's repo-side prep is complete — `docs/ops/DEEPWIKI-REFRESH-WW-PREP.md` (targets, UI refresh flow, cadence, evidence format) + campaign issue #3346 with the embedded builder session brief. Execution waits only on Jules arm recovery.

## §19 — Definition of record: Swarm (owner, 2026-11-01)

**Swarm = ALL providers' inference model endpoints participating in 3L0 DoE.** The Swarm is the participating endpoint population — the full provider catalog as experiment arms under DoE. It is not this seat, not the Termux Fleet Swarm App, and not the workflows: those are its organs (dispatch, minting, evidence). Lane usage aligned: in this record and its reports, "Swarm" names the endpoint population (the endpoint census / floor counts measure exactly that population); the App, workflows, and this seat are referred to by their own names.

## §20 — Dispatch principle: hard-select prohibited (owner, 2026-11-01)

**Hard-select is prohibited as a dispatch pattern.** Dispatched work is routed + assigned across the Swarm's arms (task-fit rotation / tranches) so every dispatch emits **comparative signal** for 3L0/DoE efficiency learning. A single hard-selected arm yields single-plane signal — incomparable, unusable for cross-arm learning. Single-arm routing is permitted only when task constraints genuinely bind (capability/credential class), and is then recorded as a **constrained arm**, never a preference.

**Application to the ww re-fire plan:** on arm recovery, probes **distribute across arms** (Jules, Gemini build_dispatch, command-dispatch, DeepSeek when restored) — not Jules alone. The wave's "Jules-gated" phrasing in §18 and the campaign issues is superseded by this section: Jules recovery unblocks the wave, but re-fire probes run as cross-arm sets with per-instance stamps ({provider, model@version, session/run, role, set index}) so the recovery itself produces comparable evidence.
