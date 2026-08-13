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
  cedrlang compile <file_or_text> [-o output_file]
  cedrlang decompile <file_or_text> [-o output_file]

Integrate with deepcli: add `--cedr` flag to auto-compress prompts.
"""

import sys
import re
import json
import argparse
from typing import Dict, List, Any, Tuple
from pathlib import Path

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

# CedrLang v2 / Grimoire Mappings
MAPPINGS = [
    ("transmute", "h4x"),
    ("scry", "scry"),
    ("probe", "pr0b3"),
    ("echo", "3ch0"),
    ("time loop", "l00p"),
    ("branch", "f0rk"),
    ("incantation", "1nc4nt"),
    ("cast", "c4st"),
    ("grimoire", "gr1m01r3"),
    ("bidder", "b1dd3r"),
    ("wager", "w4g3r"),
    ("chronomancer", "chr0n0"),
    ("linguist", "l1ngu15t"),
    ("scout", "sc0ut"),
    ("harvester", "h4rv35t3r"),
]

# ------------------------------------------------------------
# 2. Compressor (v1 prompt compression)
# ------------------------------------------------------------
def compress(text: str, aggressive: bool = True) -> str:
    """
    Convert natural language to CedrLang.
    aggressive=True removes stopwords & applies symbol substitution.
    """
    if not text:
        return ""

    # lower only for pattern matching; keep original case for identifiers
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
# 4. CedrLang v2 Compilation & Decompilation (Document Mode)
# ------------------------------------------------------------
def capitalize_word(w: str) -> str:
    """Capitalize the first alphabetic character in the word/phrase."""
    if " " in w:
        return " ".join(capitalize_word(part) for part in w.split(" "))
    chars = list(w)
    for i, c in enumerate(chars):
        if c.isalpha():
            chars[i] = c.upper()
            break
    return "".join(chars)

def lowercase_word(w: str) -> str:
    return w.lower()

def uppercase_word(w: str) -> str:
    return w.upper()

def is_capitalized(w: str) -> bool:
    """True if the first alphabetic character is uppercase."""
    for c in w:
        if c.isalpha():
            return c.isupper()
    return False

def apply_casing(src: str, dst: str) -> str:
    """Apply the casing of src to dst strictly."""
    if src.isupper():
        return uppercase_word(dst)
    if is_capitalized(src):
        return capitalize_word(dst)
    return lowercase_word(dst)

def translate_text_raw(text: str, to_compressed: bool) -> str:
    """Perform dictionary mapping translations preserving casing."""
    if to_compressed:
        # human -> compressed (sort by length descending of human term)
        sorted_mappings = sorted(MAPPINGS, key=lambda x: len(x[0]), reverse=True)
        for human, comp in sorted_mappings:
            pattern = re.compile(r'\b' + re.escape(human) + r'\b', re.IGNORECASE)
            text = pattern.sub(lambda m: apply_casing(m.group(0), comp), text)
    else:
        # compressed -> human (sort by length descending of compressed term)
        sorted_mappings = sorted(MAPPINGS, key=lambda x: len(x[1]), reverse=True)
        for human, comp in sorted_mappings:
            pattern = re.compile(r'\b' + re.escape(comp) + r'\b', re.IGNORECASE)
            text = pattern.sub(lambda m: apply_casing(m.group(0), human), text)
    return text

def translate_line(line: str, to_compressed: bool) -> str:
    """Translate a single line protecting syntax and structures."""
    placeholders = []

    def add_placeholder(val: str) -> str:
        ph = f"§§PL_{len(placeholders)}§§"
        placeholders.append((ph, val))
        return ph

    # Protect inline code
    line = re.sub(r'`[^`]+`', lambda m: add_placeholder(m.group(0)), line)

    # Protect HTML tags
    line = re.sub(r'<[^>]+>', lambda m: add_placeholder(m.group(0)), line)

    # Protect markdown links [text](url)
    def link_repl(match):
        text = match.group(1)
        url = match.group(2)
        translated_text = translate_text_raw(text, to_compressed)
        return add_placeholder(f"[{translated_text}]({url})")
    line = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', link_repl, line)

    # Protect markdown bold/emphasis **text**, *text*, __text__, _text_
    def bold_repl_2(match):
        text = match.group(1)
        translated_text = translate_text_raw(text, to_compressed)
        return add_placeholder(f"**{translated_text}**")

    def bold_repl_1(match):
        text = match.group(1)
        translated_text = translate_text_raw(text, to_compressed)
        return add_placeholder(f"*{translated_text}*")

    def bold_repl_under2(match):
        text = match.group(1)
        translated_text = translate_text_raw(text, to_compressed)
        return add_placeholder(f"____{translated_text}____")  # double underline wrapper to keep distinct

    def bold_repl_under1(match):
        text = match.group(1)
        translated_text = translate_text_raw(text, to_compressed)
        return add_placeholder(f"_{translated_text}_")

    line = re.sub(r'\*\*([^*]+)\*\*', bold_repl_2, line)
    line = re.sub(r'\*([^*]+)\*', bold_repl_1, line)
    line = re.sub(r'__([^_]+)__', bold_repl_under2, line)
    line = re.sub(r'_([^_]+)_', bold_repl_under1, line)

    # Protect paths and filenames
    path_regex = r'\b(?:~?/)?[\w\-]+(?:/[\w\-]+)*\.(?:py|js|json|md|yaml|sh|txt|yml|db|jsonl|wasm|html|cffi)\b|\b/?[\w\-]+/[\w\-\./]+\b'
    line = re.sub(path_regex, lambda m: add_placeholder(m.group(0)), line)

    # Protect decimals
    line = re.sub(r'\b\d+\.\d+\b', lambda m: add_placeholder(m.group(0)), line)

    # Perform main translations on the remaining unprotected text
    line = translate_text_raw(line, to_compressed)

    # Restore placeholders in reverse order
    for ph, orig in reversed(placeholders):
        # Unwrap special double underline bold markup back to standard __text__
        if orig.startswith("____") and orig.endswith("____"):
            content = orig[4:-4]
            orig = f"__{content}__"
        line = line.replace(ph, orig)

    return line

def compile_doc(text: str) -> str:
    """Compile human-readable markdown into CedrLang compressed markdown."""
    lines = text.splitlines(keepends=True) if isinstance(text, str) else []
    compiled_lines = []
    in_fenced_code = False

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("```"):
            in_fenced_code = not in_fenced_code
            compiled_lines.append(line)
        elif in_fenced_code:
            compiled_lines.append(line)
        else:
            compiled_lines.append(translate_line(line, to_compressed=True))

    return "".join(compiled_lines)

def decompile_doc(text: str) -> str:
    """Decompile CedrLang compressed markdown into human-readable markdown."""
    lines = text.splitlines(keepends=True) if isinstance(text, str) else []
    decompiled_lines = []
    in_fenced_code = False

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("```"):
            in_fenced_code = not in_fenced_code
            decompiled_lines.append(line)
        elif in_fenced_code:
            decompiled_lines.append(line)
        else:
            decompiled_lines.append(translate_line(line, to_compressed=False))

    return "".join(decompiled_lines)

# ------------------------------------------------------------
# 5. Token counter & Utilities
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
# 6. DeepCLI integration (proxy filter)
# ------------------------------------------------------------
def deepcli_filter(prompt: str) -> str:
    """Hook for deepcli – compress user prompt before sending to API."""
    return compress(prompt, aggressive=True)


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

    # compile command (v2 compilation)
    p_compile = subparsers.add_parser("compile", help="Compile human readable markdown to CedrLang compressed markdown")
    p_compile.add_argument("file_or_text", nargs="*", help="File path or text to compile")
    p_compile.add_argument("-o", "--output", help="Output file path")

    # decompile command (v2 decompilation)
    p_decompile = subparsers.add_parser("decompile", help="Decompile CedrLang compressed markdown to human readable markdown")
    p_decompile.add_argument("file_or_text", nargs="*", help="File path or text to decompile")
    p_decompile.add_argument("-o", "--output", help="Output file path")

    # stats command
    p_stats = subparsers.add_parser("stats", help="Show token savings stats")
    p_stats.add_argument("original", help="Original natural language")
    p_stats.add_argument("--compressed", help="Optional compressed text (otherwise compress automatically)")

    # serve command (minimal proxy for piping)
    p_serve = subparsers.add_parser("serve", help="Read stdin, compress, write stdout (for integration)")

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

    elif args.command == "compile":
        input_str = ""
        if args.file_or_text:
            path_candidate = " ".join(args.file_or_text)
            if Path(path_candidate).exists():
                input_str = Path(path_candidate).read_text()
            else:
                input_str = path_candidate
        else:
            input_str = sys.stdin.read()

        if not input_str:
            print("Error: No input text or file", file=sys.stderr)
            sys.exit(1)

        result = compile_doc(input_str)

        if args.output:
            Path(args.output).write_text(result)
        else:
            print(result, end="")

    elif args.command == "decompile":
        input_str = ""
        if args.file_or_text:
            path_candidate = " ".join(args.file_or_text)
            if Path(path_candidate).exists():
                input_str = Path(path_candidate).read_text()
            else:
                input_str = path_candidate
        else:
            input_str = sys.stdin.read()

        if not input_str:
            print("Error: No input text or file", file=sys.stderr)
            sys.exit(1)

        result = decompile_doc(input_str)

        if args.output:
            Path(args.output).write_text(result)
        else:
            print(result, end="")

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
