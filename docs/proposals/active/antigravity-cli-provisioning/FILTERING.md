# Full diagnostics, concise steering — #1497

The owner chose a programmatic filtering layer, not low CLI verbosity. The verified saved setting is `verbosity: high`, with the existing `toolPermission: always-proceed` and `artifactReviewPolicy: agent-decides` unchanged. `capture.py` and `telemetry.py` are passive consumers: they never launch the CLI. The separate opt-in `run.py` wrapper launches only an explicitly supplied command once; it has no default producer, retries, settings changes, model switching, quota probes or scheduler.

## Private capture artifacts

`scripts/antigravity/capture.py` reads an existing stream-json capture or a producer's already-authorized stdout. It creates a **new** private run directory (0700), with files restricted to 0600:

- `stream.ndjson`: every input byte verbatim, including malformed and oversized events.
- `record.json`: allowlisted final-result metadata and usage, without prompt/response/tool payloads.
- `events.ndjson`: schema-versioned allowlisted events flushed as source lines arrive, followed by a terminal run summary.
- `steering.txt`: exactly three lines for the collaborator view. The same view is printed to stdout.
- `diagnostics.stderr`: optional verbatim copy of an existing producer stderr file supplied with `--diagnostics`.

Raw diagnostics remain available privately. Never replace them with the lossy normalized record or publish them in GitHub. Use an existing private parent directory outside the repository, and normal local retention/storage controls; this utility does not rotate, truncate or delete raw captures. Archiving requires enough disk space. An I/O error stops with exit 3 rather than claiming a complete capture.

`events.ndjson` contains only the v1 allowlisted projection; it excludes prompt/response text, paths, conversation IDs, tool arguments/results, and unknown source fields. Each record is flushed before the reader requests the next source chunk. Step usage is explicitly non-authoritative and never summed; the final summary uses terminal `result.usage`. See [TELEMETRY-PIPELINE.md](TELEMETRY-PIPELINE.md) for schema versions, the disabled-by-default Hindsight outbox, encrypted archives, and current issue mapping.

## Replay existing data only

From the repository root, with Python 3 available:

```bash
# PRIVATE_PARENT exists outside the repository; RUN_ID is new and non-secret.
python3 scripts/antigravity/capture.py \
  --capture-dir "$PRIVATE_PARENT/$RUN_ID" --run-id "$RUN_ID" \
  --diagnostics "$EXISTING_STDERR_FILE" < "$EXISTING_STREAM_JSON"
```

Omit `--diagnostics` only when there is no separate stderr capture. This command does not invoke `agy`. Do not re-run the successful pilot or submit another prompt to test filtering. Retain the producer's own exit code independently; filter exit 0 means a terminal result was parsed, **not** that the producer succeeded. Missing final result yields `INCOMPLETE`, unknown tokens and exit 2. An explicit failure remains visible in `RUN` and the record.

The parser reads final `result.usage` only; step snapshots and repeated result events are not added. Unknown fields stay unknown, including dollars and remaining quota. Model identity must be supplied explicitly or observed in `init`. Arbitrary input text is not a confidentiality classifier: use non-secret model/account/run identifiers and share only the fixed steering output after review.

Optional manual `/usage` observations require `source: manual:/usage`, exact model, matching explicit non-secret `account_scope`, timestamp and remaining/unit. Supply them with `--model`, `--account-scope` and `--quota`. They are separate evidence, not deductions from token counts. Observations older than 15 minutes or past a supplied reset are stale; 15 minutes is a local display policy, not a provider quota window. No router quota counters are modified. Any error reading or validating the quota file (unreadable file, size exceeding 1 MiB, deep JSON nesting, non-object JSON, or non-finite constants) causes immediate exit code 64 without creating the capture directory, consuming input stream, or printing a Python traceback; this is distinct from missing terminal result (exit code 2 / `INCOMPLETE`).

The parser limits each event candidate to 1 MiB and metadata strings to bounded lengths. The capture layer continues preserving oversized events while dropping them from parsing; invalid UTF-8/JSON events are counted, never echoed to the steering view. Memory is bounded by the event limit plus small read buffers; disk capture is deliberately complete, not size-bounded.

## One end-to-end command for a future authorized task

**Do not execute this example as a test.** The wrapper is not authorization to spend quota or send a prompt to a device. Use it only after the owner authorizes that particular task. Run on the controller with Python 3, an existing private parent outside Git, a fresh run ID, sufficient disk space, and the existing pinned `termux-device2` SSH alias. `AUTHORIZED_PROMPT_FILE` contains only the approved task; it stays on the controller and is sent on SSH stdin, not copied to a phone file. The remote shell reads it into the CLI argument without evaluating its content. It strips trailing newlines, so this lane is for task text, not exact-byte prompt transport.

```bash
python3 scripts/antigravity/run.py \
  --capture-dir "$PRIVATE_PARENT/$RUN_ID" --run-id "$RUN_ID" \
  --account-scope secondary-owner -- \
  ssh -T -o BatchMode=yes -o StrictHostKeyChecking=yes termux-device2 '
    set -eu
    cd "$HOME/.local/share/agy-1497-secondary/worktree"
    test -f .git && test ! -L .git
    test -f .agy-secondary-id && test ! -L .agy-secondary-id
    test "$(cat .agy-secondary-id)" = tmx-node-55619bd5
    test "$(whoami)" = u0_a243
    test "$(getprop ro.product.model)" = B160V
    prompt=$(cat)
    test -n "$prompt"
    export AGY_CLI_DISABLE_AUTO_UPDATE=true
    exec "$HOME/.local/bin/agy" --agent agy-implementer \
      --print-timeout 90s --output-format stream-json --print "$prompt"
  ' < "$AUTHORIZED_PROMPT_FILE"
```

