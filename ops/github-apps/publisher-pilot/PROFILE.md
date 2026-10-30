# Termux Fleet Publisher — GitHub App profile (PROPOSED, not yet created)

- **Status:** allocation proposal #1 of the AppID lane
  (`docs/ops/GITHUB-APP-PROCESS.md` §3/§6). Package prepared; creation is
  the manifest flow — one signed-in Create click, then API conversion,
  install consent on timerloggedout-spec, custody, bucket proof.
- **Display name:** Termux Fleet Publisher — **PROPOSED only**: the full
  naming set (appName, slug, role, moniker, alias) is blocked on the
  registry/marketing naming conference (Oracle/Delphi function-identity
  precedent); nothing here is a provisioning fact.
- **Proposed slug:** `termux-fleet-publisher` — likewise provisional.
- **Bot author identity (expected form):** `termux-fleet-publisher[bot]`
- **Permissions (proposed):** metadata = read; **contents = write;
  pull_requests = write; issues = write** (coordination comments —
  cadence bundle delta, 2026-10-29). No webhooks, no events. Deliberately
  excluded at rung 1: `workflows` (needed only to publish workflow-file
  changes — rung 2, owner pick), `actions` (dispatch — deferred),
  `checks` (reviewer-ops / gate-ci roles).
- **Why a separate app, never a collector upgrade:** the collector is
  public and read-only by design; adding write to it would re-open every
  existing installation's consent and destroy the public-install safety
  argument. A publisher key leak is bounded to contents/PR write on
  selected repos of installing accounts only.
- **Visibility:** manifest ships `public: true` (fleet end-state: others
  may install the fleet's function apps). Owner may flip to account-only
  in the manifest before the Create click; the pick is recorded here at
  creation.
- **Custody (at creation):** bootstrap PEM + client secret into the
  app's connector custody dir per GITHUB-APP-PROCESS.md §2 (0600,
  fingerprint recorded, values never in chat/files/commits). Actions
  distribution (repo secret, names-only) is a separate later step.
- **Proof protocol (at creation):** mint an installation token while the
  PAT bucket reads low/0; `GET /rate_limit` shows the independent
  5000/h bucket; publish-path dry run = branch + file PUT + PR on a
  scratch branch, closed unmerged; then first real publish takes over
  the pat_publish route's principal.
