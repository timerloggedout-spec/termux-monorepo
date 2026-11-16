# Failsafe publish protocol — web fallback for the PAT wall (fleet-wide)

Codified by the AppID lane from the quota-specialist's proven route
(owner order 2026-10-29 21:28 PT: "ensure it's system wide failSafe
process|protocol|workaround"). Proven case: **PR #2399** — API merge
died 403 at 2026-10-30T04:13Z with PAT remaining = 0; web merge
succeeded in the same wall (merge commit `952b1fec`, master history
verified on-page).

## Trigger + posture

- **Trigger:** PAT core remaining = 0, or a 403 on publish/merge, with a
  PR whose merge cannot wait for the window reset.
- **Primary route stays programmatic** (PAT helper `pat_publish.py`, or
  an AppID installation token where a role app has the permission). The
  web route is a **fallback for merge** (plus small creates), never the
  standing path.

## Session basis — why this does not breach the fleet credential rule

The web route rides the Muse browser's **pre-existing signed-in owner
session**. No sign-in is performed, no credential is handled, entered,
or stored by any lane. It is therefore **not a credential-provisioning
route**: provisioning stays the vault PAT helper and AppID manifests,
exactly as before. If the session is absent/expired, or any fresh auth
/ 2FA wall appears → **STOP**. Never provision via browser; fall back to
the PAT window or the AppID route. (A sudo-mode prompt on a sensitive
page follows the warn-first auth rule.)

## What it bypasses

The PAT REST core bucket (5,000/h per user). Web UI actions ride the
browser session, not the PAT, so a merge works at PAT remaining = 0.

## Merge steps (proven leg)

1. Open `https://github.com/{owner}/{repo}/pull/{n}`.
2. Read the page state: PR open, **"No conflicts with base branch"**,
   required checks green (names + conclusions off the page — e.g.
   hygiene / smoke / guard). Note any non-required failures; never hide
   them.
3. Click **Merge pull request** → **Confirm merge** — **merge commit
   only** (fleet default; never squash/rebase unless the PR's owning
   lane says so).
4. Page confirms "Pull request successfully merged and closed" + shows
   the merge commit SHA.

## Create steps (standard UI — NOT yet exercised end-to-end by the fleet)

Branch must already exist (pushed via PAT/git in a live window, or
created in the UI) → `/compare/{base}...{branch}` → **Create pull
request** → title/body → **Create pull request**. File authoring via the
web editor = small docs only; bulk/binary stays on the API route.

## Verification — the merge oracle still binds

A UI-shown SHA alone is **not** proof (phantom-SHA rule). Required:
the PR-numbered merge commit found in master history (the web commits
page is acceptable as an interim read) **and** landed content verified
on master — via an App installation token (own bucket, wall-free) or
the PAT in the next window.

## Limits

One PR per browser task. Branch is not auto-deleted (delete via the UI
button if the owning lane wants it). No force actions, no settings
changes, no credential work under this protocol.
