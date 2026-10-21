import hashlib,json,subprocess,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class TestValidateEPS(unittest.TestCase):
 def event(self):
  e={"schema_version":"eps.v1","event_type":"file.modified","occurred_at":"2026-09-21T00:00:00Z","source":"fixture","repo":"o/r","git_sha":"a"*40,"run_id":1,"run_attempt":1,"entity_type":"commit","entity_id":"c:1","status":"observed","provenance":{"source_ref":"fixture","attribution_confidence":1},"attributes":{"actor":"agent","path":"src/a.py"}}
  s=[e.get(k) for k in ("event_type","source","repo","git_sha","run_id","run_attempt","entity_type","entity_id","status")]
  e["event_id"]="eps-"+hashlib.sha256(json.dumps(s,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()[:32]; return e
 def test_duplicate_rejected(self):
  e=self.event(); p=subprocess.run([sys.executable,str(ROOT/"scripts/telemetry/validate_eps.py"),"--unique"],input=json.dumps(e)+"\n"+json.dumps(e)+"\n",text=True,capture_output=True); self.assertNotEqual(p.returncode,0)
 def test_gource_projection(self):
  e=self.event(); p=subprocess.run([sys.executable,str(ROOT/"scripts/visualization/evidence_to_gource.py")],input=json.dumps(e)+"\n",text=True,capture_output=True); self.assertEqual(p.returncode,0); self.assertIn("|M|src/a.py",p.stdout)
if __name__=="__main__": unittest.main()
