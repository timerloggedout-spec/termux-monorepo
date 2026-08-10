#!/usr/bin/env python3
"""
CedrLang – Agentic Compression Protocol
Minimal token language for LLM↔LLM coordination.
Inspired by caveman prompting, symbolic substitution & minified JSON.

Usage:
  cedrlang compress "Your natural language instruction here"
  cedrlang expand "→cmd:build|args:clean"
  cedrlang stats  # show token savings over baseline
  cedrlang serve  # start filter proxy for deepcli/synthegration

Integrate with deepcli: add `--cedr` flag to auto-compress prompts.
"""

import sys
import os
import re
import json
import argparse
from pathlib import Path
from typing import Dict, List, Any, Tuple

# ------------------------------------------------------------
# 1. Base mappings & Dynamic Grimoire Loading
# ------------------------------------------------------------
SYMBOL_MAP = {
    " leads to ": " → ",
    " results in ": " → ",
    " implies ": " → ",
    " because ": " ← ",
    " therefore ": " ∴ ",
    " since ": " ∵ ",
    " and then ": " ⇒ ",
    " compare ": " vs ",
    " versus ": " vs ",
    " create ": " + ",
    " delete ": " - ",
    " update ": " ~ ",
    " read ": " > ",
    " write ": " < ",
    " execute ": " ! ",
    " query ": " ? ",
    " answer ": " = ",
    " set ": " := ",
    " get ": " . ",
    " if ": " ? ",
    " then ": " ⇒ ",
    " else ": " | ",
    " and ": " ∧ ",
    " or ": " ∨ ",
    " not ": " ¬ ",
    " true ": " T ",
    " false ": " F ",
    " success ": " ✓ ",
    " fail ": " ✗ ",
    " pending ": " … ",
    " error ": " ⚠ ",
    " warning ": " ⚠ ",
}

# Standard Grimoire mappings (fallback if dictionary not found)
GRIMOIRE_COMPRESS = {
    "manager agent": "4rchW1z4rd",
    "manager": "4rchW1z4rd",
    "archwizard": "4rchW1z4rd",
    "agent": "C4573r",
    "caster": "C4573r",
    "elo score": "M4n4",
    "elo": "M4n4",
    "mana": "M4n4",
    "task queue": "Sp3llb00k",
    "spellbook": "Sp3llb00k",
    "prompt template": "Run3",
    "rune": "Run3",
    "refactor": "Tr4n5mu73",
    "transmute": "Tr4n5mu73",
    "review/inspect": "5cry",
    "review": "5cry",
    "scry": "5cry",
    "test": "Pr0b3",
    "probe": "Pr0b3",
    "fragment match": "3ch0",
    "echo": "3ch0",
    "run history": "Gr1m01r3",
    "grimoire": "Gr1m01r3",
    "backup": "Phyl4c73ry",
    "phylactery": "Phyl4c73ry",
    "leetspeak": "1337sp3@k",
    "leet": "1337",
    "hacks": "h4x",
    "hacker": "h4x0r",
    "defeat": "pwn",
    "newbie": "n00b",
    "excitement": "w00t",
    "skills": "sk1llz",
    "root": "r00t",
    "admin": "r00t",
}

# Reverse mapping for expansion
GRIMOIRE_EXPAND = {
    "4rchw1z4rd": "manager agent",
    "c4573r": "agent",
    "m4n4": "elo score",
    "sp3llb00k": "task queue",
    "run3": "prompt template",
    "tr4n5mu73": "refactor",
    "5cry": "review",
    "pr0b3": "test",
    "3ch0": "echo",
    "gr1m01r3": "run history",
    "phyl4c73ry": "backup",
    "1337sp3@k": "leetspeak",
    "1337": "leet",
    "h4x": "hacks",
    "h4x0r": "hacker",
    "pwn": "defeat",
    "n00b": "newbie",
    "w00t": "excitement",
    "sk1llz": "skills",
    "r00t": "root",
}

# Attempt to dynamically load dictionary file to enrich terms
LEXICON_FILE = Path.home() / "harmony_hub/config/grimoire/1337_D1CT10N4RY.md"
if LEXICON_FILE.exists():
    try:
        content = LEXICON_FILE.read_text()
        for line in content.splitlines():
            line_str = line.strip()
            if line_str.startswith("|") and not line_str.startswith("|--") and "Term" not in line_str:
                parts = [p.strip() for p in line_str.split("|")[1:-1]]
                if len(parts) >= 2:
                    term = parts[0]
                    meaning = parts[1]
                    # If there's a third column (Leet Variant)
                    leet = parts[2] if len(parts) >= 3 else ""
                    if leet and term:
                        GRIMOIRE_COMPRESS[term.lower()] = leet
                        GRIMOIRE_EXPAND[leet.lower()] = term.lower()
                    elif term and meaning:
                        # In Core Castings, Term is the 1337, meaning is the standard English
                        GRIMOIRE_EXPAND[term.lower()] = meaning.lower()
                        GRIMOIRE_COMPRESS[meaning.lower()] = term
    except Exception:
        pass

