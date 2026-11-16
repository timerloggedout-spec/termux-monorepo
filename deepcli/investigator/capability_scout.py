#!/usr/bin/env python3
"""
capability_scout.py – Map curated DeepSeek capabilities to the source files
that implement them. Filters out dead HTML/screenshot artifacts.
"""

import re, os, json, argparse
from pathlib import Path
from collections import defaultdict

# ---- Curated capability definitions (from your blueprint) ----
CAPABILITIES = {
    "auth": {
        "label": "Authentication",
        "endpoints": ["/api/v0/users/login", "/api/v0/users/current"],
        "keywords": ["userToken", "login", "cookies", "Profile"],
        "methods": ["login", "getToken", "refreshToken"],
    },
    "session": {
        "label": "Session Management",
        "endpoints": ["/api/v0/chat_session/create", "/api/v0/chat_session/fetch_page",
                      "/api/v0/chat_session/delete", "/api/v0/chat_session/update_title"],
        "keywords": ["chat_session", "sessionId", "createSession", "fetch_page", "deleteSession"],
        "methods": ["createSession", "listSessions", "deleteSession", "updateTitle"],
    },
    "chat_completion": {
        "label": "Chat & Messaging",
        "endpoints": ["/api/v0/chat/completion", "/api/v0/chat/history_messages"],
        "keywords": ["completion", "history_messages", "parent_message_id", "SSE", "stream", "sendMessage", "prompt"],
        "methods": ["sendMessage", "getHistory", "streamReply"],
    },
    "fork_share": {
        "label": "Fork & Share",
        "endpoints": ["/api/v0/share/create", "/api/v0/share/fork"],
        "keywords": ["share", "fork", "snapshot", "remix"],
        "methods": ["forkConversation", "createShare"],
    },
    "file_upload": {
        "label": "File Upload",
        "endpoints": ["/api/v0/file/upload_file", "/api/v0/file/fetch_files"],
        "keywords": ["upload_file", "file_id", "multipart", "attach", "waitForFileChooser"],
        "methods": ["uploadFile", "getFileUrl", "attachFile"],
    },
    "pow": {
        "label": "PoW Challenge",
        "endpoints": ["/api/v0/chat/create_pow_challenge"],
        "keywords": ["pow", "challenge", "DeepSeekHash", "solvePow"],
        "methods": ["solvePow", "createPowChallenge"],
    },
    "sse_stream": {
        "label": "SSE Stream Capture",
        "endpoints": ["/api/v0/chat/completion"],
        "keywords": ["SSE", "EventSource", "data:", "replace", "append", "monkey-patch", "fetch intercept", "stream"],
        "methods": ["setupRequestInterception", "onResponse"],
    },
    "auto_retry": {
        "label": "Auto-Retry on Busy",
        "endpoints": [],
        "keywords": ["retry", "重新生成", "server busy", "handleAutoRetry", "cooldown"],
        "methods": ["handleAutoRetry", "retry"],
    },
    "local_history": {
        "label": "Local Chat History",
        "endpoints": [],
        "keywords": ["chat-history.json", "saveChatHistory", "loadChatHistory", "message log", "timestamp"],
        "methods": ["saveChatHistory", "loadChatHistory"],
    },
    "system_prompt": {
        "label": "System Prompt Injection",
        "endpoints": [],
        "keywords": ["system_prompt", "system-prompt", "systemPrompt", "prepend", "instruction"],
        "methods": ["setSystemPrompt"],
    },
    "edit_resend": {
        "label": "Edit & Resend",
        "endpoints": [],
        "keywords": ["edit", "pencil", "update button", "resend"],
        "methods": ["editMessage"],
    },
    "loop_mode": {
        "label": "Loop Mode (stdin)",
        "endpoints": [],
        "keywords": ["loop", "stdin", "readline", "multiple prompts"],
        "methods": ["loop"],
    },
    "listing_sessions": {
        "label": "List Sessions",
        "endpoints": ["/api/v0/chat_session/fetch_page"],
        "keywords": ["list", "sidebar", "fetch_page"],
        "methods": ["listSessions"],
    },
    "expert_mode": {
        "label": "Expert Mode Enforcement",
        "endpoints": [],
        "keywords": ["expert", "data-model-type", "radio"],
        "methods": ["setExpertMode"],
    },
    "headless_browser": {
        "label": "Headless Browser Control",
        "endpoints": [],
        "keywords": ["puppeteer", "page.", "browser", "Termux:X11", "headless"],
        "methods": ["launch", "newPage"],
    },
    "wasm_pow": {
        "label": "WASM PoW Solver",
        "endpoints": [],
        "keywords": ["wasm", "deepseek.wasm", "initWasm", "solvePow"],
        "methods": ["initWasm", "solvePow"],
    },
    "deepterm_api": {
        "label": "DeepTerm API Server",
        "endpoints": ["/api/v0/*"],
        "keywords": ["express", "cors", "deepterm-api.js", "app.post", "app.get"],
        "methods": ["app.get", "app.post"],
    },
    "tui_tree": {
        "label": "TUI Tree Navigation",
        "endpoints": [],
        "keywords": ["build_tree_str", "choose_parent", "remix", "categories", "projects", "visual tree"],
        "methods": ["build_tree_str", "choose_parent", "remix"],
    },
    "code_harvest": {
        "label": "Code Harvesting",
        "endpoints": [],
        "keywords": ["harvest", "extract code", "CodeBlock", "parse_export", "deduplicate"],
        "methods": ["harvest", "parse_export", "deduplicate"],
    },
    "merge_batch": {
        "label": "Batch Merge / Cluster",
        "endpoints": [],
        "keywords": ["batch_merge", "cluster_blocks", "similarity", "DeepSeekSession", "remix"],
        "methods": ["batch_merge", "cluster_blocks"],
    },
}

