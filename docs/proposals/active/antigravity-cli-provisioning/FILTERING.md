# Full diagnostics, concise steering — #1497

The owner chose a programmatic filtering layer, not low CLI verbosity. The desired saved setting is `verbosity: high`, with the existing `toolPermission: always-proceed` and `artifactReviewPolicy: agent-decides` unchanged. The filter is a passive consumer: it never launches the CLI, spends model quota, changes permissions, switches models, or schedules work.

## Three separate outputs

`scripts/antigravity/capture.py` reads an existing stream-json capture or a producer's already-authorized stdout. It creates a **new** private run directory (0700), with files restricted to 0600:

- `stream.ndjson`: every input byte verbatim, including malformed and oversized events.
- `record.json`: allowlisted final-result metadata and usage, without prompt/response/tool payloads.
- `steering.txt`: exactly three lines for the collaborator view. The same view is printed to stdout.
- `diagnostics.stderr`: optional verbatim copy of an existing producer stderr file supplied with `--diagnostics`.

Raw diagnostics remain available privately. Never replace them with the lossy normalized record or publish them in GitHub. Use an existing private parent directory outside the repository, and normal local retention/storage controls; this utility does not rotate, truncate or delete raw captures. Archiving requires enough disk space. An I/O error stops with exit 3 rather than claiming a complete capture.

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

Optional manual `/usage` observations require `source: manual:/usage`, exact model, matching explicit non-secret `account_scope`, timestamp and remaining/unit. Supply them with `--model`, `--account-scope` and `--quota`. They are separate evidence, not deductions from token counts. Observations older than 15 minutes or past a supplied reset are stale; 15 minutes is a local display policy, not a provider quota window. No router quota counters are modified.

The parser limits each event candidate to 1 MiB and metadata strings to bounded lengths. The capture layer continues preserving oversized events while dropping them from parsing; invalid UTF-8/JSON events are counted, never echoed to the steering view. Memory is bounded by the event limit plus small read buffers; disk capture is deliberately complete, not size-bounded.

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

Device 2 is currently offline on the existing tailnet route. No fresh device identity or settings read, settings write, source transfer, native filter run, or actual-device capture replay has succeeded in this follow-up. The settings discrepancy remains unresolved until that connection is restored. Offline tests are not evidence of device deployment. See [FILTERING-VALIDATION.md](FILTERING-VALIDATION.md) for executed checks and the exact remaining handoff.