# Combine Symbol Map and Grimoire for single-pass compression/expansion
COMBINED_COMPRESS_MAP = {}
for k, v in SYMBOL_MAP.items():
    COMBINED_COMPRESS_MAP[k.lower()] = v
for k, v in GRIMOIRE_COMPRESS.items():
    COMBINED_COMPRESS_MAP[k.lower()] = v

# Sort keys by descending length to match longest parts first
sorted_comp_keys = sorted(COMBINED_COMPRESS_MAP.keys(), key=len, reverse=True)
patterns_comp = []
for k in sorted_comp_keys:
    escaped = re.escape(k)
    # Require word boundary only if it begins and ends with alphanumeric
    if k[0].isalnum() and k[-1].isalnum():
        patterns_comp.append(rf"\b{escaped}\b")
    else:
        patterns_comp.append(escaped)

COMPRESS_RE = re.compile("|".join(patterns_comp), re.IGNORECASE)

COMBINED_EXPAND_MAP = {}
for k, v in SYMBOL_MAP.items():
    COMBINED_EXPAND_MAP[v.strip()] = k.strip()
for k, v in GRIMOIRE_EXPAND.items():
    COMBINED_EXPAND_MAP[k.lower()] = v

sorted_exp_keys = sorted(COMBINED_EXPAND_MAP.keys(), key=len, reverse=True)
patterns_exp = []
for k in sorted_exp_keys:
    escaped = re.escape(k)
    if k[0].isalnum() and k[-1].isalnum():
        patterns_exp.append(rf"\b{escaped}\b")
    else:
        patterns_exp.append(escaped)

EXPAND_RE = re.compile("|".join(patterns_exp), re.IGNORECASE)

# ------------------------------------------------------------
# 2. Markdown / Syntax Protection
# ------------------------------------------------------------
def protect_syntax(text: str) -> Tuple[str, List[Tuple[str, str]]]:
    """Protects Markdown syntax (code blocks, inline code, links) with placeholders."""
    block_re = re.compile(r"```[\s\S]*?```")
    inline_re = re.compile(r"`[^`\n]+`")
    link_re = re.compile(r"\[[^\]]+\]\([^)]+\)")
    html_re = re.compile(r"<[^>\n]+>")

    placeholders = []
    temp_text = text

    # Extract Code Blocks
    for match in block_re.findall(temp_text):
        ph = f"__CODE_BLOCK_PH_{len(placeholders)}__"
        placeholders.append((ph, match))
        temp_text = temp_text.replace(match, ph)

    # Extract Inline Code
    for match in inline_re.findall(temp_text):
        ph = f"__INLINE_CODE_PH_{len(placeholders)}__"
        placeholders.append((ph, match))
        temp_text = temp_text.replace(match, ph)

    # Extract Markdown Links
    for match in link_re.findall(temp_text):
        ph = f"__LINK_PH_{len(placeholders)}__"
        placeholders.append((ph, match))
        temp_text = temp_text.replace(match, ph)

    # Extract HTML
    for match in html_re.findall(temp_text):
        ph = f"__HTML_PH_{len(placeholders)}__"
        placeholders.append((ph, match))
        temp_text = temp_text.replace(match, ph)

    return temp_text, placeholders

def restore_syntax(text: str, placeholders: List[Tuple[str, str]]) -> str:
    """Restores the protected Markdown elements from placeholders."""
    result = text
    for ph, orig in reversed(placeholders):
        result = result.replace(ph, orig)
    return result

# ------------------------------------------------------------
# 3. 6-Line Caveman Stopword Stripper
# ------------------------------------------------------------
def caveman(text: str) -> str:
    # Caveman in 6 Lines - ultra-compressed text filter
    sw = {"a", "an", "the", "is", "are", "was", "were", "be", "been", "being", "to", "of", "and", "for", "in", "that", "with", "on", "at", "by", "this", "these", "those", "it", "they", "we", "you", "he", "she", "to", "from", "for", "or", "and"}
    words = re.findall(r"\b\w+'?\w*\b|[^\w\s]", text)
    cleaned = [w for w in words if w.lower() not in sw]
    return " ".join(cleaned)

# ------------------------------------------------------------
# 4. Compressor & Expander Engines
# ------------------------------------------------------------
def compress(text: str, aggressive: bool = True) -> str:
    """Compress standard English to CedrLang + Grimoire style with O(N) regex while preserving line structure."""
    if not text:
        return ""

    # 1. Protect syntax (multi-line structures are replaced by single-line placeholders)
    protected_text, placeholders = protect_syntax(text)

    # 2. Compress line-by-line to preserve structure (headings, lists, newlines)
    ph_set = {ph for ph, _ in placeholders}
    sw = {"a", "an", "the", "is", "are", "was", "were", "be", "been", "being", "to", "of", "and", "for", "in", "that", "with", "on", "at", "by", "this", "these", "those", "it", "they", "we", "you", "he", "she", "to", "from", "for", "or", "and"}

    def compress_repl(match):
        val = match.group(0).lower()
        return COMBINED_COMPRESS_MAP.get(val, match.group(0))

    compressed_lines = []
    for line in protected_text.splitlines():
        # Apply single-pass symbolic substitution on the line
        comp_line = COMPRESS_RE.sub(compress_repl, line)

        if aggressive:
            # Tokenize and strip stopwords while preserving placeholders
            words = comp_line.split()
            cleaned = [w for w in words if w in ph_set or w.lower() not in sw]
            comp_line = " ".join(cleaned)
        else:
            comp_line = re.sub(r'\s+', ' ', comp_line).strip()

        compressed_lines.append(comp_line)

    # Rejoin lines with actual newlines
    compressed = "\n".join(compressed_lines)

    # 3. Restore syntax
    return restore_syntax(compressed, placeholders)

