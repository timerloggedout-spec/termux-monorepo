# Secondary SSH recovery — AGY-1497-10

## Verified and deployed

The operator manually ran `termux-wake-lock` and `sshd`. An initial connection still closed before host verification; a subsequent connection succeeded over the existing route. Strict SSH verification matched the pre-existing pinned ED25519 key, then the local marker matched **tmx-node-55619bd5**, with the expected Termux account and B160V model. No connection to damaged-screen Origin (`tmx-node-primary`) was made.

Installed `termux-services` 0.13-1 and dependency `runit` 2.3.1 from the configured Termux mirror. No unrelated packages were upgraded. The dedicated service is **tmx-secondary-sshd**. The stock sshd service remains disabled and its definition was not overwritten.

In a new Termux zsh, run `reconnect`. In an already-open shell, run `~/.local/bin/tmx-reconnect`. This requests WakeLock, validates SSH configuration, sources the official service-start profile, raises the dedicated service with `sv-enable`, and reports state. It never kills processes, restarts all services, regenerates keys, edits Tailscale, or invokes a model. The installer preserved `.zshrc` and appended one marked alias block.

## Recovery is armed; manual SSH was not killed

A foreground runit wrapper waits for existing same-account processes named exactly `sshd` to exit, checking every five seconds. It excludes `sshd-session` children and sends no signals. When the manual listener exits, it validates configuration and execs `sshd -D -e`; runit subsequently restarts that foreground child after exit, with a five-second finish backoff.

Observed: wrapper and logger running, original manual listener PID unchanged, repeated reconnect successful, fresh pinned SSH connection successful. The log states **“Manual sshd present; non-killing recovery armed (not yet a supervised listener).”** No deliberate live crash, listener termination, or reboot was performed. Mocked Linux takeover tests are not an Android live-crash test.

Logs: `$PREFIX/var/log/sv/tmx-secondary-sshd/current`. `svlogd` rotates near 64 KiB and keeps at most two archived files; this is a threshold, not an absolute byte ceiling. State: `~/.local/state/tmx-secondary-recovery/listener-state`. Check `sv status "$PREFIX/var/service/tmx-secondary-sshd"` and a fresh SSH connection; state text alone is not listener proof.

## Boot and Android limits

Installed executable `~/.termux/boot/10-tmx-secondary-services`: WakeLock first, secondary identity guards, source `$PREFIX/etc/profile.d/start-services.sh`, then reconnect helper. It does not launch an agent or connect to another device.

`pm list packages --user 0 com.termux.boot` confirmed **Termux:Boot is installed**. First-launch activation could not be verified here. The owner must open **Termux:Boot once on the secondary**, if not already done. No app installation or ADB access is needed for that step. Reboot delivery remains untested.

WakeLock and “2 sessions” do not prove SSH is listening. WakeLock reduces CPU sleep; it does not prevent Android force-stop or process-group killing. This supervisor recovers an exited SSH child while Termux/runit survives; it cannot guarantee recovery when Android kills the whole app. Tailscale settings are unchanged.

## No supported historical crash diagnosis

At recheck, the known secondary peer was online, the controller's Tailscale backend was Running, SOCKS connection to port 8022 succeeded, and SSH subsequently authenticated. Prior refusals/closures were before authentication. No historical phone log establishes whether Tailscale, SSH, Android background handling, or another transient condition caused the earlier outage. Do not claim Tailscale never crashed or WakeLock fixed the cause.

## High restored; approval unchanged

Fresh inspection still found Low. The already-authorized AGY-1497-09 helper strictly validated the settings on the controller, prepared a candidate changing only the top-level verbosity value, and installed it with before/after hash checks and a private rollback snapshot. Re-reading the whole file matched the candidate exactly. Values now: `verbosity: high`, `toolPermission: always-proceed`, `artifactReviewPolicy: agent-decides`. All unrelated bytes were preserved. No CLI/model prompt was run. This supersedes older Low-status observations; telemetry/discovery and other earlier gaps remain unresolved.

## Tests and review

Thirteen deterministic Linux fixture tests passed before deployment, plus Bash syntax on all four recovery assets. Cases: wrong node/account/model/prefix; symlink marker/target rejection; separately enabled stock service rejection; idempotent installation; unrelated `.zshrc` preservation; repeated non-killing reconnect; Boot ordering; manual-daemon wait; foreground SSH execution. Fixtures mock Android/process/service commands and make no network calls or signals.

Self-review caught installer-lock inheritance: the lock is released and its descriptor closed before starting background services. No extra reviewer/model request was made. Native checks passed syntax, SSH configuration, service startup, log reading, alias resolution in a fresh interactive zsh, and subsequent pinned SSH access. Broader gate results are in the continuation receipt in OPERATIONAL-VALIDATION.md. PR #1514 stays open/unmerged; proposal stays in progress.

## Rollback

Private snapshots: `~/.local/state/tmx-secondary-recovery/install-before.*`; installer prints the exact directory. Settings rollback snapshot is under `~/.local/share/agy-1497-secondary/`. Never commit these or private settings/access configuration.

While the wrapper is still waiting for manual SSH, `sv-disable tmx-secondary-sshd` stops/disables only that wrapper. **After takeover this stops the supervised SSH listener and may remove remote access**: arrange local Termux/alternative access first. Remove only the dedicated Boot hook, marked alias block, helper and dedicated service. Preserve unrelated boot scripts, stock services, keys and logs. Compare snapshots before restoring over newer edits. Keep approved High unless separately asked to revert. Leave the installed packages unless removal is requested; later work may share them.

## Official guidance

[Termux:Boot](https://github.com/termux/termux-boot#readme): launch once, boot directory, WakeLock first and service-start profile. [termux-services](https://github.com/termux/termux-services/blob/master/README.md): runit, sv-enable and service logs. [Tailscale SSH](https://tailscale.com/kb/1193/tailscale-ssh) is distinct from ordinary Termux OpenSSH over the existing Android tailnet route.
