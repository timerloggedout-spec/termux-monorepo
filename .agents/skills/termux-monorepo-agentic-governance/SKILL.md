---
name: termux-monorepo-agentic-governance
display_name: termux-monorepo-agentic-governance
description: Orients any agent doing PR/proposal/maintenance work in the timerloggedout-spec GitHub org (termux-monorepo primary, plus termux-mcp, android-mcp, mcp-hub) on the real, verified governance model — the permission boundary, the 5-tier consensus model, and the practical PR-triage and proposal-lifecycle procedures. Use before merging, closing, or opening PRs/proposals in this org, or when asked what an agent is/isn't allowed to do here. Sourced only from docs/proposals/AGENTIC-PERMISSIONS.md, docs/CONSENSUS.md, docs/proposals/registry.yaml, .agents/skills/evidence-led-monorepo-ops/SKILL.md, .agents/skills/review-loop/SKILL.md.
tags: [governance, github, monorepo, consensus, permissions]
---

# termux-monorepo Agentic Governance

## Purpose & scope

This skill orients any agent (human-directed or autonomous) doing PR triage, merges,
proposal work, or repo maintenance in the `timerloggedout-spec` GitHub org: `termux-monorepo`
(primary, holds the governance docs below), `termux-mcp`, `android-mcp`, `mcp-hub`. Everything
here is paraphrased from the org's own verified files — cite them, don't improvise beyond them:

- `docs/proposals/AGENTIC-PERMISSIONS.md` — permission boundary
- `docs/CONSENSUS.md` — the 5-tier consensus model
- `docs/proposals/registry.yaml` — active-proposals ledger
- `.agents/skills/evidence-led-monorepo-ops/SKILL.md` — evidence-led triage conventions
- `.agents/skills/review-loop/SKILL.md` — review-loop / authority conventions

If any of these files drift from what's summarized here, the repo files are ground truth —
re-read them; don't trust a cached memory of this skill either.

## The permission boundary

Per `AGENTIC-PERMISSIONS.md`, an agent CAN autonomously: read repo/PRs, create branches,
create/update files, open PRs, comment, merge when the tier allows it, retarget a PR's base,
submit reviews.

Six things still need a human ("Operator"):

1. **Credential rotation** — secrets live on-device or in provider dashboards.
2. **History rewrite + force-push** — destructive; needs explicit Operator approval.
3. **Protected branch rules on master** — may be outside the agent's app scope.
4. **GitHub App permission gaps** (Contents/PRs/Checks/Workflows) — first-time grants.
5. **Device-side Termux state** — the agent is a cloud connector, not the phone.
6. **Provider API keys / browser logins** — interactive or ToS-bound.

Minimum permission checklist an agent's GitHub App/token should have: Contents R/W, Pull
requests R/W, Checks + Commit statuses R/W, Workflows R/W, Issues R/W, Administration Read.

**CodeRabbit / third-party review bots**: repo admins cannot grant `workflows: write` to an
app that never requested it. CodeRabbit's published permissions cover Contents/PRs/Issues/
Commit statuses (R/W) and Actions/Checks/Metadata/Discussions (read-only) — **not** Workflows.
So CodeRabbit autofix can touch `*.py`/docs but GitHub will reject any push touching
`.github/workflows/**` from it. That's platform policy + app manifest, not something an agent
broke. Workflow file edits are OPERATOR territory (full-scope PAT or a custom App with
Workflows R/W) — do not expect a review bot to own CI YAML, and do not attempt to work around
the rejection yourself.

## The 5-tier consensus model

```text
Tier 0  MERIT        Branch, implement, run gates — no social vote
Tier 1  DRIVER       P2-P3 claims: driver + evidence in the log
Tier 2  LIGHT        P1: driver + evidence; 1 review cycle then silence OK
Tier 3  QUORUM       P0 claims / P0 PR body: driver + distinct second mind OR Operator
Tier 4  OPERATOR     Credentials, force-push, history rewrite — human only
Tier R  RAFT-STRICT  Optional profile for named irreversible subjects
```

**Default path for code:** Tier 0 (branch + gates green) -> open PR -> Tier 1-2 disposition ->
merge when gates green and disposition is not red.
**Default path for irreversible security claims:** Tier 3-4 (optionally Tier R).

Tier 4 — the hard, human-only gate — covers exactly: **credential rotation, force-push,
history rewrite, and branch-protection / GitHub App permission changes.** Agents cannot
majority-vote their way past this tier; it needs an explicit Operator action/comment. Never
perform these unilaterally regardless of how urgent or well-justified it seems in the moment —
if a task seems to require one of these, stop and surface it to the human instead.

Three paths, not one protocol:
- **Merit path** (preferred for code): branch from the working branch, implement, run the
  repo's gates (e.g. `repo_gate.py`, `termux_smoke.py`), open a PR with an honest Status, land
  when checks are green and disposition isn't red. Merit answers "does it work?" — votes don't
  replace gates.
- **Social path** (claims & sequencing): used for proposal accepted/closed, "P0 done", a
  disposition Status, a security-scope summary. Lives in `docs/proposals/` (MANIFEST + Review
  log + registry) with a thin projection into the PR body/comments.
- **Authority path** (Operator): credential rotation, history rewrite, force-push, App
  permission changes. Not subject to agent majority.

