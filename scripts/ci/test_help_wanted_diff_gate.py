import importlib.util
from pathlib import Path
spec=importlib.util.spec_from_file_location("gate",Path(__file__).with_name("help_wanted_diff_gate.py"))
gate=importlib.util.module_from_spec(spec); spec.loader.exec_module(gate)
def pr(body=""):
    return {"number":3,"html_url":"https://github.com/o/r/pull/3","body":body,"base":{"sha":"base","repo":{"full_name":"o/r"}},"head":{"sha":"head"}}
def file(name,additions=1,deletions=0): return {"filename":name,"additions":additions,"deletions":deletions}
def test_stake_is_not_solution():
    r=gate.classify(pr("stake only"),[file(gate.STAKE_PATH,8)],"solution"); assert r["stage"]=="STAKE" and not r["gate_pass"]
def test_stake_is_valid_stake():
    r=gate.classify(pr("stake only"),[file(gate.STAKE_PATH,8)],"stake"); assert r["stage"]=="STAKE" and r["gate_pass"]
def test_solution_requires_proof():
    b="### Help-Given Tribute\n- Stage: solution\n- Diff proof: docs checklist\n- Validation: CI"
    r=gate.classify(pr(b),[file("docs/checklist.md",20)],"solution"); assert r["stage"]=="SOLUTION" and r["gate_pass"]
def test_placeholder_plus_solution_requires_proof():
    r=gate.classify(pr("### Help-Given Tribute\n- Stage: solution"),[file(gate.STAKE_PATH,8),file("docs/checklist.md",20)],"solution")
    assert not r["gate_pass"]
