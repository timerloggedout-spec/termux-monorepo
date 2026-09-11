---
id: agentic-scoped-access
title: "Agentic scoped access: per-agent scoped tokens instead of shared full-scope credentials"
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

# MANIFEST — agentic-scoped-access

## Summary

Multiple agents currently operate against this org's GitHub repos, and in at least one workflow, a shared personal access token (raw, full-scope, human-owned) is extracted from a local credentials file and handed to each agent invocation to authenticate `curl` calls. This works, but it means every agent action rides on a single credential that (a) carries whatever scopes the underlying human account has, far beyond what any one agent task needs, (b) cannot be revoked for one agent without revoking it for all of them, and (c) if leaked in a log, chat transcript, or committed file, hands over everything that human account can reach — not just repo access. This proposal asks the org to adopt per-agent scoped credentials (GitHub Apps or fine-grained PATs), runtime-injected secrets instead of chat-pasted tokens, scoped grants for non-GitHub services (email, etc.), and to tie all of it to MFA/2SV on the human accounts underneath, so that a single leaked scoped token has a small, individually revocable blast radius instead of full account takeover.

## Motivation

- **Blast radius today is "everything the human can do."** A full-scope PAT pasted into an agent's working context (even briefly, even via a wrapper script) is a single point of failure: if it leaks — in a log line, an error message, a copy-pasted debug snippet, or a committed file — the exposure is the entire account's reach, not the narrow thing the agent was actually asked to do.
- **No per-agent revocation.** When several agents (Claude, ChatGPT, Manus, Grok, Kimi, and others per `registry.yaml`) share one token, there is no way to cut off one misbehaving or compromised agent without also cutting off every other agent's access simultaneously. That is an availability risk on top of a security one.
- **No least-privilege by construction.** Most agent tasks in this repo are docs/proposal writes, PR opens, or read-only exploration. Almost none need org-admin, billing, or account-level scopes — yet a full-scope human PAT grants all of that by default, whether or not any single task needs it.
- **This repo already treats credential exposure as a first-class risk** (see `docs/CREDENTIAL-EXPOSURE.md`, referenced from the `vercel-lane-topology` proposal). This proposal generalizes that concern from "don't commit secrets" to "don't even hand out more access than the task needs in the first place."
- **This is a hardening proposal, not a blocker.** It does not ask to revoke anything immediately; it proposes a migration path the org can adopt at its own pace, reviewed and voted on like any other proposal per `CONSENSUS.md`.

## Proposed changes

### (a) GitHub Apps or fine-grained PATs scoped per-agent

- Register a **GitHub App** per distinct agent identity (or per agent *class*, e.g. one App for "docs/proposal-writing agents", one for "CI/gate-running agents") rather than continuing to share one human PAT across all of them.
  - App permissions set to the minimum needed: e.g. `contents: write` + `pull_requests: write` + `metadata: read` for an agent that only opens docs PRs; no `administration`, no `secrets`, no org-level scopes unless a specific agent role genuinely requires them.
  - App installed only on `termux-monorepo` (or the specific repos an agent actually touches) — not org-wide — unless a role is explicitly cross-repo.
  - Each App has its own installation access token, short-lived (GitHub-issued installation tokens expire in ~1 hour by default) and independently revocable by uninstalling/reinstalling that one App without touching any other agent's access.
- Where a full GitHub App is overkill for a low-frequency or experimental agent, use a **fine-grained PAT** instead of a classic PAT: scoped to the single repo, with only the specific repository permissions the task needs (e.g. `Contents: Read and write`, `Pull requests: Read and write`), and a **short expiration** (30–90 days, not "no expiration"). Fine-grained PATs are still human-account-linked, so treat them as the fallback tier below Apps, not the default.
- Maintain a small mapping doc (e.g. `docs/AGENT-ACCESS.md`, out of scope to write here but proposed as a Tier 1 follow-up item) listing: agent identity → App or fine-grained PAT → scopes granted → repos → owner who can revoke it. This turns "who can do what" into something reviewable instead of implicit in a shared secret.

### (b) Runtime-injected secrets, never pasted into chat/instructions/files

- For agent workflows that run inside GitHub Actions or Codespaces, credentials should come from **Actions secrets** / **Codespaces secrets** / **environment secrets**, injected at runtime into the job's environment (`${{ secrets.AGENT_APP_TOKEN }}` style), and never appear in:
  - chat/task instructions given to an agent,
  - committed files (including scratch/workspace files that might get swept into a commit by accident),
  - command-line arguments that land in shell history or process listings visible to other processes.
