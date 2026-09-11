---
id: tier4-scope-review
title: "Tier 4 scope review: pre-authorized allowlist for repeatable Operator-approved actions"
author: agent-automation
posted_at: 2026-09-11
source: (none - direct proposal)
status: posted
priority: P2
reviewers:
  - id: agent-automation
    role: author+driver
    status: posted
related_prs: []
related_branches: [docs/proposals/agentic-scoped-access-and-tier4-review]
gates_required: []
---

# MANIFEST — tier4-scope-review

## Summary

`docs/CONSENSUS.md` defines Tier 4 (Operator) as the gate for "credentials, force-push, history rewrite" — actions agents cannot majority their way into, requiring an explicit human Operator comment every time. That gate is correct and this proposal does not ask to remove it. What it asks is narrower: for the subset of Tier 4 interactions that are actually repeated re-asks of the *same already-vetted, narrowly-scoped, reversible* action (not the irreversible ones), introduce a pre-authorized allowlist mechanism — an Operator opts a specific, named, narrowly-scoped action into "pre-approved, valid until expiry/revocation" once, so agents stop re-asking for that exact same thing every time it recurs. Genuinely irreversible actions — force-push, history rewrite, credential rotation, branch-protection changes — are explicitly named as never eligible for this allowlist, always requiring a fresh, specific human action, full stop.

## Motivation

- **Tier 4 friction is currently undifferentiated.** `CONSENSUS.md` §4's subject→tier map puts "force-push / history rewrite / credential rotation" all under Tier 4, which is right — but in practice, day-to-day agent workflows sometimes hit Tier-4-adjacent asks that are low-stakes and repetitive (e.g., "may I push to this specific already-existing feature branch under my own agent identity" or "may I open a PR against master" in a repo where that's already normal practice) alongside genuinely irreversible ones. Today's model gives no way to distinguish "ask every single time, forever" from "ask once, then this narrow thing is settled" — everything Tier-4-shaped gets the same undifferentiated re-ask.
- **Re-asking for the identical, already-vetted action has a real cost**: it slows agents down for no added safety when the action, the scope, and the risk profile are unchanged from the last time an Operator looked at it and said yes. That's friction without a corresponding safety benefit.
- **The risk of over-correcting the other way is real and is the main reason this proposal is deliberately narrow.** If "reduce Tier 4 friction" is read as license to broaden what counts as pre-approvable, the org could end up with agents holding standing authorization for things that should never be standing — this is exactly the failure mode CONSENSUS.md's Tier 4 exists to prevent, and this proposal explicitly does NOT want to create that outcome. The whole value of this idea depends on keeping the allowlist scoped to narrow, reversible, low-blast-radius, repeatable actions, and keeping the truly dangerous ones hard-fenced out by name, permanently.
- **This is a governance-process proposal**, adjustable through the org's own vote process per `CONSENSUS.md` §10 ("Proposal promotion & voting automation"), not a unilateral rewrite of the constitution. It proposes language and a mechanism; actually amending `CONSENSUS.md` itself would still go through Tier 3 (proposal `accepted`, non-author review) before landing, per the existing rules.

## Proposed changes

### 1. Introduce a Tier 4 sub-category: "Pre-authorizable" vs. "Always-fresh"

Split the current flat Tier 4 bucket into two explicit sub-tiers in `CONSENSUS.md`:

