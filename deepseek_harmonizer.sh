#!/bin/bash
# ============================================================
# deepseek_harmonizer.sh – Universal DeepSeek code harvester
# Walks any JSON structure, extracts all fenced code blocks.
# ============================================================
set -euo pipefail

SOURCE_DIR="/data/data/com.termux/files/home/storage/downloads/_doing/_1-build/DeepSeek/exports/deepseek_data-2026-05-17"
INPUT_FILE="conversations (1).json"
WORK_DIR="$HOME/deepseek_harvest_work"
OUTPUT_DIR="${SOURCE_DIR}/_1st-processed"
PYTHON_SCRIPT="$WORK_DIR/harvest.py"
MERGE_SCRIPT="$WORK_DIR/deepseek_merge.py"
API_KEY_FILE="$HOME/.deepseek_api_key"

echo "🚀 DeepSeek Harmonizer – Universal Recursive Edition"

if [ ! -f "$SOURCE_DIR/$INPUT_FILE" ]; then
    echo "❌ Input file not found: $SOURCE_DIR/$INPUT_FILE"
    exit 1
fi

if ! command -v python3 &> /dev/null; then
    echo "🔧 Installing Python..."
    pkg install -y python
fi

# ------------------------------------------------------------------
#  PREPARE WORK DIRECTORY
# ------------------------------------------------------------------
rm -rf "$WORK_DIR"
mkdir -p "$WORK_DIR"
cp "$SOURCE_DIR/$INPUT_FILE" "$WORK_DIR/export.json"

# ------------------------------------------------------------------
#  UNIVERSAL RECURSIVE PYTHON HARVESTER
# ------------------------------------------------------------------
cat > "$PYTHON_SCRIPT" << 'PYEOF'
#!/usr/bin/env python3
"""
Recursive code‑block extractor – walks any JSON structure,
collects all text strings, and finds ```fenced code```.
Completely agnostic to DeepSeek export format.
"""
import json, re, sys, hashlib
from pathlib import Path
from typing import Any, Dict, List, Optional

class CodeBlock:
    __slots__ = (
        "conversation_id", "conversation_title",
        "message_role", "message_timestamp",
        "message_index", "block_index",
        "language", "code", "code_hash",
        "preceding_text_snippet"
    )
    def __init__(self, conv_id, conv_title, role, timestamp, msg_idx, blk_idx, lang, code):
        self.conversation_id = conv_id or "unknown"
        self.conversation_title = (conv_title or "Untitled").strip()[:120]
        self.message_role = role
        self.message_timestamp = timestamp
        self.message_index = msg_idx
        self.block_index = blk_idx
        self.language = lang.lower().strip() or "text"
        self.code = code
        self.code_hash = hashlib.sha256(code.encode("utf-8")).hexdigest()[:16]
        self.preceding_text_snippet = ""

    @property
    def safe_title(self):
        t = re.sub(r'[\\/*?:"<>|]', "_", self.conversation_title)
        return t.strip()[:80] or "untitled"

    @property
    def unique_filename(self):
        ext = {"python":"py","javascript":"js","typescript":"ts","bash":"sh","shell":"sh",
               "html":"html","css":"css","json":"json","yaml":"yaml","markdown":"md",
               "text":"txt"}.get(self.language, self.language)
        return f"{self.language}_{self.code_hash}.{ext}"

