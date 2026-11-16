import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts" / "pinecone"))

from pinecone_client import PineconeClient  # noqa: E402
from knowledge_sync import build_corpus, chunk_markdown  # noqa: E402


class FakeTransport:
    def __init__(self):
        self.calls = []
        self.indexes = []

    def __call__(self, method, url, headers, body):
        self.calls.append((method, url, headers, body))
        assert headers["Api-Key"] == "test-key"
        assert headers["X-Pinecone-Api-Version"] == "2025-10"
        if url.endswith("/indexes") and method == "GET":
            return 200, json.dumps({"indexes": self.indexes}).encode()
        if url.endswith("/indexes/create-for-model"):
            payload = json.loads(body)
            idx = {"name": payload["name"], "host": "idx-host.example",
                   "status": {"ready": True, "state": "Ready"}}
            self.indexes.append(idx)
            return 201, json.dumps(idx).encode()
        if "/indexes/" in url and method == "GET":
            return 200, json.dumps({"name": "termux-knowledge", "host": "idx-host.example",
                                    "status": {"ready": True, "state": "Ready"}}).encode()
        if url.endswith("/upsert"):
            assert headers["Content-Type"] == "application/x-ndjson"
            return 200, b""
        if url.endswith("/search"):
            return 200, json.dumps({
                "result": {"hits": [{"_id": "a--1", "_score": 0.5,
                                     "fields": {"chunk_text": "x", "source_path": "docs/ops/A.md",
                                                "section": "S"}}]},
                "usage": {"read_units": 1}}).encode()
        if url.endswith("/describe_index_stats"):
            return 200, json.dumps({"totalRecordCount": 3,
                                    "namespaces": {"repo-docs": {"recordCount": 3}}}).encode()
        raise AssertionError(f"unexpected {method} {url}")


def test_ensure_index_creates_once():
    t = FakeTransport()
    c = PineconeClient(api_key="test-key", request=t)
    desc, created = c.ensure_index("termux-knowledge")
    assert created is True and desc["host"] == "idx-host.example"
    _desc2, created2 = c.ensure_index("termux-knowledge")
    assert created2 is False


def test_upsert_batches_ndjson():
    t = FakeTransport()
    c = PineconeClient(api_key="test-key", request=t)
    recs = [{"_id": f"r{i}", "chunk_text": "body " * 20} for i in range(120)]
    assert c.upsert_records("idx-host.example", "repo-docs", recs, batch_size=50) == 120
    ups = [b for (_m, u, _h, b) in t.calls if u.endswith("/upsert")]
    assert len(ups) == 3
    assert len(ups[0].decode().splitlines()) == 50


def test_search_parses_hits():
    t = FakeTransport()
    c = PineconeClient(api_key="test-key", request=t)
    hits, usage = c.search_records("idx-host.example", "repo-docs", "q")
    assert hits[0]["fields"]["source_path"] == "docs/ops/A.md"
    assert usage == {"read_units": 1}


def test_chunking_ids_are_content_addressed(tmp_path):
    text = "# Title\n\n" + ("Pinecone stores vectors for semantic search. " * 8) + "\n"
    a = chunk_markdown(Path("docs/ops/X.md"), text)
    b = chunk_markdown(Path("docs/ops/X.md"), text)
    assert a and a == b and a[0]["_id"].endswith("--" + a[0]["_id"].split("--")[-1])
    assert a[0]["source_path"].endswith("X.md")


def test_build_corpus_reads_docs_ops(tmp_path):
    ops = tmp_path / "docs" / "ops"
    ops.mkdir(parents=True)
    (ops / "A.md").write_text("# A\n\n" + "alpha beta gamma delta epsilon zeta eta theta. " * 8, encoding="utf-8")
    files, records = build_corpus(tmp_path)
    assert len(files) == 1 and records and records[0]["source_path"] == "docs/ops/A.md"
