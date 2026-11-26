# Endpoint Diagnostic Ledger — #5587 epoch 2026-11-26

First published failure-class ledger for the endpoint diagnostic {secrets-census ⋈ endpoints-db ⋈ quota → fireable set + failure classes}, productized under QUE #5587 (owner-designated REQUIRED UPGRADE, 2026-11-26). Every figure cites its source of record; silent records yield **NOT_ESTABLISHED** entries — figures carry citations, and counts from different surfaces stay unblended.

Compiled 2026-11-26 by direct execution (owner order: Muse lands #5587 itself where the queue claims without executing). Sources read at compile time: `ops/quota/endpoints-db.csv` @ master · `ops/que/feeds/{arm-census,bucket-headroom,pool-cadence}.json` · `ops/quota/{four-counts.md,quota-probe-ledger.jsonl,rate-limit-events.json,availability-observation-2026-11-02.json}` · `ops/compute/{BACKLOG,ALLOCATION}.md` · the #5587 issue record (body + 30 comments).

## Headline counts

| Measure | Count | Source of record |
|---|---|---|
| Registered (endpoints-db rows, provider×model) | **9,589** | `ops/quota/endpoints-db.csv` @ master (read 2026-11-26) |
| Registered provider classes (endpoints-db) | **68** | same (distinct `provider` values) |
| Pool participants generated | **9,588** across 160 g4f provider classes | pool generation 2026-11-18 (#5587 c.6981336032); registries 2026-11-24/25 read {9,588 · 67 providers · 160 probe_ok} (#5587 c.7191886537) |
| Historical catalogue counts (separate denominators; blending barred) | 5,337 floor (census PR #3175) · 7,341 provider×model (counted 2026-11-01) · desk feed 110 providers all lanes / 89 model-lane providers / 95 inference-availability records | #5587 c.6975871317, c.7037762792 |
| Probe-verified (probe_ok = true) | **161** of 9,589 db rows | `endpoints-db.csv` (`probe_ok` column); probe file `probed_at` **2026-11-01** — stale, see failure class F9 |
| Wired | **89** | #3095 burn-down closed 89/89 (#5587 body) |
| Fired (of the wired 89) | **18** | two hand-fired waves, stamped deviations (#5587 c.7191886537) |
| Unfired (of the wired 89) | **~71** | same |
| Activated (provider returned a completion) | **1 — baseten** | wave 2 (#5587 c.6987434610, c.7191886537) |
| Agent-loop PROVEN (receipted transacting dispatch ∧ agent-loop marker, the #3095 acceptance bar) | **4 arms** {sealion · cohere · baseten · gemini-pool} | #5587 c.6980470697; arm-census verdicts 2026-11-13 |
| Participation (activated / registered) | **1 / 9,588 ≈ 0.01%** vs the 100% requirement — **below requirement**, stated as such | derived from the rows above |
| Fired fraction of wired | 18 / 89 ≈ 20.2% | derived |
| Unmapped endpoints-db rows (quota_record empty) | **3,443** | `endpoints-db.csv` (`quota_record` empty); `ops/compute/BACKLOG.md` item 4 |

## Failure-class ledger

| # | Failure class | Count | Evidence of record |
|---|---|---|---|
| F1 | **quota_unknown HOLD** — headroom unreadable at pre-flight, dispatch held | Executor first conversion: **10 eligible / 0 fired / 10 HOLD**. Named-roster pool feed: **7/7 arms deferred, eligible_count 0** (defer reasons incl. quota_unknown ×1 arm, quota_unbudgeted ×5, census_not_passed ×6, route_dead ×2, entitlement_unknown ×1); ledger snapshot itself `unavailable` ⇒ arms defer on quota_unknown | #5587 body + c.6955844381; `ops/que/feeds/pool-cadence.json` (generated 2026-11-12) |
| F2 | **absent-credential deaths** — fired with credential absent from the census, deaths predictable from that census | Wave 1: **3 deaths**. Availability observation 2026-11-02: **7 of 28** catalog rows `error_class=missing_secret` {baseten · cerebras · deepinfra · friendli · kilo · novita · omni} (secret **names** only; credential_present false on 11/28 rows) | #5587 c.6987434610; `ops/quota/availability-observation-2026-11-02.json` |
| F3 | **quota-terminal 429** — bucket terminal at fire time | **1 arm** of record: mistral-codestral, `quota_terminal_429` during agent loop, terminal date 2026-11-11. Class rule: a 429 discovered by a run is a pre-flight defect datum, counted here in the open | `ops/que/feeds/arm-census.json` (2026-11-13) |
| F4 | **pre-flight held (correct holds)** — held by the gate; blind firing excluded | Wave 2: **7 held** (baseten activated from the same wave) | #5587 c.6987434610 |
| F5 | **not_censusable** — census path absent for the arm | **2 arms**: jules · webwrapper-class (verdict failed, `error_class=not_censusable`) | `ops/que/feeds/arm-census.json` |
| F6 | **free_account_unverified** | **1 row**: gemini (availability observation 2026-11-02) | `ops/quota/availability-observation-2026-11-02.json` |
| F7 | **inference_ok = 0** at last full availability observation | **0 of 28** rows inference_ok (credential_present 17 · catalog_ok 21 · inference_ok 0), observed 2026-11-02 — historical, superseded in part by the wave receipts above | `ops/quota/four-counts.md`; availability observation 2026-11-02 |
| F8 | **quota_probe ledger sparsity** — quota_unknown converts only via bounded probes; the probe ledger holds almost nothing | **1 event total** in `quota-probe-ledger.jsonl` (gemini-api-free, 2026-11-13, success, lower-bound headroom 1 request) | `ops/quota/quota-probe-ledger.jsonl` |
| F9 | **stale / fossil inputs** — diagnostic inputs frozen while outputs regenerate | Pool probe file `probed_at` **2026-11-01** (25 days old at this reading); pool registries 2026-11-24 and 2026-11-25 **identical** {9,588 · 67 · 160}; arm-census feed dated **2026-11-13** (7 arms) against 89 wired | #5587 c.7191886537; `ops/que/feeds/arm-census.json` |
| F10 | **execution-plane failures** (machinery, kept apart from endpoint verdicts) | build-dispatch run 44420320995 failed at *Select build arm* (empty arm output off the stale census → **0 provider invocations**); dispatch-watchdog sweep step failed in runs 44434278480 + 44573358888 (`dispatch_watchdog.py` non-zero, intermittent); #5587 itself sat **unclaimed 957 min**, then claimed 2026-11-18 with **zero verdict stamps since 2026-11-20** (placement_failed class) | #5587 c.7029112697, c.7037762792, c.6974568197, c.6994438506, c.7138817189 |
| F11 | **GitHub API bucket walls** (adjacent surface: the fleet's own API bucket; provider inference stays out of this class) | **10 events**: core-exhaustion ×8 · secondary-403 ×1 · unclassified-403 ×1 (2026-10-28 → 2026-10-30) | `ops/quota/rate-limit-events.json` |

Outside the failure classes: HTTP 401 carrying a `WWW-Authenticate` challenge classifies **AUTH-GATED — a LIVE state** (liveness rule, #5587 c.6984866891); failure-class membership excluded, zero-count treatment excluded. Counted AUTH-GATED instances in the records read: **NOT_ESTABLISHED**.

## Specialty field (first-class catalogue field — owner addendum 2026-11-26)

Every catalogue row carries a **specialty** field: what the provider/endpoint is good for (code · long-context · bulk classification · vision · triage/review · agent-loop build · gateway/routing · research). `endpoints-db.csv` ships without a specialty column today — the field stands defined here and populated only where a repo record states the assignment; all remaining rows read **NOT_ESTABLISHED**. Model names alone establish nothing.

Record-stated specialty assignments at this epoch:

| Provider / surface | Specialty (record-stated) | Source of record |
|---|---|---|
| Gemini (AI Studio / API) | primary triage · review · invoke | `docs/schemas/provider-capabilities.md` routing matrix |
| OpenRouter | free peer fallback (tools-capable) | same |
| OmniRoute · Felo | free peer | same |
| wrapper/colab | **code execution** | same (capability flags: code_execution = yes) |
| Bifrost | gateway + MCP agent loop (evaluation only) | same |
| HuggingFace | research / optional | same |
| Build-arm set {sealion · cohere · baseten · gemini-cli · mistral-codestral} | **agent-loop build (code)** — census gate = invocable from Actions ∧ agent-loop tool round-trip for build dispatch | `ops/que/feeds/arm-census.json`; #5151 census spec |
| CompactifAI (carina-60b · quasar-1-2-358b) | **bulk classification** {endpoints-db alias reconciliation · System-1 intake classification} · **long-context** (quasar 1M ctx) | `ops/compute/BACKLOG.md` item 18 |
| g4f pool (the 9,588) | unmetered **bulk inference** | `ops/compute/ALLOCATION.md` surface card |
| All other registered providers/endpoints (incl. vision/media classes such as HuggingFaceMedia) | **NOT_ESTABLISHED** — repo records leave specialty unstated for these rows | — |

### Pool generation — composition by specialty (mix'n'match)

The specialty field is the **composition key for the DoE pool generator** (owner design note 2026-11-26: "DoE can mix'n match catalogue specialists"). Generated sets are composed **heterogeneously by specialty** — e.g. one code arm + one long-context arm + one bulk-classification arm in a single set — with heterogeneous composition in the lead and like-for-like comparison available within one specialty. A set's receipt set therefore records the specialty mix it ran, and DoE scoring reads performance per specialty slot as well as per arm.

## End-state framing (owner addendum 2026-11-26)

**End state:** ALL available inference endpoints enrolled → active pool generated **from the fireable set** (the diagnostic's live join output, with fossil inputs retired) → triggered for duty.

**Standing today, plainly:** of **9,589** registered endpoints, the number sitting in an active pool generated from a live fireable set and triggered for duty is **1 (baseten)**. The generated pool registry holds 9,588 participants, built from fossil inputs (F9) rather than the fireable set; the fireable set's own size awaits publication and reads **NOT_ESTABLISHED** at this epoch. Enrollment stands nearly complete; activation stands at 1.

## Pending enrollments (owner directive 2026-11-26 — autonomous enrollment, highest QUE priority)

| Provider | Status | Source |
|---|---|---|
| Concentrate | **enrolled-pending-census** | reference intake #5591 c.7202373902; directive #5587 c.7202912452 |
| Prima Labs | **enrolled-pending-census** | reference intake #5591 c.7202373902; directive #5587 c.7202912452 |

Enrollment ≠ participant: both rows advance to census → pre-flight → activation under the standing gates (live headroom read or coverage-stamped upper bound · parallel sets ≥3 arms · per-arm receipts).

## NOT_ESTABLISHED register

- **Per-endpoint verdicts for the wired 89** — aggregate wave counts exist (18 fired · 1 activation · 4 proven arms named); the per-endpoint verdict list awaits publication. This ledger is the aggregate of record; the per-endpoint list remains owed by the wired-89 completion leg (#5587 upgrade scope ②③).
- **Wave membership** — which 18 endpoints fired across waves 1–2 (wave 1 = 8 providers per `ops/compute/BACKLOG.md` item 1); per-endpoint wave receipts are absent from the repo records read.
- **Balance-gated endpoint count** — repo records carry zero counts of balance-held endpoints; the class exists in the gate rules while its population reads NOT_ESTABLISHED.
- **429 counts during waves 1–2** — wave receipt files are absent from the repo records read.
- **Per-endpoint live headroom (inference buckets)** — `bucket-headroom.json` covers GitHub-side buckets only; inference-endpoint headroom reads NOT_ESTABLISHED at this epoch.
- **DoE scoring stamp on the stress test** — the #5587 record at compile time carries zero scoring stamps.
- **Fireable-set size at this epoch** — the diagnostic join's output count awaits publication; sizing the end-state metric (pool generated from the fireable set) waits on it.
- **Specialty population** — the specialty field is populated only for the record-stated assignments in the specialty table; the remaining registered set reads NOT_ESTABLISHED pending a census recording specialty per provider/endpoint.

## Refresh rule

This ledger is per-epoch. The diagnostic refreshes every cycle from live inputs {secrets-census (names only) ⋈ endpoints-db ⋈ quota}; a stale diagnostic is a pre-flight defect (flywheel POLICY Rule 11: STALE = FAIL). The next epoch supersedes this file's counts with a fresh compile; silent edits stay barred.
