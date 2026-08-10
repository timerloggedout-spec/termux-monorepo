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
    "hacks": "h4x",
    "hacker": "h4x0r",
    "pwn": "defeat",
    "n00b": "newbie",
    "w00t": "excitement",
    "sk1llz": "skills",
    "r00t": "root",
}

# Module-level Stopwords Constant
STOPWORDS = {
    "a", "an", "the", "is", "are", "was", "were", "be", "been", "being",
    "to", "of", "and", "for", "in", "that", "with", "on", "at", "by",
    "this", "these", "those", "it", "they", "we", "you", "he", "she",
    "basically", "actually", "just", "really"
}

def load_dynamic_lexicon() -> Tuple[Dict[str, str], Dict[str, str]]:
    """Loads and returns Grimoire lexicon dictionary mappings."""
    compress_map = dict(GRIMOIRE_COMPRESS)
    expand_map = dict(GRIMOIRE_EXPAND)
    lexicon_file = Path.home() / "harmony_hub/config/grimoire/1337_D1CT10N4RY.md"
    if lexicon_file.exists():
        try:
            content = lexicon_file.read_text()
            in_lexicon_section = False
            for line in content.splitlines():
                line_str = line.strip()
                if line_str.startswith("## Core Castings") or line_str.startswith("## Grimoire Protocol"):
                    in_lexicon_section = True
                    continue
                elif line_str.startswith("## ") or line_str.startswith("# "):
                    in_lexicon_section = False
                    continue

                if in_lexicon_section and line_str.startswith("|") and not line_str.startswith("|--") and "Term" not in line_str:
                    parts = [p.strip() for p in line_str.split("|")[1:-1]]
                    if len(parts) >= 2:
                        term = parts[0]
                        meaning = parts[1]
                        leet = parts[2] if len(parts) >= 3 else ""
                        if len(term) <= 1 or len(meaning) <= 1:
                            continue
                        if leet and term:
                            compress_map[term.lower()] = leet
                            expand_map[leet.lower()] = term.lower()
                        elif term and meaning:
                            expand_map[term.lower()] = meaning.lower()
                            compress_map[meaning.lower()] = term
        except Exception:
            pass
    return compress_map, expand_map

# Load dynamic maps
GRIMOIRE_COMPRESS, GRIMOIRE_EXPAND = load_dynamic_lexicon()

# Combine Symbol Map and Grimoire for single-pass compression/expansion
COMBINED_COMPRESS_MAP = {}
for k, v in SYMBOL_MAP.items():
    COMBINED_COMPRESS_MAP[k.strip().lower()] = v.strip()
for k, v in GRIMOIRE_COMPRESS.items():
    COMBINED_COMPRESS_MAP[k.strip().lower()] = v.strip()

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
SAFE_EXPAND_SYMBOLS = {"→", "←", "∴", "∵", "⇒", "∧", "∨", "¬", "✓", "✗", "…", "⚠"}

for k, v in SYMBOL_MAP.items():
    symbol_stripped = v.strip().lower()
    # Expand only standalone unique symbols or alphanumeric words
    if symbol_stripped.isalnum() or symbol_stripped in SAFE_EXPAND_SYMBOLS:
        COMBINED_EXPAND_MAP[symbol_stripped] = k.strip()

for k, v in GRIMOIRE_EXPAND.items():
    COMBINED_EXPAND_MAP[k.lower()] = v

sorted_exp_keys = sorted(COMBINED_EXPAND_MAP.keys(), key=len, reverse=True)
patterns_exp = []
for k in sorted_exp_keys:
    escaped = re.escape(k)
    if k[0].isalnum() and k[-1].isalnum():
        patterns_exp.append(rf"\b{escaped}\b")
    else:
        # Match standalone non-alphanumeric symbols (like standalone "+", "-", "→")
        patterns_exp.append(rf"(?:^|\s){escaped}(?=\s|$)")

EXPAND_RE = re.compile("|".join(patterns_exp), re.IGNORECASE)

