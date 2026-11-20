#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ERROR EXTR4CT0R 9000 ⚡🧬
Streams message_index.json / session_store files, extracts error patterns,
builds JSONL database + queryable interface.
"""

import json
import re
import sys
import argparse
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Generator, Any
from collections import defaultdict

# ┌────────────────────────────────────────────────────────────────────┐
# │   C0R3 P4TT3RN5 – 1337 SP3@K M0D3                                 │
# └────────────────────────────────────────────────────────────────────┘
ERROR_PATTERNS = re.compile(
    r'(Traceback|Error:|Exception:|FAILED|curl: \(|\bSyntaxError\b|\bIndentationError\b|\bNameError\b|'
    r'\bTypeError\b|\bOSError\b|\bFileNotFoundError\b|\bValueError\b|\bKeyError\b|\bAttributeError\b|'
    r'\bRuntimeError\b|\bImportError\b|\bModuleNotFoundError\b|\bConnectionError\b|\bTimeoutError\b)',
    re.IGNORECASE
)

# ┌────────────────────────────────────────────────────────────────────┐
# │   STR34M1NG P4RS3R – 0N TH3 FLY                                    │
# └────────────────────────────────────────────────────────────────────┘
def stream_jsonl_objects(filepath: Path) -> Generator[Dict, None, None]:
    """Yields JSON objects from .jsonl or .json (if array/obj per line)."""
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        for lineno, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
                yield obj
            except json.JSONDecodeError:
                # attempt to parse whole file as single JSON array
                f.seek(0)
                try:
                    data = json.load(f)
                    if isinstance(data, list):
                        for item in data:
                            yield item
                    elif isinstance(data, dict):
                        yield data
                except json.JSONDecodeError:
                    pass
                break

def extract_errors_from_session(obj: Dict, session_id: str) -> List[Dict]:
    """Extract errors from a single session object."""
    errors = []
    timestamp = obj.get('timestamp') or obj.get('created_at') or obj.get('time') or ''
    messages = obj.get('messages') or obj.get('chat_history') or obj.get('conversation') or []
    
    # If no messages array but direct log lines
    if not messages and isinstance(obj, dict):
        # treat entire obj as context
        messages = [{'role': 'unknown', 'content': json.dumps(obj)}]
    
    for idx, msg in enumerate(messages):
        if not isinstance(msg, dict):
            msg = {'role': 'unknown', 'content': str(msg)}
        
        role = msg.get('role', 'unknown')
        content = msg.get('content', '')
        if not isinstance(content, str):
            content = str(content)
        
        lines = content.splitlines()
        prev_user_msg = _get_prev_user_message(messages, idx)
        
        i = 0
        while i < len(lines):
            line = lines[i]
            if ERROR_PATTERNS.search(line):
                # collect error block (traceback)
                error_block_lines = [line]
                j = i + 1
                while j < len(lines) and (lines[j].startswith(' ') or lines[j].startswith('\t') or 
                                          lines[j].startswith('File ') or '^' in lines[j] or
                                          not lines[j].strip() or lines[j].strip().startswith('<')):
                    error_block_lines.append(lines[j])
                    j += 1
                
                error_type = _extract_error_type(line, error_block_lines)
                error_message = '\n'.join(error_block_lines[:20])  # cap at 20 lines
                
                errors.append({
                    'session_id': session_id,
                    'timestamp': timestamp,
                    'error_type': error_type,
                    'error_message': error_message,
                    'context': prev_user_msg,
                    'role': role
                })
                i = j
            else:
                i += 1
    return errors

def _get_prev_user_message(messages: List[Dict], current_idx: int) -> str:
    """Get content of preceding user message."""
    for k in range(current_idx - 1, -1, -1):
        if messages[k].get('role') == 'user':
            raw = messages[k].get('content', '')
            if isinstance(raw, str):
                return raw[:500]  # truncate
            return str(raw)[:500]
    return ''

def _extract_error_type(first_line: str, block_lines: List[str]) -> str:
    """Extract specific error type from line or block."""
    # direct match
    for pattern in ['SyntaxError', 'IndentationError', 'NameError', 'TypeError', 
                    'OSError', 'FileNotFoundError', 'ValueError', 'KeyError',
                    'AttributeError', 'RuntimeError', 'ImportError', 'ModuleNotFoundError',
                    'ConnectionError', 'TimeoutError', 'curl:', 'Traceback']:
        if pattern in first_line:
            return pattern
    # fallback: first word after error keywords
    match = re.search(r'(Error:|Exception:|FAILED|curl:)\s*(\S+)', first_line, re.IGNORECASE)
    if match:
        return match.group(2).rstrip(':')
    return 'UnknownError'

# ┌────────────────────────────────────────────────────────────────────┐
# │   BU1LD D4T4B4S3 – JSONL OUT                                      │
# └────────────────────────────────────────────────────────────────────┘
def build_error_database(input_paths: List[Path], output_file: Path) -> int:
    """Scan all input files, write errors.jsonl, return error count."""
    total_errors = 0
    session_counter = 0
    
    with open(output_file, 'w', encoding='utf-8') as out_f:
        for input_path in input_paths:
            if not input_path.exists():
                print(f"[!] SK1P: {input_path} not found", file=sys.stderr)
                continue
            
            # determine if it's a session_store file (multiple sessions)
            data = None
            try:
                with open(input_path, 'r', encoding='utf-8', errors='ignore') as f:
                    data = json.load(f)
            except:
                pass
            
            if data and isinstance(data, dict):
                # single session file
                sess_id = input_path.stem
                errors = extract_errors_from_session(data, sess_id)
                for err in errors:
                    out_f.write(json.dumps(err) + '\n')
                total_errors += len(errors)
                session_counter += 1
            else:
                # stream as JSONL or array-of-obj
                for obj in stream_jsonl_objects(input_path):
                    # try to get session_id from object
                    sess_id = obj.get('session_id') or obj.get('id') or f"session_{session_counter}"
                    errors = extract_errors_from_session(obj, str(sess_id))
                    for err in errors:
                        out_f.write(json.dumps(err) + '\n')
                    total_errors += len(errors)
                    session_counter += 1
    
    return total_errors

# ┌────────────────────────────────────────────────────────────────────┐
# │   QU3RY4BL3 1NT3RF4C3 – error-query                               │
# └────────────────────────────────────────────────────────────────────┘
def query_database(db_path: Path, search_term: str, case_sensitive: bool = False) -> List[Dict]:
    """Search errors.jsonl for search_term."""
    results = []
    if not db_path.exists():
        return results
    
    flag = 0 if case_sensitive else re.IGNORECASE
    pattern = re.compile(re.escape(search_term), flag)
    
    with open(db_path, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                err = json.loads(line)
                haystack = f"{err.get('error_type','')} {err.get('error_message','')} {err.get('context','')}"
                if pattern.search(haystack):
                    results.append(err)
            except json.JSONDecodeError:
                continue
    return results

def main():
    parser = argparse.ArgumentParser(
        description='🔮 3RR0R 3XTR4CT0R & QU3RY – Build error DB and search it.',
        usage='''usage: %(prog)s <command> [options]

Commands:
  build   <file_or_dir> [output.jsonl]   – Extract errors to JSONL database
  query   <search_term>                  – Query existing errors.jsonl
'''
    )
    subparsers = parser.add_subparsers(dest='command', required=True)
    
    # BUILD command
    build_parser = subparsers.add_parser('build', help='Build error database from sessions')
    build_parser.add_argument('input', nargs='+', help='Files/directories to scan (message_index.json, session_store, *.jsonl)')
    build_parser.add_argument('-o', '--output', default='errors.jsonl', help='Output JSONL file (default: errors.jsonl)')
    
    # QUERY command
    query_parser = subparsers.add_parser('query', help='Query error database')
    query_parser.add_argument('search_term', help='Text to search for in error messages')
    query_parser.add_argument('-i', '--ignore-case', action='store_true', default=True, help='Case-insensitive (default)')
    query_parser.add_argument('-s', '--case-sensitive', action='store_true', help='Case-sensitive search')
    query_parser.add_argument('-d', '--db', default='errors.jsonl', help='Path to errors.jsonl (default: errors.jsonl)')
    query_parser.add_argument('--format', choices=['json', 'pretty'], default='pretty', help='Output format')
    
    args = parser.parse_args()
    
    if args.command == 'build':
        input_paths = []
        for item in args.input:
            p = Path(item)
            if p.is_dir():
                input_paths.extend(p.glob('*.json') if p.glob('*.json') else p.glob('*.jsonl'))
                input_paths.extend(p.glob('session_store*'))
                input_paths.extend(p.glob('message_index*'))
            else:
                input_paths.append(p)
        
        # remove duplicates
        input_paths = list(set(input_paths))
        
        if not input_paths:
            print("[!] N0 1NPUT F1L3S F0UND.", file=sys.stderr)
            sys.exit(1)
        
        print(f"[*] Scanning {len(input_paths)} files...")
        total = build_error_database(input_paths, Path(args.output))
        print(f"[✔] D0N3! {total} errors extracted -> {args.output}")
        
    elif args.command == 'query':
        case_sensitive = args.case_sensitive
        results = query_database(Path(args.db), args.search_term, case_sensitive)
        
        if not results:
            print(f"[!] N0 M4TCH3S F0UND F0R '{args.search_term}'")
            sys.exit(0)
        
        if args.format == 'json':
            print(json.dumps(results, indent=2))
        else:
            print(f"\n🔍 F0UND {len(results)} error(s):\n")
            for i, err in enumerate(results, 1):
                print(f"───── [{i}] ─────────────────────────────────────────")
                print(f"📌 Session: {err.get('session_id', 'N/A')}")
                print(f"⏱️  Timestamp: {err.get('timestamp', 'N/A')}")
                print(f"🔥 Error Type: {err.get('error_type', 'Unknown')}")
                print(f"💬 Context (prev user msg):\n    {err.get('context', 'N/A')[:200]}")
                print(f"⚠️  Message:\n{err.get('error_message', '')[:500]}")
                print()
    
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == '__main__':
    main()
