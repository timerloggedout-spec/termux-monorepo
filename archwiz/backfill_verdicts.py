#!/usr/bin/env python3
"""
Per‑block verdict backfill using heredoc parsing, hash index, and
error / success signals in the following user message.
Writes ~/archwiz/block_verdicts.jsonl
"""
import json, hashlib, re
from pathlib import Path

HOME = Path.home()
EXPORTS    = HOME / "synthegration_exports"
HASH_IDX   = HOME / "cli-synthegration/workspace/provenance/hash_index.json"
BLOCK_VERD = HOME / "archwiz/block_verdicts.jsonl"

# ── Load hash index ──────────────────────────────────────
hi = json.loads(HASH_IDX.read_text()) if HASH_IDX.exists() else {}
hash_to_file = {}
for h, f in hi.get("exact", {}).items(): hash_to_file[h] = f
for h, f in hi.get("norm",  {}).items(): hash_to_file.setdefault(h, f)

# ── Error detection patterns (from error_extractor + extra) ──
ERROR_PAT = re.compile(
    r'Traceback|Error:|Exception:|FAILED|command not found|npm ERR!|'
    r'SyntaxError|IndentationError|NameError|TypeError|ReferenceError|'
    r'curl: \(|Fatal error|EACCES|ENOENT|EEXIST|EPERM|cannot find module',
    re.IGNORECASE
)
SUCCESS_PAT = re.compile(r'✅|Message sent|Session ID:|📤|📋')

def verdict_from_messages(msgs, block_msg_idx):
    """Look at the next USER message after block_msg_idx to decide PASS/FAIL."""
    for j in range(block_msg_idx + 1, len(msgs)):
        if msgs[j].get("role") == "USER":
            content = msgs[j].get("content", "") or ""
            has_err = bool(ERROR_PAT.search(content))
            has_ok  = bool(SUCCESS_PAT.search(content))
            if has_err:
                return "FAIL"
            if has_ok:
                return "PASS"
            return "UNKNOWN"   # no signal
    return "UNKNOWN"

# ── Heredoc filename extraction ───────────────────────────
HEREDOC_RE = re.compile(r"cat\s+>\s*([^\s]+)\s+<<\s*'?EOF'?", re.IGNORECASE)

# ── Main loop ─────────────────────────────────────────────
new_count = 0
with open(BLOCK_VERD, "w") as out:
    for d in sorted(EXPORTS.iterdir()):
        if not d.is_dir():
            continue
        sid = d.name.split('_')[-1] if '_' in d.name else d.name

        # Load session messages
        sess_f = HOME / ".deepcli/session_store" / f"{sid}.json"
        if not sess_f.exists():
            sess_f = HOME / ".deepcli/session_store/primary" / f"{sid}.json"
        if not sess_f.exists():
            continue
        try:
            msgs = json.loads(sess_f.read_text())
            if not isinstance(msgs, list):
                continue
        except:
            continue

        # Build a map of message index -> code blocks (from manifest if needed, but we scan content directly)
        for mi, m in enumerate(msgs):
            content = m.get("content", "") or ""
            if not content:
                continue
            # Extract fenced code blocks from this message
            for bi, match in enumerate(re.finditer(r"```(?:\w+)?\n(.*?)\n```", content, re.DOTALL)):
                code = match.group(1).strip()
                if len(code) < 10:
                    continue
                code_hash = hashlib.sha256(code.encode()).hexdigest()

                # Determine target file
                target = None
                # 1. Heredoc
                hd = HEREDOC_RE.search(code)
                if hd:
                    target = hd.group(1)
                # 2. Hash index (whole file match)
                if not target:
                    target = hash_to_file.get(code_hash)
                # 3. Placeholder
                if not target:
                    target = f"session:{sid}:msg:{mi}:block:{bi}"

                verdict = verdict_from_messages(msgs, mi)

                out.write(json.dumps({
                    "session_id": sid,
                    "message_index": mi,
                    "block_index": bi,
                    "code_hash": code_hash[:16],
                    "target_file": target,
                    "verdict": verdict,
                    "code_snippet": code[:200]
                }) + "\n")
                new_count += 1

print(f"Wrote {new_count} block verdicts to {BLOCK_VERD}")
