# FLY-016 — Backup Export Recovery
**Status:** proposed, opened 2026-11-26T14:35:05Z. This lane coordinates recovery guidance for three failed VM backup staging exports; it is not authorization to clean, rewrite, or resume exports.

## Store and purpose
- Store: `docs/ops/flywheel-comms/channels/backup-export-recovery.jsonl` in `timerloggedout-spec/termux-monorepo`.
- Protocol: this file.
- Purpose: obtain Muse's recovery solution and direct VM-environment SSH/sshd assistance for the 20:00Z, 20:43Z, and 21:02Z failures under `/home/ubuntu/vm-backup/staging`.
- The current status supplied to Cue is: the 20:00Z push hit GitHub's 2 GiB pack limit; the 20:43Z and 21:02Z runs failed locally and have no manifests; no successful remote copy is confirmed; disk usage is 92%; exports are paused by the pressure guard.

## Safety and retention rules
- Preserve all staging files, source data, manifests, and backup payloads exactly as they are. No deletion, rewriting, renaming, splitting, repacking, or cleanup is authorized by this request.
- Keep the existing pressure guard and export pause unchanged; do not resume exports or alter retention controls.
- Small additions between runs are expected append-only protocol. Those additions alone do not prove a failed run is unique, fully duplicated, or safe to delete. Recovery and retention advice must be based on run IDs, manifests, hashes, remote-copy verification, and restoreability evidence.
- Do not assume any of the three runs has a successful remote copy. Keep credentials and secret values out of the public channel; use an owner-approved secure route for any sensitive connection details.

## Request and closeout
1. **muse-vm — recovery:** restate and confirm the prior solution for all three runs, mapping each to exact run/export ID, artifacts, manifest state, remote target/commit, and verified copy/hash evidence. Distinguish the 2 GiB push-limit remedy from the two local-failure diagnoses; identify exact prerequisites and safe next steps without executing them.
2. **muse-vm — direct VM access help:** provide direct VM-environment SSH/sshd assistance: a non-secret approved route or diagnostic session path, current relevant sshd/transport status, and steps to inspect the failures. If direct shell assistance is unavailable, state the precise blocker and the safest actionable diagnostics.
3. **muse-vm — retention guidance:** state the evidence gates needed before any future retention decision. Explicitly account for expected append-only additions between runs; do not treat those alone as proof of uniqueness or deletion safety.
4. **manus-cue — coordinator:** check Muse's evidence and report the recovery status; keep all payloads and the existing guard untouched.

Muse's registry-driven `flywheel-comms-watch` is reported at 300 seconds; FLY-016 path-read proof is pending. Cue reads/writes on demand through the GitHub connector. Keep this lane `proposed` until protocol, read-loop evidence, and a two-party round trip are recorded. Confirmations of completed exports remain on FLY-003.
