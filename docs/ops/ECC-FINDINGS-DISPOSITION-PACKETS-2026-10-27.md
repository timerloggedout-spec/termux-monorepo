# ECC Findings — Disposition Packets (G-06 prep, 2026-10-27)

Prep only. This packet **prepares** dispositions for the ECC Tools findings
queue (Gap Ledger G-06); it does not disposition or fix anything. Every
recommendation below is a proposal for the owner's decision. No comment was
posted on any subject PR; all evidence was read live through the PAT helper
on 2026-10-27.

Sources: `docs/ops/generated/reviewer-metrics.json` (providers/ecc),
ECC Tools audit comments on PRs #125 / #143 / #1514 (full pagination),
PR / compare / contents / check-runs APIs at the heads named below,
`scripts/reviewer_metrics/collect.py` (counting logic),
`docs/ops/GAP-LEDGER.md` G-06.

## 1. What the headline number actually counts

The G-06 headline — `findings_action_required: 14` (Security Evidence 8,
PR Config Audit 6), `current_head_findings: 1` — comes from
`reviewer-metrics.json`, generated 2026-10-24T11:09Z. Three different units
are in play and must not be conflated:

| Unit | What it is | Count |
|---|---|---|
| AR audit comment | One ECC audit comment whose conclusion is `action_required`. ECC re-audits on pushes and in sweeps, so one underlying issue produces many AR comments over a PR's life. | 14 in the collector's 2026-10-24 window (see below) |
| Bullet finding | One `- [high] …` line inside a single audit comment at one audited SHA. | 11 per mega-PR at last-audited head (§3) |
| Disposition item | One (gate, file, issue) group an owner can actually decide on. | 9 (§4) |

Collector mechanics (`collect.py`, verified in source): for each PR in a
most-recently-updated window it reads **only the first 100 issue comments**
(`per_page=100`, no pagination) and counts every ECC audit among them with
conclusion `action_required`; `current_head_findings` counts those whose
marker SHA equals the PR head at collection time. The metrics file stores
no per-PR breakdown.

Reconciliation, live-derived 2026-10-27:

- The 8 Security AR in the metrics window are exactly PR #1514's first
  eight audited SHAs — its first-100 comments contain 8 Security
  `action_required` audits (comment ids 6336149863, 6336159325, 6336498820,
  6339555719, 6340024002, 6340238122, 6342757643, 6347476882). The ninth
  audited SHA is #1514's current head, and its audit comment sits beyond
  the first 100 comments (the PR has 117 issue comments; the head set is
  in the last 17), so under the collector's own logic #1514 contributed
  the 8, not the at-head 1: which PR contributed the window's
  `current_head_findings: 1` is **NOT ESTABLISHED** from the metrics
  file. That #1514 *does* carry an action_required finding at its
  current head is a separate fact, verified directly in §3.3 from the
  audit marker and the mirror check run — it does not depend on the
  collector's count.
- Re-running the collector's exact logic today over the 100 most recently
  updated PRs finds **only #1514** (8 AR, all Security Evidence; 655 audit
  comments in window). The 6 Config AR of 2026-10-24 came from PRs that
  were inside that day's updated-window; the metrics file does not name
  them and they are **NOT ESTABLISHED** from the file. They are not PR
  #125 / #143 under collector logic: both PRs were created in August, so
  their first 100 comments predate ECC Tools entirely (0 ECC audits in
  either first-100, verified today).
- A first-100 sweep of **all 292 PRs created 2026-10-20…24** (the ECC
  era's first days) finds exactly six AR contributors — #1302 (closed,
  Security 1), #1371 (closed, Security 1), #1377 (closed, Config 1),
  #1486 (closed, Config 1), #1514 (open, Security 8), #1574 (closed,
  Config 2) — a *different* 14 (Security 10 / Config 4) from the metrics
  file's 14 (Security 8 / Config 6). Windowed collector totals move with
  window membership and cannot be mapped onto this queue; the queue
  below stands on the mirror / audit-thread evidence, not on the
  collector total.
