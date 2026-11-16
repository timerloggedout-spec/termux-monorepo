./deepcli.py new

# Send a message (with streaming response)
./deepcli.py send "Explain quantum computing"

# Send with thinking mode
./deepcli.py send "Write a Python script" --thinking

# Attach files
./deepcli.py send "Summarize this document" --attach report.pdf

# List sessions
./deepcli.py list

# View conversation history
./deepcli.py history --session <session_id>

# Export to JSON
./deepcli.py export --format json --output chat.json

# Fork a conversation
./deepcli.py fork --session <source_id> --message-id <msg_id>

## Hindsight API (server.py)

When `server.py` is running (port 8800), the Hindsight memory tools are
exposed over HTTP:

- `GET  /v1/hindsight/tools`  - list registered retain/recall/reflect tool specs
- `GET  /v1/hindsight/health` - endpoint + bank + routed-lane status
- `GET  /v1/hindsight/router` - circuit-breaker / lane health
- `POST /v1/hindsight/invoke` - call one tool by name

Invoke example:

```bash
curl -s localhost:8800/v1/hindsight/invoke \
  -H 'Content-Type: application/json' \
  -d '{"tool":"hindsight_recall","args":{"query":"fly.io quota"}}'
```

Returns `{"tool": <name>, "ok": true, "result": {...}}`. Unknown tool -> 404;
malformed `args` -> 400. Semantics match the in-process deepagent tool path.

## TUI Mode

A terminal interface with conversation tree and fork selection.

```bash
cd ~/deepcli-tui
./tui.py