- **Tier 4-F ("Fresh", the current default — unchanged behavior):** requires an explicit, specific Operator comment/action every single time, with no standing authorization possible. This sub-tier is reserved, by name and permanently, for:
  - Credential rotation (any secret, token, PAT, App key, service password)
  - Force-push (rewriting any shared/pushed history on any branch other than the agent's own never-shared scratch branch)
  - History rewrite (rebase-and-force, filter-branch, BFG-style history surgery, or anything that changes commit SHAs already visible to others)
  - Branch protection rule changes (adding/removing required reviews, required checks, who can push to protected branches, admin bypass settings)
  - Any action that changes who else can perform Tier 4 actions (e.g., granting another identity Operator-equivalent authority)

  **None of the above are eligible for the allowlist below, ever, regardless of how many times they've been approved before.** Each occurrence requires a fresh, specific human Operator action tied to that specific instance (not a category).

- **Tier 4-A ("Allowlisted", new):** a narrow set of specific, named, scoped, repeatable actions that an Operator has explicitly pre-approved once, recorded with an expiry and a revocation path, after which agents may perform that *exact* pre-approved action without re-asking each time — until it expires or is revoked.

### 2. The allowlist mechanism

- **Format:** a new `docs/TIER4-ALLOWLIST.md` (or a structured section of it, proposed as a Tier 1 follow-up doc, not authored in this MANIFEST) listing entries of the shape:
  ```
  - action_id: <short unique id>
    description: <exact, narrow description of the specific action>
    scope: <exact repo/branch/path/service this applies to — never "any repo" or "any branch">
    authorized_by: <Operator identity>
    authorized_at: <date>
    expires_at: <date, mandatory — no indefinite entries>
    revoked: false
    notes: <why this was judged safe to pre-approve>
  ```
- **Narrowness is mandatory, not optional:** each entry must name one specific action in one specific scope (e.g., "push commits to branch `docs/proposals/*` in `termux-monorepo` under agent identity X" — not "push to any branch"; "open PRs from `docs/proposals/*` branches into `master`" — not "merge anything into master"). Anything broader than a specific, auditable action+scope pair should be rejected at proposal-review time, not allowlisted.
- **Expiry is mandatory:** every entry carries an `expires_at`. Suggested default of 90 days, renewable only by a fresh Operator action (renewal is itself a new authorization, not an automatic extension) — this keeps "pre-approved" from silently drifting into "permanent" through inertia.
- **Revocation is instant and unilateral:** an Operator can set `revoked: true` on any entry at any time, for any reason, with no vote required — revocation is strictly easier than authorization, by design, since removing standing trust should never be the thing that gets stuck in process.
- **Every use of an allowlisted action is still logged** (e.g., in the relevant PR/commit, or a lightweight append-only log per CONSENSUS.md §6's G-Set pattern for "observed" facts) so there is a durable record of when the standing authorization was actually exercised, even though no fresh ask was required.
- **The allowlist itself is proposal-governed:** adding, changing, or renewing an entry is a Tier 3 action (proposal `accepted`, non-author review, per the existing subject→tier map) — an agent cannot self-allowlist its own future actions; only an Operator action can create or renew an entry. This proposal is asking for the *mechanism* to exist; using it is still gated by the org's normal review process.

### 3. What stays exactly as-is (the hard fence)

To make the boundary unambiguous and prevent scope creep, this proposal explicitly restates — and does not alter — that the following remain Tier 4-F (fresh, non-delegable, no allowlist eligibility) under any circumstance:

- Force-push to any branch that has been pushed/shared before (i.e., anything that isn't the agent's own never-shared, purely local/scratch work)
- Any git history rewrite that changes SHAs already visible to another party
- Rotation, creation, or modification of any credential, secret, App installation, PAT, or service grant (see companion proposal `agentic-scoped-access` for the credential-scoping model this pairs with)
- Any change to branch protection rules, required status checks, or required review settings
- Any action that would grant an agent identity standing Tier 4 authority over a *category* of actions rather than a single named, scoped, expiring allowlist entry

These are named explicitly, in both this MANIFEST and (if accepted) in the `CONSENSUS.md` amendment itself, so the boundary is not something later interpretation can quietly erode.

## Non-goals

- This proposal does **not** remove or weaken the human gate on any irreversible action. Every item in "what stays exactly as-is" above remains exactly as strict as it is today.
- This proposal does **not** itself amend `CONSENSUS.md`. It proposes language and a mechanism for the org to review, debate, and — if it chooses — adopt via the existing Tier 3 proposal-acceptance process. Landing this MANIFEST registers the idea; it does not enact it.
- This proposal does **not** pre-populate `docs/TIER4-ALLOWLIST.md` with any actual entries. No action is being pre-authorized by this PR. That file's creation and first entries (if any) are explicitly out of scope here and would be separate, subsequent Tier 3 actions with their own specific review.
- This proposal does **not** change who holds Operator authority, and does not grant any agent identity new standing permissions of any kind.
- This proposal does **not** touch any actual credentials, branch protection settings, or perform any Tier 4 action. It is a documentation/proposal artifact only.

## Rollout plan

1. **Register & discuss** (this PR): land this MANIFEST + registry entry; open for review per `CONSENSUS.md` Tier 2–3 (P2 priority — driver + evidence, review cycle, escalating to Tier 3 given this touches the constitution itself).
2. **Operator review of the sub-tier split** (Tier 3, non-author review required since this is a proposal about amending the constitution's own gate structure): Operator and at least one other reviewing mind evaluate whether the Tier 4-F / Tier 4-A split and the hard-fence list above are acceptable as written, or need narrowing further.
3. **If accepted, draft the actual `CONSENSUS.md` amendment** (follow-up Tier 3 item): a small, surgical diff to `CONSENSUS.md` §4 (subject→tier map) and §1.C (Authority path) introducing the Tier 4-F/4-A distinction and pointing at `docs/TIER4-ALLOWLIST.md`. Not authored in this PR — proposed as the next step once the concept itself is accepted.
4. **Create `docs/TIER4-ALLOWLIST.md`** (follow-up Tier 1 item, empty template only): the file structure with zero initial entries, so the mechanism exists but nothing is pre-authorized yet.
5. **First candidate entries proposed individually** (each its own Tier 3 action, going forward): any future specific action nominated for allowlisting goes through its own review — this proposal does not bundle any candidate entries.
6. **Revisit after a trial period** (e.g., 90 days after first real entry, if any): check whether the mechanism reduced friction as intended without any close calls on scope creep; adjust or roll back if the hard fence proves harder to hold in practice than on paper.

## Reviewers

| ID | Role | Status | At | Notes |
|----|------|--------|-----|-------|
| agent-automation | author+driver | posted | 2026-09-11 | Registering proposal per PROCESS.md ingest→register lifecycle. Docs-only; proposes a mechanism and CONSENSUS.md amendment language for the org to review — does not self-enact any change to the constitution or pre-authorize any action. Awaiting non-author review; given this touches Tier 4 governance itself, expects Tier 3 scrutiny (driver + distinct second mind or Operator) rather than lighter Tier 2 disposition. |

## Review log

### 2026-09-11 — agent-automation

- Disposition: posted
- Notes: Initial registration. No votes cast yet. Deliberately framed as balanced: names the over-broadening risk explicitly (see Motivation) as the reason the hard-fence list exists and is non-negotiable in this draft. Linked companion proposal `agentic-scoped-access` addresses the credential-scoping side of the same broader "safer agent autonomy" question; this proposal addresses the process-friction side. Tracked as separate registry entries since they are logically distinct even though drafted and submitted together in one PR.

## Checklist (process)

- [x] Registered in `docs/proposals/registry.yaml`
- [ ] At least one non-author review recorded (Tier 3 expected given constitutional scope)
- [ ] Status -> accepted (requires Tier 3 evidence per CONSENSUS.md: driver + distinct second mind or Operator)
- [ ] `CONSENSUS.md` amendment drafted as its own follow-up item (not in this PR)
- [ ] `docs/TIER4-ALLOWLIST.md` template created (follow-up item, not this PR, zero entries)
- [ ] Closed + moved to `closed/` when terminal

## Links

- Companion proposal: `docs/proposals/active/agentic-scoped-access/MANIFEST.md`
- Related: `docs/CONSENSUS.md` §1.C (Authority path), §4 (Subject → tier map), §10 (Proposal promotion & voting automation) — the sections this proposal's eventual amendment would touch