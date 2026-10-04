from pathlib import Path
import json
import subprocess
import sys
ROOT=Path(__file__).resolve().parents[1]
SEED=ROOT/'docs/proposals/active/domain-composition-matrix/seed.json'
VALIDATOR=ROOT/'scripts/ci/validate_domain_composition.py'
def test_seed_is_valid():
    r=subprocess.run([sys.executable,str(VALIDATOR)],cwd=ROOT,capture_output=True,text=True)
    assert r.returncode==0, r.stderr
    assert 'domain-composition: OK' in r.stdout
def test_domain_specific_notation_is_not_collapsed():
    d=json.loads(SEED.read_text(encoding='utf-8'))
    surfaces={(x['domain_id'],x['surface']) for x in d['notations']}
    assert ('category_theory','f ; g') in surfaces
    assert ('lean','f ≫ g') in surfaces
    assert ('haskell','m >>= f') in surfaces