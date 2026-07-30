python3 << 'PYEOF'
import sys, io, contextlib
from pathlib import Path

HOME = Path.home()
SESSION_ID = '417ddd6d-9711-465d-ab90-c92cc04aeabf'

sys.path.insert(0, str(HOME / 'deepcli'))
from deepcli.core import get_token, stream_completion

# Capture full output including errors
buf = io.StringIO()
try:
    with contextlib.redirect_stdout(buf):
        stream_completion(get_token(), "Diagnostic test from ArchWiz", SESSION_ID, None)
    output = buf.getvalue()
    print("=== STREAM OUTPUT ===")
    print(output[:500] if output else "(empty)")
except Exception as e:
    print(f"=== EXCEPTION ===\n{e}")
PYEOF