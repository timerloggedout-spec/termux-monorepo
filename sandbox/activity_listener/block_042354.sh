python3 << 'PYEOF'
import pathlib, re

p = pathlib.Path.home() / 'archwiz/lexicon_harvest.py'
src = p.read_text()

# 1. Update the review function's command parser to add seed action
# Add 'sN' handler after 'rN' handler
old_reject = "                    print(f\"  Rejected {batch[idx][1]}\")"
new_reject = "                    print(f\"  Rejected {batch[idx][1]}\")\n            elif part.startswith('s') and part[1:].isdigit():\n                idx = int(part[1:]) - 1\n                if 0 <= idx < len(batch):\n                    cid = batch[idx][0]\n                    meaning = input(f\"Seed meaning for {batch[idx][1]}: \").strip()\n                    conn.execute('UPDATE terms SET approved=0, category=?, meaning=? WHERE id=?', ('seed', meaning, cid))\n                    print(f\"  Saved {batch[idx][1]} as seed.\")"
src = src.replace(old_reject, new_reject)

# 2. Update the command prompt to show 'sN' option
old_cmd = "Commands: numbers=approve, rN=reject, eN=edit, bN=bloat session, all=approve all, q=quit, Enter=next page"
new_cmd = "Commands: n=approve, rN=reject, sN=seed, eN=edit, bN=bloat, all=approve all, q=quit, Enter=next"
src = src.replace(old_cmd, new_cmd)

# 3. Update the row display to show category if already set
old_row = """            print(f\"  {G}{idx+1:3d}{N}  {Y}{term:<25s}{N}  {C}{affinity:.1f}{N}  {ctx}\")"""
new_row = """            cat = conn.execute('SELECT category FROM terms WHERE id=?', (cid,)).fetchone()
            cat_str = f\" [{cat[0]}]\" if cat and cat[0] and cat[0] != 'unknown' else \"\"
            print(f\"  {G}{idx+1:3d}{N}  {Y}{term:<25s}{N}  {C}{affinity:.1f}{N}{cat_str}  {ctx}\")"""
src = src.replace(old_row, new_row)

# 4. Add a 'query seed' command to show all seed terms
old_query_help = """    if cmd == 'query':"""
new_query_help = """    if cmd == 'seeds':
        rows = conn.execute('SELECT term, meaning, affinity_score FROM terms WHERE category=\"seed\" ORDER BY affinity_score DESC').fetchall()
        for r in rows:
            print(f\"{r[0]}: {r[1]} (affinity {r[2]:.1f})\")
    elif cmd == 'query':"""
src = src.replace(old_query_help, new_query_help)

# Update usage to mention seeds
src = src.replace(
    "print(\"Usage: lexicon_harvest.py scan|review|correlate|query <term>\")",
    "print(\"Usage: lexicon_harvest.py scan|review|correlate|query <term>|seeds\")"
)

p.write_text(src)
print("Seed category added. Use 'sN' to mark terms as inspirational seeds.")
PYEOF