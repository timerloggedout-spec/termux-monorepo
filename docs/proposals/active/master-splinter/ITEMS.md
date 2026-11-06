# Work Items — AppID control plane

| ID | Priority | Status | Scope | Acceptance criteria / evidence |
|---|---:|---|---|---|
| APPID-CP-01 | P1 | done | Establish the read-only AppID inventory and permission-snapshot read model over the existing eight-AppID family. | PR #4642 merged; schema and loader live in the monorepo; inventory dry-run and G4-shaped receipt recorded. No ninth App is created. |
| APPID-CP-02 | P1 | done | Preserve migration-wave lineage and dry-run replay as a control-plane read-model concern. | PR #4642 merged; migration-wave/replay read-model structures and dispatch-only loader exist; initial inventory dry-run was recorded as MATCH. Repo Replay and Commit Replay remain separate engines/stores. |
| APPID-CP-03 | P1 | done | Join per-App usage from QUE admission records, telemetry receipts, and lane-events without creating a competing usage store. | SPEC.md defines usage as a VIEW; PR #4642 reports the read-model schema includes a usage VIEW. |
| APPID-CP-04 | P1 | executing | Complete permission drift readback: compare declared manifests with observed installation-token permissions. | TEL-04 remains open in ops/github-apps/MIGRATION-ITEMS.md; evidence must show declared and observed separately, with drift receipts and negative-path coverage. |
| APPID-CP-05 | P1 | executing | Reconcile AppID adoption and migration per item using the fleet migration ledger. | MIG-07 rollout and MIG-11 per-item calls/run accounting remain explicit open items in MIGRATION-ITEMS.md; no bulk PAT retirement. |
| APPID-CP-06 | P1 | proposed | Establish a refresh cadence only after measured need and source-owner agreement. | Dispatch-only workflow remains the current contract; no schedule is inferred. Any cadence proposal includes quota impact, freshness target, failure handling, and owner approval. |
| APPID-CP-07 | P1 | proposed | Reconcile the private Registrar repository and monorepo implementation lineage without splitting source-of-truth ownership. | Record exact repo/branch/commit references; define per-item migration and terminal states; no duplicate database or unverified code move. |

## Disposition

The proposal is adapted, not adopted under its original name. The control-plane implementation has a merged first slice (#4642); remaining work is tracked against the existing AppID migration ledger. No App creation, credential cutover, or deployment is authorized by this manifest.
