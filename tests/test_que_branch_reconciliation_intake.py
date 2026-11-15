import json
import tempfile
import unittest
from pathlib import Path

from scripts.que.branch_reconciliation_intake import branch_reconciliation_groups

class IntakeTests(unittest.TestCase):
    def test_actionable_only_and_pr_context(self):
        payload = {"schema": "branch-reconciliation-registry/v1", "branches": [
            {"branch":"ahead","sha":"a"*40,"disposition":"ahead-only","ahead_of_default":2,"behind_default":0,"pull_requests":[]},
            {"branch":"diverged","sha":"b"*40,"disposition":"diverged","ahead_of_default":3,"behind_default":4,"pull_requests":[{"number":17,"base_ref":"release"}]},
            {"branch":"clean","sha":"c"*40,"disposition":"identical","ahead_of_default":0,"behind_default":0,"pull_requests":[]},
            {"branch":"unknown","sha":"d"*40,"disposition":"unresolved-local-ref","ahead_of_default":None,"behind_default":None,"pull_requests":[]}
        ]}
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/"inventory.json"
            path.write_text(json.dumps(payload),encoding="utf-8")
            rows=branch_reconciliation_groups(str(path))
        self.assertEqual({r["name"] for r in rows},{"ahead","diverged","unknown"})
        self.assertIn("#17 base=release",next(r for r in rows if r["name"]=="diverged")["detail"])

    def test_new_tip_has_new_identity(self):
        def key(sha):
            payload={"schema":"branch-reconciliation-registry/v1","branches":[{"branch":"feature/x","sha":sha,"disposition":"ahead-only"}]}
            with tempfile.TemporaryDirectory() as tmp:
                path=Path(tmp)/"i.json"; path.write_text(json.dumps(payload),encoding="utf-8")
                return branch_reconciliation_groups(str(path))[0]["key"]
        self.assertNotEqual(key("a"*40),key("b"*40))

    def test_bad_schema_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/"i.json"; path.write_text('{"schema":"wrong"}',encoding="utf-8")
            with self.assertRaises(ValueError): branch_reconciliation_groups(str(path))

if __name__ == "__main__": unittest.main()
