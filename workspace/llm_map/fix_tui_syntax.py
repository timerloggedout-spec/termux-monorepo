from pathlib import Path

tui_path = Path.home() / 'deepcli-tui/tui.py'
content = tui_path.read_text()

# Show the exact characters around line 311
lines = content.split('\n')
for i, line in enumerate(lines[308:315], start=309):
    print(f"{i}: {repr(line)}")

# Fix the literal newline inside input() — replace the exact broken sequence
# The file contains: input("\nPress Enter...
# where \n is an actual newline. We need: input("\\nPress Enter...")
content = content.replace('input("\nPress Enter to continue...")', 'input("\\nPress Enter to continue...")')

# Also fix any remaining broken input("⏎...) patterns with embedded newlines
# Use a more robust approach: read lines, fix the two broken input lines
fixed_lines = []
for line in content.split('\n'):
    if 'input("' in line and 'Press Enter to continue...")' in line:
        # This line has a broken input — replace the entire line with correct version
        indent = line[:len(line) - len(line.lstrip())]
        fixed_lines.append(f'{indent}input("\\nPress Enter to continue...")')
    else:
        fixed_lines.append(line)
content = '\n'.join(fixed_lines)

# Restore the missing sid = create_session(token) line
old_block = '''        if user_input.lower() == '/new':
            parent_id = None
            attached_file_id = None'''
new_block = '''        if user_input.lower() == '/new':
            sid = create_session(token)
            parent_id = None
            attached_file_id = None'''
if old_block in content:
    content = content.replace(old_block, new_block)
    print("✅ Restored create_session line")
else:
    # Try alternative patterns
    for pattern in [
        "if user_input.lower() == '/new':\n            parent_id = None",
        "if user_input.lower() == '/new':\n            parent_id = None\n            attached_file_id = None",
    ]:
        if pattern in content:
            fixed = pattern.replace("parent_id = None", "sid = create_session(token)\n            parent_id = None", 1)
            content = content.replace(pattern, fixed)
            print("✅ Restored create_session line (alt pattern)")
            break

tui_path.write_text(content)
print("✅ Syntax fixed")
