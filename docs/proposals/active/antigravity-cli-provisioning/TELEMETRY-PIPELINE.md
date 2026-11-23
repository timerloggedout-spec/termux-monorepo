# Issue #1497 status map: streaming telemetry, Hindsight, and encrypted archives

## What this follow-up covers

This is a controller-side follow-up in [PR #1514](https://github.com/timerloggedout-spec/termux-monorepo/pull/1514) for [issue #1497](https://github.com/timerloggedout-spec/termux-monorepo/issues/1497). It implements the requested event filtering, privacy boundary, versioned archive, and a future Hindsight outbox. It does not ask the on-device `agy` agent to wire itself, and it does not create a new Device 2 connection or model request.

| Issue #1497 lane | Current implementation in the PR branch | Live/deployed status |
|---|---|---|
| SSH-run the Termux CLI explicitly | `scripts/antigravity/run.py` launches only the exact command after `--`; existing examples use the pinned `termux-device2` SSH alias and stream stdout back to the controller. No default task or retry was added. | The existing wrapper and earlier capture are documented. This follow-up does not invoke SSH, change Termux, or establish a background service. |
| Keep full diagnostics private while showing concise steering | Raw stdout and stderr remain in private 0700/0600 capture files; the three-line steering output remains unchanged. `events.ndjson` adds sanitized event records alongside (not instead of) the raw stream. | Code path is implemented on this branch. No new Device 2 stream was captured. |
| Feed event usage immediately into telemetry | Each complete NDJSON event is projected to the v1 allowlist and flushed before the reader asks for the next source chunk. It keeps sequence numbers, valid/malformed counts, safe tool-step names, and step/final usage roles. | Synthetic streaming fixtures pass. There is no continuous phone-side or background feed deployed. |
| Account for usage correctly | `step_update.usage` is marked `non_authoritative_step_snapshot`; it is never summed. The final aggregate uses terminal `result.usage` only. Manual `/usage` quota remains separate, and no dollar cost or remaining quota is inferred. | Implemented in the controller parser; no new real run or usage data was produced. |
| Send telemetry to Hindsight | `hindsight_outbox.py` only accepts the allowlisted aggregate, requires explicit human review, and queues locally with a stable per-run `document_id`. It sends only after an explicit `deliver --enable-hindsight --reviewed`; duplicate payloads are squashed, revisions use append, and ambiguous acknowledgements are held for an explicit same-`operation_id` retry. | Opt-in code only. No endpoint or API credential is configured, and no Hindsight request or user data was sent. |
| Archive privately for later schema comparison | `archive.py` streams a private file through `age`, placing archive/schema versions and payload hash/length inside the encrypted envelope. `decrypt` streams to stdout/a consumer; `compare` decrypts to a discard sink and compares versions/hashes without writing plaintext. | Synthetic fake-age fixtures pass. No real recipient/identity key or encrypted payload exists. Runtime activation is blocked until the owner supplies an external recipient key; decryption also requires the external private identity and installed `age`. |
| Store larger ciphertext | Git LFS may store already-encrypted ciphertext as an optional large-object transport. | Not configured or used. LFS pointer/blob management is not confidentiality; plaintext must never be sent to LFS. |
| Origin's DeepSeek wrapper/export pipeline | A future adapter boundary can be documented after this lane is reviewed. | Not connected or copied. |
| Collab | Separate lane. | Not implemented here. |

## Streaming and privacy contract

The Google [headless CLI documentation](https://antigravity.google/docs/cli/headless/) describes the `init`, `step_update`, and terminal `result` stream events. `events.ndjson` uses [telemetry-event-v1.schema.json](../../../../schemas/antigravity/telemetry-event-v1.schema.json). It can contain only the bounded model label, step index/type/state, safe canonical tool name, durations, token counters, categorical status, and malformed-event reason. It excludes conversation IDs, working paths, prompt/response text, tool arguments/results, tool errors, subagent contents, and unknown source fields. Full raw stream and stderr remain private local diagnostics.

Local event rows are emitted while reading the source. The final run-summary row is appended after termination and marks the last `result.usage` as the authoritative run total. `event_count` counts valid JSON objects; malformed candidates are counted separately. Repeated terminal results remain separate event rows for audit, but the final record selects the last one and never adds repeated totals together.

This is not a local accounting database replacement. Hindsight `retain` extracts facts from submitted text using an LLM, as described in its [retain documentation](https://hindsight.vectorize.io/developer/api/retain); Hindsight is not a precise token ledger. The outbox payload conforms to [hindsight-summary-v1.schema.json](../../../../schemas/antigravity/hindsight-summary-v1.schema.json) and submits only an aggregate JSON summary after review, not each live event or any raw stream. The Hindsight [quickstart](https://hindsight.vectorize.io/developer/api/quickstart) requires an LLM provider configuration, so any later activation needs separate owner consent for the endpoint, bank, model/provider, retention/privacy consequences, and potential extraction cost. Async acceptance is not processing completion; production use still needs an explicit operation-status review policy.

The outbox uses Hindsight's documented `document_id` upsert and `update_mode: append` behavior. A duplicate payload for the same run is a local no-op. A revised payload uses the same document ID and a deterministic UUID `operation_id`; the official docs state that retrying an async request with the same operation ID returns the existing operation rather than queuing duplicate work. The adapter marks an acknowledgement as `accepted`, not `completed`. Timeouts and missing/mismatched acknowledgements become `uncertain`; they are never retried automatically.

## Encrypted archive contract

The archive header is inside the encrypted plaintext envelope and conforms to [encrypted-archive-v1.schema.json](../../../../schemas/antigravity/encrypted-archive-v1.schema.json). The recipient comes only from `AGE_RECIPIENT`; decryption reads `AGE_IDENTITY_FILE`, rejects an identity in a Git worktree or with permissive mode bits, and pipes decrypted bytes directly to a chosen consumer or stdout. The script creates no plaintext temp file; a consumer must treat streamed input as provisional until it exits successfully. Test-only fake identities live only in temporary fixtures and are not valid encryption keys.

Use private storage paths outside the repository for ciphertext and any local manifests. Do not commit ciphertext, plaintext, payload hashes, manifests, transcripts, logs, tool data, recipient values, or identity files. Schema version and payload-hash comparison is local: `archive.py compare --left ... --right ...` verifies/decrypts both archives to a discard sink and prints only comparison metadata. The optional large-file documentation for [Git LFS](https://docs.github.com/repositories/working-with-files/managing-large-files/about-git-large-file-storage) describes pointer files and external blob storage; it does not provide encryption.

## Current evidence and remaining gate

The checked-out PR head at the start of this work was `dbb302b5aa4ac21d27de9e34bf16b22914076109`, open and unmerged. This implementation is still controller-side repository code; the earlier Device 2 implementer stream ended at SSH exit 255 without terminal usage, so its model/token totals remain unknown. Do not replay that stream or infer continuity from these local tests. Before any later push or activation, recheck the live PR head, review requests, checks, and storage; keep the PR open and unmerged unless the owner separately decides otherwise.

## Sources

- [Antigravity CLI headless and streaming JSON](https://antigravity.google/docs/cli/headless/)
- [Hindsight retain and async operation IDs](https://hindsight.vectorize.io/developer/api/retain)
- [Hindsight quickstart and LLM provider configuration](https://hindsight.vectorize.io/developer/api/quickstart)
- [Hindsight HTTP API reference](https://hindsight.vectorize.io/api-reference)
- [age project and command-line interface](https://github.com/FiloSottile/age)
- [GitHub: About Git Large File Storage](https://docs.github.com/repositories/working-with-files/managing-large-files/about-git-large-file-storage)
