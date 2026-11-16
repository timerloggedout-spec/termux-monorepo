"""Tribute System 1 -> Delphi delta: changed-only, deduped per thread."""
import json
import tempfile
import unittest
from pathlib import Path

from scripts.ci import tribute_s1_delphi_delta as dd


def rec(url, outcome, weight, repo="o/r"):
    return {"subject": {"url": url}, "delphi_signal": {"surface": "tribute-lane", "repo": repo, "outcome": outcome, "weight": weight}}


class Delta(unittest.TestCase):
    def test_dedupes_per_thread_newest_wins(self):
        sig, st = dd.delta([rec("u1", "changes_requested", 0.1), rec("u1", "merged", 1.0)], {}, now="T")
        self.assertEqual(sig, [{"surface": "tribute-lane", "repo": "o/r", "outcome": "merged", "weight": 1.0, "key": "u1"}])
        self.assertEqual(st["u1"]["outcome"], "merged")

    def test_unchanged_is_skipped(self):
        state = {"u1": {"outcome": "claimed_by_other", "weight": -0.3, "at": "old"}}
        sig, st = dd.delta([rec("u1", "claimed_by_other", -0.3)], state, now="T")
        self.assertEqual(sig, [])
        self.assertEqual(st, state)

    def test_changed_outcome_reemits(self):
        state = {"u1": {"outcome": "approved", "weight": 0.5, "at": "old"}}
        sig, _ = dd.delta([rec("u1", "merged", 0.0)], state, now="T")  # placeholder merge, weight 0
        self.assertEqual([(s["outcome"], s["weight"]) for s in sig], [("merged", 0.0)])

    def test_cap_leaves_rest_pending(self):
        recs = [rec(f"u{i:03d}", "claimed_by_other", -0.3) for i in range(5)]
        sig, st = dd.delta(recs, {}, cap=2, now="T")
        self.assertEqual([s["key"] for s in sig], ["u000", "u001"])
        self.assertEqual(sorted(st), ["u000", "u001"])
        sig2, st2 = dd.delta(recs, st, cap=2, now="T")
        self.assertEqual([s["key"] for s in sig2], ["u002", "u003"])

    def test_records_without_signal_or_url_ignored(self):
        sig, _ = dd.delta([{"subject": {"url": "u"}}, rec("", "merged", 1.0)], {}, now="T")
        self.assertEqual(sig, [])

    def test_cli_roundtrip_matches_delphi_signal_shape(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "dec.jsonl"
            p.write_text("\n".join(json.dumps(r) for r in [rec("u1", "merged", 1.0), rec("u2", "hostile_spam_flag", -1.0)]))
            st = Path(d) / "st.json"
            import io, contextlib
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                self.assertEqual(dd.main([str(p), "--new-state", str(st)]), 0)
            out = json.loads(buf.getvalue())
            self.assertEqual(len(out), 2)
            for s in out:
                self.assertTrue(-1 <= s["weight"] <= 1)
                self.assertRegex(s["surface"], r"^[a-z0-9][a-z0-9._-]{0,63}$")
            self.assertEqual(sorted(json.loads(st.read_text())), ["u1", "u2"])


if __name__ == "__main__":
    unittest.main()
