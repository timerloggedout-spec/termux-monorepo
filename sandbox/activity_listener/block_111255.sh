python3 << 'PYEOF'
import pathlib
p = pathlib.Path.home() / 'deepcli/deepcli/core.py'
src = p.read_text()

# Fix send_message: add thinking_enabled and search_enabled to the payload
old_send = """    payload = {
        'chat_session_id': session_id,
        'parent_message_id': parent_message_id,
        'prompt': prompt,
        'ref_file_ids': [],
        'stream': False,
    }"""
new_send = """    payload = {
        'chat_session_id': session_id,
        'parent_message_id': parent_message_id,
        'prompt': prompt,
        'ref_file_ids': [],
        'thinking_enabled': False,
        'search_enabled': False,
        'stream': False,
    }"""
src = src.replace(old_send, new_send)

# Also add a fallback in stream_completion for accounts without expert access
# Find the error handling block and add the fallback message
old_err = "console.print(f\"[red]API error {resp.status_code}: {body}[/] retry in {delay:.1f}s\")"
new_err = """console.print(f\"[red]API error {resp.status_code}: {body}[/] retry in {delay:.1f}s\")
                # Fallback: if expert mode not available, force instant
                if 'expert' in body.lower() or 'upgrade' in body.lower():
                    console.print(\"[yellow]Expert mode unavailable — falling back to instant.[/]\")
                    # Force thinking/search off for instant mode
                    payload['thinking_enabled'] = False
                    payload['search_enabled'] = False"""
src = src.replace(old_err, new_err)

p.write_text(src)
print("send_message payload fixed; stream_completion fallback added.")
PYEOF