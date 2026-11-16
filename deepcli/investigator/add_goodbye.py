#!/usr/bin/env python3
"""Replace static /quit message with cycling motivational goodbyes."""
import random

TUI = '/data/data/com.termux/files/home/deepcli-tui/tui.py'
with open(TUI) as f:
    content = f.read()

goodbye_list = '''GOODBYES = [
    "Keep shipping. 🚀",
    "Your future self is already proud. 💪🏽",
    "Code hard, stay humble. 🌿",
    "One session closer to mastery. 🔥",
    "Rest, then build again. ⚡",
    "The terminal never truly closes. 🖥️",
    "See you in the next branch. 🌱",
    "gg wp – now go make something. 🎯",
]'''

# Insert GOODBYES list near the top after imports
old_import_end = 'readline.set_completer(_smart_completer)\nreadline.parse_and_bind("tab: complete")'
new_import_end = old_import_end + '\n\n' + goodbye_list
content = content.replace(old_import_end, new_import_end)

# Replace "Goodbye!" in prompt_session_id
content = content.replace(
    'console.print("Goodbye!")',
    'console.print(random.choice(GOODBYES))'
)

# Replace break on /quit /exit in main loop
old_quit = '''if user_input.lower() in ['exit', 'quit', '/quit']:
            break'''
new_quit = '''if user_input.lower() in ['exit', 'quit', '/quit']:
            console.print(random.choice(GOODBYES))
            time.sleep(0.8)
            break'''
content = content.replace(old_quit, new_quit)

# Add import random if not present
if 'import random' not in content:
    content = content.replace('import time\n', 'import time\nimport random\n')

with open(TUI, 'w') as f:
    f.write(content)
print("✅ Motivational goodbyes added.")
