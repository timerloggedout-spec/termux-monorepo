#!/usr/bin/env python3
"""Backfill ELO ratings by analyzing existing conversations for refactor patterns."""
import sys, json, re
from pathlib import Path
from datetime import datetime, timezone

HOME = Path.home()
sys.path.insert(0, str(HOME / 'cli-synthegration'))
from success_metrics import RefactorELO, ComplexityEstimator
from synthegration_index import MessageIndex

EXPORT = HOME / 'storage/downloads/_doing/_1-build/DeepSeek/exports/deepseek_data-2026-05-17/conversations.json'
elo = RefactorELO()
comp = ComplexityEstimator()

def extract_refactor_pairs(conversation):
    """Walk mapping tree, find user→assistant pairs where code was generated."""
    mapping = conversation.get('mapping', {})
    nodes = {}
    for nid, node in mapping.items():
        msg = node.get('message')
        if not msg:
            continue
        fragments = msg.get('fragments', [])
        for frag in fragments:
            ftype = frag.get('type', '')
            if 'REQUEST' in ftype or 'RESPONSE' in ftype:
                nodes[nid] = {
                    'id': nid,
                    'parent': node.get('parent'),
                    'role': 'user' if 'REQUEST' in ftype else 'assistant',
                    'content': frag.get('content', ''),
                    'timestamp': msg.get('inserted_at', '')
                }
                break  # one fragment per node for scoring

    pairs = []
    for nid, node in nodes.items():
        if node['role'] != 'assistant':
            continue
        # Find the user request that triggered this
        user_nid = node['parent']
        if user_nid not in nodes:
            continue
        user_node = nodes[user_nid]
        if user_node['role'] != 'user':
            continue

        # Check if assistant response contains a code block
        assistant_content = node['content']
        code_blocks = re.findall(r'```(\w+)?\n(.*?)```', assistant_content, re.DOTALL)
        if not code_blocks:
            continue

        # Check if conversation continued after this (success signal)
        conversation_continued = any(
            n['parent'] == nid for n in nodes.values()
        )

        # Check title for success indicators
        title = (conversation.get('title') or '').lower()
        title_success = any(w in title for w in [
            'refactor', 'fix', 'implement', 'build', 'complete',
            'success', 'working', 'solution', 'finished'
        ])

        # Score: continuation = strong success, title match = moderate
        success_score = 0.0
        if conversation_continued:
            success_score += 0.6
        if title_success:
            success_score += 0.4
        # If conversation continued past multiple messages, very likely success
        continued_count = sum(1 for n in nodes.values() if n['parent'] == nid)
        if continued_count >= 2:
            success_score = min(1.0, success_score + 0.2)

        success = success_score >= 0.5
        language = code_blocks[0][0] or 'text'
        code = code_blocks[0][1]
        complexity_level, _ = comp.estimate(code)
        effort = {'low': 1, 'medium': 3, 'high': 5}.get(complexity_level, 2)

        pairs.append({
            'prompt': user_node['content'],
            'language': language,
            'success': success,
            'effort': effort,
            'score': success_score,
            'title': conversation.get('title', ''),
            'session_id': conversation.get('id', ''),
            'continued': conversation_continued,
            'timestamp': node['timestamp']
        })

    return pairs

def main():
    print("Loading export...")
    with open(EXPORT) as f:
        data = json.load(f)

    conversations = data if isinstance(data, list) else data.get('conversations', [])
    total_pairs = 0
    successful = 0

    print(f"Processing {len(conversations)} conversations...")
    for i, conv in enumerate(conversations):
        if i % 50 == 0:
            print(f"  {i}/{len(conversations)}...")
        pairs = extract_refactor_pairs(conv)
        for p in pairs:
            total_pairs += 1
            if p['success']:
                successful += 1
            elo.update(p['prompt'], p['language'], p['success'], p['effort'])

    print(f"\nBackfill complete:")
    print(f"  Total refactor pairs: {total_pairs}")
    print(f"  Successful: {successful}")
    print(f"  Success rate: {successful/max(total_pairs,1)*100:.1f}%")
    print(f"  ELO moving average: {elo.moving_average(window=100):.2f}")
    print(f"  Top 5 ELO patterns:")
    for h, rating in elo.top_patterns(5):
        print(f"    {h}: {rating:.0f}")

if __name__ == '__main__':
    main()
