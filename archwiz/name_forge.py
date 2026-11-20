#!/usr/bin/env python3
"""Name Forge — suggest tool names from the full ArchWiz Grimoire."""
import re, sys
from pathlib import Path

HOME = Path.home()
GRIMOIRE = HOME / 'harmony_hub/config/grimoire/1337_D1CT10N4RY.md'

def load_all_terms():
    """Parse Core Castings and Grimoire Protocol tables."""
    terms = []
    if not GRIMOIRE.exists():
        return terms
    text = GRIMOIRE.read_text()
    current_section = None
    for line in text.splitlines():
        if '## Core Castings' in line:
            current_section = 'core'
            continue
        if '## Grimoire Protocol' in line:
            current_section = 'system'
            continue
        if current_section and line.startswith('|') and not line.startswith('|--') and not line.startswith('| 🪄 Term'):
            cols = [c.strip() for c in line.split('|')[1:-1]]
            if current_section == 'core' and len(cols) >= 2 and cols[0] not in ('Term', ''):
                terms.append((cols[0], cols[1], ''))  # term, meaning, no leet variant in core
            elif current_section == 'system' and len(cols) >= 3 and cols[0] not in ('🪄 Term', ''):
                terms.append((cols[0], cols[1], cols[2]))  # term, meaning, leet variant
        if current_section and not line.startswith('|') and line.strip():
            current_section = None
    return terms

def suggest(concept):
    terms = load_all_terms()
    if not terms:
        print("No terms loaded from Grimoire.")
        return
    concept_words = concept.lower().split()
    matches = []
    for term, meaning, leet in terms:
        score = 0
        term_lower = term.lower()
        meaning_lower = meaning.lower()
        leet_lower = leet.lower() if leet else ''
        for w in concept_words:
            if w in term_lower: score += 4
            if w in meaning_lower: score += 3
            if w in leet_lower: score += 2
        if score > 0:
            matches.append((score, term, meaning, leet))
    matches.sort(key=lambda x: -x[0])
    print(f"\n🔥 Name Forge — suggestions for '{concept}'\n")
    if matches:
        for score, term, meaning, leet in matches[:10]:
            leet_str = f"  →  {leet}" if leet else ''
            print(f"  🪄 {term:<15s}  {meaning:<25s}{leet_str}")
    else:
        print("  No direct matches. Try a different concept word.")
        print("  Available terms:", ', '.join(t[0] for t in terms[:15]))

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: name_forge.py <concept>")
        sys.exit(1)
    suggest(' '.join(sys.argv[1:]))