The alias already pins the known host key, account, identity file and existing SOCKS route. Do not recreate it from an IP, bypass host-key checking, or substitute Origin. Local marker/account/model guards corroborate that pin; they are not a sandbox or replacement for host authentication. No Python or filter source is installed on the phone. No permission or verbosity flags are supplied, so the saved High and approval policies remain intact. No new model choice is made: model identity remains UNKNOWN unless actually emitted in `init` or supplied as observed metadata with the wrapper's `--model` (that option does **not** change the producer's model).

`run.py` creates the private raw stream, stderr, event, final-record, and steering artifacts; stderr is captured directly from process start to a file rather than a pipe or terminal. It consumes stdout while the producer runs and emits exactly three steering lines after completion. Raw stdout is never forwarded. `record.json` additionally retains `producer_exit_code` (negative for a signal), or a bounded launch-error class and null exit code when launch failed. The first steering line shows the reported CLI status **and** process exit separately; a SUCCESS event followed by SSH failure is not reported as overall success.

Runner exit policy: invalid, unreadable, oversized, deeply nested, non-object or non-finite quota JSON is rejected before producer launch/capture with exit 64; nonzero producer exit is preserved (signals map to 128 + signal); producer exit 0 plus SUCCESS returns 0; exit 0 without a result returns 2; exit 0 with any other status returns 1; launch/archive failure returns 3. These codes can overlap producer codes: use the private record to distinguish them. On archive failure/interruption, the local producer group is stopped without retry; partial archives are not completion proof. Stopping local SSH cannot guarantee cancellation of an already-started remote task. Inspect before any later retry. The wrapper does not impose a new timer; the example uses the documented CLI timeout.

The [official headless documentation](https://antigravity.google/docs/cli/headless/) confirms stdout/stderr separation, `--print`, NDJSON `init` / `step_update` / `result`, final `result.usage`, optional model identity and settings-based permissions. Multi-turn stdin mode exists in the current docs, but is not required by this command or claimed tested on installed 1.4.5. Its usage counters are cumulative: the adapter retains the **last** result, never sums snapshots or repeated results. Manual `/usage` is a separate observation (not a stream prompt); router invocation counters are neither populated nor modified. No dollars or remaining quota are inferred from tokens.

## Device 2 correction and deployment

Only the pinned secondary `tmx-node-55619bd5` is authorized. Origin (`tmx-node-primary`) and its backup remain excluded. Verify the existing pinned SSH host key and canonical mapping **before any transfer or write**. A copied marker alone is not authentication.

After identity verification, privately capture the current settings on the controller, then generate a byte-preserving candidate with strict JSON validation:

```bash
python3 scripts/antigravity/settings.py \
  --input "$PRIVATE_SETTINGS_CAPTURE" --output "$PRIVATE_CANDIDATE"
```

This requires actual top-level `verbosity`, `toolPermission` and `artifactReviewPolicy` keys, rejects duplicates/malformed JSON, and checks that both auto-approve values are already enabled. It replaces only the actual top-level `low` value with `high`, preserving every other byte (or returns unchanged bytes if already High). An unrelated nested key or quoted string cannot masquerade as the setting. Only before/after SHA-256 receipts are printed, never settings content.

Transfer the validated candidate privately to `$HOME/.local/share/agy-1497-secondary/verbosity-high.candidate.json`, then from the existing dedicated linked worktree on the verified secondary:

```bash
bash scripts/antigravity/secondary_settings.sh check
# Use the exact digests returned by settings.py; never hand-construct a candidate.
bash scripts/antigravity/secondary_settings.sh apply "$BEFORE_SHA256" "$AFTER_SHA256"
```

`check` verifies local identity guards and prints only the current settings hash; it does not claim to parse or verify High. `apply` requires the exact workspace, marker, Android model/account and hash-pinned validated candidate. It rejects symlinks, stale settings and altered candidates, retains a private rollback snapshot, preserves file permissions and verifies the installed candidate hash. Shell alone does not validate JSON: the controller preparation and its exact receipts are mandatory. Re-read and JSON-validate the installed settings on the controller after applying, comparing the complete candidate hash. Coordinate with interactive settings editors; the helper detects changes before replacement but the CLI does not share its lock.

The secondary's previous inspection found no Python on PATH. The Python filter may run in the controller workspace against an existing secondary capture without installing software on the phone. Do not claim native filter execution or install a runtime without a separate deliberate boundary. Source transfer, High-setting verification and use against a real existing capture must be reported separately from offline fixtures.

## Current delivery boundary

Repository integration is authorized in open PR #1514, whose live head is `cue/1497-operational-device2`, targeting `master-staging`. The older `cue/1497-antigravity-provisioning` branch is not the live PR head. No merge is authorized.

The later [secondary recovery receipt](SECONDARY-RECOVERY.md) supersedes the earlier offline/Low observations: pinned secondary identity, High restoration, unchanged auto-approve, a supervised SSH-child restart and fresh pinned reconnect were verified. The owner then authorized one bounded implementer and one sequential verifier in the live secondary project. Their real stream-json output was captured by the controller filter. The implementer stream is INCOMPLETE at transport exit 255, with unknown model/token totals; the verifier completed but its PASS missed a deterministic quota regression. No reliable production-task success is claimed. This controller repair makes no new phone connection, model request or settings change. Boot first-launch activation, boot delivery/reboot, native discovery/internal restrictions, nested delegation and full provisioning remain gaps. See [FILTERING-VALIDATION.md](FILTERING-VALIDATION.md) for separate receipts and executed checks; PR stays open and unmerged.
