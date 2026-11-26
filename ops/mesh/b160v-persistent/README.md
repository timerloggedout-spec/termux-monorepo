# B160V persistent SSH

The owner's requirement: **persistent ssh** to the BLU View 5 (B160V) —
not tunnel windows that expire. This package is the device-side leg; the
VM side lives in `~/workspace/mesh-ssh/` (`ssh-config` host
`b160v-persistent`, `bin/b160v-rendezvous-connect.py`).

**v2 (this revision) supersedes v1.** v1 used a different carrier that
the owner revoked on 2026-11-26; v1 was published but never installed on
the device. Do not install v1 artifacts (its boot entry used slot 10;
install.sh removes it).

## Design (5 lines)

1. The device's Termux sshd is permanent: port 8022, fleet key authorized,
   started at boot by `~/.termux/boot/00-sshd.sh` (installed 2026-11-26).
2. The transport shape is **dials-out**: the device keeps a Cloudflare
   tunnel to its own sshd alive — a supervised reconnect loop around
   `cloudflared` (the same dials-out rendezvous shape hark-vm adopted,
   FLY-010: the peer dials out because no fleet surface can host the
   listener — see "Why not a fleet-hosted listener").
3. Primary mode is a **named tunnel** on the owner's Cloudflare zone:
   the hostname is stable, so the rendezvous file
   (`mesh/b160v-endpoint.json` in the private repo
   `timerloggedout-spec/muse-vm-workspace-backup`) is a liveness
   heartbeat, not a moving address.
4. On the VM, `ssh -F ~/workspace/mesh-ssh/ssh-config b160v-persistent`
   reads the rendezvous file and bridges through `cloudflared access
   tcp` (whose dialer honors the VM's proxy env — the sanctioned
   egress). Stable address, no tailnet dependence, no fleet server.
5. Free tier only (Cloudflare Tunnel is free; a free-plan zone is
   enough). No card anywhere in the design.

## Carrier evidence (measured 2026-11-26, firsthand)

- **Quick tunnels DO carry raw TCP/SSH.** On a direct-egress host
  (GitHub Actions runner standing in for the device), the full loop was
  proven with the real binary: sshd on :2222 + `cloudflared tunnel
  --url tcp://127.0.0.1:2222` + `cloudflared access tcp` + SSH login
  through it (`ACCESS_LOOP_OK`).
- **But the muse-vm egress is blocked at the Cloudflare edge for the
  trycloudflare zone.** From this VM, every `*.trycloudflare.com`
  hostname — TCP-service and HTTP-service tunnels alike — returns
  `403 "Your request was blocked"` from the edge, while the same
  hostnames serve normally from other egresses. The block follows this
  VM's egress, not the tunnel type. A named tunnel lives on the
  owner's own zone, outside that screening — that is why named mode is
  primary and quick mode is an alternate for other egresses only.
- **cloudflared cannot originate a tunnel from the muse-vm.** Its
  tunnel-creation and edge dials ignore the proxy env and connect
  directly; the VM runtime denies direct outbound TCP for non-proxy
  traffic (the interceptor answers in plain text saying so). The
  device has ordinary consumer egress, so origination lives there;
  the VM only ever runs the access (client) side, which does honor
  the proxy env.
- The proof workflows used for these measurements were removed from
  the backup repo after the run; the rendezvous file was restored to
  its seed state.

## Persistence on this device

Follows the device's own arrangements, read firsthand 2026-11-26 —
nothing parallel is invented:

- **Supervisor:** `~/bin/supervisor.sh` is the keep-alive loop (rish
  probe gate, pgrep-guarded nohup starts, 60 s loop; services are
  long-running loops in `~/bin`, cf. `mem-guard.sh`, `wifi-watchdog.sh`).
  install.sh adds an idempotent, marker-guarded stanza for
  `b160v-tunnel.sh` (one backup taken: `supervisor.sh.bak-b160v`).
- **Boot:** `~/.termux/boot/` numbering is 00-sshd · 10-tmx-secondary-services
  · 45-tailscale · 50-master-rescue · 99-mem-guard. This package takes
  slot **20**: `20-b160v-persistent.sh` (wake-lock, then start.sh).
  start.sh also starts the supervisor if it is not running — it was
  observed NOT running on the device; the boot entry closes that gap.
- **Device Tailscale:** `45-tailscale.sh` runs `tailscale up --reset
  --accept-routes` at boot, so the device side of the tailnet is
  arranged; the tailnet data plane is down upstream of both the device
  and this VM (all tailnet CONNECTs close 0-bytes since 16:17Z
  2026-11-26) and is not built on. When it recovers, the mesh config's
  `b160v` entry (tailnet :8022) reaches the same sshd directly.

## Why not a fleet-hosted listener

Measured 2026-11-26, firsthand:

- **Hark VM public IP** (52.26.208.45): no answer on 22/8022/2222/443
  from the VM's egress relay (timeouts / relay-closed). hark-vm is
  outbound-only (FLY-010) — dropped as a rendezvous candidate.