def expand(cedr: str) -> str:
    """Expand CedrLang back to approximate readable English."""
    if not cedr:
        return ""

    protected_text, placeholders = protect_syntax(cedr)

    def expand_repl(match):
        val = match.group(0).lower()
        res = COMBINED_EXPAND_MAP.get(val, match.group(0))
        # Add space pads for smooth reading
        return f" {res} "

    expanded = EXPAND_RE.sub(expand_repl, protected_text)
    expanded = re.sub(r'\s+', ' ', expanded).strip()

    return restore_syntax(expanded, placeholders)

# ------------------------------------------------------------
# 5. Token Counter & Stats
# ------------------------------------------------------------
def count_tokens(text: str) -> int:
    """Whitespace and punctuation-based token approximation."""
    return len(re.findall(r'\b\w+\b|[^\w\s]', text))

def stats_report(original: str, compressed: str) -> Dict[str, Any]:
    orig_tokens = count_tokens(original)
    comp_tokens = count_tokens(compressed)
    savings = ((orig_tokens - comp_tokens) / orig_tokens) * 100 if orig_tokens else 0
    return {
        "original_tokens": orig_tokens,
        "compressed_tokens": comp_tokens,
        "savings_percent": round(savings, 2),
        "original_chars": len(original),
        "compressed_chars": len(compressed)
    }

# ------------------------------------------------------------
# 6. Main CLI
# ------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="CedrLang – Agentic Compression Protocol")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Compress Command
    p_compress = subparsers.add_parser("compress", help="Compress natural language to CedrLang")
    p_compress.add_argument("text", nargs="*", help="Text to compress")
    p_compress.add_argument("-f", "--file", help="Input file path to compress")
    p_compress.add_argument("-o", "--output", help="Output file path (default: write to stdout)")
    p_compress.add_argument("--no-aggressive", dest="aggressive", action="store_false", default=True, help="Disable aggressive stopword stripping")

    # Expand Command
    p_expand = subparsers.add_parser("expand", help="Expand CedrLang to approximate English")
    p_expand.add_argument("text", nargs="*", help="CedrLang text to expand")
    p_expand.add_argument("-f", "--file", help="Input file path to expand")
    p_expand.add_argument("-o", "--output", help="Output file path (default: write to stdout)")

    # Stats Command
    p_stats = subparsers.add_parser("stats", help="Show token savings stats")
    p_stats.add_argument("original", help="Original natural language")
    p_stats.add_argument("--compressed", help="Optional compressed text (otherwise compress automatically)")

    # Serve Command
    p_serve = subparsers.add_parser("serve", help="Read stdin, compress, write stdout")

    args = parser.parse_args()

    if args.command == "compress":
        if args.file:
            input_path = Path(args.file)
            if not input_path.exists():
                print(f"Error: File not found: {args.file}", file=sys.stderr)
                sys.exit(1)
            text = input_path.read_text()
        else:
            text = " ".join(args.text) if args.text else sys.stdin.read().strip()

        if not text:
            print("Error: No input text", file=sys.stderr)
            sys.exit(1)

        result = compress(text, aggressive=args.aggressive)

        if args.output:
            Path(args.output).write_text(result)
        else:
            print(result)

    elif args.command == "expand":
        if args.file:
            input_path = Path(args.file)
            if not input_path.exists():
                print(f"Error: File not found: {args.file}", file=sys.stderr)
                sys.exit(1)
            text = input_path.read_text()
        else:
            text = " ".join(args.text) if args.text else sys.stdin.read().strip()

        if not text:
            print("Error: No input text", file=sys.stderr)
            sys.exit(1)

        result = expand(text)

        if args.output:
            Path(args.output).write_text(result)
        else:
            print(result)

    elif args.command == "stats":
        original = args.original
        compressed = args.compressed if args.compressed else compress(original)
        stats = stats_report(original, compressed)
        print(json.dumps(stats, indent=2))
        print(f"\n✓ Savings: {stats['savings_percent']}% tokens")

    elif args.command == "serve":
        for line in sys.stdin:
            compressed_line = compress(line.rstrip('\n'), aggressive=True)
            sys.stdout.write(compressed_line + "\n")
            sys.stdout.flush()

if __name__ == "__main__":
    main()