def recursive_texts(obj, parent_key="", conv_meta: Optional[Dict]=None) -> List[Dict[str, Any]]:
    """
    Walk entire JSON tree, yield every string found along with
    contextual breadcrumbs: the conversation id/title and the message timestamp/role if present.
    Returns list of dicts with: text, timestamp, role, conversation_id, conversation_title
    """
    results = []
    if isinstance(obj, str):
        # Use conv_meta if available, otherwise defaults
        cid = conv_meta.get("conversation_id", "unknown") if conv_meta else "unknown"
        ctitle = conv_meta.get("conversation_title", "Untitled") if conv_meta else "Untitled"
        timestamp = conv_meta.get("timestamp", "unknown") if conv_meta else "unknown"
        role = conv_meta.get("role", "unknown") if conv_meta else "unknown"
        results.append({
            "text": obj,
            "timestamp": timestamp,
            "role": role,
            "conversation_id": cid,
            "conversation_title": ctitle
        })
    elif isinstance(obj, list):
        for item in obj:
            results.extend(recursive_texts(item, parent_key, conv_meta))
    elif isinstance(obj, dict):
        # Try to extract conversation‑level metadata
        new_meta = dict(conv_meta) if conv_meta else {}
        if "id" in obj and parent_key == "":   # top-level conversation id
            new_meta["conversation_id"] = obj.get("id", new_meta.get("conversation_id"))
        if "title" in obj:
            new_meta["conversation_title"] = obj.get("title", new_meta.get("conversation_title"))
        if "inserted_at" in obj:
            new_meta["timestamp"] = obj.get("inserted_at", new_meta.get("timestamp"))
        # Common DeepSeek mapping structure: message -> content -> parts
        # Try to grab role and timestamp from message objects
        if "message" in obj:
            msg_obj = obj["message"]
            if isinstance(msg_obj, dict):
                role = msg_obj.get("author", {}).get("role") or msg_obj.get("role")
                if role:
                    new_meta["role"] = role
                ts = msg_obj.get("create_time") or msg_obj.get("timestamp") or msg_obj.get("inserted_at")
                if ts:
                    new_meta["timestamp"] = ts
        for key, value in obj.items():
            results.extend(recursive_texts(value, key, new_meta))
    return results

def parse_export(json_path: str) -> List[CodeBlock]:
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Normalise to a list of conversations
    if isinstance(data, dict):
        for possible_key in ["conversations", "chats", "chat_history", "history", "exports", "messages"]:
            if possible_key in data and isinstance(data[possible_key], list):
                data = data[possible_key]
                break
        else:
            data = [data]
    if not isinstance(data, list):
        data = [data]

    fence_re = re.compile(r"```(\w*)\s*\n(.*?)```", re.DOTALL)
    blocks = []

    for conv_idx, conv in enumerate(data):
        # Recursively collect all text strings from this conversation, with metadata gathered on the fly
        texts = recursive_texts(conv)
        for msg_idx, tinfo in enumerate(texts):
            content = tinfo["text"]
            if not isinstance(content, str):
                continue
            for blk_idx, match in enumerate(fence_re.finditer(content)):
                lang = match.group(1) or "text"
                code = match.group(2).rstrip("\n")
                if not code.strip():
                    continue
                cb = CodeBlock(
                    conv_id=tinfo["conversation_id"],
                    conv_title=tinfo["conversation_title"],
                    role=tinfo["role"],
                    timestamp=tinfo["timestamp"],
                    msg_idx=msg_idx,
                    blk_idx=blk_idx,
                    lang=lang,
                    code=code
                )
                start = match.start()
                before = content[max(0, start-120):start].strip()
                cb.preceding_text_snippet = before
                blocks.append(cb)

    return blocks

def deduplicate(blocks):
    seen = {}
    for blk in blocks:
        if blk.code_hash not in seen:
            seen[blk.code_hash] = blk
    return list(seen.values())

