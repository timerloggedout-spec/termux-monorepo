# DeepSeek Web Continue Contract — Verified 2026-09-29

## Summary
`/api/v0/chat/completion` returns an SSE stream that can end without a
`FINISHED` marker when the upstream model pauses for token budget, quota,
or a server-side interruption. The web UI surfaces this as a **Continue**
button. The API equivalent is a second POST to `/api/v0/chat/continue`,
carrying the same `chat_session_id` and the `message_id` of the assistant
turn that was cut off.

## Endpoint
    POST https://chat.deepseek.com/api/v0/chat/continue
    Headers:
      Authorization: Bearer <token>
      Content-Type: application/json
      Accept: text/event-stream
      X-Ds-Pow-Response: <pow for target_path=/api/v0/chat/continue>
    Body:
      {"chat_session_id": "<uuid>", "message_id": <int>}
    Response: SSE, same frame grammar as /chat/completion

## PoW
Continue is in the PoW-protected set. The challenge must be requested with
`target_path=/api/v0/chat/continue` — a completion-scoped PoW will be rejected.

## Body shape evolution
Some upstream proxies send `{"message_id": <int>}` only (session inferred);
canonical web client sends `chat_session_id` + `message_id` together. Always
send both.

## Why not retry /chat/completion?
Completion creates a **new** assistant message. Retrying orphans the partial
reply and desyncs the session history used for parent_message_id chaining.
Continue **appends** to the same message_id.

## Implementation location
    ~/deepcli/deepcli/core.py
        get_last_assistant_message_id(token, session_id) -> int | None
        continue_completion(token, session_id, message_id, thinking=False) -> str

## Sandbox + promotion
All mutations to core.py flow through:
    ~/deepcli/scripts/core-continue-sandbox.sh      (build)
    ~/deepcli/scripts/promote-with-validation.sh    (validated promote)
Rollback is automatic on AST failure or server-unreadiness.

## Sources (verified 2026-09-29)
1. LLM-Red-Team/deepseek-free-api — body shape `{"message_id": data.get(...)}`
   for the continue call; drives the "response message ID to continue" claim.
2. DeepSeeker userscript (qt-kaneko) — endpoint whitelist confirms
   `/api/v0/chat/continue` alongside completion, regenerate, resume_stream.
3. Fundiman/dskpp — SSE frame tracking of `message_ids` per chat_session_id,
   used as the resume target.
4. sums001/Deepseek-API — snapshot-frame extraction of `message_id`;
   `session_id:message_id` treated as resume token.
5. HsiangNianian/dsh-auto-continue (v0.11.4) — retry classification:
   transient (network/5xx/429) → continue; permanent (401/403/auth/
   unknown-model/context-length) → skip. Grace period on self-recovery.
6. qwert702/dsh-continue-on-limit — detection of `turn-max-tokens` node;
   re-prompt with `continue` text through the queue.
7. haochi72/dsh-auto-continue-429 — 20-consecutive-failure cap per session.

## Prior bugs resolved by this contract
- `body_preview = resp.text[:200]` on a streamed response buffered the whole
  body → infinite block. Replaced with post-stream check on `raw[:800]`.
- `chat_completion(auto_continue=True)` was a no-op; retries re-posted
  completion instead of continuing. Now routes to continue_completion.

## Operational rules
1. Never promote core.py without a passing smoke test.
2. Never `sleep N` after servers-up; use `wait-ready`.
3. Never edit live; always sandbox + promote.
4. Backups are timestamped; the newest backup is the pre-promote state.
