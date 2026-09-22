import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

class LayaSweepTests(unittest.TestCase):
    def test_mock_sweep_emits_all_categories(self):
        out=ROOT/"tests"/"_laya_sweep.jsonl"
        try:
            p=subprocess.run([sys.executable,str(ROOT/"scripts/laya_sweep.py"),"--output",str(out)],cwd=ROOT,check=True,capture_output=True,text=True)
            rows=[json.loads(x) for x in out.read_text().splitlines()]
            self.assertEqual(len(rows),6)
            self.assertEqual({r["mode"] for r in rows},{"mock"})
            self.assertTrue({"routing","security","agent","code","ops"} <= {r["category"] for r in rows})
        finally:
            out.unlink(missing_ok=True)

if __name__=="__main__":
    unittest.main()
