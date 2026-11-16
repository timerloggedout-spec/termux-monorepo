import contextlib
import io
import json
import tempfile
import unittest
from unittest import mock
from pathlib import Path
from scripts.model_selection_market import resource_index as ri


class ResourceIndexTests(unittest.TestCase):
    def fixtures(self):
        resource = {"id": "r-α", "title": "Café Search Reference", "url": "https://example.org/resource", "kind": "guide", "tags": ["résumé", "Search"], "mesh_roles": ["planner"], "implementation_paths": ["src/a.py"], "next_action": "Review", "status": "cataloged, not activated", "evidence_class": "SUPPLIED_NOTE", "runtime_eligible": False}
        registry = {"schema_version": ri.REGISTRY_SCHEMA, "resources": [resource], "source_inputs": [{"id": "notes", "url": "https://example.org/notes", "resource_ids": ["r-α"]}]}
        repo, sha, path = "org/project", "a" * 40, "src/index.py"
        url = f"https://raw.githubusercontent.com/{repo}/{sha}/{path}"
        provider = {"schema_version": ri.PROVIDER_SCHEMA, "sources": [{"repo": repo, "commit_sha": sha, "files": {path: {"url": url, "sha256": "b" * 64}}}], "model_candidates": [{"provider_key": "provider-x", "provider_name": "Provider X", "model_key": "model-y", "model_name": "Model Y", "source_repo": repo, "claims": {"context": 100}, "evidence_class": "THIRD_PARTY_CLAIM", "runtime_eligible": False, "quota_remaining": None, "blocked_reasons": ["unverified"]}]}
        return registry, provider

    def test_determinism_reordering_identity_and_provenance(self):
        registry, providers = self.fixtures()
        a = ri.build_index(registry, providers)
        registry["resources"].reverse(); registry["source_inputs"].reverse()
        providers["sources"].reverse(); providers["model_candidates"].reverse()
        self.assertEqual(a, ri.build_index(registry, providers))
        self.assertEqual(a["schema_version"], ri.SCHEMA_VERSION)
        self.assertEqual(a["sources"], providers["sources"])
        self.assertEqual(a["source_inputs"], registry["source_inputs"])
        candidate = next(r for r in a["resources"] if r["record_type"] == "provider_candidate")
        self.assertEqual(candidate["id"], 'provider:["org/project","provider-x","model-y"]')
        for key in ("source_repo", "provider_key", "model_key", "claims", "evidence_class", "blocked_reasons"):
            self.assertEqual(candidate[key], providers["model_candidates"][0][key])
        self.assertFalse(any(x["runtime_eligible"] is not False for x in a["resources"]))

    def test_registry_and_provider_fail_closed(self):
        reg, prov = self.fixtures()
        for flag in (True, None, 0, "false"):
            bad = json.loads(json.dumps(reg)); bad["resources"][0]["runtime_eligible"] = flag
            with self.subTest(flag=flag), self.assertRaises(ri.IndexError): ri.build_index(bad, prov)
        bad = json.loads(json.dumps(prov)); bad["model_candidates"][0]["runtime_eligible"] = True
        with self.assertRaises(ri.IndexError): ri.build_index(reg, bad)
        for schema in (None, "future-schema", ri.PROVIDER_SCHEMA + "x"):
            bad = json.loads(json.dumps(prov)); bad["schema_version"] = schema
            with self.assertRaises(ri.IndexError): ri.build_index(reg, bad)
        bad = json.loads(json.dumps(prov)); bad["model_candidates"][0]["source_repo"] = "unknown/repo"
        with self.assertRaises(ri.IndexError): ri.build_index(reg, bad)

    def test_url_secrets_and_bad_pins_rejected(self):
        reg, prov = self.fixtures()
        for url in ("http://example.org/a", "https://user:pass@example.org/a", "https://token@example.org/a", "https://example.org:bad/a"):
            bad = json.loads(json.dumps(reg)); bad["resources"][0]["url"] = url
            with self.subTest(url=url), self.assertRaises(ri.IndexError): ri.build_index(bad, prov)
        bad = json.loads(json.dumps(prov)); bad["sources"][0]["commit_sha"] = "ab12"
        with self.assertRaises(ri.IndexError): ri.build_index(reg, bad)
        bad = json.loads(json.dumps(prov)); bad["sources"][0]["files"]["src/index.py"]["sha256"] = "not-a-hash"
        with self.assertRaises(ri.IndexError): ri.build_index(reg, bad)
        bad = json.loads(json.dumps(prov)); bad["sources"][0]["files"]["src/index.py"]["url"] = "https://raw.githubusercontent.com/org/project/" + "c" * 40 + "/src/index.py"
        with self.assertRaises(ri.IndexError): ri.build_index(reg, bad)

    def test_duplicates_missing_types_and_dangling_refs(self):
        reg, prov = self.fixtures()
        for bad in ({**reg, "resources": reg["resources"] * 2}, {**reg, "source_inputs": [{"id": "x", "url": "https://example.org", "resource_ids": ["missing"]}]}):
            with self.assertRaises(ri.IndexError): ri.build_index(bad, prov)
        bad = json.loads(json.dumps(reg)); bad["resources"][0]["tags"] = "not-list"
        with self.assertRaises(ri.IndexError): ri.build_index(bad, prov)
        bad = json.loads(json.dumps(reg)); bad["resources"][0].pop("title")
        with self.assertRaises(ri.IndexError): ri.build_index(bad, prov)
        bad = json.loads(json.dumps(prov)); bad["model_candidates"].append(dict(bad["model_candidates"][0]))
        with self.assertRaises(ri.IndexError): ri.build_index(reg, bad)


    def test_multi_record_reordering_and_provenance_hashes(self):
        reg, prov = self.fixtures()
        reg["notes_sha256"] = "d" * 64
        reg["resources"].append(dict(reg["resources"][0], id="r-second", title="Second"))
        reg["source_inputs"].append({"id": "z-notes", "url": "https://example.org/z", "resource_ids": ["r-second"], "sha256": "e" * 64})
        prov["sources"].append({"repo": "other/project", "commit_sha": "c" * 40, "files": {"x.py": {"url": f"https://raw.githubusercontent.com/other/project/{'c' * 40}/x.py", "sha256": "f" * 64}}})
        prov["model_candidates"].append(dict(prov["model_candidates"][0], provider_key="provider-z", model_key="model-z"))
        first = ri.build_index(reg, prov)
        reg["resources"].reverse(); reg["source_inputs"].reverse(); prov["sources"].reverse(); prov["model_candidates"].reverse()
        second = ri.build_index(reg, prov)
        self.assertEqual(first, second)
        self.assertEqual(first["notes_sha256"], "d" * 64)
        self.assertEqual(first["sources"], sorted(prov["sources"], key=lambda x: x["repo"]))
        self.assertEqual(first["source_inputs"], sorted(reg["source_inputs"], key=lambda x: x["id"]))
        other = next(source for source in first["sources"] if source["repo"] == "other/project")
        self.assertEqual(other["files"]["x.py"]["sha256"], "f" * 64)

    def test_strict_candidate_refs_and_duplicate_source_input(self):
        reg, prov = self.fixtures()
        for field, value in (("quota_remaining", 0), ("quota_remaining", "unknown"), ("evidence_class", "VERIFIED"), ("evidence_class", None)):
            bad = json.loads(json.dumps(prov)); bad["model_candidates"][0][field] = value
            with self.subTest(field=field, value=value), self.assertRaises(ri.IndexError): ri.build_index(reg, bad)
        for refs in ([], [""], [1], "r-α"):
            bad = json.loads(json.dumps(reg)); bad["source_inputs"][0]["resource_ids"] = refs
            with self.subTest(refs=refs), self.assertRaises(ri.IndexError): ri.build_index(bad, prov)
        bad = json.loads(json.dumps(reg)); bad["source_inputs"].append(dict(bad["source_inputs"][0]))
        with self.assertRaises(ri.IndexError): ri.build_index(bad, prov)
        for candidates in ([None], ["x"]):
            bad = json.loads(json.dumps(prov)); bad["model_candidates"] = candidates
            with self.assertRaises(ri.IndexError): ri.build_index(reg, bad)
        bad = json.loads(json.dumps(prov)); bad["sources"] = [None]
        with self.assertRaises(ri.IndexError): ri.build_index(reg, bad)

    def test_url_query_secret_and_control_characters_rejected(self):
        reg, prov = self.fixtures()
        for suffix in ("?token=secret", "?api_key=secret", "?access_token=x", "?key=x", "?auth=x", "?password=x", "?x=ok\n"):
            bad = json.loads(json.dumps(reg)); bad["resources"][0]["url"] += suffix
            with self.subTest(suffix=suffix), self.assertRaises(ri.IndexError) as caught: ri.build_index(bad, prov)
            self.assertNotIn("secret", str(caught.exception))
        reg["resources"][0]["url"] = "https://google.com/search?q=hello"
        ri.build_index(reg, prov)

    def test_positive_unbounded_search_limit_and_cli_filtering(self):
        reg, prov = self.fixtures(); index = ri.build_index(reg, prov)
        self.assertEqual(len(ri.search(index, "", limit=1001)), 2)
        with self.assertRaises(ri.IndexError): ri.search(index, "", limit=True)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); rp=root/"r.json"; pp=root/"p.json"
            rp.write_text(json.dumps(reg)); pp.write_text(json.dumps(prov)); stdout=io.StringIO()
            with contextlib.redirect_stdout(stdout): ri.main(["--registry", str(rp), "--providers", str(pp), "--query", "", "--limit", "1"])
            self.assertEqual(len(json.loads(stdout.getvalue())), 1)

    def test_writer_failure_cleans_temporary_file(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)/"snapshot.json"
            with mock.patch.object(ri.os, "replace", side_effect=OSError("failed")):
                with self.assertRaises(OSError): ri.write_snapshot(target, {"x": 1})
            self.assertEqual(list(Path(directory).iterdir()), [])

    def test_search_unicode_filters_cross_field_and_empty(self):
        reg, prov = self.fixtures(); index = ri.build_index(reg, prov)
        self.assertEqual([r["id"] for r in ri.search(index, "CAFÉ résumé")], ["r-α"])
        self.assertEqual(len(ri.search(index, "café planner", kind="guide", mesh_role="PLANNER")), 1)
        self.assertEqual(ri.search(index, "Café guide", kind="provider"), [])
        self.assertEqual(ri.search(index, "never matches"), [])
        self.assertEqual(ri.search({"schema_version": ri.SCHEMA_VERSION, "resources": []}, "anything"), [])
        with self.assertRaises(ri.IndexError): ri.search(index, "", limit=0)

    def test_writer_sorted_json_and_cli_atomic_invalid(self):
        reg, prov = self.fixtures()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); rp = root / "registry.json"; pp = root / "providers.json"; out = root / "out.json"
            rp.write_text(json.dumps(reg), encoding="utf-8"); pp.write_text(json.dumps(prov), encoding="utf-8")
            out.write_text("original", encoding="utf-8")
            stderr = io.StringIO()
            with contextlib.redirect_stderr(stderr):
                self.assertEqual(ri.main(["--registry", str(rp), "--providers", str(pp), "--output", str(out)]), 0)
            # Valid build replaces output atomically; sorted-key JSON is stable.
            expected = out.read_text(encoding="utf-8")
            self.assertIn('"schema_version": "msm-resource-index-v1"', expected)
            bad = dict(reg); bad["resources"] = [dict(reg["resources"][0], runtime_eligible=True)]
            rp.write_text(json.dumps(bad), encoding="utf-8"); out.write_text("keep", encoding="utf-8")
            with contextlib.redirect_stderr(stderr), self.assertRaises(SystemExit) as caught:
                ri.main(["--registry", str(rp), "--providers", str(pp), "--output", str(out)])
            self.assertEqual(caught.exception.code, 2); self.assertEqual(out.read_text(), "keep")
            rp.write_text(json.dumps(reg), encoding="utf-8")
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                self.assertEqual(ri.main(["--registry", str(rp), "--providers", str(pp), "--query", "model-y"]), 0)
            self.assertEqual(json.loads(stdout.getvalue())[0]["record_type"], "provider_candidate")


if __name__ == "__main__":
    unittest.main()
