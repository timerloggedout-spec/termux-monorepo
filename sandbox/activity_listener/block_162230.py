# The regex on line 43 is still wounded, and now the indentation is broken too.
# Let's surgically replace the entire extract_blocks function with the correct one.
python3 << 'PYEOF'
import pathlib, re

p = pathlib.Path.home() / 'archwiz/live_view.py'
src = p.read_text()

# Replace the broken extract_blocks function with a clean version
old_func = r"""def extract_blocks(msgs, already):
    out=[]; seen=set()
    for m in msgs:
        if m.get('role','').lower()!='assistant': continue
        mid=str(m.get('message_id',''))
        content=m.get('content','')
        for match in re.finditer(r"