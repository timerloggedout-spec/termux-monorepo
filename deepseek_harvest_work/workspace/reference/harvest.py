#!/usr/bin/env python3
"""
Recursive code‑block extractor – walks any JSON structure,
collects all text strings, and finds ```fenced code```.
Completely agnostic to DeepSeek export format.
"""
import json, re, sys, hashlib
from pathlib import Path
from typing import Any, Dict, List, Optional

def discover_sources():
    """Yield every session json on device. Dynamic — no hardcoded paths."""
    roots = [
        Path.home() / ".deepcli/session_store",
        Path.home() / "synthegration_exports",
        Path.home() / ".deepcli/exports",
        Path.home() / "storage/downloads/synthegration_exports",
    ]
    seen = set()
    for root in roots:
        if not root.is_dir():
            continue
        for f in root.rglob("*.json"):
            if f.stat().st_size < 200 or f.stat().st_size > 200_000_000:
                continue
            rp = str(f.resolve())
            if rp in seen:
                continue
            seen.add(rp)
            yield f

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
        t = self.conversation_title
        t = re.sub(r'[\n\r]', ' ', t)                # newlines → space
        t = re.sub(r'[\\/*?:"\'<>\|\[\]]', '_', t)   # illegal chars → underscore
        t = re.sub(r'\s+', ' ', t).strip()            # collapse whitespace
        return t[:80] or "untitled"

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
    _heredoc_re = re.compile(r"cat\s*>\s*(~?[\w./\-]+)\s*<<\s*'?([A-Za-z_][A-Za-z0-9_]*)'?\s*\n(.*?)\n\2", re.DOTALL)

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
            # heredoc bodies: cat > path <<TAG ... TAG
            for hd in _heredoc_re.finditer(content):
                _path, _tag, _body = hd.group(1), hd.group(2), hd.group(3)
                _name = _path.rsplit("/", 1)[-1] or "heredoc"
                _ext = {"py":"python","sh":"bash","json":"json","md":"markdown"}.get(
                    _name.rsplit(".", 1)[-1] if "." in _name else "", "text")
                if not _body.strip():
                    continue
                cb = CodeBlock(
                    conv_id=tinfo["conversation_id"],
                    conv_title=f"{tinfo['conversation_title']}#{_name}",
                    role=tinfo["role"],
                    timestamp=tinfo["timestamp"],
                    msg_idx=msg_idx,
                    blk_idx=10000 + len(blocks),
                    lang=_ext,
                    code=_body,
                )
                cb.preceding_text_snippet = f"heredoc {_path} <<{_tag}"
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
    import argparse, hashlib, json as _j
    p = argparse.ArgumentParser()
    p.add_argument("-i", "--input", help="single session json")
    p.add_argument("-o", "--output", default=str(Path.home()/"deepseek_harvest_work/code_harvest"))
    p.add_argument("--auto", action="store_true", help="scan every source on device")
    p.add_argument("--incremental", action="store_true", help="skip already-harvested hashes")
    a = p.parse_args()

    out = Path(a.output); out.mkdir(parents=True, exist_ok=True)
    manifest_path = out / "manifest.json"
    existing = []
    seen_hashes = set()
    if a.incremental and manifest_path.exists():
        try:
            existing = _j.loads(manifest_path.read_text())
            seen_hashes = {b.get("code_hash") for b in existing if b.get("code_hash")}
            print(f"incremental: {len(seen_hashes)} hashes already indexed")
        except Exception: pass

    sources = [Path(a.input)] if a.input else (list(discover_sources()) if a.auto else [])
    if not sources:
        print("usage: harvest.py -i <file> | --auto [--incremental]", file=sys.stderr)
        sys.exit(2)
    print(f"sources: {len(sources)}")

    all_blocks = []
    for src_p in sources:
        try:
            blocks = parse_export(str(src_p))
        except Exception as e:
            print(f"  skip {src_p.name}: {type(e).__name__}: {e}")
            continue
        for b in blocks:
            if b.code_hash in seen_hashes: continue
            all_blocks.append(b)
            seen_hashes.add(b.code_hash)

    print(f"new blocks: {len(all_blocks)}")

    # write as flat manifest (append mode)
    merged = existing + [{s: getattr(b, s) for s in b.__slots__} for b in all_blocks]
    manifest_path.write_text(_j.dumps(merged, indent=2, ensure_ascii=False))
    print(f"manifest: {manifest_path} ({len(merged)} total)")

    # grep report
    for needle in ("gpg-prime","gh-code","gh2fa","2fa-pass","pass otp"):
        n = sum(1 for b in all_blocks if needle in (b.code or ""))
        if n: print(f"  HIT {needle}: {n} new blocks")
