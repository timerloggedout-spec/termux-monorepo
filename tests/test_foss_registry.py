import subprocess,sys,unittest,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

class FossRegistryContractTests(unittest.TestCase):
    def test_registry_json(self):
        for rel in (
            'docs/ops/FOSS-FORESIGHT-PROCUREMENT-REGISTRY.json',
            'docs/schemas/FOSS-RESOURCE-EVIDENCE.schema.json',
            'config/foresight_digest_sources.json',
            'config/agent_stack_integrations.json',
        ):
            with (ROOT/rel).open(encoding='utf-8') as h:
                json.load(h)

    def test_agent_stack_wiring(self):
        with (ROOT/'config/agent_stack_integrations.json').open(encoding='utf-8') as h:
            cfg=json.load(h)
        ids={x['id'] for x in cfg['integrations']}
        self.assertTrue({'otel-core','wso2-agent-manager','nvidia-openshell','orchbench-preflight','nist-ir8536-provenance','llama-cpp-vulkan','needle-3-cactus'} <= ids)
        states={x['id']:x['status'] for x in cfg['integrations']}
        self.assertEqual(states['otel-core'],'ADOPT')
        self.assertEqual(states['llama-cpp-vulkan'],'HOLD')
        self.assertEqual(states['needle-3-cactus'],'INVESTIGATE')

    def test_validator(self):
        r=subprocess.run([sys.executable,str(ROOT/'scripts/ci/verify_foss_registry.py')],cwd=ROOT,capture_output=True,text=True)
        self.assertEqual(r.returncode,0,r.stdout+r.stderr)

if __name__=='__main__':
    unittest.main()