# Files to skip (artifacts, screenshots, saved HTML)
SKIP_FILES = {
    'chat-page.html', 'footer-buttons.html', 'debug-page-html.txt',
    'debug-page-text.txt', 'debug-screenshot.png', 'debug-send.png',
    'debug2-screenshot.png', 'debug3-after-set.png', 'debug3-current.png',
    'detective-send.png', 'inspect-page.png', 'diag-screenshot.png',
    'cookies.json', 'test.txt'
}

IGNORE_DIRS = {'node_modules', '__pycache__', '.git', 'browser-data', 'code_harvest'}

def analyze_file(file_path):
    """Return set of capability keys matched in this file."""
    try:
        with open(file_path, 'r', errors='ignore') as f:
            content = f.read()
    except:
        return set()
    matched = set()
    lower = content.lower()
    for key, cap in CAPABILITIES.items():
        # Check endpoints in content
        for ep in cap['endpoints']:
            if ep.lower() in lower:
                matched.add(key)
                break
        else:
            # Check keywords
            for kw in cap['keywords']:
                if kw.lower() in lower:
                    matched.add(key)
                    break
            else:
                # Check method names
                for meth in cap['methods']:
                    if meth.lower() in lower:
                        matched.add(key)
                        break
    return matched

def main():
    parser = argparse.ArgumentParser(description='Map capabilities to source files')
    parser.add_argument('paths', nargs='*', default=['.'])
    parser.add_argument('--include', '-i', action='append', default=[])
    parser.add_argument('--output', '-o', choices=['text','json'], default='text')
    args = parser.parse_args()

    files_to_scan = set()
    for path in args.paths:
        p = Path(path).expanduser().resolve()
        if p.is_file():
            if p.name not in SKIP_FILES:
                files_to_scan.add(str(p))
        elif p.is_dir():
            for root, dirs, filenames in os.walk(p):
                dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
                for f in filenames:
                    if f in SKIP_FILES:
                        continue
                    files_to_scan.add(os.path.join(root, f))
    for inc in args.include:
        inc = os.path.expanduser(inc)
        if os.path.isfile(inc):
            files_to_scan.add(inc)

    # Map capability -> list of files
    cap_files = defaultdict(list)
    for f in sorted(files_to_scan):
        caps = analyze_file(f)
        for c in caps:
            cap_files[c].append(f)

    if args.output == 'json':
        out = {c: [os.path.basename(f) for f in fl] for c, fl in cap_files.items()}
        print(json.dumps(out, indent=2))
        return

    print("🧩 DeepSeek Capability ↔ File Map")
    print("=" * 60)
    for key, cap in CAPABILITIES.items():
        files = cap_files.get(key, [])
        print(f"\n📌 {cap['label']} ({key})")
        if files:
            for f in files:
                print(f"   📄 {os.path.basename(f)}")
        else:
            print("   ❌ No implementation found in scanned files")
    print("\n" + "=" * 60)
    print("✅ Summary of implemented capabilities:", len([k for k in CAPABILITIES if cap_files.get(k)]), "/", len(CAPABILITIES))
    missing = [k for k in CAPABILITIES if not cap_files.get(k)]
    if missing:
        print("🚧 Missing capabilities:", ', '.join(missing))
    else:
        print("🎉 All capabilities have at least one file matched.")

if __name__ == '__main__':
    main()
