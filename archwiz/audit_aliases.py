import re, os

rcfile = os.path.expanduser("~/.zshrc")
with open(rcfile) as f:
    lines = f.readlines()

seen = {}   # name -> list of (line_number, line_text)

for i, line in enumerate(lines, 1):
    # alias name=...
    m = re.match(r'^alias\s+([^=]+)=', line)
    if not m:
        # bare assignments that look like alias: name=... with a command path
        m = re.match(r'^(\w[\w_-]*)=(.*)', line)
        if m and not line.startswith(('#', 'export', 'typeset', 'function', 'if', 'for', 'PATH')):
            val = m.group(2)
            if any(cmd in val for cmd in ['python3', 'bash', 'cd ', 'jq', '~/', './']):
                pass  # treat as alias
            else:
                m = None
    if m:
        name = m.group(1).strip()
        seen.setdefault(name, []).append((i, line.rstrip()))

# Also functions
for i, line in enumerate(lines, 1):
    m = re.match(r'(?:function\s+)?(\w[\w_-]*)\s*\(\)\s*\{', line)
    if m:
        name = m.group(1)
        seen.setdefault(name, []).append((i, line.rstrip()))

print("=== Duplicate Aliases/Functions in .zshrc ===\n")
for name, occurrences in sorted(seen.items()):
    if len(occurrences) > 1:
        print(f"{name}:")
        for ln, txt in occurrences:
            print(f"  line {ln:4d}: {txt}")
        print()
