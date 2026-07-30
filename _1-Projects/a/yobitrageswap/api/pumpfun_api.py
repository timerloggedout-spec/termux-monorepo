from .base_api import BaseAPI
import aiohttp
from typing import Dict, List

    def __init__(self, rpc_url: str):
        self.rpc_url = rpc_url

    async def get_recent_tokens(self) -> List[Dict]:
        url = "https://pumpportal.fun/api/data/recent_tokens?limit=10"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                return await resp.json()

    async def close(self):
        await self.client.close()

    def fetch_orderbook(self, symbol: str):
        # Stub: return dummy bids/asks
        return {
            "bids": [(100.0, 1.0), (99.5, 2.0)],
            "asks": [(101.0, 1.5), (101.5, 2.5)]
        }

    def place_order(self, symbol, side, qty, price=None):
        return {"status": "stub", "symbol": symbol, "side": side, "qty": qty, "price": price}

