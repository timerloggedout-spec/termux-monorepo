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

## TUI Mode

A terminal interface with conversation tree and fork selection.

```bash
cd ~/deepcli-tui
./tui.py
