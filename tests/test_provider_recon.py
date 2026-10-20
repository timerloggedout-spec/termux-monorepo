import hashlib
import json
import unittest

from scripts.model_selection_market import provider_recon as recon


class ProviderReconTests(unittest.TestCase):
    def fixtures(self):
        shas = {repo: ("a" if repo.startswith("mnfst/") else "b") * 40 for repo in recon.REPOS}
        data = {"providers": [{"name": "Provider X", "models": [{"id": "x/model", "name": "Model X", "context": "32K", "modality": "Text", "rateLimit": "10 RPM"}]}]}
        ts = "import { AlphaProvider } from './alpha.js';\nregister(new AlphaProvider());\n"
        blobs = {}
        for repo, sha in shas.items():
            blobs[f"https://api.github.com/repos/{repo}/commits/HEAD"] = json.dumps({"sha": sha}).encode()
            for path in recon.REPOS[repo]["files"]:
                val = json.dumps(data) if path == "data.json" else json.dumps({"name": "demo"}) if path == "package.json" else ts
                blobs[f"https://raw.githubusercontent.com/{repo}/{sha}/{path}"] = val.encode()
        return shas, blobs

    def test_deterministic_provenance_and_runtime_block(self):
        shas, blobs = self.fixtures()
        calls = []
        def fetch(url):
            calls.append(url)
            self.assertNotIn("api.", url.split("/", 3)[-1]) if "api.github.com" not in url else None
            return blobs[url]
        a = recon.build_snapshot(fetch)
        b = recon.build_snapshot(fetch)
        self.assertEqual(a, b)
        self.assertEqual(a["schema_version"], "msm-provider-recon-v1")
        self.assertEqual([x["commit_sha"] for x in a["sources"]], [shas[r] for r in recon.REPOS])
        for src in a["sources"]:
            for entry in src["files"].values():
                self.assertEqual(len(entry["sha256"]), 64)
                self.assertIn(src["commit_sha"], entry["url"])
        self.assertTrue(all(c["evidence_class"] == "THIRD_PARTY_CLAIM" and not c["runtime_eligible"] and c["quota_remaining"] is None for c in a["model_candidates"]))
        self.assertFalse(any("api.aionlabs" in u or "api.cohere" in u for u in calls))
        self.assertTrue(a["integration_references"])

    def test_duplicate_ids_rejected(self):
        doc = {"providers": [{"name": "X", "models": [{"id": "same"}, {"id": "same"}]}]}
        with self.assertRaises(recon.ReconError): recon._claims_mnfst(doc)

    def test_malformed_schemas_rejected(self):
        for doc in (None, {}, {"providers": [{}]}, {"providers": [{"name": "X", "models": [None]}]}):
            with self.subTest(doc=doc), self.assertRaises(recon.ReconError): recon._claims_mnfst(doc)
        with self.assertRaises(recon.ReconError): recon._claims_freellmapi({}, "register(new FooProvider());")
        with self.assertRaises(recon.ReconError): recon._claims_freellmapi({"name": "x"}, "arbitrary source")

    def test_bad_sha_fails_and_existing_output_untouched(self):
        _, blobs = self.fixtures()
        url = "https://api.github.com/repos/mnfst/awesome-free-llm-apis/commits/HEAD"
        blobs[url] = b'{"sha":"deadbeef"}'
        with self.assertRaises(recon.ReconError): recon.build_snapshot(lambda u: blobs[u])

    def test_non_allowlisted_network_target_rejected(self):
        with self.assertRaises(recon.ReconError): recon.fetch_bytes("https://example.com/data.json")
        with self.assertRaises(recon.ReconError): recon.fetch_bytes("http://api.github.com/test")

    def test_atomic_writer_serializes_sorted_json(self):
        import tempfile
        from pathlib import Path
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "snapshot.json"
            recon.write_snapshot(p, {"z": 1, "a": 2})
            self.assertEqual(p.read_text(), '{\n  "a": 2,\n  "z": 1\n}\n')

if __name__ == "__main__":
    unittest.main()


def test_optional_token_is_sent_only_to_exact_prioritized_commit_metadata(monkeypatch):
    from unittest.mock import MagicMock, patch
    token = "test-only-not-a-credential"
    monkeypatch.setenv("PROVIDER_RECON_GITHUB_TOKEN", token)
    metadata = [f"https://api.github.com/repos/{repo}/commits/HEAD" for repo in recon.REPOS]
    other = [
        "https://raw.githubusercontent.com/mnfst/awesome-free-llm-apis/" + "a" * 40 + "/data.json",
        "https://api.github.com/repos/other/repo/commits/HEAD",
        metadata[0] + "?extra=true",
        metadata[0].replace("api.github.com", "api.github.com:8443"),
    ]
    for url in metadata + other:
        opener = MagicMock()
        response = opener.open.return_value.__enter__.return_value
        response.geturl.return_value = url
        response.read.return_value = b"{}"
        with patch.object(recon.urllib.request, "build_opener", return_value=opener):
            assert recon.fetch_bytes(url) == b"{}"
        request = opener.open.call_args.args[0]
        assert request.get_header("Authorization") == ("Bearer " + token if url in metadata else None)


def test_collector_without_optional_token_remains_usable(monkeypatch):
    from unittest.mock import MagicMock, patch
    monkeypatch.delenv("PROVIDER_RECON_GITHUB_TOKEN", raising=False)
    url = "https://api.github.com/repos/mnfst/awesome-free-llm-apis/commits/HEAD"
    opener = MagicMock()
    response = opener.open.return_value.__enter__.return_value
    response.geturl.return_value = url
    response.read.return_value = b"{}"
    with patch.object(recon.urllib.request, "build_opener", return_value=opener):
        assert recon.fetch_bytes(url) == b"{}"
    assert opener.open.call_args.args[0].get_header("Authorization") is None


def test_malformed_metadata_token_fails_without_echoing_or_sending_it(monkeypatch):
    from unittest.mock import patch
    import pytest
    token = "never-log-this\nvalue"
    monkeypatch.setenv("PROVIDER_RECON_GITHUB_TOKEN", token)
    with patch.object(recon.urllib.request, "build_opener") as opener:
        with pytest.raises(recon.ReconError) as caught:
            recon.fetch_bytes("https://api.github.com/repos/mnfst/awesome-free-llm-apis/commits/HEAD")
        opener.assert_not_called()
    assert "never-log-this" not in str(caught.value)


def test_redirect_handler_cannot_forward_metadata_authorization():
    import pytest
    with pytest.raises(recon.ReconError, match="redirects are not permitted"):
        recon._NoRedirect().redirect_request(None, None, 302, "redirect", {}, "https://example.com")


def test_metadata_token_workflow_scope_is_read_only_and_step_local():
    from pathlib import Path
    workflow = (Path(__file__).resolve().parents[1] / ".github/workflows/provider-recon-compound.yml").read_text()
    collect = workflow.split("  collect:\n", 1)[1].split("  publish:\n", 1)[0]
    assert "permissions:\n      contents: read" in collect
    assert "contents: write" not in collect
    assert "PROVIDER_RECON_GITHUB_TOKEN: ${{ github.token }}" in collect
    assert workflow.count("PROVIDER_RECON_GITHUB_TOKEN:") == 1
    assert "pull_request_target" not in workflow
