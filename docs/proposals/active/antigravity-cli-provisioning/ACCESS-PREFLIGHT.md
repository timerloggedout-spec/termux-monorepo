# Reliable access checks without task replay

This is the controller-only continuation of **AGY-1497-10**, not a new priority or a device-service change. It keeps the existing `termux-device2` route and SSH pin. The offline `readiness.py` inventory remains offline and unchanged.

## Run the bounded preflight

From the repository on the controller:

```bash
python3 scripts/antigravity/access_preflight.py
# One handshake attempt instead of at most three:
python3 scripts/antigravity/access_preflight.py --attempts 1
# Only if the existing userspace daemon needs an explicit local socket:
python3 scripts/antigravity/access_preflight.py --tailscale-socket /run/tailscale/tailscaled.sock
```

The command prints sanitized JSON. It accepts no task, command, alternate device, repository, or model argument. It does not install anything, invoke AGY, read AGY settings, start services, refresh endpoints, change Tailscale, or repair credentials. No connection to Origin is selected.

## Three different checks

1. **Tailscale observation:** read the existing backend state and exact configured peer IP from `tailscale status --json`. Online is only a peer observation, never SSH readiness. An offline or unknown peer still receives the bounded SSH diagnostic; stale status is not proof of failure.
2. **SSH listener, host trust, authentication and secondary identity:** require the existing secondary account, port, pinned host-key alias, existing `known_hosts.device2` file, tailnet address and ProxyCommand. A fresh connection uses strict host-key checking and verifies the local secondary marker, account and model. Refused TCP, host-key rejection, authentication rejection and unknown outcomes remain distinct. Only a completed identity handshake verifies authenticated access.
3. **GitHub CLI and public Git:** after the handshake, open exactly one further SSH connection and recheck secondary identity. Independently check `gh auth status --active`, an authenticated `gh api user` request, and `git ls-remote` against the explicit repository's public HTTPS HEAD. Public Git success does **not** verify private-repository access or push permission. Git ignores global/system/repository configuration and credential helpers, URL rewrites, hooks and interactive prompts; it cannot repair Git authentication.

The existing SSH alias selects the private key and pinned key file. The helper neither learns a key nor replaces one. It disables key updates, agent additions/forwarding, port/X11 forwarding, configured local commands and SSH multiplex reuse. A successful check is a point-in-time observation, not a promise that the next connection will work.

## What retries, and what never does

Only the fixed, read-only identity handshake can retry: at most three total attempts, with one-second then two-second backoff. Recognized connection-establishment errors may retry; host-key/authentication/identity errors, unrecognized failures, any returned stdout, and whole-process deadlines stop immediately. Exit 255 alone is not enough to retry. Once authentication completes, the GitHub/Git connection and its commands are attempted once. There is no task-launching or resume path.

Each handshake has an eight-second SSH connect timeout and a fifteen-second controller deadline. Tailscale status and effective SSH-config reads each have a five-second deadline. The GitHub/Git connection has a forty-five-second controller deadline; remote checks have ten/ten/fifteen-second deadlines and a two-second kill grace. Controller deadlines also kill local SSH/proxy descendants. If remote `timeout` is unavailable, GitHub/Git commands are not started.

Per-command `deadline_unknown`, `unavailable` and `not_verified` are separate from `verified`. A missing/truncated completion protocol, disconnect, or SSH exit during the final connection makes all its results unknown. No ambiguous response is upgraded to success or definitive credential rejection. Raw SSH output, account details, paths, peer addresses, credential output and API response bodies are not included in the report.

## Recovery decisions

| Result | Next step |
|---|---|
| Tailscale online, SSH refused/unknown | Do not treat the peer as ready. After connectivity returns, rerun only this preflight. It cannot revive a phone with no reachable SSH listener. |
| Host-key or identity rejected | Stop. Preserve the pin; independently establish the correct device/key. Do not disable verification or reset keys. |
| Authentication rejected | Stop and investigate existing authorized credentials separately; do not loop. |
| SSH verified, GitHub CLI unavailable | Inspect the existing noninteractive PATH or installation in a separately authorized change. This helper does not install or configure `gh`. |
| SSH verified, GitHub/API/Git not verified | Investigate the reported layer. A deadline is uncertainty, not proof that credentials are invalid. |
| Final connection lost | Inspect the state of any **previous** task independently. Do not relaunch AGY, repeat a pilot, or replay a write because reconnect succeeded. |
| All checks verified | Access was verified at that instant. No task ran and no task replay is authorized. |

The previously deployed [device recovery service](SECONDARY-RECOVERY.md) is unchanged. This helper does not call its reconnect/service commands. Recovery after Android force-stop or reboot is not claimed.

## Exit codes

| Code | Meaning |
|---|---|
| 0 | All access checks verified; no task executed |
| 2 | Invalid local arguments |
| 10 | Existing pinned secondary SSH configuration is missing or not accepted |
| 20 | SSH/secondary identity not verified; GitHub/Git checks not launched |
| 30 | Final remote outcome unknown; no replay |
| 31 | Final protocol completed, but at least one GitHub/Git check is not verified |

## Validation and observed limits

Thirty-one new offline tests cover strict pin/config guards, exact peer matching, unknown/offline Tailscale states, listener/auth distinctions, bounded retry/recovery, terminal failures, ambiguous disconnects, no task interface, exact completion markers, raw-output redaction, descendant termination, remote deadlines, and actual shell/Git-config isolation with fixture binaries. No test contacts the network or invokes AGY.

Validation passed: **124 focused `test_agy*.py` tests**, **7 existing offline readiness tests**, `repo_gate.py --base origin/master-staging` against 38 changed PR paths, Linux `termux_smoke.py`, and staged diff whitespace checks. The new fixture tests use the platform temporary-directory selection rather than hardcoding a Linux-only location; the controller sets its temporary directory to RAM. Independent review identified Git-helper/config side effects and ambiguous per-command deadline reporting; both were hardened and covered by executable shell fixtures before the final live run. This is not a claim of native Android test execution or resolution of unrelated open PR review findings.

A live read-only run first observed a running Tailscale backend and online peer but an unknown SSH outcome; no GitHub/Git command was launched. A separate fixed identity-only diagnostic then passed. The hardened preflight subsequently verified a fresh pinned SSH/secondary identity handshake and public Git HEAD connectivity. Both GitHub CLI checks returned **unavailable on the noninteractive PATH**. Exit was 31; full readiness was correctly false. This does not establish whether `gh` is installed elsewhere or why the earlier SSH connection closed. No automatic task execution or replay occurred.

Work is confined to a new RAM-backed scratch checkout because the original root filesystem is full. The original worktree and all unrelated data are preserved. PR #1514 remains open and **DO NOT MERGE**; existing runner/quota and recovery-test review findings are outside this controller-access change.
