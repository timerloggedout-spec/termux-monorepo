import json, subprocess, sys
from pathlib import Path
ROOT=Path(__file__).parents[1]
SCRIPT=ROOT/"scripts/agentic/build_knowledge_fabric_manifest.py"

def test_redacted_cross_repo_manifest(tmp_path):
    source=tmp_path/"repos.json"; output=tmp_path/"manifest.json"
    source.write_text(json.dumps([
        {"full_name":"o/a","default_branch":"main","has_wiki":True,"archived":False,"fork":False},
        {"full_name":"o/archived","default_branch":"main","has_wiki":True,"archived":True,"fork":False},
    ]))
    subprocess.run([sys.executable,str(SCRIPT),"--repos",str(source),"--output",str(output),"--include-devin"],check=True)
    result=json.loads(output.read_text())
    assert result["count"]==1
    entry=result["repositories"][0]
    assert entry["repo"]=="o/a"
    assert entry["devinwiki"]["status"]=="provider-check-required"
    assert entry["wiki_rs"]["status"]=="validation-and-manifest"
    assert entry["deepwiki_rs"]["engine"]=="sopaco/deepwiki-rs"
    assert entry["deepwiki_rs"]["release"]=="1.6.0"
    serialized=json.dumps(result).lower()
    assert "token" not in serialized
    assert "private_key" not in serialized