# ------------------------------------------------------------
# 2. Markdown / Syntax Protection
# ------------------------------------------------------------
def protect_syntax(text: str) -> Tuple[str, List[Tuple[str, str]]]:
    """Protects Markdown syntax (code blocks, inline code, links) and URLs/paths with placeholders."""
    block_re = re.compile(r"```[\s\S]*?```")
    inline_re = re.compile(r"`[^`\n]+`")
    link_re = re.compile(r"\[[^\]]+\]\([^)]+\)")
    html_re = re.compile(r"</?[A-Za-z][^>\n]*>")
    # Match URLs (e.g., http://... or https://...)
    url_re = re.compile(r"https?://[^\s)]+")
    # Match file paths or filenames containing '/' or ending with common extensions
    path_re = re.compile(r"\b[\w.-]+/[\w.-]+(?:\.[\w.-]+)+\b")

    placeholders = []
    temp_text = text
    match_to_ph = {}

    def get_placeholder(match_str, prefix):
        if match_str in match_to_ph:
            return match_to_ph[match_str]
        ph = f"__{prefix}_PH_{len(placeholders)}__"
        match_to_ph[match_str] = ph
        placeholders.append((ph, match_str))
        return ph

    # 1. Code blocks
    def block_sub(m):
        return get_placeholder(m.group(0), "CODE_BLOCK")
    temp_text = block_re.sub(block_sub, temp_text)

    # 2. Inline code
    def inline_sub(m):
        return get_placeholder(m.group(0), "INLINE_CODE")
    temp_text = inline_re.sub(inline_sub, temp_text)

    # 3. Markdown links
    def link_sub(m):
        return get_placeholder(m.group(0), "LINK")
    temp_text = link_re.sub(link_sub, temp_text)

    # 4. HTML tags
    def html_sub(m):
        return get_placeholder(m.group(0), "HTML")
    temp_text = html_re.sub(html_sub, temp_text)

    # 5. URLs
    def url_sub(m):
        return get_placeholder(m.group(0), "URL")
    temp_text = url_re.sub(url_sub, temp_text)

    # 6. Paths
    def path_sub(m):
        return get_placeholder(m.group(0), "PATH")
    temp_text = path_re.sub(path_sub, temp_text)

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
    words = re.findall(r"\b\w+'?\w*\b|[^\w\s]", text)
    cleaned = [w for w in words if w.lower() not in STOPWORDS]
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

    def compress_repl(match):
        val = match.group(0).strip().lower()
        res = COMBINED_COMPRESS_MAP.get(val, match.group(0))
        return res

    compressed_lines = []
    has_trailing_newline = text.endswith('\n')

    for line in protected_text.splitlines():
        # Match leading indentation
        indent_match = re.match(r"^(\s*)", line)
        indent = indent_match.group(1) if indent_match else ""
        content_line = line[len(indent):]

        # Apply single-pass symbolic substitution on the line content
        comp_line = COMPRESS_RE.sub(compress_repl, content_line)

        if aggressive:
            # Tokenize and strip stopwords while preserving placeholders
            words = comp_line.split()
            cleaned = [w for w in words if w in ph_set or w.lower() not in STOPWORDS]
            comp_line = " ".join(cleaned)
        else:
            comp_line = re.sub(r'\s+', ' ', comp_line).strip()

        compressed_lines.append(indent + comp_line)

    # Rejoin lines with actual newlines
    compressed = "\n".join(compressed_lines)
    if has_trailing_newline:
        compressed += '\n'

    # 3. Restore syntax
    return restore_syntax(compressed, placeholders)

def expand(cedr: str) -> str:
    """Expand CedrLang back to approximate readable English while preserving format."""
    if not cedr:
        return ""

    protected_text, placeholders = protect_syntax(cedr)

    def expand_repl(match):
        full_match = match.group(0)
        val = full_match.strip()
        leading_space = full_match[:len(full_match)-len(full_match.lstrip())]
        if val == "T":
            res = "true"
        elif val == "F":
            res = "false"
        else:
            res = COMBINED_EXPAND_MAP.get(val.lower(), val)
        return leading_space + res

    expanded_lines = []
    has_trailing_newline = cedr.endswith('\n')

    for line in protected_text.splitlines():
        # Match leading indentation
        indent_match = re.match(r"^(\s*)", line)
        indent = indent_match.group(1) if indent_match else ""
        content_line = line[len(indent):]

        # Apply expand pattern on line
        expanded_line = EXPAND_RE.sub(expand_repl, content_line)
        # Collapse double horizontal spaces only
        expanded_line = re.sub(r'[ \t]+', ' ', expanded_line).strip()
        expanded_lines.append(indent + expanded_line)

    expanded = "\n".join(expanded_lines)
    if has_trailing_newline:
        expanded += '\n'

    return restore_syntax(expanded, placeholders)

# Public helper deepcli_filter (kept for legacy support/external scripts)
def deepcli_filter(prompt: str) -> str:
    """Hook for deepcli – compress user prompt before sending to API."""
    return compress(prompt, aggressive=True)

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
    p_compress.add_argument("--aggressive", action="store_true", default=True, help="Enable aggressive stopword stripping")
    p_compress.add_argument("--no-aggressive", dest="aggressive", action="store_false", help="Disable aggressive stopword stripping")

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