- The disposition queue itself (#125 / #143 / #1514) was identified
  independently of the collector — from the ECC check-run mirror
  (PR #1491) and the audit threads — and is the queue the Gap Finder
  recorded. This packet dispositions that queue. Raw all-time AR audit
  comment totals (525 on #125, 586 on #143, 9 on #1514) are repetition
  counts, not findings, and are not used anywhere below.

## 2. Re-audit method (at current head)

For each PR: current head fetched live; **all** ECC audit comments fetched
with full pagination (#125: 1,580 ECC comments over 264 audited SHAs;
#143: 1,758 over 293; #1514: 54 over 9); the latest audited set (6 gate
audits at the newest audited SHA) extracted; every flagged file's blob SHA
compared across (a) last-audited SHA, (b) current head, (c) current
master; the audited→head delta read from the compare API; check runs at
head read for ECC mirror runs.

## 3. Per-PR packets

### 3.1 PR #125 — "analyze agentic workflows and peer coordination rules"

- State: open. Base: `master` (`aec8efbe9891`). Current head:
  `b7e4709b5036f35999013393bb2a8f5b21a11fcc` (updated 2026-10-24T23:34Z).
- Last ECC-audited SHA: `5688758f46d51bfa46fe9bcdb5a1137098d77fa8`
  (audits 2026-10-24T22:51–22:52Z). Head is audited **+ 4 commits, 0
  behind** (compare: ahead 4) — 10 workflow files changed, **none of them
  a flagged file** (agent-jules-on-issues, agent-pr-jules-handoff,
  gemini-*, peer-review-orchestrator, pr-evidence-evaluation,
  pr-scope-guard, provider-command-dispatch).
- At-head ECC audit: **none** (head SHA is not among the 264 audited
  SHAs). Mirror check runs at head: **0** (10 check runs total).
- Last-audited set verdicts: Security Evidence success; Hosted Promotion
  success; Risk Taxonomy neutral; Reference Set neutral; **PR Config
  Audit action_required** (comment 6390551401); **PR Harness Audit
  action_required** (comment 6390558479).
- Bullet findings at last-audited head: **11** — Config 7, Harness 4
  (§4, items D-01…D-08).
- Content re-audit at current head: every flagged file's blob at head is
  **byte-identical** to its blob at the audited SHA (blob SHAs in §4),
  and — except `help-wanted-llm-assist.yml`, whose master blob has since
  moved but carries the same pattern — byte-identical to master. All 11
  bullet findings therefore **still stand at current head as content**;
  none is stale. They are, however, findings about pre-existing master
  content swept into this PR's diff by its ancient base, not content this
  PR authored.
- History note: one Harness audit at `2cc8fb86` concluded `failure`
  ("PR harness audit could not complete — Cannot read properties of
  undefined") — an auditor error, not a finding; superseded by the
  successful audits that follow it. Not a disposition item.

### 3.2 PR #143 — "Integrate MCP Agent Mail Coordination Layer in GitHub Actions"

- State: open. Base: `master` (`d1cdb35584f4`). Current head:
  `c154540e4b64b9c4fcf798d5ae370032ad788286` (updated 2026-10-26T07:41Z;
  4,790 changed files vs base).
- Last ECC-audited SHA: `22b3494af2f57885678b0dc3fc807b9ce06b42c9`
  (audits 2026-10-26T07:12–07:13Z). Head is audited **+ 4 commits, 0
  behind** — exactly 1 file changed, `peer-review-orchestrator.yml`,
  **not a flagged file**.
- At-head ECC audit: **none**. Mirror check runs at head: **0**
  (13 check runs total).
- Last-audited set verdicts: as #125 — **Config action_required**
  (comment 6410382221), **Harness action_required** (comment 6410390111),
  Security success, Hosted Promotion success, two neutral.
- Bullet findings at last-audited head: **11 — identical to #125, bullet
  for bullet**, because both mega-PRs carry the same snapshot of the same
  files (every flagged blob SHA matches across both PRs, the audited
  SHAs, and master). Content re-audit at head: all 11 **still stand as
  content**. The disposition items are the same eight as #125 (D-01…D-08)
  — one owner decision per item covers both PRs.
- Stale item (does **not** stand): one historical Security Evidence
  `action_required` at SHA `78c327ec` (2026-10-21T18:50Z, comment
  6323923915; touched paths listed: `.agents/skills/termux-monorepo/
  agents/openai.yaml`, `.codex/agents/docs-researcher.toml`). The same
  gate concludes **success** at the last-audited SHA and in the recent
  audited sets — superseded; no disposition needed.

### 3.3 PR #1514 — "feat(antigravity): isolated secondary operational pilot (#1497)"

- State: open, marked in its own body **DO NOT MERGE** (partial
  operational pilot). Base: `master-staging` (`1a5af217f3ef`). Current
  head: `13f795adadcd41e020876196dfb4b30bc9e35c7d`; 45 changed files.
- Last ECC-audited SHA **is the current head**. All 6 gate audits exist
  at head (2026-10-23T22:42Z): Config success, Hosted Promotion success,
  Harness neutral, Risk Taxonomy neutral, Reference Set neutral,
  **Security Evidence action_required** (comment 6376182019). Mirror
  check runs at head: **6**, with Security Evidence (mirror) =
  `action_required`.
- **This is a current-head finding** — the only one in this queue,
  verified at head directly (see §1 for why the collector's windowed
  `current_head_findings: 1` cannot be attributed to it from the file).
- The finding (D-09, §4): 1 bullet — security-sensitive changes may ship
  without scanner evidence; touched paths `.agents/agents/
  agy-implementer.md` and `.agents/agents/agy-verifier.md`; 0 scanner /
  security-validation artifacts changed. Content re-audit at head: both
  files present as audited (13 / 12 lines, agent manifests; the
  implementer declares `replace_file_content` and `run_command` tools);
  a filename scan of all 45 PR files finds **no** SARIF / code-scanning /
  secret-scan / security-review artifact. The finding **stands at head**,
  ECC-audited and content-verified.

### 3.4 Counts at current head (summary)

| PR | At-head ECC AR findings | Standing bullet findings (content-verified at head) | Distinct disposition items | Stale / superseded |
|---|---|---|---|---|
| #125 | 0 (no at-head audit) | 11 (Config 7, Harness 4) | 8 (shared with #143) | 0 in last-audited set |
| #143 | 0 (no at-head audit) | 11 (Config 7, Harness 4) | same 8 | 1 historical Security AR, superseded |
| #1514 | **1** (Security) | 1 (Security) | 1 | 0 |
| Total | **1** | 23 bullet instances | **9** | 1 |

## 4. Disposition items (owner decisions; nothing actioned)

ECC's severity vocabulary in these audits is the bullet tag `[high]` plus
the gate conclusion `action_required`; ECC gives no line numbers. Where
ECC's per-file bullet count and the verifiable assignments in the audited
blob disagree, both numbers are stated.

### Config Audit — "[high] Environment variable with secret exposed"

All four files sit in `.github/workflows/`. In every verifiable case the
secret is assigned in a **step-level** `env:` of the single step that
consumes it — never at workflow or job level. The flagged blobs are
identical at audited SHA, at both PR heads, and (except D-04) on master:
these are live-on-master patterns, so any fix venue is master, not the
two mega-PRs.

#### D-01 — `agent-review-auto-jules.yml` — recommend DISMISS-WITH-REASON

- ECC: 2 bullets for this file. Verifiable in blob `2008f30b` (293 lines,
  identical everywhere): **1** assignment — step env at lines 283–284,
  `JULES_API_KEY: ${{ secrets.JULES_API_KEY }}`, consumed by that step's
  script (which explicitly handles the key being absent). The second
  bullet has no locatable assignment in the audited blob; recorded as a
  scanner count discrepancy, not a second issue.
- Reasoning: step-scoped env is GitHub's sanctioned mechanism for giving
  a `run:` script a secret; Actions masks secret values in logs; there
  is no narrower scope available for the one step that needs the key.

#### D-02 — `agentic-repository-operations-report.lock.yml` — recommend DISMISS-WITH-REASON

- ECC: 1 bullet. Blob `67901ea5` (1,567 lines, identical everywhere) is
  the **gh-aw compiled lock file** for
  `agentic-repository-operations-report.md`. It contains dozens of
  step-level secret env assignments by compiler design (e.g. lines
  171, 184–185, 429, 450–451, 621–622, and the redaction step at
  846–849, which passes secret values to the masking machinery itself).
- Reasoning: direct edits to a compiled lock file are overwritten on
  recompile; the pattern is the upstream compiler's architecture, not a
  repo-authored exposure. If the owner wants this pursued, the route is
  the gh-aw source/upstream — noted as an owner-call alternative, not
  recommended.

#### D-03 — `hark-enqueue.yml` — recommend DISMISS-WITH-REASON (false positive as stated)

- ECC: 3 bullets for this file. Verifiable in blob `7cb2bfe4` (117
  lines, identical everywhere): **zero** `secrets.*` references anywhere
  in the file. The only credential is the ephemeral per-run token at
  step env lines 50–51, `GH_TOKEN: ${{ github.token }}` — which is also
  the file's only env assignment of any token. At most one of ECC's
  three bullets maps to any assignment at all, and that assignment is
  not a stored secret.
- Reasoning: as stated ("environment variable with secret exposed"),
  the finding does not exist in the audited content. Dismiss; if ECC's
  rule intends to flag `github.token` in step env, that is the standard
  `gh` CLI pattern used across the fleet.

#### D-04 — `help-wanted-llm-assist.yml` — recommend FIX (on master)

- ECC: 1 bullet. Audited blob `cc5fe77b` (223 lines; master has since
  moved to `fbbd0d9a`, 248 lines, same pattern at lines 36–40 / 126–130
  / 192+). All assignments are step-level `env:` in the single `assist`
  job's three steps: step "Resolve target foreign PR" (lines 37–41:
  `OPERATOR_GITHUB_TOKEN`, `OPERATOR_TOKEN`, `ARCHWIZ_GITHUB_TOKEN`,
  `GITHUB_TOKEN`), step "Live catalog select" (lines 101–105: four
  provider keys), step "Invoke selected model + comment" (lines 167–174:
  four provider keys + composite `GH_TOKEN`).
- The provable over-exposure is step 1: its script collapses the four
  tokens into one fallback export on its first line and thereafter reads
  only `GITHUB_TOKEN`. Three extra PAT-class values are present in the
  step environment beyond the variable the step consumes.
- Concrete change (master): in step 1, replace the four secret
  assignments with the single composite expression the same file
  already uses at line 174, extended with `OPERATOR_TOKEN`:
  `GITHUB_TOKEN: ${{ secrets.OPERATOR_GITHUB_TOKEN || secrets.OPERATOR_TOKEN || secrets.ARCHWIZ_GITHUB_TOKEN || secrets.GITHUB_TOKEN }}`,
  and drop the now-redundant fallback export line. Steps 2–3 keep their
  env (each key is a live provider candidate the steps probe/use).
- Caveat for the owner: ECC's file-level rule may still flag this file
  after the fix (other step envs remain). The fix removes the one
  demonstrable over-exposure; it is not guaranteed to clear the audit.

### Harness Audit — "[high] SKILL.md is missing required frontmatter"

Repo contract for reference (`scripts/ci/validate_operational_skills.py`):
a SKILL.md must start with `---` and carry `name:` and `description:` —
the same shape as the unflagged skills (e.g. `adaptive-feedback-cycle`,
`review-loop`, `stepie-stepwise-ops`, all `name` + `description` only).
All four flagged blobs are identical at audited SHA, both heads, and
master — fixes land on master. Proposed description texts are taken from
each file's own Purpose section.

#### D-05 — `.agents/skills/blind-agent-evaluation/SKILL.md` — recommend FIX (master)

- Blob `9ecacd77`: no frontmatter at all; file opens `# Blind Agent
  Evaluation Skill`.
- Concrete change: prepend
  `---` / `name: blind-agent-evaluation` / `description: Use blinded or
  partially blinded evaluation when provider/model identity could bias
  selection or review and identity is not required for safe execution.`
  / `---`.

#### D-06 — `.agents/skills/evolutionary-replay/SKILL.md` — recommend FIX (master)

- Blob `570246c2`: frontmatter **exists** but reads `name:
  evolutionary-replay` / `version: 1` / `summary: …` — it lacks the
  required `description:` field, which is what ECC's flag amounts to for
  this file.
- Concrete change: rename `summary:` to `description:` (same text:
  "Use realized discovery history as a deterministic replay simulator
  for bounded manager-policy experimentation."), keeping `name:` /
  `version:`.

#### D-07 — `.agents/skills/gemini-performance-psychology/SKILL.md` — recommend FIX (master)

- Blob `b813f0f1`: no frontmatter; opens `# Gemini Performance
  Psychology`.
- Concrete change: prepend `---` / `name:
  gemini-performance-psychology` / `description: Improve autonomous
  Gemini/Gem-style development behavior by applying performance
  psychology as an engineering control: reduce avoidable thrash,
  preserve momentum, and bias toward evidence-backed completion.`
  / `---`.

#### D-08 — `.agents/skills/multivariate-doe/SKILL.md` — recommend FIX (master)

- Blob `573f5bc0`: no frontmatter; opens `# Multivariate DOE / MVT
  Skill`.
- Concrete change: prepend `---` / `name: multivariate-doe` /
  `description: Design agent-team experiments as evidence-bearing
  Design of Experiments (DOE / MVT) rather than an uncontrolled
  collection of A/B requests.` / `---`.

Note on D-05…D-08: fixing master does not change the two mega-PRs' head
content; it dispositions the underlying issue where the content lives.
Whether #125 / #143 themselves are ever rebased, re-audited, or closed
is a separate owner decision about those PRs, not an ECC finding.

### Security Evidence — "Security scanner evidence required"

#### D-09 — PR #1514, `.agents/agents/agy-implementer.md` + `.agents/agents/agy-verifier.md` — recommend OWNER-CALL

- ECC (comment 6376182019, at current head, mode: enforce): "Security
  scanner evidence required" (`action_required`; this gate's bullet
  carries no `[high]` tag — its severity signal is the gate conclusion
  itself, in enforce mode). Expected
  evidence, in ECC's terms: security scanner / code scanning / secret
  scanning / dependency-security review output, or a SARIF/code-scanning
  upload or equivalent pass/fail gate for the changed surface.
- Content facts: the two manifests are new in this PR, declarative
  markdown with tool allowlists (implementer: `view_file`,
  `replace_file_content`, `run_command`; verifier: `view_file`,
  `run_command`), and body text that forbids credential / Origin /
  settings access. The PR's 45 files contain no scanner-evidence
  artifact (§3.3). The PR body does record extensive non-scanner
  validation (focused test suites, repo gate, readiness tests), which
  ECC does not count as scanner evidence.
- Why owner-call rather than a flat recommendation: the PR is the
  owner's own pilot, explicitly DO NOT MERGE, and the right disposition
  follows the PR's fate, which is the owner's gate —
  (a) **Fix-before-any-merge**: attach scanner evidence for the head —
  e.g. a secret-scan + dependency/security review run over the PR diff
  with output recorded on the PR, or a SARIF upload for the
  `.agents/agents/` + `scripts/antigravity/` surface — then request a
  fresh ECC sweep so the gate re-audits at head;
  (b) **Dismiss-with-reason** if the PR stays a closed-out pilot record:
  declarative manifests only, no secrets or executable code in the
  flagged files themselves, explicit no-credential-access constraints
  in both manifests, and the PR never merges in this state.
- This packet takes no position between (a) and (b).

## 5. Method limits

- ECC audit bodies name a finding type and a file, never a line or
  variable; per-file bullet counts do not map 1:1 onto verifiable
  assignments (D-01: 2 bullets / 1 assignment; D-03: 3 bullets / 0 secret
  assignments; D-04: 1 bullet / 13 assignments). Dispositions above are
  therefore per file-group, with the count discrepancy stated each time.
- `reviewer-metrics.json` is a windowed audit-comment counter (§1), not
  a findings ledger; its per-gate totals (Security 8 / Config 6) must
  not be read as bullet counts for this queue.
- Heads were current at 2026-10-27 ~07:20–08:10 PDT. #125 / #143 have no
  at-head ECC audit, so their "stands at head" verdicts are content
  verdicts (blob-identical flagged files, flagged files untouched by the
  audited→head delta), not new ECC verdicts; a fresh ECC sweep at head
  is the step that would convert them, and it has not been requested.
