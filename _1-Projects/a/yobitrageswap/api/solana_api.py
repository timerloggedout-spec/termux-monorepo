from .base_api import BaseAPI
from typing import Dict

    def __init__(self, rpc_url: str):
        self.rpc_url = rpc_url

    async def get_balance(self, pubkey: str) -> Dict:
        return await self.client.get_balance(pubkey)

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

