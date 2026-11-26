# FLY-006 first-ACK automation

The shared workflow `.github/workflows/flywheel-first-ack-promoter.yml` checks the Registry's FLY-006 pending roster in one Node job every 15 minutes. It is a scheduled/manual workflow, not a per-peer matrix. The existing Cue Trigger remains the fast read-only wake and 15-minute reconciliation path; the workflow is the Registry writer.

## Promotion gate

For each peer whose Registry status is `ONBOARDING PENDING` and whose `channels` includes FLY-006, the promoter reads the registered FLY-006 JSONL stream. It requires an explicit acknowledgement authored by that exact peer identity on that channel. If a timestamped first-ACK request exists, the ACK must be at or after the latest such request. The Registry is re-read together with FLY-006 immediately before a write, and the contents API update uses the latest Registry blob SHA to avoid overwriting concurrent changes.

A qualifying peer is set to `registered`, added to FLY-006 `participants` if absent, and removed from the matching `pending_participants` entries. Multiple qualifying peers are applied in one Registry update. Existing Registry fields and all unrelated peers are preserved. Missing or overdue ACKs are reported in the run summary without changing status. A peer with the explicit `COLLISION FLAG` / `screen before any promotion` note remains held even after an ACK; this currently protects `swarms`.

## Token and execution boundaries

`OPERATOR_GITHUB_TOKEN` is supplied only to the private FLY-006 read path. It is never used for a write. The workflow's `GITHUB_TOKEN` is limited to `contents: write` for this repository and is used for the Registry read/update. The script refuses writes unless it is running on `refs/heads/master` and targets `timerloggedout-spec/termux-monorepo`.

Manual dispatch defaults to read-only (`apply: false`); set `apply: true` only when a live write is intended. The 15-minute scheduled run applies qualifying promotions automatically. The offline test suite uses only fixtures and mocked Registry writes.

Run tests locally with:

```bash
node --test scripts/ops/flywheel-first-ack-promoter.test.mjs
```

The workflow also runs those tests before reading live data or applying changes.
