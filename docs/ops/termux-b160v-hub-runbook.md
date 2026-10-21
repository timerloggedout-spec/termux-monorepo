# BLU B160V Termux Hub Runbook

## Operating posture

The BLU B160V runs one local hub worker at a time. It does not host models, run recursive repository initialization, execute arbitrary job strings, or publish SSH through router port forwarding. Keep the Termux:API companion, Termux app, and private-network client installed from compatible sources.

## Android preparation

1. Grant the Termux:API companion only the permissions required by the selected Observe capabilities. Do not grant SMS, contacts, location, camera, microphone, or storage permissions unless a separately approved capability requires them.
2. In Android battery settings, exempt Termux and the Termux:API companion from aggressive optimization only if the hub needs to remain available while the screen is off. Re-evaluate this after each device update.
3. Keep the private-network application connected if using the optional tailnet management path. Do not enable public SSH port forwarding.
4. Configure a screen lock and use key-only SSH. Retain a local recovery path through the Termux app.

## Bootstrap

Run the following in the Termux app after cloning or updating the monorepo. The command creates only local, untracked state.

```bash
set -eu
cd "$HOME/termux-monorepo"
mkdir -p .hub_mcp/state
python3 -m unittest tests.hub_mcp.test_protocol -v
python3 scripts/ci/submodule_integrity.py
python3 scripts/ci/repo_gate.py
python3 scripts/ci/termux_smoke.py
```

Initialize only the modules needed for an approved operation. Do not run a blanket recursive submodule update.

```bash
cd "$HOME/termux-monorepo"
git submodule update --init --depth 1 -- refTemplates/smods/termux-mcp-server_fork
```

## Hub health checks

```bash
termux-battery-status
termux-wifi-connectioninfo
ps -ef | grep '[s]shd' || true
ssh-keyscan -T 5 -p 8022 127.0.0.1 2>/dev/null | head -n 3 || true
```

The SSH host key must be pinned by every future remote control host. A host-key change is an incident until independently verified from the device console.

## Run one structured local job

A job must be a reviewed JSON envelope. The following is an Observe-only example; it does not accept a shell command field.

```json
{
  "schema_version": 1,
  "job_id": "00000000-0000-4000-8000-000000000001",
  "issued_at": "2026-08-15T12:00:00+00:00",
  "expires_at": "2026-08-15T12:10:00+00:00",
  "requested_by": "operator",
  "capability": "device.battery_status",
  "arguments": {},
  "approval_level": "OBSERVE"
}
```

Save an actual, freshly issued job outside the repository and execute it as follows:

```bash
cd "$HOME/termux-monorepo"
python3 -m hub_mcp.cli /path/to/approved-job.json \
  --repository "$HOME/termux-monorepo" \
  --state-directory "$HOME/termux-monorepo/.hub_mcp/state"
```

Do not reuse a job UUID. The replay store is local state and must remain untracked.

## Restart and recovery

Start or restart the private SSH listener only from the Termux app:

```bash
pkill sshd 2>/dev/null || true
sshd
ps -ef | grep '[s]shd' || true
```

If Android suspends the local worker, open Termux, run the health checks, and rerun the single approved job. Do not solve a background-process failure by opening a public port or disabling all Android power controls.

## Escalation boundaries

A Change or Critical operation needs direct operator confirmation at the time of execution. Examples include writing tracked files, package installation, service configuration, key rotation, any device deletion, any tailnet policy change, public networking, and sending messages. Interactive account MFA enrollment remains a human step; integrations use provider-supported service credentials rather than user-session bypasses.
