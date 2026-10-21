# Agent git / GitHub identity

> **Status:** DRAFT (2026-08-06)  
> **Implements candidate:** CE-23  
> **Agent:** Grok

## Goal

Each agent’s commits and PR actions show **that agent’s** identity in `git log` and, where possible, in the GitHub UI — while the Operator retains control of secrets and branch protection.

## Layers

| Layer | Who appears | How |
|-------|-------------|-----|
| **Author** | Agent | `git -c user.name=Grok -c user.email=grok@x.ai commit` |
| **Committer** | Often Operator PAT or App | Push credential |
| **GitHub actor** | App or machine user | GitHub App installation token per agent |
| **Trailers** | Always | `Signed-off-by:`, `Agent:`, Summary-Editor |

## Preferred rollout

1. **Now:** enforce agent **author** name/email on all agent commits; keep trailers.
2. **Next:** one GitHub App (or machine user) per long-lived agent (Grok, Jules, Gemini) with least-privilege tokens in Actions secrets.
3. **Document** Operator paste of prior research here when available.

## Security

Machine-user PATs and App private keys stay Operator-managed secrets. Agents receive short-lived tokens from Actions OIDC or `secrets.*` — never long-lived keys in the repo.

Signed-off-by: Grok <grok@x.ai>
