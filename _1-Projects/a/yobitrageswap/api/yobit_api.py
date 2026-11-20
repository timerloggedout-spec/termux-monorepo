from .base_api import BaseAPI
import aiohttp
import time
import hmac
import hashlib
from typing import Optional, Dict, List
from yobitrageswap.config.config import load_config
from yobitrageswap.database.database import store_fee, store_order, store_order_execution, get_latest_fee, get_recent_implied_fees, get_order_execution
from yobitrageswap.metrics.metrics import Metrics
import statistics

CONFIG = load_config()
metrics = Metrics()

    def __init__(self, api_key: str, secret_key: str):
        self.api_key = api_key
        self.secret_key = secret_key.encode()
        self.public_api_url = 'https://yobit.net/api/3/'
        self.trade_api_url = 'https://yobit.net/tapi'
        self.nonce = int(time.time() * 1000)
        self.session = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, *args):
        if self.session:
            await self.session.close()

    async def _make_public_request(self, endpoint: str) -> Optional[Dict]:
        start_time = time.perf_counter()
        for attempt in range(CONFIG['RETRY_ATTEMPTS']):
            try:
                async with self.session.get(f"{self.public_api_url}{endpoint}", timeout=CONFIG['REQUEST_TIMEOUT']) as resp:
                    if resp.status == 200:
                        result = await resp.json()
                        metrics.record_ping('yobit', time.perf_counter() - start_time)
                        return result
            except Exception:
                if attempt < CONFIG['RETRY_ATTEMPTS'] - 1:
                    await asyncio.sleep(CONFIG['RETRY_DELAY'] * (2 ** attempt))
        metrics.record_ping('yobit', time.perf_counter() - start_time)
        return None

    async def _make_trade_request(self, method: str, params: Optional[Dict] = None) -> Optional[Dict]:
        if params is None:
            params = {}
        self.nonce += 1
        params['method'] = method
        params['nonce'] = self.nonce
        post_data = '&'.join([f"{k}={v}" for k, v in params.items()])
        signature = hmac.new(self.secret_key, post_data.encode(), hashlib.sha512).hexdigest()
        headers = {'Content-Type': 'application/x-www-form-urlencoded', 'Key': self.api_key, 'Sign': signature}
        start_time = time.perf_counter()
        for attempt in range(CONFIG['RETRY_ATTEMPTS']):
            try:
                async with self.session.post(self.trade_api_url, headers=headers, data=post_data, timeout=CONFIG['REQUEST_TIMEOUT']) as resp:
                    if resp.status == 200:
                        result = await resp.json()
                        metrics.record_ping('yobit', time.perf_counter() - start_time)
                        return result
            except Exception:
                if attempt < CONFIG['RETRY_ATTEMPTS'] - 1:
                    await asyncio.sleep(CONFIG['RETRY_DELAY'] * (2 ** attempt))
        metrics.record_ping('yobit', time.perf_counter() - start_time)
        return None

    async def get_info(self) -> Optional[Dict]:
        return await self._make_public_request('info')

    async def get_depth(self, pairs: List[str], limit: int = 150) -> Optional[Dict]:
        pair_string = '-'.join([p for p in pairs if 'yovi' not in p.lower()])
        return await self._make_public_request(f'depth/{pair_string}?limit={limit}')

    async def get_balances(self) -> Optional[Dict]:
        return await self._make_trade_request('getInfo')

    async def get_fee(self) -> float:
        fee = get_latest_fee('Yobit')
        if fee and not metrics.need_fee_update():
            recent_fees = get_recent_implied_fees('Yobit')
            if recent_fees:
                avg_fee = statistics.mean(recent_fees)
                if abs(avg_fee - fee) / fee < CONFIG['FEE_DISCREPANCY_THRESHOLD']:
                    return avg_fee
        info = await self._make_trade_request('getInfo')
        if info and 'return' in info and 'fee' in info['return']:
            fee = float(info['return']['fee']) / 100
            store_fee('Yobit', fee)
            return fee
        return statistics.mean(get_recent_implied_fees('Yobit')) if get_recent_implied_fees('Yobit') else CONFIG['YOBIT_FEE']

    async def place_order(self, pair: str, type: str, amount: float, rate: float) -> Optional[Dict]:
        if 'yovi' in pair.lower():
            return None
        params = {'pair': pair.lower(), 'type': type.lower(), 'amount': amount, 'rate': rate}
        start_time = time.perf_counter()
        result = await self._make_trade_request('Trade', params)
        execution_time = time.perf_counter() - start_time
        metrics.record_order_execution_time(execution_time)
        if result and 'return' in result and 'order_id' in result['return']:
            order_id = str(result['return']['order_id'])
            store_order('Yobit', order_id, pair, type, amount, rate)
            execution_order = await self.determine_execution_order('Yobit', order_id)
            store_order_execution('Yobit', order_id, execution_order)
        return result

    async def determine_execution_order(self, exchange: str, order_id: str) -> str:
        execution_order = get_order_execution(exchange, order_id)
        if execution_order:
            return execution_order
        test_amount = 0.0001
        test_rate = 1.0
        test_pair = 'ltc_btc'
        order_ids = []
        timestamps = []
        for i in range(3):
            result = await self._make_trade_request('Trade', {
                'pair': test_pair,
                'type': 'buy',
                'amount': test_amount,
                'rate': test_rate
            })
            if result and 'return' in result and 'order_id' in result['return']:
                order_id = str(result['return']['order_id'])
                order_ids.append(order_id)
                timestamps.append(int(datetime.now().timestamp()))
                await asyncio.sleep(0.1)
        
        fifo_count = 0
        filo_count = 0
        for order_id in order_ids:
            status = await self._make_trade_request('OrderInfo', {'order_id': order_id})
            if status and 'return' in status and order_id in status['return']:
                if status['return'][order_id]['status'] == 0:
                    index = order_ids.index(order_id)
                    if index == 0:
                        fifo_count += 1
                    elif index == len(order_ids) - 1:
                        filo_count += 1
        
        if fifo_count >= 2:
            execution_order = 'FIFO'
        elif filo_count >= 2:
            execution_order = 'FILO'
        else:
            execution_order = 'MIXED'
        
        for order_id in order_ids:
            await self._make_trade_request('CancelOrder', {'order_id': order_id})
        
        return execution_order

    def fetch_orderbook(self, symbol: str):
        # Stub: return dummy bids/asks
        return {
            "bids": [(100.0, 1.0), (99.5, 2.0)],
            "asks": [(101.0, 1.5), (101.5, 2.5)]
        }

    def place_order(self, symbol, side, qty, price=None):
        return {"status": "stub", "symbol": symbol, "side": side, "qty": qty, "price": price}

