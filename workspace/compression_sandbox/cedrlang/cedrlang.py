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
  cedrlang compile <file_path_or_text>  # compiles markdown (e.g. AGENTS.hum.md to AGENTS.md)
  cedrlang decompile <file_path_or_text>  # decompiles markdown (e.g. AGENTS.md to AGENTS.hum.md)

Integrate with deepcli: add `--cedr` flag to auto-compress prompts.
"""

import os
import sys
import re
import json
import argparse
from typing import Dict, List, Any, Tuple

# ------------------------------------------------------------
# 1. Core mapping tables (symbolic substitution)
# ------------------------------------------------------------
SYMBOL_MAP = {
    # direction & causality
    " leads to ": " → ",
    " results in ": " → ",
    " implies ": " → ",
    " because ": " ← ",
    " therefore ": " ∴ ",
    " since ": " ∵ ",
    " and then ": " ⇒ ",
    " compare ": " vs ",
    " versus ": " vs ",
    # actions
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
    # logic
    " if ": " ? ",
    " then ": " ⇒ ",
    " else ": " | ",
    " and ": " ∧ ",
    " or ": " ∨ ",
    " not ": " ¬ ",
    " true ": " T ",
    " false ": " F ",
    # status
    " success ": " ✓ ",
    " fail ": " ✗ ",
    " pending ": " … ",
    " error ": " ⚠ ",
    " warning ": " ⚠ ",
}

# stopwords to strip (caveman compression)
STOPWORDS = {
    "a", "an", "the", "is", "are", "was", "were", "be", "been", "being",
    "to", "of", "and", "for", "in", "that", "with", "on", "at", "by",
    "this", "these", "those", "it", "they", "we", "you", "he", "she"
}

# ------------------------------------------------------------
# Grimoire & 1337speak Compiler Mapping Tables
# ------------------------------------------------------------
COMPILER_MAP = {
    # Grimoire DICTIONARY
    "refactor": "tr4n5mu73",
    "Refactor": "Tr4n5mu73",
    "REFACTOR": "TR4N5MU73",
    "review": "5cry",
    "Review": "5cry",
    "REVIEW": "5CRY",
    "test": "pr0b3",
    "Test": "Pr0b3",
    "TEST": "PR0B3",
    "fragment match": "3ch0",
    "Fragment match": "3ch0",
    "Fragment Match": "3ch0",
    "run history": "gr1m01r3",
    "Run history": "Gr1m01r3",
    "Run History": "Gr1m01r3",
    "backup": "phyl4c73ry",
    "Backup": "Phyl4c73ry",
    "manager agent": "4rchw1z4rd",
    "Manager agent": "4rchw1z4rd",
    "Manager Agent": "4rchW1z4rd",
    "agent": "c4573r",
    "Agent": "C4573r",
    "AGENT": "C4573R",
    "elo score": "m4n4",
    "Elo score": "M4n4",
    "Elo Score": "M4n4",
    "task queue": "sp3llb00k",
    "Task queue": "Sp3llb00k",
    "Task Queue": "Sp3llb00k",
    "prompt template": "run3",
    "Prompt template": "Run3",
    "Prompt Template": "Run3",
    "chronomancer": "chr0n0",
    "Chronomancer": "chr0n0",
    "linguist": "l1ngu15t",
    "Linguist": "l1ngu15t",
    "bidder": "b1dd3r",
    "Bidder": "b1dd3r",
    "scout": "sc0ut",
    "Scout": "sc0ut",
    "harvester": "h4rv35t3r",
    "Harvester": "h4rv35t3r",

    # Core Castings / 1337speak
    "elite": "1337",
    "leet": "1337",
    "hacks": "h4x",
    "hacker": "h4x0r",
    "own": "pwn",
    "newbie": "n00b",
    "excitement": "w00t",
    "skills": "sk1llz",
    "root": "r00t",
    "zero-day": "0day",
    "exploit": "spl01t",
    "shellcode": "sh3llc0d3",
    "crack": "cr4ck",
    "phreak": "phr34k",

    # Distinct Safe Symbols
    "leads to": "→",
    "results in": "→",
    "implies": "→",
    "because": "←",
    "therefore": "∴",
    "since": "∵",
    "and then": "⇒",
    "then": "⇒",
    "compare": "vs",
    "versus": "vs",
    "and": "∧",
    "or": "∨",
    "not": "¬",
    "success": "✓",
    "fail": "✗",
    "pending": "…",
    "error": "⚠",
    "warning": "⚠",
}

DECOMPILER_MAP = {
    # Grimoire DICTIONARY
    "Tr4n5mu73": "Refactor",
    "tr4n5mu73": "refactor",
    "TR4N5MU73": "REFACTOR",
    "5cry": "Review",
    "5CRY": "REVIEW",
    "Pr0b3": "Test",
    "pr0b3": "test",
    "PR0B3": "TEST",
    "3ch0": "Fragment Match",
    "gr1m01r3": "run history",
    "Gr1m01r3": "Run History",
    "phyl4c73ry": "backup",
    "Phyl4c73ry": "Backup",
    "4rchw1z4rd": "manager agent",
    "4rchW1z4rd": "Manager Agent",
    "C4573r": "Agent",
    "c4573r": "agent",
    "C4573R": "AGENT",
    "m4n4": "elo score",
    "M4n4": "Elo Score",
    "sp3llb00k": "task queue",
    "Sp3llb00k": "Task Queue",
    "run3": "prompt template",
    "Run3": "Prompt Template",
    "chr0n0": "Chronomancer",
    "l1ngu15t": "Linguist",
    "b1dd3r": "Bidder",
    "sc0ut": "Scout",
    "h4rv35t3r": "Harvester",

    # Core Castings / 1337speak
    "1337": "elite",
    "h4x": "hacks",
    "h4x0r": "hacker",
    "pwn": "own",
    "n00b": "newbie",
    "w00t": "excitement",
    "sk1llz": "skills",
    "r00t": "root",
    "0day": "zero-day",
    "spl01t": "exploit",
    "sh3llc0d3": "shellcode",
    "cr4ck": "crack",
    "phr34k": "phreak",

    # Distinct Safe Symbols
    "→": "leads to",
    "←": "because",
    "∴": "therefore",
    "∵": "since",
    "⇒": "then",
    "vs": "versus",
    "∧": "and",
    "∨": "or",
    "¬": "not",
    "✓": "success",
    "✗": "fail",
    "…": "pending",
    "⚠": "error",
}

# ------------------------------------------------------------
# 2. Compressor
# ------------------------------------------------------------
def compress(text: str, aggressive: bool = True) -> str:
    """
    Convert natural language to CedrLang.
    aggressive=True removes stopwords & applies symbol substitution.
    """
    if not text:
        return ""

    # lower only for pattern matching; keep original case for identifiers
    lower_text = text.lower()
    result = text[:]  # start with original case

    # symbol replacement (case‑insensitive, word boundaries)
    for phrase, symbol in SYMBOL_MAP.items():
        pattern = re.compile(re.escape(phrase), re.IGNORECASE)
        result = pattern.sub(symbol, result)

    if not aggressive:
        return result.strip()

    # strip stopwords (caveman style)
    words = result.split()
    filtered = [w for w in words if w.lower() not in STOPWORDS]
    result = " ".join(filtered)

    # remove duplicate spaces & punctuation trimming
    result = re.sub(r'\s+', ' ', result).strip()
    # optional: remove trailing punctuation except symbols
    result = re.sub(r'[.,!?;:]$', '', result)
    return result


# ------------------------------------------------------------
# 3. Expander (for debugging / human reading)
# ------------------------------------------------------------
def expand(cedr: str) -> str:
    """Rudimentary expansion – reverses most symbols to English."""
    rev_map = {v.strip(): k.strip() for k, v in SYMBOL_MAP.items()}
    result = cedr
    for sym, phrase in rev_map.items():
        result = result.replace(sym, f" {phrase} ")
    # restore stopwords approximately (add 'the' before nouns? skip for simplicity)
    result = re.sub(r'\s+', ' ', result)
    return result.strip()


# ------------------------------------------------------------
# 4. Token counter (using cl100k_base approximation)
# ------------------------------------------------------------
def count_tokens(text: str) -> int:
    """Rough token count using whitespace + punctuation heuristic."""
    # simple but decent for comparison (error <10% vs cl100k)
    tokens = re.findall(r'\b\w+\b|[^\w\s]', text)
    return len(tokens)


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
# 5. DeepCLI integration (proxy filter)
# ------------------------------------------------------------
def deepcli_filter(prompt: str) -> str:
    """Hook for deepcli – compress user prompt before sending to API."""
    return compress(prompt, aggressive=True)


# ------------------------------------------------------------
# 6. Document Compilation & Decompilation Engine (O(N))
# ------------------------------------------------------------
def protect_line(line: str) -> Tuple[str, List[str]]:
    """Shields formatted code/HTML/paths/decimals/numbers/bold elements with placeholders."""
    placeholders = []

    def replacer(match):
        val = match.group(0)
        # Never protect compiled tokens that are meant to be decompiled
        if val in DECOMPILER_MAP:
            return val
        ph = f"__CEDR_PROTECTED_{len(placeholders)}__"
        placeholders.append(val)
        return ph

    current_line = line

    # 1. Protect leading markdown elements (headers, lists, bullets)
    leading_re = re.compile(r'^(?:\s*[-*+]\s+|\s*\d+\.\s+|\s*#+\s+)')
    current_line = leading_re.sub(replacer, current_line)

    # 2. Inline code blocks (e.g., `code`)
    inline_code_re = re.compile(r'`[^`\n]+`')
    current_line = inline_code_re.sub(replacer, current_line)

    # 3. Links (e.g., [text](url))
    link_re = re.compile(r'\[[^\]\n]+\]\([^)\n]+\)')
    current_line = link_re.sub(replacer, current_line)

    # 4. HTML tags (e.g., <div align="center">)
    html_re = re.compile(r'<[^>\n]+>')
    current_line = html_re.sub(replacer, current_line)

    # 5. Bold/emphasis (e.g., **bold**, *emphasis*)
    bold_re = re.compile(r'\*\*[^*^\n]+\*\*|__[^\_\n]+__|_[^\_\n]+_|\*[^*^\n]+\*')
    current_line = bold_re.sub(replacer, current_line)

    # 6. Filenames/Paths with extensions
    file_re = re.compile(r'\b[a-zA-Z0-9_\-\./]+\.[a-zA-Z0-9\-_]+\b')
    current_line = file_re.sub(replacer, current_line)

    # 7. Absolute paths or typical home paths without extension (e.g. /tmp/model-router, ~/.deepcli)
    path_re = re.compile(r'\b[~/]?[a-zA-Z0-9_\-]+/[a-zA-Z0-9_\-\./]+\b')
    current_line = path_re.sub(replacer, current_line)

    # 8. Decimals (e.g. 3.14)
    decimal_re = re.compile(r'\b\d+\.\d+\b')
    current_line = decimal_re.sub(replacer, current_line)

    # 9. Octals, Hex, integers
    number_re = re.compile(r'\b0o[0-7]+\b|\b0x[0-9a-fA-F]+\b|\b\d+\b')
    current_line = number_re.sub(replacer, current_line)

    return current_line, placeholders


def restore_line(line: str, placeholders: List[str]) -> str:
    """Restores the original protected contents of the line."""
    current_line = line
    for idx in reversed(range(len(placeholders))):
        ph = f"__CEDR_PROTECTED_{idx}__"
        current_line = current_line.replace(ph, placeholders[idx])
    return current_line


def compile_line(line: str) -> str:
    """Compiles a single line using 1337speak, Grimoire mappings, and boundary replacements."""
    protected_line, placeholders = protect_line(line)

    sorted_keys = sorted(COMPILER_MAP.keys(), key=len, reverse=True)
    for key in sorted_keys:
        val = COMPILER_MAP[key]
        pattern_str = rf'\b{re.escape(key)}\b'
        pattern = re.compile(pattern_str)
        protected_line = pattern.sub(val, protected_line)

    return restore_line(protected_line, placeholders)


def decompile_line(line: str) -> str:
    """Decompiles a single line, reversing all symbol and keyword translations."""
    protected_line, placeholders = protect_line(line)

    sorted_keys = sorted(DECOMPILER_MAP.keys(), key=len, reverse=True)
    for key in sorted_keys:
        val = DECOMPILER_MAP[key]
        if key.isalnum():
            pattern_str = rf'\b{re.escape(key)}\b'
        else:
            pattern_str = re.escape(key)
        pattern = re.compile(pattern_str)
        protected_line = pattern.sub(val, protected_line)

    return restore_line(protected_line, placeholders)


def compile_document(text: str) -> str:
    """Line-by-line single pass compiler preserving block formatting/code blocks."""
    lines = text.splitlines()
    compiled_lines = []
    in_code_block = False

    for line in lines:
        if line.strip().startswith("```"):
            in_code_block = not in_code_block
            compiled_lines.append(line)
        elif in_code_block:
            compiled_lines.append(line)
        else:
            compiled_lines.append(compile_line(line))

    return "\n".join(compiled_lines)


def decompile_document(text: str) -> str:
    """Line-by-line single pass decompiler preserving block formatting/code blocks."""
    lines = text.splitlines()
    decompiled_lines = []
    in_code_block = False

    for line in lines:
        if line.strip().startswith("```"):
            in_code_block = not in_code_block
            decompiled_lines.append(line)
        elif in_code_block:
            decompiled_lines.append(line)
        else:
            decompiled_lines.append(decompile_line(line))

    return "\n".join(decompiled_lines)


# ------------------------------------------------------------
# 7. CLI & main
# ------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="CedrLang – Agentic Compression Protocol")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # compress command
    p_compress = subparsers.add_parser("compress", help="Compress natural language to CedrLang")
    p_compress.add_argument("text", nargs="*", help="Text to compress")
    p_compress.add_argument("--aggressive", action="store_true", default=True, help="Enable stopword stripping (default)")
    p_compress.add_argument("--no-aggressive", dest="aggressive", action="store_false", help="Disable stopword stripping")

    # expand command
    p_expand = subparsers.add_parser("expand", help="Expand CedrLang to approximate English")
    p_expand.add_argument("text", nargs="*", help="CedrLang text to expand")

    # stats command
    p_stats = subparsers.add_parser("stats", help="Show token savings stats")
    p_stats.add_argument("original", help="Original natural language")
    p_stats.add_argument("--compressed", help="Optional compressed text (otherwise compress automatically)")

    # serve command (minimal proxy for piping)
    p_serve = subparsers.add_parser("serve", help="Read stdin, compress, write stdout (for integration)")

    # compile command
    p_compile = subparsers.add_parser("compile", help="Compile markdown to token-compressed format")
    p_compile.add_argument("text", nargs="*", help="File path or text to compile")

    # decompile command
    p_decompile = subparsers.add_parser("decompile", help="Decompile token-compressed format back to standard markdown")
    p_decompile.add_argument("text", nargs="*", help="File path or text to decompile")

    args = parser.parse_args()

    if args.command == "compress":
        text = " ".join(args.text) if args.text else sys.stdin.read().strip()
        if not text:
            print("Error: No input text", file=sys.stderr)
            sys.exit(1)
        result = compress(text, aggressive=args.aggressive)
        print(result)

    elif args.command == "expand":
        text = " ".join(args.text) if args.text else sys.stdin.read().strip()
        if not text:
            print("Error: No input text", file=sys.stderr)
            sys.exit(1)
        result = expand(text)
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

    elif args.command == "compile":
        text = " ".join(args.text) if args.text else sys.stdin.read().strip()
        if not text:
            print("Error: No input text", file=sys.stderr)
            sys.exit(1)
        # Check if the single text arg is actually an existing file path
        if len(args.text) == 1 and os.path.exists(args.text[0]):
            with open(args.text[0], 'r', encoding='utf-8') as f:
                content = f.read()
        else:
            content = text
        print(compile_document(content))

    elif args.command == "decompile":
        text = " ".join(args.text) if args.text else sys.stdin.read().strip()
        if not text:
            print("Error: No input text", file=sys.stderr)
            sys.exit(1)
        # Check if the single text arg is actually an existing file path
        if len(args.text) == 1 and os.path.exists(args.text[0]):
            with open(args.text[0], 'r', encoding='utf-8') as f:
                content = f.read()
        else:
            content = text
        print(decompile_document(content))

if __name__ == "__main__":
    main()
