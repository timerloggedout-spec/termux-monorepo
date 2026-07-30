import re, os, sys

STRATEGY = "last"  # change to "first" if you want first wins

rcfile = os.path.expanduser("~/.zshrc")
outfile = os.path.expanduser("~/.zshrc.clean")

with open(rcfile) as f:
    lines = f.readlines()

# Pass 1: map name -> list of (line_index, line_text)
aliases = {}
functions = {}
for i, line in enumerate(lines):
    # Skip comments and empty lines for mapping purposes? We'll keep them.
    m = re.match(r'^alias\s+([^=]+)=', line)
    if not m:
        m = re.match(r'^(\w[\w_-]*)=(.*)', line)
        if m and not line.startswith(('#', 'export', 'typeset', 'function', 'if', 'for', 'PATH', 'setopt')):
            val = m.group(2)
            if any(cmd in val for cmd in ['python3', 'bash', 'cd ', 'jq', '~/', './']):
                pass  # treat as alias
            else:
                m = None
    if m:
        name = m.group(1).strip()
        aliases.setdefault(name, []).append(i)

    m = re.match(r'(?:function\s+)?(\w[\w_-]*)\s*\(\)\s*\{', line)
    if m:
        name = m.group(1)
        functions.setdefault(name, []).append(i)

# Determine indices to remove
remove_indices = set()
for name, indices in aliases.items():
    if len(indices) > 1:
        if STRATEGY == "last":
            keep = indices[-1]
        else:
            keep = indices[0]
        for idx in indices:
            if idx != keep:
                remove_indices.add(idx)
for name, indices in functions.items():
    if len(indices) > 1:
        if STRATEGY == "last":
            keep = indices[-1]
        else:
            keep = indices[0]
        for idx in indices:
            if idx != keep:
                remove_indices.add(idx)

# Also remove any bare variable assignments that duplicate aliases? 
# The above already catches bare assignments if they look like alias commands.
# We'll also remove empty lines at the end? No.

# Write clean file
with open(outfile, 'w') as f:
    for i, line in enumerate(lines):
        if i not in remove_indices:
            f.write(line)

print(f"✅ Clean .zshrc written to {outfile}")
print(f"   Strategy: {STRATEGY}")
print(f"   Removed {len(remove_indices)} duplicate lines.")
