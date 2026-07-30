import os, json
from curl_cffi import requests as curl_requests
from .base import ChatBackend

class ColabBackend(ChatBackend):
    def __init__(self, session_manager):
        self.cookie_path = session_manager.get("colab", "cookie_path")
        self.notebook_id = session_manager.get("colab", "notebook_id") or "default"
        self.session = None

    def is_available(self):
        self._ensure_session()
        try:
            return self.session.get("https://colab.research.google.com/api/contents", params={"id": self.notebook_id}).status_code == 200
        except:
            return False

    def _ensure_session(self):
        if self.session is None:
            self.session = curl_requests.Session(impersonate="chrome110")
            if self.cookie_path:
                p = os.path.expanduser(self.cookie_path)
                if os.path.exists(p):
                    with open(p) as f:
                        for c in json.load(f):
                            self.session.cookies.set(c["name"], c["value"], domain=c.get("domain", ".google.com"), path=c.get("path", "/"))

    def send_message(self, message: str, context: list[dict]) -> str:
        self._ensure_session()
        nb_resp = self.session.get(f"https://colab.research.google.com/api/contents/{self.notebook_id}")
        nb = nb_resp.json()
        new_cell = {"cell_type": "code", "source": [message], "metadata": {}}
        cells = nb.get("content", nb).get("cells", nb.get("cells", []))
        cells.append(new_cell)
        self.session.put(
            f"https://colab.research.google.com/api/contents/{self.notebook_id}",
            json={"content": nb.get("content", nb), "type": "notebook"}
        )
        return f"Cell injected into '{self.notebook_id}'. Open notebook to run."
