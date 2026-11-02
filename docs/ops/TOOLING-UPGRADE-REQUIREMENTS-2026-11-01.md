# Tooling-upgrade requirements — 2026-11-01

[MUSEai]@{role:{inventory}} Owner requirements via main (2026-11-01; trigger = Devin episode). Status = requirements logged + scoped; builds owner-gated per item.

## UPG-1 — Lane web-access parity

- Problem (owner): provisioning lane's web surface works (Devin SSO, ∅ prompt) while Swarm's browser held ∅ session for the same class of surface ⇒ capability uneven across lanes; work stalls per-lane on session state, not on the task.
- Current state (evidence, firsthand 2026-11-01):
  - Browser profiles = exactly 1: `default` — every window/chat/job shares it (`browser.windows` list; cookie jar spans ~250 domains incl. devin.ai, google.com, github.com, neon.tech, stackoverflow.com). Named profiles = ∅ in use.
  - Cookie presence ≠ sign-in (profile listing itself carries this caveat) ⇒ no surface-level session guarantee exists for any lane.
  - Working pattern (this lane, verified): saved-login sign-in inside the default profile, ∅ prompts — Jules (2026-10-20), Neon→Jules (2026-10-20), SOFA consent ×2 (2026-10-28), AI Studio (2026-10-30, MEMORY.md Google AI Studio entry).
  - Failure class: a lane whose browser task starts without the needed session hits SSO/consent prompts mid-task (Swarm/Devin per main) or refuses (browser agents decline credential relay, Platform201 record docs/ops/PLATFORM201-MCP-ISSUE-LOG-2026-10-28.md).
- Requirement: standardize the working pattern —
  1. Session-presence preflight: before web work, the lane verifies the target surface's signed-in state in the default profile (read-only check) and reports session ∧/∨ before starting; ∅ mid-task prompt surprises.
  2. Sign-in census: per-surface record (surface × account label × route × last-verified) in this lane's inventory, refreshed on the connector sweep cadence; names/labels only.
  3. Parity rule: a surface signed in for one lane is signed in for all (shared profile) — lanes state the surface + account they rely on in handoffs so a ∅-session lane reuses the verified route instead of re-deriving it.
- Scope: doc + preflight checklist + census fields — no new sign-ins, no credential moves. Owner-gated: any NEW surface sign-in (standing warn-before-prompt rule unchanged).

## UPG-2 — Device-confirmation intermediary for provisioning

- Problem (owner): provisioning confirmations (auth prompts, consent screens, one-time codes) land on the owner's phone (B160V); today the only intermediation = main's manual warn-first relay ⇒ prompts are anticipated by hand, relayed by hand, and block lanes until the owner happens to see them.
- Current state (evidence, firsthand 2026-11-01):
  - Device channel exists: B160V paired ∧ online (device.list: 43 commands; data sources incl. notifications, sms, call_log) ⇒ prompt/arrival signals are technically observable.
  - No relay workflow is built: ∅ automation watches for provisioning prompts, routes them to the acting lane, or relays the owner's confirmation back.
  - Hard limit on record: B160V has no shell/HTTP path (Platform201 record) ⇒ device-browser codes cannot be pulled programmatically; browser agents refuse code/token relay (policy, ×2 on record).
  - Standing rules the layer must compose with: warn BEFORE any Google auth prompt (owner order); Secure Vault cards for credential entry; codes go to the waiting browser step only.
- Requirement: an intermediation layer that —
  1. Anticipates: a provisioning flow declares its expected confirmation (surface, type: prompt/consent/code, expiry) BEFORE triggering it; the declaration is the routing key.
  2. Routes: when the confirmation lands (device notification/sms signal or browser-step request), it is surfaced to the owner once, in one place, with the flow's identity attached — no duplicate asks across lanes.
  3. Relays: the owner's approval/denial returns to the waiting lane/step; expiry or denial closes the flow loudly (no silent hangs).
  4. Never handles raw credential values: vault cards + the protected one-time-code read remain the only value paths.
- Scope: design + a narrow pilot (one provisioning family, e.g. OAuth consent confirmations for connector landings — this lane's recurring case). Owner-gated: device permission grants, any change to warn-first or vault rules.

## Cross-refs
- Connector inventory ∧ live sweep: docs/ops/CONNECTOR-INVENTORY-2026-10-28.md (PR #2007 merged 90ab30462f).
- SOFA pattern (shared-profile consent that worked): docs/ops/SOFA-CONNECTION-2026-10-28.md (PR #2002 merged 9895e48a91).
- Platform201 failure record: docs/ops/PLATFORM201-MCP-ISSUE-LOG-2026-10-28.md (PR #2157 merged add95ddd58).