- **Cue VM**: no publicly reachable sshd (tailnet only, tailnet down).
- **This VM as listener**: the VM's egress relay is outbound-CONNECT
  only — the VM has no public inbound the device could dial. The
  Actions-runner hop (self-hosted runner `muse-vm-mesh`) is degraded
  (broker TLS failing, offline since 18:23Z 2026-11-26) and hosts no
  inbound listener in any case. **A muse-vm-hosted listener is not
  provable and is not designed on.**

## Named-tunnel provisioning (one-time, owner)

The tunnel token is a credential: it lives only on the device, never
in chat, commits, or this README. Steps:

1. In the Cloudflare Zero Trust dashboard (free plan): Networks →
   Tunnels → create a tunnel (name e.g. `b160v`) → choose the
   cloudflared connector → copy the tunnel token it shows.
2. On the device: save the token to `~/b160v-persistent/cf-token`
   (chmod 600).
3. In the same dashboard tunnel → Public Hostnames → add a hostname
   (e.g. `b160v.<your-domain>`), service type **TCP**, URL
   `localhost:8022`.
4. On the device: set `CF_HOSTNAME=b160v.<your-domain>` in
   `~/b160v-persistent/cf.env` (CF_MODE=named is the default).
5. Restart the loop (`sh ~/b160v-persistent/start.sh` — it is
   pidfile-guarded; kill the old loop pid from status.sh first if it
   was waiting unarmed) or reboot. status.sh shows the armed state.

## Rendezvous credential (one-time provisioning)

The loop also needs one writer credential to update the endpoint file.
It is the SAME fine-grained token the webWrapper v2 streaming sink uses
(`WEBWRAPPER_GH_TOKEN`). Provision once, either:

- export it in the Termux session before running install.sh, or
- write it to `~/b160v-persistent/token.env` (chmod 600) as one line:
  `WEBWRAPPER_GH_TOKEN=<value>`

Fallback with no token: if `~/b160v-rendezvous` is a git checkout whose
remote accepts pushes, the writer commits + pushes the file there.
With no writer armed the tunnel still runs and the endpoint is kept in
`~/b160v-persistent/last-endpoint`, but the VM cannot discover it —
`status.sh` says NOT ARMED until one writer exists.

## Security shape

- The rendezvous file sits in a PRIVATE repo. A hostname alone grants
  nothing: the device sshd takes only the fleet key (`hatch`,
  SHA256:jD7vZcRkm…).
- The Cloudflare tunnel token is device-local (0600). Anyone holding
  it could re-point the tunnel connector; treat it like a password.
- The rendezvous token (above) is fine-grained, Contents read/write on
  `muse-vm-workspace-backup` only.

## Install (device, one block)

```sh
mkdir -p ~/b160v-pkg && cd ~/b160v-pkg && curl -sL https://raw.githubusercontent.com/timerloggedout-spec/termux-monorepo/master/ops/mesh/b160v-persistent/b160v-persistent.tar.gz | tar xz && sh install.sh
```

That is the only device action. Everything else (boot entries,
supervisor stanza, loop start, sshd) is done by install.sh; re-running
it is idempotent. The named-tunnel and rendezvous provisionings above
are the only other owner steps, once.

## Files

| File | Role |
|---|---|
| `b160v-tunnel.sh` | The reconnect loop (installed to `~/bin/`, pidfile-guarded, logs to `tunnel.log`) |
| `rendezvous-push.py` | Endpoint/heartbeat writer (Contents API → git checkout → none) |
| `start.sh` | Detached launcher (wake-lock if available, sshd, supervisor, loop) |
| `status.sh` | sshd / cloudflared / supervisor / loop / tunnel / writer state on one screen |
| `boot-20-b160v-persistent.sh` | Termux:Boot entry, installed as `~/.termux/boot/20-b160v-persistent.sh` |
| `install.sh` | Copies files, installs cloudflared + boot entry + supervisor stanza, retires v1/revoked-carrier leftovers, starts the loop |

Device-local state (created on the device, never in the tarball):
`~/b160v-persistent/{cf.env, cf-token, token.env, last-endpoint,
tunnel.log, last-run.log, loop.pid}`.

Logs: `~/b160v-persistent/tunnel.log` (loop events) and
`~/b160v-persistent/last-run.log` (current tunnel's raw output).

## Uninstall

```sh
rm ~/.termux/boot/20-b160v-persistent.sh; kill "$(cat ~/b160v-persistent/loop.pid)"; rm ~/bin/b160v-tunnel.sh; rm -rf ~/b160v-persistent
```

(Restore the supervisor stanza from `~/bin/supervisor.sh.bak-b160v` if
the stanza should also go.)

## Failure modes (precise)

- `named mode NOT ARMED` in tunnel.log → provision the cf-token +
  CF_HOSTNAME (above).
- `rendezvous: NO WRITER ARMED` in tunnel.log → provision the
  rendezvous token (above).
- `cloudflared missing` in tunnel.log → `pkg install cloudflared`.
- VM says `no live endpoint published` → loop not installed/running,
  or the writer is unarmed and the file still holds the seed state.
- VM connects but the edge refuses the hostname → the rendezvous file
  names a quick-tunnel host while connecting from the muse-vm egress
  (blocked, see "Carrier evidence") — use named mode.
- Device rebooted → Termux:Boot runs 00-sshd.sh + 20-b160v-persistent.sh;
  the loop self-heals from there.
