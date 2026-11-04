import importlib.util, io, json, sys
from contextlib import redirect_stdout
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.github-app-publisher/bin")
import github_app_publisher as pub
TOK = pub.mint_token()["token"]
class FakeFP:
    def __init__(self, data=b""): self._d = data
    def write(self, s): self._d = s.encode() if isinstance(s, str) else s
    def read(self): return self._d
    def __enter__(self): return self
    def __exit__(self, *a): return False
STATE = {"data": None}
def v_open(path, mode="r", *a, **k):
    if "quota_preflight.py" in str(path) and "r" in mode:
        return FakeFP(TOK)
    if "quota_preflight.py" in str(path) and "w" in mode:
        fp = FakeFP()
        orig_write = fp.write
        def w2(s):
            STATE["data"] = s.encode() if isinstance(s, str) else s
            return orig_write(s)
        fp.write = w2
        return fp
    return io.open(path, mode, *a, **k)
import builtins
real_open = builtins.open
def patched(path, mode="r", *a, **k):
    if "quota_preflight.py" in str(path):
        if "r" in mode: return FakeFP(TOK)
        if "w" in mode:
            fp = FakeFP()
            ow = fp.write
            def w2(s):
                STATE["data"] = s.encode() if isinstance(s, str) else s
                return ow(s)
            fp.write = w2
            return fp
    return real_open(path, mode, *a, **k)
builtins.open = patched
spec = importlib.util.spec_from_file_location("quota_preflight", "/home/hatch/workspace/scratch/cons/scripts/quota_preflight.py")
mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
buf = io.StringIO()
try:
    with redirect_stdout(buf):
        sys.argv = ["quota_preflight.py", "--batch", "30", "--publisher-token-file", "/home/hatch/workspace/scratch/cons/scripts/quota_preflight.py"]
        code = mod.main()
except SystemExit as e:
    code = e.code
print("VERDICT_LINE:", buf.getvalue().strip().splitlines()[-1] if buf.getvalue().strip() else "(none)")
print("gate_exit:", code)
