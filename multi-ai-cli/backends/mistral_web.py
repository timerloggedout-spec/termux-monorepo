import json, asyncio
import websockets
from .base import ChatBackend

BRIDGE_URI = "ws://127.0.0.1:9876"

class MistralWebBackend(ChatBackend):
    def __init__(self, session_manager=None):
        self.bridge_uri = BRIDGE_URI

    def is_available(self):
        return True  # bridge handles availability

    def send_message(self, message: str, context: list[dict]) -> str:
        async def _send():
            async with websockets.connect(self.bridge_uri) as ws:
                await ws.send(json.dumps({"prompt": message}))
                resp = await ws.recv()
                return json.loads(resp).get("response", "")
        return asyncio.run(_send())
