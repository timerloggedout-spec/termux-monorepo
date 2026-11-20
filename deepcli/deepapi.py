#!/usr/bin/env python3
"""
deepapi.py – Thin Python wrapper around deepterm-core.js.
Uses a persistent Node.js subprocess for all API calls.
"""
import json, subprocess, os, time, sys
from pathlib import Path
from typing import Optional, List, Dict, Any

DEEPTERM_DIR = Path.home() / "deepseek-cli" / "deepterm"
BRIDGE_SCRIPT = DEEPTERM_DIR / "bridge.js"

# Write the Node.js bridge if it doesn't exist
BRIDGE_SCRIPT.parent.mkdir(parents=True, exist_ok=True)
if not BRIDGE_SCRIPT.exists():
    BRIDGE_SCRIPT.write_text("""\
import { getCurrentProfile, createChatSession, fetchAllChatSessions,
         fetchHistoryMessages, completion, uploadFile, getFileUrl,
         deleteAllChatSessions } from './deepterm-core.js';

const TOKEN = process.argv[2];

function respond(data) {
    process.stdout.write(JSON.stringify(data) + '\\n');
}

async function handle(cmd) {
    try {
        switch (cmd.action) {
            case 'auth':
                return respond(await getCurrentProfile(TOKEN));
            case 'create_session':
                return respond(await createChatSession(TOKEN));
            case 'list_sessions':
                return respond(await fetchAllChatSessions(TOKEN));
            case 'history': {
                const msgs = await fetchHistoryMessages(TOKEN, cmd.session_id);
                return respond(msgs);
            }
            case 'send': {
                const gen = completion(TOKEN, cmd.prompt, cmd.session_id,
                    cmd.parent_message_id, true, cmd.search_enabled || false,
                    cmd.thinking_enabled || false, cmd.file_ids || []);
                for await (const chunk of gen) {
                    if (typeof chunk === 'string') {
                        process.stdout.write(chunk);
                    } else {
                        respond(chunk);
                    }
                }
                process.stdout.write('\\n__END_STREAM__\\n');
                return;
            }
            case 'upload': {
                const result = await uploadFile(TOKEN, cmd.session_id, cmd.file_path);
                return respond(result);
            }
            case 'file_status': {
                const result = await getFileUrl(TOKEN, cmd.session_id, cmd.file_id);
                return respond(result);
            }
            case 'delete_sessions':
                return respond(await deleteAllChatSessions(TOKEN, cmd.session_id));
            default:
                respond({error: 'Unknown action: ' + cmd.action});
        }
    } catch (e) {
        respond({error: e.message});
    }
}

process.stdin.on('data', (chunk) => {
    const lines = chunk.toString().trim().split('\\n');
    for (const line of lines) {
        if (!line) continue;
        try { handle(JSON.parse(line)); } catch(e) { respond({error: e.message}); }
    }
});
""")

class DeepAPI:
    def __init__(self, token: str):
        self.token = token
        self.proc = None

    def _start(self):
        if self.proc is not None and self.proc.poll() is None:
            return
        self.proc = subprocess.Popen(
            ["node", str(BRIDGE_SCRIPT), self.token],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True, bufsize=1
        )

    def _call(self, action: str, **kwargs) -> Dict[str, Any]:
        self._start()
        payload = {"action": action, **kwargs}
        self.proc.stdin.write(json.dumps(payload) + "\n")
        self.proc.stdin.flush()
        line = self.proc.stdout.readline()
        if not line:
            raise RuntimeError("Bridge process died")
        return json.loads(line)

    def auth(self) -> dict:
        return self._call("auth")

    def create_session(self) -> str:
        resp = self._call("create_session")
        return resp.get("data", {}).get("biz_data", {}).get("id")

    def list_sessions(self) -> list:
        resp = self._call("list_sessions")
        return resp.get("data", {}).get("biz_data", {}).get("chat_sessions", [])

    def get_history(self, session_id: str) -> list:
        resp = self._call("history", session_id=session_id)
        return resp.get("data", {}).get("biz_data", {}).get("chat_messages", [])

    def send_message(self, prompt: str, session_id: str,
                     parent_message_id: str,
                     thinking: bool = False, search: bool = False,
                     file_ids: List[str] = None) -> str:
        self._start()
        payload = {
            "action": "send",
            "prompt": prompt,
            "session_id": session_id,
            "parent_message_id": parent_message_id,
            "thinking_enabled": thinking,
            "search_enabled": search,
            "file_ids": file_ids or []
        }
        self.proc.stdin.write(json.dumps(payload) + "\n")
        self.proc.stdin.flush()
        response = ""
        while True:
            chunk = self.proc.stdout.read(1)
            if not chunk:
                break
            response += chunk
            if response.endswith("\n__END_STREAM__\n"):
                response = response[:-len("\n__END_STREAM__\n")]
                break
            print(chunk, end="", flush=True)
        return response.strip()

    def upload_file(self, session_id: str, file_path: str) -> Optional[str]:
        resp = self._call("upload", session_id=session_id, file_path=file_path)
        return resp.get("data", {}).get("biz_data", {}).get("id")

    def close(self):
        if self.proc:
            self.proc.terminate()
            self.proc = None