- Where an agent must authenticate outside of Actions/Codespaces (e.g. this session's `~/.git-credentials` pattern), the credential should still be sourced from a local, non-committed, permission-restricted file read fresh per call — which is the existing convention this proposal wants to keep and extend, not replace — but the **content** of that file should be a scoped App/fine-grained-PAT token per (a), not a full-scope human PAT.
- No agent output (PR body, commit message, log, this MANIFEST, etc.) should ever contain a raw token, even partially, even for debugging.

### (c) Scoped grants for email/other services

- For non-GitHub services an agent needs (e.g. sending email on the org's behalf), avoid handing over the full account password. Prefer, in order of preference:
  1. **OAuth app grant** scoped to the specific function (e.g. Gmail API `gmail.send` scope only — cannot read inbox, cannot delete, cannot change settings).
  2. **App-specific password** scoped to a single function/client if the service doesn't support OAuth scopes finely enough, generated per-agent so it can be revoked individually.
  3. Full account password: **never**, for any agent workflow, under this proposal.
- Same revocability principle as (a): each service grant should be traceable to one agent identity and independently revocable without affecting others.

### (d) Tie to MFA/2SV on underlying human accounts

- Require MFA/2SV (2-step verification) to be **enabled and enforced** on every human account whose identity underlies an agent-facing App installation, fine-grained PAT, or service grant. GitHub orgs can enforce this at the org level (`Settings → Authentication security → Require two-factor authentication`).
- Rationale: scoping a token limits what a *leaked token* can do, but it does not protect the *account* that issued it. If that human account itself is compromised (phished, credential-stuffed), an attacker could reissue new tokens/grants under the same scoped model. MFA/2SV on the human account is the layer that keeps a scoped-token leak from escalating into "attacker now controls the account that mints these tokens."
- This is a natural pairing, not a separate ask: scoped access reduces blast radius per credential; MFA/2SV protects the root of trust that issues credentials. Doing (a)–(c) without (d) leaves the escalation path open; doing (d) alone doesn't fix the shared-full-scope-PAT problem this proposal is about.

## Non-goals

- This proposal does **not** ask to immediately revoke any currently working credential or break any in-flight agent workflow. Migration is proposed as a rollout (below), not a cutover.
- This proposal does **not** cover Tier 4 (Operator-only) authority itself — credential rotation, force-push, and history rewrite remain human-only actions regardless of how access is scoped. See the companion proposal `tier4-scope-review` for that separate question.
- This proposal does **not** specify exact GitHub App names, exact scope lists per existing named agent (Claude/Manus/ChatGPT/Grok/Kimi/etc.), or a timeline with hard dates — those are implementation details for a follow-up Tier 1–2 item once this proposal's direction is accepted.
- This proposal does **not** touch any actual credentials, branch protection settings, or perform any Tier 4 action. It is a documentation/proposal artifact only.

## Rollout plan

1. **Register & discuss** (this PR): land this MANIFEST + registry entry; open for review per `CONSENSUS.md` Tier 2–3 (P2, ordinary proposal disposition — driver + evidence, one review cycle).
2. **Pilot on one agent role** (follow-up, Tier 1–2): stand up a single GitHub App scoped to `contents: write` + `pull_requests: write` on `termux-monorepo` for the docs/proposal-writing agent role (the role this very PR was produced under), run it in parallel with the existing shared-PAT path for a trial period.
3. **Expand per-role** (follow-up, Tier 1–2 per role): once the pilot is validated, create additional Apps/fine-grained PATs for other agent roles (CI/gate-runners, code-implementation agents, etc.), each scoped to only what that role's tasks demonstrably need.
4. **Deprecate shared full-scope PAT usage** (Tier 3, since this changes a security-relevant default): once per-role credentials are validated in production use, propose retiring the shared full-scope PAT as the default agent credential, with Operator sign-off given the security-sensitivity of this step.
5. **Org MFA/2SV enforcement check** (can proceed independently, any time): confirm/enable org-level 2FA requirement; this has no dependency on the App/PAT rollout above and can land first.
6. **Document** (Tier 1): add `docs/AGENT-ACCESS.md` mapping agents → credential type → scopes → repos → revocation owner, kept current as roles change.

Each step above is independently reversible and low-risk (adding a new scoped credential path alongside an existing one, not removing anything until the replacement is proven).

## Reviewers

| ID | Role | Status | At | Notes |
|----|------|--------|-----|-------|
| agent-automation | author+driver | posted | 2026-09-11 | Registering proposal per PROCESS.md ingest→register lifecycle. Docs-only; no code or credential changes performed. Awaiting non-author review per Tier 2 (P2 priority). |

## Review log

### 2026-09-11 — agent-automation

- Disposition: posted
- Notes: Initial registration. No votes cast yet. This proposal and its companion `tier4-scope-review` are linked (see each MANIFEST's Links section) but tracked as separate registry entries since they address distinct concerns — credential scoping vs. Tier 4 gate friction — even though both were drafted together and submitted in one PR.

## Checklist (process)

- [x] Registered in `docs/proposals/registry.yaml`
- [ ] At least one non-author review recorded
- [ ] Status -> accepted (requires Tier 2-3 evidence per CONSENSUS.md)
- [ ] Pilot GitHub App/fine-grained PAT role stood up (follow-up item, not this PR)
- [ ] `docs/AGENT-ACCESS.md` created (follow-up item, not this PR)
- [ ] Closed + moved to `closed/` when terminal

## Links

- Companion proposal: `docs/proposals/active/tier4-scope-review/MANIFEST.md`
- Related: `docs/CONSENSUS.md` (Tier model this proposal operates under), `docs/CREDENTIAL-EXPOSURE.md` (prior credential-exposure incident referenced by `vercel-lane-topology`)