def write_output(blocks, output_root, dedup=True):
    if dedup:
        blocks = deduplicate(blocks)
    output_root = Path(output_root)
    output_root.mkdir(parents=True, exist_ok=True)
    proj_map = {}
    for blk in blocks:
        proj_map.setdefault(blk.safe_title, []).append(blk)
    manifest = []
    for proj, blks in sorted(proj_map.items()):
        proj_dir = output_root / proj
        proj_dir.mkdir(exist_ok=True)
        notes = [f"# Project: {proj}\n"]
        for blk in blks:
            fname = blk.unique_filename
            (proj_dir / fname).write_text(blk.code, encoding="utf-8")
            meta = {s: getattr(blk, s) for s in blk.__slots__}
            (proj_dir / (fname+".meta.json")).write_text(
                json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")
            manifest.append(meta)
            snippet = blk.preceding_text_snippet.replace("\n", " ")
            notes.append(
                f"### {fname}\n- Role: {blk.message_role}\n"
                f"- Timestamp: {blk.message_timestamp}\n"
                f"- Msg idx: {blk.message_index}, block {blk.block_index}\n"
                f"- Language: {blk.language}\n- Context: {snippet[:200]}\n"
            )
        (proj_dir / "NOTES.md").write_text("\n".join(notes), encoding="utf-8")
    (output_root / "manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    return len(blocks)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", required=True)
    parser.add_argument("-o", "--output", required=True)
    args = parser.parse_args()
    blocks = parse_export(args.input)
    if not blocks:
        print("⚠️  No code blocks found even after recursive scan.", file=sys.stderr)
        sys.exit(0)
    count = write_output(blocks, args.output, dedup=True)
    print(f"✔ Extracted {count} unique code blocks into {args.output}")
PYEOF

# ------------------------------------------------------------------
#  RUN HARVESTER
# ------------------------------------------------------------------
echo "📂 Extracting code blocks..."
python3 "$PYTHON_SCRIPT" -i "$WORK_DIR/export.json" -o "$WORK_DIR/code_harvest"

mkdir -p "$OUTPUT_DIR"
if [ -d "$WORK_DIR/code_harvest" ]; then
    cp -r "$WORK_DIR/code_harvest"/* "$OUTPUT_DIR/"
    echo "✅ Code organised in: $OUTPUT_DIR"
else
    echo "⚠️  Harvest directory not created – no code blocks extracted."
fi

# ------------------------------------------------------------------
#  OPTIONAL AI MERGE SETUP
# ------------------------------------------------------------------
echo ""
echo "🤖 Optional: Use DeepSeek AI to auto‑merge similar code versions?"
read -p "   Enable AI merging? [y/N] " enable_ai
if [[ "$enable_ai" =~ ^[Yy]$ ]]; then
    if [ -f "$API_KEY_FILE" ]; then
        echo "🔑 Using stored API key from $API_KEY_FILE"
        api_key=$(cat "$API_KEY_FILE")
    else
        read -sp "🔑 Paste your DeepSeek API key: " api_key
        echo ""
        if [ -z "$api_key" ]; then
            echo "❌ No key provided – skipping AI merge."
        else
            echo "$api_key" > "$API_KEY_FILE"
            chmod 600 "$API_KEY_FILE"
            echo "🔒 Key saved to $API_KEY_FILE"
        fi
    fi

    if [ -n "${api_key:-}" ]; then
        cat > "$MERGE_SCRIPT" << PYEOF2
#!/usr/bin/env python3
import os, sys, json, requests

API_KEY = os.environ["DEEPSEEK_API_KEY"]
API_URL = "https://api.deepseek.com/v1/chat/completions"

def merge_three(base, ours, theirs):
    prompt = f"""You are a 3-way merge expert. Given BASE, OURS, and THEIRS code versions, output the resolved merge with conflict markers resolved. Choose the most robust combination.
BASE:
\`\`\`
{base}
\`\`\`
OURS:
\`\`\`
{ours}
\`\`\`
THEIRS:
\`\`\`
{theirs}
\`\`\`"""
    resp = requests.post(API_URL,
        headers={"Authorization": f"Bearer {API_KEY}"},
        json={"model": "deepseek-chat", "messages": [{"role": "user", "content": prompt}],
              "temperature": 0.1, "max_tokens": 4000})
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]

if __name__ == "__main__":
    base_file = sys.argv[1]
    ours_file = sys.argv[2]
    theirs_file = sys.argv[3]
    base = open(base_file).read()
    ours = open(ours_file).read()
    theirs = open(theirs_file).read()
    merged = merge_three(base, ours, theirs)
    print(merged)
PYEOF2
        chmod +x "$MERGE_SCRIPT"
        echo "🧠 AI merge helper ready: $MERGE_SCRIPT"
        echo "   Usage: DEEPSEEK_API_KEY='...' python3 $MERGE_SCRIPT base.py ours.py theirs.py"
    fi
fi

echo ""
echo "🏁 All done. Your structured code is in:"
echo "   $OUTPUT_DIR"
echo "   You can now feed these files into the Codebase Harmonizer."
