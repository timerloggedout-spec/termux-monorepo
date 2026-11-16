python3 << 'PYEOF'
import pathlib
p = pathlib.Path.home() / 'archwiz/live_view.py'
src = p.read_text()

# Increase sleep between refreshes and add a guard against zero-message loops
src = src.replace("time.sleep(2)", "time.sleep(5)")
src = src.replace("time.sleep(1)", "time.sleep(3)")

# Add a guard: don't refresh if we just did
old_loop = "while True:\n            # Fetch latest messages"
new_loop = """fetch_count = 0
        while True:
            fetch_count += 1
            if fetch_count % 3 != 0:
                time.sleep(5)
                continue
            # Fetch latest messages"""
src = src.replace(old_loop, new_loop)

p.write_text(src)
print("Live View patched: slower refresh, no spin loop.")
PYEOF