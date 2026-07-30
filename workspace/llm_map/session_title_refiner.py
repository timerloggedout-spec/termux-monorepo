#!/usr/bin/env python3
"""Propose a better session title by extracting top keywords from all messages."""
import json, sys, re
from pathlib import Path
from collections import Counter

HOME = Path.home()
MI = HOME / 'cli-synthegration/codex/message_index.json'
STOP_WORDS = {'the', 'a', 'an', 'is', 'to', 'in', 'for', 'of', 'and', 'or', 'this', 'that', 'it', 'with', 'on', 'be', 'we', 'can', 'will', 'have', 'has', 'are', 'not', 'but', 'from', 'they', 'you', 'i', 'he', 'she', 'as', 'by', 'at', 'all', 'no', 'if', 'so', 'me', 'my'}

def keywords(text):
    words = re.findall(r'[a-zA-Z]{4,}', text.lower())
    return [w for w in words if w not in STOP_WORDS]

def propose_title(session_id):
    with open(MI) as f:
        data = json.load(f)
    if session_id not in data:
        print(f"Session {session_id} not found in message_index.")
        return
    messages = data[session_id]
    all_text = ' '.join([m.get('content', '') for m in messages if isinstance(m, dict)])
    counter = Counter(keywords(all_text))
    top = [word for word, _ in counter.most_common(8)]
    return ' '.join(top[:5]).title()

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python3 session_title_refiner.py <session_id>")
        sys.exit(1)
    sid = sys.argv[1]
    title = propose_title(sid)
    if title:
        print(f"Original title: (first user message)")
        print(f"Proposed title: {title}")
