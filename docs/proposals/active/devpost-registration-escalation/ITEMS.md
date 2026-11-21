# Work Items — devpost-registration-escalation

| ID | Priority | Status | Scope | Acceptance criteria |
|---|---:|---|---|---|
| DRE-001 | P1 | done | Capture authenticated Devpost registrations and reconcile C12 submission evidence. | Snapshot is names-only and timestamped; C12 submission timestamp is compared with the official Round 1 wall; C18/C19 registration-only state is explicit. |
| DRE-002 | P1 | done | Update coordinator, schema, registration moniker registry, 4N0N protocol, event log, desk-feed and countdown feed. | Official event windows, prize data, eligibility/judging rules, and internal escalation tiers are represented consistently; no unsupported calendar event is claimed. |
| DRE-003 | P1 | done | Update Wagering Book and public dashboard. | 41 subjects reconcile across source/public feeds; C12-24 settles Y from Devpost evidence; C18/C19 propositions carry exact official walls; Gantt horizon and count are feed-driven. |
| DRE-004 | P1 | executing | Reconcile implementation against current master, run repo-gate and termux-smoke, inspect CI and resolve all critical failures. | Master-based PR is reviewable; both gates green; checks and artifacts inspected; no merge before review and verified outcome. |
| DRE-005 | P1 | blocked | Bind C12 conditional Round 2, C18, and C19 escalation tiers to deadline-reminders/v1 Tracking register and external calendar records. | Each register item has stable ID, calendar event ID, exact local wall, reminder offsets, and verified event state. Tracking register source is currently unavailable in this workspace. |
| DRE-006 | P2 | todo | Reconcile C12 after the Nov 21 finalist announcement. | Activate Round 2 timebox only if Devpost confirms finalist status; otherwise close the conditional lane with evidence. |


Implementation PR: https://github.com/timerloggedout-spec/termux-monorepo/pull/5727 (draft; master-based).
