"""Tests for the new deepcli/package.json.

This minimal manifest exists solely to give pow_solver.js (which uses ESM
`import` syntax) module context under Node 20 without renaming it to
`.mjs`. These tests validate the file is valid JSON and contains exactly
the fields required for that purpose.
"""
import json
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
PACKAGE_JSON_PATH = REPO_ROOT / "deepcli" / "package.json"


@pytest.fixture(scope="module")
def package_json_text():
    assert PACKAGE_JSON_PATH.is_file(), f"Missing file: {PACKAGE_JSON_PATH}"
    return PACKAGE_JSON_PATH.read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def package_data(package_json_text):
    return json.loads(package_json_text)


class TestDeepcliPackageJsonIsValid:
    def test_file_exists(self):
        assert PACKAGE_JSON_PATH.is_file()

    def test_is_valid_json(self, package_json_text):
        # Raises json.JSONDecodeError (failing the test) if malformed.
        json.loads(package_json_text)

    def test_is_a_json_object(self, package_data):
        assert isinstance(package_data, dict)


class TestDeepcliPackageJsonFields:
    def test_name_field(self, package_data):
        assert package_data["name"] == "deepcli-pow-solver"

    def test_private_is_boolean_true(self, package_data):
        assert package_data["private"] is True

    def test_type_is_module_for_esm_support(self, package_data):
        # This is the field that actually makes Node 20 treat pow_solver.js
        # (which uses `import`) as an ES module without a .mjs extension.
        assert package_data["type"] == "module"

    def test_description_present_and_explanatory(self, package_data):
        description = package_data["description"]
        assert isinstance(description, str) and description
        assert "pow_solver.js" in description
        assert "Node 20" in description


class TestDeepcliPackageJsonIsMinimal:
    """The manifest is intentionally minimal: it should not accumulate
    dependencies, scripts, or other fields it doesn't need."""

    EXPECTED_KEYS = {"name", "private", "type", "description"}

    def test_no_unexpected_top_level_keys(self, package_data):
        assert set(package_data.keys()) == self.EXPECTED_KEYS

    def test_no_dependency_fields(self, package_data):
        for field in ("dependencies", "devDependencies", "peerDependencies", "scripts"):
            assert field not in package_data

    def test_no_version_field_required(self, package_data):
        # `private: true` packages are not published, so an explicit
        # semantic version is not required here.
        assert "version" not in package_data or isinstance(package_data["version"], str)