# B160V persistent SSH

The owner's requirement: **persistent ssh** to the BLU View 5 (B160V) —
not 60-minute tunnel windows. This package is the device-side leg; the
VM side lives in `~/workspace/mesh-ssh/` (`ssh-config` host
`b160v-persistent`, `bin/b160v-rendezvous-connect.py`,
`bin/connect8899.py`).

## Design (5 lines)

1. The device's Termux sshd is permanent: port 8022, fleet key authorized,
   started at boot by `~/.termux/boot/00-sshd.sh` (already installed).
2. The missing leg was transport: the tailnet data plane is down and the
   VM has no public inbound, so the device dials OUT and keeps a reverse
   tunnel alive — a reconnect loop around Pinggy free TCP tunnels
   (`ssh -p 443 -R0:127.0.0.1:8022 tcp@free.pinggy.io`).
3. Pinggy free endpoints rotate at every reconnect (~60 min cap), so the
   loop publishes the current endpoint after each reconnect to a
   rendezvous file: `mesh/b160v-endpoint.json` in the private repo
   `timerloggedout-spec/muse-vm-workspace-backup`.
4. On the VM, `ssh -F ~/workspace/mesh-ssh/ssh-config b160v-persistent`
   reads the rendezvous file, CONNECTs to the endpoint through the local
   egress relay (127.0.0.1:8899), and logs in as `u0_a243` with the fleet
   key. Stable address, rotating plumbing.
5. Free tier only, no tailnet dependence, no fleet server to run.

Why not a fleet server as rendezvous: measured 2026-11-26 — Hark VM
public IP answers nothing on 22/8022/2222/443 from the VM's egress relay
(timeouts / relay-closed), Cue has no publicly reachable sshd (tailnet
only, and the tailnet data plane is down). Pinggy was already
provisioned on the device for Termux–GitHub and is proven end-to-end.

## Security shape

- The rendezvous file sits in a PRIVATE repo. An endpoint alone grants
  nothing: the device sshd takes only the fleet key (`hatch`,
  SHA256:jD7vZcRkm…), and Pinggy exposes exactly one forwarded port.
- The device's tunnel identity is its own `~/.ssh/id_ed25519` (created
  by install.sh if absent) — used only to authenticate to Pinggy.
- The rendezvous token (below) is fine-grained, Contents read/write on
  `muse-vm-workspace-backup` only.

## Rendezvous credential (one-time provisioning)

The loop needs one writer credential to update the endpoint file. It is
the SAME fine-grained token the webWrapper v2 streaming sink uses
(`WEBWRAPPER_GH_TOKEN`). Provision once, either:

- export it in the Termux session before running install.sh, or
- write it to `~/b160v-persistent/token.env` (chmod 600) as one line:
  `WEBWRAPPER_GH_TOKEN=<value>`

Fallback with no token: if `~/b160v-rendezvous` is a git checkout whose
remote accepts pushes, the writer commits + pushes the file there.
With no writer armed the tunnel still runs and the endpoint is kept in
`~/b160v-persistent/last-endpoint`, but the VM cannot discover rotations
— `status.sh` says NOT ARMED until one writer exists.

## Install (device, one block)

```sh
mkdir -p ~/b160v-pkg && cd ~/b160v-pkg && curl -sL https://raw.githubusercontent.com/timerloggedout-spec/termux-monorepo/master/ops/mesh/b160v-persistent/b160v-persistent.tar.gz | tar xz && sh install.sh
```

That is the only device action. Everything else (boot entries, loop
start, sshd) is done by install.sh; re-running it is idempotent.

## Files

| File | Role |
|---|---|
| `b160v-tunnel.sh` | The reconnect loop (pidfile-guarded, logs to `tunnel.log`) |
| `rendezvous-push.py` | Endpoint writer (Contents API → git checkout → none) |
| `start.sh` | Detached launcher (wake-lock if available, sshd, loop) |
| `status.sh` | sshd / loop / endpoint / writer state on one screen |
| `boot-10-b160v-tunnel.sh` | Termux:Boot entry, installed as `~/.termux/boot/10-b160v-tunnel.sh` |
| `install.sh` | Copies files, installs boot entries, ensures keypair, starts the loop |

Logs: `~/b160v-persistent/tunnel.log` (loop events) and
`~/b160v-persistent/last-run.log` (current tunnel's raw output).

## Uninstall

```sh
rm ~/.termux/boot/10-b160v-tunnel.sh; kill "$(cat ~/b160v-persistent/loop.pid)"; rm -rf ~/b160v-persistent
```

## Failure modes (precise)

- `rendezvous: NO WRITER ARMED` in tunnel.log → provision the token (above).
- VM says `no live endpoint published` → loop not installed/running, or
  the writer is unarmed and the file still holds the seed state.
- VM connects but the session drops within the hour → the endpoint was
  near its 60-min cap; the loop republishes within ~1 min of reconnect —
  retry the ssh command.
- Device rebooted → Termux:Boot runs 00-sshd.sh + 10-b160v-tunnel.sh;
  the loop self-heals from there.
