import json
import threading
import unittest
import urllib.request
import urllib.error
from http.server import ThreadingHTTPServer
import server


class CatalogApiTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.httpd = ThreadingHTTPServer(("127.0.0.1", 0), server.Handler)
        cls.port = cls.httpd.server_address[1]
        threading.Thread(target=cls.httpd.serve_forever, daemon=True).start()

    @classmethod
    def tearDownClass(cls):
        cls.httpd.shutdown()

    def get(self, path):
        with urllib.request.urlopen(f"http://127.0.0.1:{self.port}{path}") as r:
            return r.status, json.loads(r.read())

    def test_health(self):
        code, body = self.get("/health")
        self.assertEqual(code, 200)
        self.assertEqual(body["status"], "ok")

    def test_catalog_lists_pilots(self):
        code, body = self.get("/blueprints")
        ids = [b["id"] for b in body["blueprints"]]
        self.assertIn("catalog-api", ids)
        self.assertIn("planning-queue", ids)

    def test_single_entry(self):
        code, body = self.get("/blueprints/catalog-api")
        self.assertEqual(body["id"], "catalog-api")

    def test_unknown_404(self):
        with self.assertRaises(urllib.error.HTTPError) as cm:
            self.get("/blueprints/nope")
        self.assertEqual(cm.exception.code, 404)

    def test_writes_disabled(self):
        req = urllib.request.Request(
            f"http://127.0.0.1:{self.port}/blueprints",
            data=b"{}", method="POST")
        with self.assertRaises(urllib.error.HTTPError) as cm:
            urllib.request.urlopen(req)
        self.assertEqual(cm.exception.code, 405)


if __name__ == "__main__":
    unittest.main()
