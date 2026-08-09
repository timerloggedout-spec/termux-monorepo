"""Tests for the DeepSeek web-wrapper opt-in CI smoke test block added to
.gitignore.

These tests exercise the real `.gitignore` file via ``git check-ignore`` so
they validate exactly what Git will do, rather than re-implementing gitignore
pattern-matching semantics. They do not create or modify any files; they only
query how hypothetical paths would be classified.
"""
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
GITIGNORE_PATH = REPO_ROOT / ".gitignore"


def _check_ignore(*relative_paths):
    """Return the set of paths (from relative_paths) that Git would ignore."""
    result = subprocess.run(
        ["git", "check-ignore", *relative_paths],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    # `git check-ignore` exits 0 if at least one path is ignored, 1 if none
    # are ignored, and >1 on a fatal error (e.g. not a git repo).
    assert result.returncode in (0, 1), (
        f"git check-ignore failed unexpectedly: {result.stderr}"
    )
    return set(result.stdout.splitlines())


def _is_ignored(relative_path):
    return relative_path in _check_ignore(relative_path)


@pytest.fixture(scope="module", autouse=True)
def require_gitignore_file():
    assert GITIGNORE_PATH.is_file(), f".gitignore not found: {GITIGNORE_PATH}"


class TestDeepSeekWebWrapperHomeIsIgnored:
    def test_directory_itself_is_ignored(self):
        assert _is_ignored("deepseek-webwrapper-home/")

    def test_files_within_directory_are_ignored(self):
        assert _is_ignored("deepseek-webwrapper-home/config.json")
        assert _is_ignored("deepseek-webwrapper-home/.deepcli/config.json")

    def test_directory_is_ignored_regardless_of_nesting(self):
        # No leading slash in the pattern -> matches at any depth.
        assert _is_ignored("some/nested/path/deepseek-webwrapper-home/file.txt")


class TestDeepSeekOutputJsonIsIgnored:
    def test_ignored_at_repo_root(self):
        assert _is_ignored("deepseek_output.json")

    def test_ignored_when_nested(self):
        assert _is_ignored("nested/dir/deepseek_output.json")


class TestDeepcliSessionAndCookiesAreIgnored:
    def test_deepcli_session_json_is_ignored(self):
        assert _is_ignored("deepcli/session.json")

    def test_deepcli_cookies_2_json_is_ignored(self):
        assert _is_ignored("deepcli/cookies_2.json")

    def test_session_json_pattern_is_anchored_to_deepcli_dir(self):
        # `deepcli/session.json` contains a slash so it is anchored relative
        # to the .gitignore location; it must not match a differently-rooted
        # `deepcli/session.json` (e.g. nested under another directory), nor
        # a `session.json` outside of `deepcli/`.
        assert not _is_ignored("other/deepcli/session.json")
        assert not _is_ignored("session.json")
        assert not _is_ignored("deepcli/nested/session.json")


class TestLegitimateTrackedFilesAreNotHidden:
    """Regression test for the explicit intent documented in the .gitignore
    comment: broad/bare patterns must not accidentally hide real source
    files such as deepcli/pow_solver.js or the new deepcli/package.json.
    """

    def test_pow_solver_js_is_not_ignored(self):
        assert not _is_ignored("deepcli/pow_solver.js")

    def test_deepcli_package_json_is_not_ignored(self):
        assert not _is_ignored("deepcli/package.json")

    def test_unrelated_deepcli_json_file_is_not_ignored(self):
        assert not _is_ignored("deepcli/other-config.json")

    def test_pow_solver_js_is_actually_tracked_in_git(self):
        # Belt-and-braces: confirm the file is tracked, not merely "not
        # ignored" (a file can be untracked-but-not-ignored too).
        result = subprocess.run(
            ["git", "ls-files", "--error-unmatch", "deepcli/pow_solver.js"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, (
            "deepcli/pow_solver.js must remain tracked by git: "
            f"{result.stderr}"
        )


class TestGitignoreFileContainsExpectedSection:
    def test_section_header_present(self):
        content = GITIGNORE_PATH.read_text(encoding="utf-8")
        assert "DeepSeek web-wrapper opt-in CI smoke test" in content

    def test_expected_patterns_present_verbatim(self):
        content = GITIGNORE_PATH.read_text(encoding="utf-8")
        for pattern in (
            "deepseek-webwrapper-home/",
            "deepseek_output.json",
            "deepcli/session.json",
            "deepcli/cookies_2.json",
        ):
            assert pattern in content.splitlines(), (
                f"Expected exact-line pattern {pattern!r} in .gitignore"
            )

    def test_no_bare_pow_solver_or_session_pattern_added(self):
        # Guard against regressions where someone "simplifies" the section
        # by adding a bare `pow_solver.js` or `session.json` pattern, which
        # would shadow legitimate tracked files anywhere in the repo.
        content = GITIGNORE_PATH.read_text(encoding="utf-8")
        lines = {line.strip() for line in content.splitlines()}
        assert "pow_solver.js" not in lines
        assert "session.json" not in lines