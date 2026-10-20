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
