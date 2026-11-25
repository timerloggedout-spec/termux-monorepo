from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts" / "ci"))

import validate_siglary_mandate as siglary  # noqa: E402

BASE_SHA = "a" * 40
HEAD_SHA = "b" * 40
ZERO_SHA = "0" * 40


class SiglaryMandateTests(unittest.TestCase):
    def test_rule_id_registry_parser_preserves_all_ids_in_order(self):
        rows = "\n".join(f"| {rule_id} | DO | example |" for rule_id in siglary.EXPECTED_RULE_IDS)
        text = f"## SG rule registry and enforcement boundary\n{rows}\n### Automated coverage\n"
        self.assertEqual(siglary.rule_ids(text), siglary.EXPECTED_RULE_IDS)

    def test_repository_registry_matches_expected_ids(self):
        self.assertEqual(
            siglary.rule_ids((ROOT / siglary.MANDATE).read_text(encoding="utf-8")),
            siglary.EXPECTED_RULE_IDS,
        )

    def test_repository_crosswalk_contains_every_supplied_symbol(self):
        observed = siglary.crosswalk_tokens((ROOT / siglary.MATRICE).read_text(encoding="utf-8"))
        self.assertTrue(set(siglary.CROSSWALK_TOKENS).issubset(observed))

    def test_avoid_vocabulary_is_case_insensitive(self):
        self.assertEqual(siglary.avoid_matches("No, not, NEVER, and don't."), ["No", "not", "NEVER", "don't"])

    def test_inline_code_remains_literal(self):
        self.assertEqual(siglary.avoid_matches("Use `not` as an exact token."), [])

    def test_link_destination_is_excluded(self):
        self.assertEqual(siglary.avoid_matches("Read [the guide](https://example.test/not-here)."), [])

    def test_exact_quotes_are_excluded(self):
        self.assertEqual(siglary.avoid_matches('Preserve "Never reword this source quote."'), [])
        self.assertEqual(siglary.avoid_matches("Preserve ‘not in this quoted passage’ verbatim."), [])
        self.assertEqual(siglary.avoid_matches("Preserve 'not in this source passage' verbatim."), [])

    def test_fenced_and_blockquote_source_text_is_excluded(self):
        self.assertEqual(siglary.avoid_matches("> Never alter this quotation.\n\n```text\nNot source prose.\n```"), [])

    def test_raw_url_is_excluded(self):
        self.assertEqual(siglary.avoid_matches("See https://example.test/not-found for details."), [])

    def test_nonlisted_words_do_not_match(self):
        self.assertEqual(siglary.avoid_matches("Notebook notes and noteworthy items."), [])

    def test_pull_request_range_uses_event_pinned_revisions(self):
        event = {
            "pull_request": {
                "base": {"sha": BASE_SHA},
                "head": {"sha": HEAD_SHA},
            }
        }
        self.assertEqual(siglary.resolve_event_range(event), (BASE_SHA, HEAD_SHA))

    def test_workflow_dispatch_resolves_fetched_base_and_checkout_head(self):
        event = {"inputs": {}, "ref": "refs/heads/work"}
        results = [
            mock.Mock(returncode=0, stdout=f"{BASE_SHA}\n", stderr=""),
            mock.Mock(returncode=0, stdout=f"{HEAD_SHA}\n", stderr=""),
        ]
        with mock.patch.object(siglary.subprocess, "run", side_effect=results) as run:
            self.assertEqual(
                siglary.resolve_event_range(event, "origin/master"),
                (BASE_SHA, HEAD_SHA),
            )
        self.assertEqual(
            run.call_args_list[0].args[0],
            ["git", "rev-parse", "--verify", "origin/master^{commit}"],
        )
        self.assertEqual(
            run.call_args_list[1].args[0],
            ["git", "rev-parse", "--verify", "HEAD^{commit}"],
        )

    def test_push_range_uses_before_and_after_revisions(self):
        event = {"before": BASE_SHA, "after": HEAD_SHA, "commits": []}
        self.assertEqual(siglary.resolve_event_range(event), (BASE_SHA, HEAD_SHA))

    def test_all_zero_before_uses_first_pushed_commit_parent(self):
        parent = "c" * 40
        event = {
            "before": ZERO_SHA,
            "after": HEAD_SHA,
            "size": 1,
            "commits": [{"id": HEAD_SHA, "parents": [{"sha": parent}]}],
        }
        self.assertEqual(siglary.resolve_event_range(event), (parent, HEAD_SHA))

    def test_all_zero_before_on_root_push_uses_empty_tree(self):
        event = {
            "before": ZERO_SHA,
            "after": HEAD_SHA,
            "size": 1,
            "commits": [{"id": HEAD_SHA, "parents": []}],
        }
        with mock.patch.object(siglary, "_empty_tree_oid", return_value="e" * 40):
            self.assertEqual(siglary.resolve_event_range(event), ("e" * 40, HEAD_SHA))

    def test_truncated_all_zero_push_uses_distinct_fetched_merge_base(self):
        event = {
            "before": ZERO_SHA,
            "after": HEAD_SHA,
            "size": 25,
            "commits": [{"id": HEAD_SHA, "parents": []}],
        }
        with mock.patch.object(
            siglary.subprocess,
            "run",
            return_value=mock.Mock(returncode=0, stdout=f"{BASE_SHA}\n", stderr=""),
        ) as run:
            self.assertEqual(
                siglary.resolve_event_range(event, "origin/master"),
                (BASE_SHA, HEAD_SHA),
            )
        self.assertEqual(run.call_args.args[0][:3], ["git", "merge-base", HEAD_SHA])

    def test_all_zero_push_fails_closed_when_range_is_unavailable(self):
        event = {"before": ZERO_SHA, "after": HEAD_SHA, "size": 25, "commits": []}
        with mock.patch.object(
            siglary.subprocess,
            "run",
            return_value=mock.Mock(returncode=1, stdout="", stderr="no merge base"),
        ):
            with self.assertRaisesRegex(siglary.ValidationError, "complete commit list or a distinct fetched base"):
                siglary.resolve_event_range(event, "origin/master")

    def test_branch_deletion_has_an_empty_post_update_range(self):
        event = {"before": BASE_SHA, "after": ZERO_SHA}
        self.assertEqual(siglary.resolve_event_range(event), (BASE_SHA, BASE_SHA))

    def test_changed_markdown_uses_the_pinned_range(self):
        diff = (
            "diff --git a/notes.md b/notes.md\n"
            "--- a/notes.md\n"
            "+++ b/notes.md\n"
            "@@ -1 +1 @@\n-old\n+new\n"
        )
        with mock.patch.object(
            siglary.subprocess,
            "run",
            return_value=mock.Mock(returncode=0, stdout=diff, stderr=""),
        ) as run:
            additions = siglary.changed_markdown(BASE_SHA, HEAD_SHA)
        self.assertEqual(additions, {"notes.md": {1}})
        self.assertEqual(
            run.call_args.args[0],
            ["git", "diff", "--no-ext-diff", "--unified=0", BASE_SHA, HEAD_SHA, "--"],
        )

    def test_exact_generated_output_allowlist_preserves_policy_docs_in_scope(self):
        self.assertEqual(
            siglary.GENERATED_MARKDOWN_PATHS,
            frozenset(
                {
                    "ops/tracking/tracking.md",
                    "docs/ops/generated/lane-matrix-status.md",
                }
            ),
        )
        self.assertNotIn("docs/ops/REPO-TRACKING.md", siglary.GENERATED_MARKDOWN_PATHS)
        self.assertNotIn("docs/ops/LANE-MATRIX.md", siglary.GENERATED_MARKDOWN_PATHS)

    def test_generated_reports_skip_authored_prose_lint_but_policy_docs_remain(self):
        changed = {
            "ops/tracking/tracking.md": {1},
            "docs/ops/generated/lane-matrix-status.md": {1},
            "docs/ops/REPO-TRACKING.md": {1},
            "docs/ops/LANE-MATRIX.md": {1},
        }
        linted_paths: list[str] = []

        def lint_path(path: str, line_numbers: set[int]) -> list[tuple[int, str]]:
            linted_paths.append(path)
            return [(1, "not")] if path == "docs/ops/REPO-TRACKING.md" else []

        with mock.patch.object(siglary, "changed_markdown", return_value=changed):
            with mock.patch.object(siglary, "markdown_added_prose", side_effect=lint_path):
                with mock.patch.object(siglary, "commit_text", return_value=""):
                    errors = siglary.validate_new_text(BASE_SHA, None)
        self.assertEqual(linted_paths, ["docs/ops/REPO-TRACKING.md", "docs/ops/LANE-MATRIX.md"])
        self.assertEqual(errors, ["docs/ops/REPO-TRACKING.md:1: AVOID vocabulary match: 'not'"])

    def test_generated_output_paths_match_their_producer_templates(self):
        tracking_generator = (ROOT / "scripts/tracking/repo_tracking.py").read_text(encoding="utf-8")
        lane_generator = (ROOT / "scripts/ops/lane_matrix_sweep.py").read_text(encoding="utf-8")
        self.assertIn('(ROOT / "ops" / "tracking" / "tracking.md").write_text', tracking_generator)
        self.assertIn("do not hand-edit", tracking_generator)
        self.assertIn('default="docs/ops/generated/lane-matrix-status.md"', lane_generator)
        self.assertIn('reasons.append("bot-no-auto-promote")', lane_generator)

    def test_local_and_ci_siglary_gates_align_and_pr_edits_rerun(self):
        workflow = (ROOT / ".github/workflows/repo-gate.yml").read_text(encoding="utf-8")
        gate_doc = (ROOT / "docs/ARCHW1Z-GATE.md").read_text(encoding="utf-8")
        self.assertIn("edited", workflow)
        self.assertIn('--event-file "$GITHUB_EVENT_PATH" --fallback-base', workflow)
        self.assertIn("python3 scripts/ci/validate_siglary_mandate.py --base origin/master", gate_doc)

    def test_main_uses_pinned_webhook_endpoints(self):
        event = {
            "pull_request": {
                "base": {"sha": BASE_SHA},
                "head": {"sha": HEAD_SHA},
            }
        }
        with tempfile.TemporaryDirectory() as directory:
            event_path = Path(directory) / "event.json"
            event_path.write_text(json.dumps(event), encoding="utf-8")
            with mock.patch.object(siglary, "validate_registry", return_value=[]):
                with mock.patch.object(siglary, "validate_new_text", return_value=[]) as validate_text:
                    self.assertEqual(siglary.main(["--event-file", str(event_path)]), 0)
        validate_text.assert_called_once_with(BASE_SHA, str(event_path), HEAD_SHA)

    def test_main_uses_default_base_for_workflow_dispatch(self):
        event = {"inputs": {}, "ref": "refs/heads/work"}
        with tempfile.TemporaryDirectory() as directory:
            event_path = Path(directory) / "event.json"
            event_path.write_text(json.dumps(event), encoding="utf-8")
            with mock.patch.object(
                siglary, "resolve_event_range", return_value=(BASE_SHA, HEAD_SHA)
            ) as resolve_range:
                with mock.patch.object(siglary, "validate_registry", return_value=[]):
                    with mock.patch.object(siglary, "validate_new_text", return_value=[]) as validate_text:
                        self.assertEqual(siglary.main(["--event-file", str(event_path)]), 0)
        resolve_range.assert_called_once_with(event, "origin/master")
        validate_text.assert_called_once_with(BASE_SHA, str(event_path), HEAD_SHA)


if __name__ == "__main__":
    unittest.main()
