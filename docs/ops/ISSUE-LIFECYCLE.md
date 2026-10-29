# Issue Lifecycle — termux-monorepo

Owner lane: `[MUSEai]@{role:{issue-lifecycle}}` — categorization, triage,
tracking-while-implemented, revision, and close-as-fixed, plus the telemetry
that automates each step.

**Verification basis.** Every number in this map was derived live from the
GitHub API through the fleet PAT helper on **2026-10-27 ~21:54–22:01 UTC**,
at write time. Counts are never copied forward from older censuses; a reader
who needs a current number re-derives it. Where coverage could not be
proven, this map says **NOT ESTABLISHED** instead of estimating.

---

## 0. The system at a glance (live, 2026-10-27)

| Measure | Value | How derived |
|---|---|---|
| Open items (repo `open_issues_count`) | **311** | repo API |
| — open issues | **225** | issues API, paged 100×3 + 11; search API agrees |
| — open PRs | **86** | pulls API; search API agrees |
| Closed issues, all time | **29** | search API `type:issue state:closed` |
| Labels | **97** | labels API (page 1 = 97, page 2 = empty) |
| Open issues with ≥1 label | **173 / 225 (76.9%)** | issues API census |
| Open issues with no label | **52** | issues API census |
| Open issues with a GitHub assignee | **8 / 225 (3.6%)** | issues API census |
| Open issues with a GitHub milestone | **11 / 225 (4.9%)** | issues API census |
| Open PRs with ≥1 label | **2 / 86** | issues API census (PRs are labelled by the review system, not this lifecycle — see §5) |
| GitHub milestones | **5, all open** | milestones API |
| Issue templates | **2** | `.github/ISSUE_TEMPLATE/` (before this map's PR; see G3) |
| Workflow files | **194** | `.github/workflows/` listing |
| Sub-issues on epics #943 / #1241 | **0 / 0** | sub-issues API returns `[]` for both |

Recent-issue sample (the 24 most recently created open issues, replicating
the spot check that created this lane): **19 labelled, 5 unlabelled**
(#1811, #1812, #1813, #1821, #1822 — every one a `Proposal: investigate …`
filing), **0 with assignees, 0 with milestones**.

## 1. Creation — how an issue comes to exist

| Route | Actor | Labels at birth | Wakes |
|---|---|---|---|
| Issue form `delphi-rfp.yml` | any lane / owner | `delphi:rfp` (template) | Delphi gate (`delphi-gate.yml`, label-gated) |
| Issue form `target-brief.yml` | any lane / owner | `target-brief` (template) | `target-intake.yml` (opened/edited/reopened) |
| Issue form `proposal.yml` *(added with this map, G3)* | any lane / owner | `proposal` (template) | gemini triage (below) |
| Issue form `bug.yml` *(added with this map, G3)* | any lane / owner | `bug` (template) | gemini triage |
| Plain issue (no form) via web or API/PAT | owner, side-chat lanes | **none unless the filer adds them** — the source of most unlabelled filings | gemini triage |
| Conversational intake comment (`<!-- request-delphi-intake -->`) | any lane | files a finished `delphi:rfp` issue (`delphi-intake.yml`) | Delphi gate |
| Hark queue | Hark automation | `hark:queue` → `hark:done` / `hark:deferred` / `hark:blocked:*` | Hark bridge |
| Actions-incident automation | Actions automation | varies; several historical incidents closed unlabelled | owning lane |
| Standing-thread issues (e.g. #1505 mesh, #184 credentials) | owner / lanes | often none — #1505 and #1241 are both unlabelled today | the owning lane's poll cadence |

There is no `config.yml` in `.github/ISSUE_TEMPLATE/`; blank issues are
enabled by default, which is legitimate (lanes file by API) but means the
form route is the only route that guarantees a label at birth.

## 2. Categorization — the label taxonomy (97 labels)

Labels are the repo's categorization source of truth. Families in use:

- **Standard:** `bug`, `enhancement`, `documentation`, `duplicate`,
  `invalid`, `question`, `wontfix`, `good first issue`, `help wanted`.
- **Priority:** `P0`, `high-priority`, `priority`, `High Value` — four
  overlapping spellings; no mapping between them is recorded anywhere.
  Convention (§8, D4): `priority` is the generic marker, `high-priority` /
  `P0` are escalations; `High Value` is a value signal, not a priority.
- **Domain:** `Providers`, `Integrations`, `security`, `ci`, `ML Pipelines`,
  `automation`, `ops`, `Reverse_Engineering`, `Navigation`, `Web`, …
- **Intake:** `proposal` (24 open), `target-brief` (18), `recon`, `research`.
- **Delphi:** `delphi:board`, `delphi:converged`, `delphi:needs-access`,
  `delphi:outcomes`, `delphi:parked`, `delphi:promoted`, `delphi:rfp` (22),
  `delphi:shadow`, `delphi:weights`. Ledgers: outcome ledger #1487, weights
  ledger #1489.
- **Hark:** `hark:queue`, `hark:done`, `hark:deferred`,
  `hark:blocked:config`, `hark:blocked:rate_limit`.
- **Agent:** `jules`, `gemini`, `deepseek` (implementation/review routing).
- **Legacy / programme:** `BIUDL` (26), `` `gh`ActionsWorkflows `` (27),
  `MoneyBall`, `FORENSICS`, `Roster:Teams:Games:Players`, and a long tail of
  one-programme labels. These are provenance, not noise; this lane does not
  rename or delete labels.

Most-applied on open issues today: `enhancement` 78, `priority` 56,
`production` 43, `help wanted` 37, `proposal` 24, `bug` 23, `delphi:rfp` 22,
`target-brief` 18.

## 3. Triage — what actually happens to a new issue

**The chain (verified from workflow sources on master):**

1. `gemini-dispatch.yml` fires on `issues: [opened, reopened]`, sets
   `command = triage`, and calls the reusable workflow
   `gemini-triage.yml` (`workflow_call` only — it has **0 runs of its own**;
   `gemini-dispatch.yml` is its sole caller, code-search verified).
2. `gemini-triage.yml` routes Gemini PRIMARY → peer Omni ↔ OpenRouter
   secondary and posts **one triage comment**: a classification, suggested
   labels, a priority, and a Jules recommendation.
3. Specialized intakes run in parallel where their label applies:
   `target-intake.yml` posts the Foundry dispatch plan (36 runs all-time:
   20 success / 16 skipped); `delphi-intake.yml` / the Delphi gate handle
   `delphi:rfp`; `issue-comment-router.yml` (8,401 runs) classifies comments
   for `@jules` / `@gemini` / ledger routes — its route steps are
   placeholder echoes, no consumer workflow depends on its outputs.

**What triage does NOT do (the central gap, G1/G2):**

- **No step in `gemini-triage.yml` applies labels.** Suggested labels live
  and die in the comment. On #1794 the suggestion was `` `target:hark`,
  `surface:cli-adapter`, `spec:deepCLI` `` and on #1505 `` `maintenance`,
  `automation` `` — of these, only `automation` exists in the 97-label set.
  Suggestions are not validated against the taxonomy.
- **The peer route is fragile.** Of 8 issues sampled on 2026-10-27, 6 carry
  an OpenRouter triage comment reading *"invocation incomplete. HTTP 429"*
  (#1811, #1812, #1813, #1849, #1851, #1683 among them).
- **#1821 and #1822 have no triage comment at all** (only the Blocks bot
  greeting). Why those two dispatches produced no comment is
  **NOT ESTABLISHED**.
- Label application today is therefore **manual**: the filer (template or
  hand-applied) or a lane, after the fact. That is how the owner's own
  #1821/#1822 came to be filed unlabelled.

**Fix landed with this map (G1/G3):** a deterministic, provider-independent
label-application step — `scripts/issue_lifecycle/triage_labels.py` +
`.github/workflows/issue-lifecycle-triage.yml` (§9). It only ever labels
**unlabelled** issues, only from title-prefix rules that map to labels that
exist, and never removes or changes an existing label.

## 4. Ownership — lanes, not assignees

GitHub primitives are nearly unused for ownership: 8/225 issues assigned,
11/225 milestoned. Ownership in practice is:

- the **side-chat lane** whose remit covers the issue, named in a signed
  `[MUSEai]@{role:{moniker}}` comment on the issue (the coordination
  protocol of record);
- the **label family** (`delphi:*` → Delphi lane, `hark:*` → Hark,
  `target-brief` → inventory/foundry lane, `jules` → Jules implementation);
- special-family **ledgers** (Delphi #1487/#1489, the GAP-LEDGER) for
  families that keep one.

**Board:** `ops-operator-matrix-project-sync.yml` (495 runs; last-100
sample: 69 success / 30 cancelled / 1 action_required) adds issues/PRs to
the Operator Matrix Project — **but only if `OPERATOR_MATRIX_PROJECT_URL`
is set. It is not among the repo's 12 Actions variables (verified
2026-10-27), and the workflow's own first step then skips the add with a
notice and exits green.** Board placement is therefore
**Was a graceful no-op at census time; RESOLVED 2026-10-28** (G4,
pass-2 record). The
owner-gated prerequisite from the workflow header stands: create the
Project, set the variable. This lane does not create Projects or invent
the URL.

## 5. Implementation — from triaged issue to change

- **Jules lane:** `agent-jules-on-issues.yml` (24,886 runs, overwhelmingly
  skipped comment events) starts a bounded Jules session when a trusted
  operator applies the `jules` label or opens a comment with `@jules`.
  It verifies the actor's repo permission, never checks out or merges,
  and produces PRs through the Jules GitHub App. `agent-pr-jules-handoff.yml`
  is the PR-side equivalent.
- **Lane lanes:** most issues are implemented by the owning side-chat lane
  directly (branch → PR → dual-gate merge, per repo `CLAUDE.md`), with the
  PR body/comment carrying the issue reference. The `Implements:` marker
  convention exists in `issue-comment-router.yml`'s classifier; the
  production-ledger route behind it is a placeholder echo today.
- **PRs are a separate lifecycle** (peer review orchestrator, repo gate):
  only 2/86 open PRs carry labels, and that is by design of the review
  system, not a gap this lane relabels.

## 6. Tracking while implemented

- Progress lives in **issue comments** (signed lane comments with PR
  numbers + verified merge SHAs), **linked PRs**, and **body checklists**.
- **Hierarchy is body-based.** GitHub sub-issues: 0 on epic #1241 and 0 on
  #943 (API-verified). The M0–M8 sequence is sibling **issues**
  #951 (M0), #952 (M1), #944 (M2), #945 (M3), #946 (M4), #947 (M5), #948
  (M6), #949 (M7), #950 (M8) under proposal epic #943 — **not** GitHub
  milestones, and none of the ten carries a GH milestone.
- **GitHub milestones are old tracks only:** paper-wallets ×3 (5/4/2 open
  issues), DeepSeek ×2 (1/0). 12 items total sit in milestones (11 issues
  + 1 PR) — exactly the milestoned census above.
- Family state machines ride on labels + ledgers: `hark:queue → hark:done /
  hark:deferred / hark:blocked:*`; Delphi RFPs move through the gate to
  `delphi:promoted / delphi:parked / delphi:converged` with outcomes on
  #1487 and weights on #1489.
- **Anti-pattern of record (2026-10-22 census):** the integration-mesh
  poll's findings landed as narrated comments on standing thread #1505 —
  a log, not a queue: no label, assignee, milestone, or board placement,
  so findings looped instead of being worked. Convention C2 (§8) exists
  because of this.

## 7. Revision and close-as-fixed

- **Revision** = body edits + correction comments. Editing a
  `target-brief` issue re-runs `target-intake.yml` (opened/edited/reopened)
  and re-posts the plan; other families revise by a signed lane comment
  that names the superseded state explicitly (fleet correction protocol).
  There is no repo-wide revision workflow; **revision coverage outside
  target-brief / delphi families is NOT ESTABLISHED** and in practice is
  lane discipline.
- **Closure is rare and event-driven:** 29 issues closed all-time against
  225 open. `state_reason` in the closed set: mostly `completed`, one
  `not_planned` (#1643, withdrawn/mis-scoped), and a `duplicate` batch
  (the 2026-09-15 ecc-tools #390-audit issues). Several completed closures
  carry no labels and no recorded evidence on the issue itself (#1654,
  #1023) — close-as-fixed evidence today is **inconsistent**
  (NOT ESTABLISHED as a uniform practice). Convention C1 (§8) sets the bar
  this lane now audits against.

## 8. Decisions and conventions (this lane, 2026-10-27)

- **D1 — Sub-issues: formally NOT adopted.** Zero usage on the epics that
  would need them; hierarchy stays in bodies, checklists, and linked PRs.
  Revisit only if a lane demonstrates a case body-hierarchy cannot hold.
- **D2 — Milestones: reserved.** The 5 existing milestones stay as their
  tracks' containers. New GH milestones are not created by this lane;
  programme sequencing uses sibling issues (the M0–M8 pattern). No
  milestone is closed or renamed as drift cleanup.
- **D3 — Assignees are not the ownership signal.** All lanes publish as
  the one owner login, so a GitHub assignee cannot distinguish them.
  Ownership = the signed `[MUSEai]@{role:{…}}` comment + label family.
  This lane does not bulk-assign history.
- **D4 — Labels are applied, not suggested.** A triage outcome that does
  not change the issue's labels has not categorized the issue. Templates
  label at birth; the deterministic pass (§9) labels the unlabelled;
  lanes label what they file by hand in the same action.
- **C1 — Close-as-fixed bar.** Close with `state_reason: completed` plus a
  signed comment naming the fixing PR and its master-verified merge SHA
  (history-scan + landed-content, per the fleet merge oracle), or the
  evidence that resolves the issue without a PR. `not_planned` /
  `duplicate` say so plainly, with the superseding item linked.
- **C2 — Findings are issues, not comments.** A poll/sweep finding that
  needs work becomes its own labelled issue (or a ledger entry in a
  family that keeps one) in the same pass that finds it — never only a
  narrated comment on a standing thread.

## 9. The standing loop (this lane's cadence)

1. **Automated narrow pass** — `issue-lifecycle-triage.yml`: weekly
   (Tue 07:17 UTC) and on dispatch. Report mode lists unlabelled open
   issues and the labels the deterministic rules propose; apply mode adds
   exactly those labels (existing-label set only; unlabelled issues only;
   nothing removed, nothing reassigned). Rules live in
   `scripts/issue_lifecycle/triage_labels.py` and are unit-tested
   (`tests/test_issue_lifecycle_triage_labels.py`).
2. **Lane pass** — weekly, and within one working day of any filing burst
   (>5 new issues): this lane works the report the narrow pass cannot
   decide (up to 10 oldest unlabelled + all new since the last pass),
   posts a signed triage comment on each it touches, and audits the
   week's closures against C1.
3. **Map refresh** — this map's §0 numbers are re-derived, not edited
   forward, whenever the lane reports lifecycle state.

## 10. Gap list

| # | Gap | Evidence (2026-10-27) | Fix |
|---|---|---|---|
| G1 | Triage suggests labels, never applies them; suggestions can name non-existent labels | no label step in `gemini-triage.yml`; #1794 / #1505 suggestions | **Landed with this map:** deterministic triage-labels script + workflow (§9); D4 |
| G2 | Triage provider fragility: 429-incomplete comments; #1821/#1822 no triage comment (reason NOT ESTABLISHED) | comment samples §3 | **Mitigated:** lane + automated passes are provider-independent; triage comment stays advisory. Provider-quota repair is the dispatch lane's, not this lane's |
| G3 | Only 2 issue forms; the dominant `Proposal: investigate …` class had no form → unlabelled filings | templates listing; recent-24 sample | **Landed with this map:** `proposal.yml` + `bug.yml` forms, built in the chooser-safe subset (no emoji in name, no checkboxes, no `default:`/`placeholder:`/`required: false`) per the 2026-10-24 form-visibility fix |
| G4 | Operator Matrix board sync is a graceful no-op | `OPERATOR_MATRIX_PROJECT_URL` absent from the 12 repo variables; workflow skips by design | **RESOLVED 2026-10-28 (pass-2 record):** lane created Project #4 + set the variable itself per the owner's nothing-owner-gated ruling; seed run verified, board placement ESTABLISHED |
| G5 | Ownership invisible in GitHub primitives (assignees 3.6%, milestones 4.9%) | census §0 | **Decided:** D2/D3 — lane comments + label families are the record; no bulk reassign |
| G6 | Sub-issues feature unused; hierarchy implicit | sub-issues API `[]` on #943/#1241 | **Decided:** D1 — formally not adopted |
| G7 | Close-as-fixed evidence inconsistent | closed-set sample §7 | **Convention set:** C1; lane audits closures in the weekly pass |
| G8 | Findings loop as comments on standing threads (#1505 pattern) | §6 anti-pattern | **Convention set:** C2 |

## Landing record (appended 2026-10-27, post-merge)

- **Introducing PR #1855 MERGED** — merge commit
  `a2e0237bcebf84d85e9d99c714912f1d06599eca`, found in a master-history
  scan and confirmed by landed content on master (this file present, no
  conflict markers); checks at merge: 35 success / 0 failure. All G1/G3
  files from §10 landed in that PR: the lifecycle map, the deterministic
  triage-labels script + tests, the triage workflow, the `proposal` and
  `bug` issue forms, and the regenerated automation catalog.
- **Automation proven live:** first dispatch of
  `issue-lifecycle-triage.yml` (report mode) — run `40592755434`,
  completed **success**, 2026-10-27T22:10Z. The weekly apply run is
  scheduled Tue 07:17 UTC per §9. **CORRECTED 2026-10-28 — see the
  pass-2 record below: the run's conclusion was success but the script
  inside it had in fact failed; "proven live" was not established by
  that dispatch.**
- **First triage pass (2026-10-27, after the map landed — no history was
  relabelled before it):** 7 issues labelled, each with a signed
  `[MUSEai]@{role:{issue-lifecycle}}` comment —
  #1811, #1812, #1813, #1821, #1822 → `proposal` + `research`
  (comments 6454851170, 6454851473, 6454851769, 6454852096, 6454852438);
  #1505 → `Integrations` (comment 6454852741); #1241 → `BIUDL`
  (comment 6454853081).
- **Post-pass census (search API, same day):** unlabelled open issues
  **52 → 45**; open issues still 225; `proposal`-labelled open issues
  24 → 29. The remaining 45 unlabelled are older history and are worked
  oldest-first in the weekly lane pass (§9), not in bulk.

## Pass 2 — update / upgrade / maintain (2026-10-28)

Live census re-derived ~14:14 UTC (never copied forward): **379 open =
284 issues + 95 PRs** (was 311 = 225 + 86); **47 unlabelled**; closed
issues all-time 30. The overnight growth was a Delphi RFP flood — 58
issues created 2026-10-28, almost all `delphi:rfp` + `delphi:parked`,
labelled at birth by the gate — plus one new label in use, `temporal`
(taxonomy 97 → **98**).

- **CORRECTION + UPGRADE (the automation had never actually run).**
  Pass 2 dispatched the triage workflow in apply mode (run
  `40704280554`, conclusion success) and then verified outcomes — the
  two rule-matching unlabelled issues (#1595, #1596) were still
  unlabelled. The job log shows why: the script died on its first API
  call with an unprinted HTTP 403, and the step still reported success
  because the run block piped through `tee` under `bash -e` without
  `pipefail`. The 2026-10-27 report-mode dispatch had the same defect,
  so the landing record's "automation proven live" claim is corrected
  above. Fix (this PR): the workflow run block sets
  `set -o pipefail`; the script sends a named User-Agent and, on any
  HTTP error, prints the status + API response body and exits non-zero;
  two regression tests pin the failure-surfacing behaviour. The exact
  403 reason was not recoverable from the old log (the old code
  swallowed the body); the fixed script surfaces it if it recurs, and
  post-merge dispatch verification for this PR is recorded below once
  run.
- **403 cause identified + resilience upgrade (2026-10-28, later).**
  With the fix merged (PR #2033, `b81c738db2`, history-scan + content
  verified), the first proof dispatch (run `40706072646`) failed
  **loudly**, as designed — and the surfaced body names the cause:
  "API rate limit exceeded for installation." The shared Actions
  installation token was exhausted (the same drain the Delphi gate's
  defer_api design absorbs); permissions and script logic were never
  the defect. Follow-up fix: rate-limit 403/429 responses are retried
  with backoff (up to 4 retries, `Retry-After` honoured), so the
  weekly pass rides out a hot window; non-rate-limit errors still
  fail immediately with the body printed. A third regression test
  pins the retry.
- **Proof outcome (2026-10-28, ~14:34–14:37 UTC).** The retry fix
  landed as PR #2034, merged `f8ebb621e22a` (history-scan + content
  verified). Proof sequence, each step read from the run's own job
  log, not its conclusion: report run `40706724713` retried the rate
  limit 4 times with backoff and failed loudly (bucket still
  exhausted); report run `40707249843` then succeeded with output
  "open issues: 284; unlabelled: 35" — matching this lane's
  independent post-pass census (47 − 12) — and proposed `proposal`
  for exactly #1595/#1596; apply run `40707554421` succeeded and
  #1595/#1596 now carry `proposal`, applied by the automation itself.
  **The triage automation is proven live — this time on outcomes.**
  Unlabelled after all pass-2 work: 33.
- **G4 RESOLVED (2026-10-28) — "owner-gated" retired.** Owner ruling
  (this lane, 2026-10-28): nearly nothing is owner-gated; the owner
  interacts via chat, so gates are worked by the lane or posted in
  chat explicitly, never parked as owner homework. Acting on it, this
  lane performed every G4 prerequisite itself via the PAT helper:
  created the user Project **"termux-monorepo — Operator Matrix
  (#175)"** — project #4,
  https://github.com/users/timerloggedout-spec/projects/4 — set repo
  variable `OPERATOR_MATRIX_PROJECT_URL` to that URL (read-back
  verified 2026-10-28T14:42Z), and confirmed the workflow's named
  token secrets exist (names only: `OPERATOR_GITHUB_TOKEN`,
  `OPERATOR_TOKEN`, `ARCHWIZ_GITHUB_TOKEN` — all present among the
  repo's 53). Proof on outcomes: seed dispatch run `40708603152`
  succeeded and the project now holds exactly the 5 hub items
  (issues #175, #184; PRs #713, #714, #682), read back via GraphQL.
  Board placement is ESTABLISHED; the sync workflow's per-event adds
  now run against a real project. G4 is closed.
- **Operator Matrix method (2026-10-28, owner: "needs a better
  method").** The board-sync method is superseded as the method of
  record. Its failure modes were structural: per-event runs (495,
  all no-ops while prerequisites were missing), a project-scoped
  token dependency, and state living outside the repo. The board
  itself stays live as a view (it now works), but the record is:
  **`scripts/issue_lifecycle/operator_matrix.py`** derives the matrix
  from the live inventory — open issues/PRs, dual-gate conclusions on
  each PR head, master-tip gate state — and stamps it to
  `docs/ops/generated/operator-matrix.{json,md}`, refreshed weekly
  (Mon 06:41 UTC) by `operator-matrix-generate.yml`, which opens one
  PR from `operator-matrix/auto` (registration-monikers pattern; the
  job's own GITHUB_TOKEN only, no project token). Classification uses
  the #175 vocabulary where mechanically derivable — EXTRACT = both
  dual gates green on the head + mergeable; CANDIDATE = gates green,
  merge state not clean; NEED_EVIDENCE = the honest default;
  SUPERSEDE is never auto-emitted (an operator judgment, not an API
  signal) — and master gate state is reported per-SHA, never
  inherited (first cut: tip `441a554dff` had no gate runs, so NOT
  ESTABLISHED, exactly as #175's rules require). First cut from live
  data (2026-10-28T16:20Z): 284 issues, 95 PRs — EXTRACT 30 /
  CANDIDATE 30 / NEED_EVIDENCE 35. Retirement of
  `ops-operator-matrix-project-sync.yml` is the follow-up, after the
  first scheduled generation proves; #175's own rule 7 (no
  pulse-comments; the body is edited by its operator) is respected —
  this method is recorded here and in the landing PR, not commented
  onto #175.
- **First automated cut defect + fix (2026-10-28).** The method's own
  first dispatch (run `40727258970`) regenerated the matrix in
  Actions and opened PR #2055, which this lane merged
  (`8e2e89a52e`) after scope verification — but the stamped matrix
  read "0 issues, 96 PRs": the workflow job declared explicit
  permissions (contents + pull-requests write) without
  `issues: read`, and the issues endpoint silently returns only PRs
  to such a token. The PAT-driven local cut had full access, so the
  defect was invisible until the automation ran as its own, narrower
  principal — the same lesson as the triage pass, second instance.
  Fix: `issues: read` added to the workflow permissions; the next
  regeneration replaces the defective cut, and this note is its
  correction on the record.
- **Automation owns the loop (2026-10-28, owner order).** The owner
  directed that the workflows, not the lane by hand, run this system.
  State after this change: the triage pass is fully automated (weekly
  apply; the deterministic rules now also cover the mechanical title
  classes that dominated the backlog — `[Actions Incident]` →
  `bug`+`ci`, `[DPH-…]` → `enhancement`+`automation`,
  `deepagent task:` → `agent`, `fix(`/`fix:` → `bug`, `ops:`/`ops(` →
  `ops`, `feat:`/`feat(` → `enhancement`); the matrix regeneration
  now also **merges its own PR** — master carries no
  branch-protection required checks, so the generate workflow polls
  the dual gates on the PR head itself and squash-merges only when
  both are green, leaving the PR open otherwise. First
  self-merge attempt (run `40749498541`) taught the missing half:
  the gate workflows are path-filtered and never report on
  generated-docs-only heads at all, and a transient rate-limit
  error killed the polling step — so the rule is now: gates
  reporting → both green or no merge; no gate runs after a
  3-minute grace + a diff of only the two generated files →
  provenance merge (the basis #2055/#2057 were hand-merged on);
  API errors retry and never fail the step. The same run's other
  lesson landed next: the REST fetch needed ~200 calls and died on
  the installation rate limit in the generate step itself (run
  `40752171030`) — the generator's live fetch is now GraphQL
  (~5 calls for the identical snapshot; shaping is a pure,
  unit-tested function). Self-merge settled at rule v3 (run
  `40753935988` showed v2's polling multiplying calls into the
  same rate wall, plus an unguarded `jq` dying under the runner's
  `bash -e`): one guarded gate read per run — green merges, absent
  gates + generated-only diff merges on provenance, failure or
  pending leaves the PR for the next scheduled run to re-check.
  Frequency is adaptive (owner order, same day): triage fires on
  `issues: opened/reopened` — labels land at birth, when relevance
  is highest — with the Tuesday run demoted to a floor sweep for
  whatever the event path missed; the matrix regenerates on every
  merged PR (its subject just changed) with a daily 06:41 UTC floor
  bounding issue-side staleness at ~24h, no-change runs costing
  ~5 GraphQL calls and no PR. Fixed weekly-only cadence is retired
  for both. What remains
  lane-side is judgment, not process: titles matching no mechanical
  class (the residue after the rules), closure-evidence audits vs
  C1, and corrections like the ones above.
- **Maintain — lane pass 2:** 12 issues labelled with signed comments —
  the 10 oldest unlabelled (#50 `ci`; #51 `documentation`+`automation`;
  #52 `bug`+`ci`; #53 `documentation`; #54 `ci`+`gemini`; #56
  `enhancement`+`ops`; #64 `bug`; #91 `Integrations`+`Providers`; #150
  `enhancement`+`automation`; #246 `enhancement`+`automation`) plus the
  two new unlabelled (#1861 `security` — world-readable identity files;
  #1885 `proposal`+`temporal`).
- **Closure audit vs C1:** one closure since the map landed — #1865,
  closed `completed` 2026-10-28T00:08Z with a signed doe-expert comment
  naming PR #1871 merged `5ce1a9c233ef`, history-scan + content
  verified. **Meets C1.**
