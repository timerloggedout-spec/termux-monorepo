#!/usr/bin/env python3
"""
capability_focus.py — Clean capability‑to‑source mapping.
Filters out test reports, backups, screenshots, HTML artifacts, etc.
Shows only primary implementation files for each capability.
"""

import re, os, json, argparse
from pathlib import Path
from collections import defaultdict

# ---- Capability definitions (same as before) ----
CAPABILITIES = {
    "auth": {"label": "Authentication", "keywords": ["userToken","login","getToken","/api/v0/users/current"]},
    "session": {"label": "Session Management", "keywords": ["chat_session","createSession","fetch_page","deleteSession","/api/v0/chat_session"]},
    "chat_completion": {"label": "Chat & Messaging", "keywords": ["completion","sendMessage","parent_message_id","/api/v0/chat/completion","history_messages"]},
    "fork_share": {"label": "Fork & Share", "keywords": ["share","fork","/api/v0/share"]},
    "file_upload": {"label": "File Upload", "keywords": ["upload_file","file_id","multipart","attach","waitForFileChooser","/api/v0/file"]},
    "pow": {"label": "PoW Challenge", "keywords": ["pow","challenge","solvePow","create_pow_challenge","/api/v0/chat/create_pow_challenge"]},
    "sse_stream": {"label": "SSE Stream Capture", "keywords": ["SSE","EventSource","data:","replace","append","monkey-patch","setupRequestInterception"]},
    "auto_retry": {"label": "Auto-Retry on Busy", "keywords": ["retry","handleAutoRetry","cooldown","重新生成"]},
    "local_history": {"label": "Local Chat History", "keywords": ["chat-history.json","saveChatHistory","loadChatHistory"]},
    "system_prompt": {"label": "System Prompt Injection", "keywords": ["system_prompt","systemPrompt","prepend"]},
    "edit_resend": {"label": "Edit & Resend", "keywords": ["edit","pencil","update button","resend"]},
    "loop_mode": {"label": "Loop Mode", "keywords": ["loop","stdin","readline","multiple prompts"]},
    "listing_sessions": {"label": "List Sessions", "keywords": ["list","sidebar","fetch_page"]},
    "expert_mode": {"label": "Expert Mode", "keywords": ["expert","data-model-type","radio"]},
    "headless_browser": {"label": "Headless Browser", "keywords": ["puppeteer","page.","browser","headless","launch"]},
    "wasm_pow": {"label": "WASM PoW Solver", "keywords": ["wasm","deepseek.wasm","initWasm","solvePow"]},
    "deepterm_api": {"label": "DeepTerm API Server", "keywords": ["express","cors","deepterm-api.js","app.post"]},
    "tui_tree": {"label": "TUI Tree Navigation", "keywords": ["build_tree_str","choose_parent","remix","categories"]},
    "code_harvest": {"label": "Code Harvesting", "keywords": ["harvest","parse_export","deduplicate","CodeBlock"]},
    "merge_batch": {"label": "Batch Merge", "keywords": ["batch_merge","cluster_blocks","similarity","DeepSeekSession"]},
}

# ---- Files to IGNORE ----
SKIP_EXTS = {'.png','.jpg','.gif','.txt','.json','.md','.html','.bak','.log','.yaml','.yml','.ini','.cfg','.conf'}
SKIP_NAMES = {'package.json','package-lock.json','README.md','LICENSE','.gitignore','chat-history.json','cookies.json','upload-api.json','pow-details.json','footer-elements.json','endpoint-intelligence.json','selector-intelligence.json','export.json'}
SKIP_DIRS = {'node_modules','__pycache__','.git','browser-data','code_harvest','test-reports','fixtures'}

def should_skip(filepath):
    name = os.path.basename(filepath)
    ext = os.path.splitext(name)[1].lower()
    if ext in SKIP_EXTS or name in SKIP_NAMES or name.endswith('.bak'):
        return True
    # skip any path containing test-reports or fixtures
    if '/test-reports/' in filepath or '/fixtures/' in filepath:
        return True
    return False

def analyze_file(filepath):
    try:
        with open(filepath, 'r', errors='ignore') as f:
            content = f.read().lower()
    except:
        return set()
    matched = set()
    for key, cap in CAPABILITIES.items():
        for kw in cap['keywords']:
            if kw.lower() in content:
                matched.add(key)
                break
    return matched

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('paths', nargs='*', default=['.'])
    parser.add_argument('--include', '-i', action='append', default=[])
    parser.add_argument('--output', '-o', choices=['text','json'], default='text')
    args = parser.parse_args()

    files_to_scan = set()
    for path in args.paths:
        p = Path(path).expanduser().resolve()
        if p.is_file():
            if not should_skip(str(p)):
                files_to_scan.add(str(p))
        elif p.is_dir():
            for root, dirs, filenames in os.walk(p):
                dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
                for f in filenames:
                    fp = os.path.join(root, f)
                    if not should_skip(fp):
                        files_to_scan.add(fp)
    for inc in args.include:
        inc = os.path.expanduser(inc)
        if os.path.isfile(inc) and not should_skip(inc):
            files_to_scan.add(inc)

    # Map capability -> source files
    cap_sources = defaultdict(set)
    for fp in sorted(files_to_scan):
        caps = analyze_file(fp)
        for c in caps:
            cap_sources[c].add(os.path.basename(fp))

    if args.output == 'json':
        print(json.dumps({c: list(fs) for c, fs in cap_sources.items()}, indent=2))
        return

    print("🎯 Clean Capability → Source File Map")
    print("=" * 60)
    for key, cap in CAPABILITIES.items():
        files = cap_sources.get(key, set())
        # Separate primary from secondary (heuristic: key filename matches)
        primary = [f for f in files if key.replace('_','-') in f.lower() or key.replace('_','') in f.lower()]
        secondary = [f for f in files if f not in primary]
        print(f"\n📌 {cap['label']} ({key})")
        if primary:
            print(f"   ⭐ Primary: {', '.join(sorted(primary))}")
        else:
            print(f"   ⭐ Primary: (none obvious)")
        if secondary:
            print(f"   🔹 Also in: {', '.join(sorted(secondary)[:5])}{'...' if len(secondary)>5 else ''}")
        else:
            print(f"   🔹 Also in: —")
    print("\n" + "=" * 60)
    total_caps = len(CAPABILITIES)
    implemented = len([k for k in CAPABILITIES if cap_sources.get(k)])
    print(f"✅ {implemented}/{total_caps} capabilities found in core source files.")

if __name__ == '__main__':
    main()
