import subprocess,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class FossRegistryContractTests(unittest.TestCase):
    def test_registry_json(self):
        import json
        for rel in ('docs/ops/FOSS-FORESIGHT-PROCUREMENT-REGISTRY.json','docs/schemas/FOSS-RESOURCE-EVIDENCE.schema.json'):
            with (ROOT/rel).open(encoding='utf-8') as h: json.load(h)
    def test_validator(self):
        r=subprocess.run([sys.executable,str(ROOT/'scripts/ci/verify_foss_registry.py')],cwd=ROOT,capture_output=True,text=True)
        self.assertEqual(r.returncode,0,r.stdout+r.stderr)
if __name__=='__main__': unittest.main()