Ballot labels for the social path: `VOTE: accept` / `VOTE: reject` (state reason) /
`VOTE: abstain` (present, doesn't count toward quorum) / `VOTE: summary OK` (P0 PR body
rewrite ack). One vote per voter id per **term** (`subject-id/n`, e.g. `pr-3/summary/2`); an
unposted chat opinion does not count as a vote.

Subject -> tier quick map: create branch/push experiments = 0; P2-P3 item done = 1; P1 item /
ordinary PR disposition = 2; proposal accepted (non-author review) = 3 (or Operator self-accept,
logged); P0 item done / P0 PR body rewrite = 3; merge to the staging branch = Tier 0 checks +
disposition not red; promote to `master` = Tier 0 checks + may require Operator; force-push /
history rewrite / credential rotation = 4.

## Practical PR triage procedure

This is the operational core an agent actually executes:

**For a PR NOT authored by the repo owner** (bots like `google-labs-jules[bot]`,
`coderabbitai[bot]`, or any external contributor):
1. Fetch `mergeable` and `mergeable_state` — but do not stop there. `mergeable_state: unstable`
   is frequently a **false negative** caused by cancelled/skipped concurrency runs, not a real
   failure.
2. Pull the actual check-run conclusions for the head SHA and filter out
   `success` / `skipped` / `cancelled` — what's left (real `failure` / `timed_out`) is the
   signal that matters. Also check legacy commit-status contexts; a failing context clearly
   unrelated to the PR's changed files (e.g. a preview-deploy status for an app the PR doesn't
   touch) is noise, one plausibly tied to the changed files is real.
3. Check the changed-files list for red flags: anything under `.github/workflows/**`, or
   touching credentials/secrets/tokens/env files — do not merge, flag for the owner regardless
   of check status (this is Operator/Tier-4 territory, not a bot's call to make).
4. Check for changed-file overlap against other open PRs you're about to act on in the same
   sweep — don't merge two PRs that silently conflict on the same files; flag the overlap.
5. If mergeable, no real check failures, no red-flag files, no overlap: merge via the Tier-0
   Merit path (checks green + disposition not red — no vote needed).

**For a PR authored by the repo owner**: merging it yourself requires the owner's own explicit,
specific consent for that PR (or an explicit standing rule naming it) — an owner consenting to
merge their own work is normal and is not a Tier-4 issue, but **never assume blanket
authorization** just because a similar PR was previously approved. Absent that consent, triage
and report status; leave the merge decision to the owner.

**Closing a PR**: only with concrete evidence of staleness, duplication, or supersession (e.g.
another open/merged PR's body explicitly states it rebases/replaces this one, with an
overlapping file set you've actually diffed). Never close on suspicion or to reduce backlog
count — state the evidence in the closing comment.

## Proposal lifecycle

1. **Register**: add an entry to `docs/proposals/registry.yaml` (id, title, author, status,
   priority, path pointing at `active/<id>/`, reviewers, related_prs/branches,
   gates_required). Keep the registry entry thin — a pointer, not the content.
2. **Draft**: the full proposal body lives under `docs/proposals/active/<id>/` (a MANIFEST +
   optionally an `ITEMS.md`/`DEBATE.md`) — never paste a multi-KB proposal directly into
   `CONSENSUS.md`.
3. **Debate/vote**: structured `VOTE:` blocks tied to a term, logged in the Review log — chat
   alone is void.
4. **Promote**: status transitions are forward-only (no `--force`); `accepted` requires
   `--evidence` per Tier 2-3.
5. **Close**: move `active/<id>/` -> `closed/<id>/` and update the registry path.

**CRDT vs Vote vs Gate** (rule of thumb from `CONSENSUS.md` §6):
```text
CRDT  -> concurrent facts that should converge without a meeting (e.g. G-Set of observed SHAs,
         OR-Set of roster members)
Vote  -> authorization to treat something as shared institutional truth
Gate  -> mechanical proof about a concrete revision (CI checks)
```
Never CRDT-merge authorization or a disposition Status — Status is a single-value register
under social tier (MV-Register until Tier 2-3 resolves), not last-write-wins; wall-clock races
between agents must not flip a security claim.

## Working conventions (from the collaborator skills)

- **Evidence-led triage**: before concluding something is broken/stuck/failing, go find the
  actual evidence (real check-run conclusions, actual diffs, actual logs) rather than trusting
  a summary flag.
- **Quota != run prevention**: a quota/rate-limit gate constrains automated retries or spend —
  it does not by itself mean the underlying work is blocked or failed; check what actually ran.
- **Authority > ranking**: whoever holds the standing tier-based authority on a claim outranks
  any popularity- or ranking-based signal (e.g. review approvals count, upvotes) — don't let a
  numeric tally override the tier that actually governs the decision.

## Anti-patterns to avoid

- Treating `mergeable_state` alone as ground truth instead of checking real check-run
  conclusions underneath it.
- Assuming owner-authorship of a PR implies standing consent to merge it — consent must be
  specific to that PR (or an explicit rule naming it).
- Using last-write-wins semantics for `Status` or proposal state, letting a slower/faster agent
  clock flip a claim.
- Pasting full proposal prose into `CONSENSUS.md` instead of a pointer + `active/<id>/`.
- Closing PRs as "stale/duplicate" without citing the specific superseding PR/evidence.
- Attempting to route around a rejected `.github/workflows/**` push instead of surfacing it as
  Operator (Tier-4) territory.
- Performing any Tier-4 action (credential rotation, force-push, history rewrite,
  branch-protection/App permission changes) unilaterally, however reasonable it seems in the
  moment — these always route to a human.
