python3 << 'PYEOF'
import pathlib
p = pathlib.Path.home() / 'archwiz/live_view.py'
src = p.read_text()
# Heal the raw newline in the regex
src = src.replace(
    "for match in re.finditer(r'\n",
    "for match in re.finditer(r'\\n"
)
p.write_text(src)
print("Regex healed.")
PYEOF
python3 -c "import py_compile; py_compile.compile('/data/data/com.termux/files/home/archwiz/live_view.py', doraise=True)" && echo "✅ Panel compiles" || echo "❌ Syntax error"