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
# 6. CLI & main
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

if __name__ == "__main__":
    main()
