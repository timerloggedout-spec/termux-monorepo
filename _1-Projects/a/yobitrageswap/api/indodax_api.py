from .base_api import BaseAPI
import ccxt.async_support as ccxt
from typing import Dict, List

    def __init__(self, api_key: str = '', secret: str = ''):
        self.exchange = ccxt.indodax({
            'apiKey': api_key,
            'secret': secret,
            'enableRateLimit': True
        })

    async def get_ticker(self, pair: str) -> Dict:
        return await self.exchange.fetch_ticker(pair.upper())

    async def close(self):
        await self.exchange.close()

    def fetch_orderbook(self, symbol: str):
        # Stub: return dummy bids/asks
        return {
            "bids": [(100.0, 1.0), (99.5, 2.0)],
            "asks": [(101.0, 1.5), (101.5, 2.5)]
        }

    def place_order(self, symbol, side, qty, price=None):
        return {"status": "stub", "symbol": symbol, "side": side, "qty": qty, "price": price}

