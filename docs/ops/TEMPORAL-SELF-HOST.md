# Temporal — fleet self-host

**Owner decision (2026-10-27):** Temporal is **self-hosted** on the
fleet's own infrastructure. Temporal Cloud is not used (the free
tier is not permanent, and the card rule closes the paid route).
This page is the operator record; the pass evidence lives in
`docs/proposals/passes/temporal-durable-execution/`.

## What runs

| Piece | Value |
|---|---|
| Server | Temporal dev-server mode (CLI 1.9.1 / Server 1.32.0), single node |
| Bind | `localhost:7233` frontend, `localhost:8233` Web UI |
| Persistence | sqlite DB at `~/workspace/temporal-selfhost/temporal.db` (durable workspace disk) |
| Supervision | systemd units `temporal-selfhost` + `temporal-relay` (Restart=always) |
| Exposure | socat relay `0.0.0.0:7234 -> 127.0.0.1:7233` (see below) |
| Recovery | hourly keepalive job reinstalls the units from the workspace copies after a VM replacement (`/etc` does not persist; `install.sh` restores) |
| Files | `scripts/temporal/selfhost/` (repo mirror) = `~/workspace/temporal-selfhost/` (live copies) |

## Why localhost + a relay

Advertising `0.0.0.0` from the dev server **stalls its cluster
bootstrap** in this network namespace (found firsthand 2026-10-28:
process alive, internal port only, never binds 7233; localhost
bind is up in ~10s). So the server binds loopback, and the socat
relay gives every other interface a path in. Verified: the §6
harness passes through the relay (`127.0.0.1:7234`) exactly as
direct (`localhost:7233`).

**Known middlebox limit:** gRPC through this VM's sandbox host
link (host0, 198.19.0.2) garbles the HTTP/2 preface — reproduced
with two independent relays (socat + a python relay), so the fault
is the link, not the relay. A clean interface (e.g. a real tailnet
interface in the VM's namespace) carries the relay fine; the
host link does not. Multi-node Temporal clustering is **not**
claimed: redundancy here = persistence + supervision + relay +
reinstall recovery, on one node.

## Proof of record

Re-proven 2026-10-28 against this self-host (pass addendum
`implementation/ADDENDUM-2026-10-28-SELFHOST.json`):

- §6 kill-resume harness vs `localhost:7233`: **PASS** — worker
  SIGKILLed mid-activity, workflow completed, receipt count
  exactly 1, unknown outcome reconciled, history digest in the
  evidence envelope.
- Same proof via the relay (`127.0.0.1:7234`): PASS, receipt 1.
- Persistence: after a service restart, both proof workflows
  still list Completed from the sqlite DB.

## Operate

- Status: `systemctl status temporal-selfhost temporal-relay`
- Logs: `journalctl -u temporal-selfhost`
- Repair/reinstall: `sh ~/workspace/temporal-selfhost/install.sh`
- Connect: SDK/CLI `--address localhost:7233` (or `:7234` via the
  relay); UI at `http://localhost:8233`.
