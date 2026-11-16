from .base_api import BaseAPI
import aiohttp
import time
from typing import Optional, Dict, List, Tuple
from yobitrageswap.config.config import load_config
from yobitrageswap.constants.constants import SWAP_ROUTER_ABI, ERC20_ABI, TOKEN_ADDRESSES
from yobitrageswap.database.database import store_fee, get_latest_fee, get_recent_implied_fees, store_order, store_order_execution, get_order_execution
from yobitrageswap.metrics.metrics import Metrics
import statistics

CONFIG = load_config()
metrics = Metrics()

    def __init__(self, rpc_url: str, private_key: str):
        self.subgraph_url = 'https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v3'
        self.account = self.w3.eth.account.from_key(private_key) if private_key else None
        self.swap_router_address = '0xE592427A0AEce92De3Edee1F18E0157C05861564'
        self.swap_router = self.w3.eth.contract(address=self.swap_router_address, abi=SWAP_ROUTER_ABI) if self.account else None
        self.session = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, *args):
        if self.session:
            await self.session.close()

    async def query_subgraph(self, query: str) -> Optional[Dict]:
        start_time = time.perf_counter()
        payload = {'query': query}
        for attempt in range(CONFIG['RETRY_ATTEMPTS']):
            try:
                async with self.session.post(self.subgraph_url, json=payload, timeout=CONFIG['REQUEST_TIMEOUT']) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        if 'errors' not in data:
                            metrics.record_ping('uniswap', time.perf_counter() - start_time)
                            return data['data']
            except Exception:
                if attempt < CONFIG['RETRY_ATTEMPTS'] - 1:
                    await asyncio.sleep(CONFIG['RETRY_DELAY'] * (2 ** attempt))
        metrics.record_ping('uniswap', time.perf_counter() - start_time)
        return None

    async def get_top_pools(self, first: int = 1000) -> Optional[List[Dict]]:
        query = f"""
        {{
          pools(first: {first}, orderBy: liquidity, orderDirection: desc) {{
            id
            token0 {{ id symbol decimals }}
            token1 {{ id symbol decimals }}
            sqrtPrice
            feeTier
            liquidity
            token0Price
            token1Price
          }}
        }}
        """
        return await self.query_subgraph(query)

    async def get_balance(self, token_symbol: str) -> float:
        if not self.account:
            return 0
        token_address = TOKEN_ADDRESSES.get(token_symbol.lower())
        if not token_address:
            return 0
        token_contract = self.w3.eth.contract(address=token_address, abi=ERC20_ABI)
        balance = await token_contract.functions.balanceOf(self.account.address).call()
        decimals = await token_contract.functions.decimals().call()
        return balance / (10 ** decimals)

    async def approve_token(self, token_symbol: str, amount: float) -> bool:
        token_address = TOKEN_ADDRESSES.get(token_symbol.lower())
        if not token_address:
            return False
        token_contract = self.w3.eth.contract(address=token_address, abi=ERC20_ABI)
        amount_wei = int(amount * (10 ** await token_contract.functions.decimals().call()))
        tx = await token_contract.functions.approve(self.swap_router_address, amount_wei).build_transaction({
            'from': self.account.address,
            'nonce': await self.w3.eth.get_transaction_count(self.account.address),
            'gas': 100000,
            'gasPrice': await self.w3.eth.gas_price
        })
        signed_tx = self.w3.eth.account.sign_transaction(tx, self.account.key)
        try:
            tx_hash = await self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
            receipt = await self.w3.eth.wait_for_transaction_receipt(tx_hash)
            return receipt['status'] == 1
        except Exception:
            return False

    async def swap(self, path: Tuple[str, str, str], amount_in: float, min_out: float) -> Dict:
        if not self.account or not self.swap_router:
            return {'success': False, 'error': 'No private key or router'}
        a, b, c = [x.lower() for x in path]
        if 'yovi' in [a, b, c]:
            return {'success': False, 'error': 'YOVI excluded'}
        tokens = [TOKEN_ADDRESSES.get(a), TOKEN_ADDRESSES.get(b), TOKEN_ADDRESSES.get(c), TOKEN_ADDRESSES.get(a)]
        if not all(tokens):
            return {'success': False, 'error': 'Missing token address'}
        fee_tiers = [3000, 500, 10000]
        path_bytes = b''
        for i in range(3):
            for fee in fee_tiers:
                path_segment = bytes.fromhex(tokens[i][2:]) + fee.to_bytes(3, 'big') + bytes.fromhex(tokens[i+1][2:])
                path_bytes += path_segment
                break
        amount_in_wei = int(amount_in * (10 ** 18))
        min_out_wei = int(min_out * (1 - CONFIG['MAX_SLIPPAGE']) * (10 ** 18))
        params = {
            'path': path_bytes,
            'recipient': self.account.address,
            'deadline': int(time.time()) + 1200,
            'amountIn': amount_in_wei,
            'amountOutMinimum': min_out_wei
        }
        start_time = time.perf_counter()
        try:
            if a != 'weth':
                await self.approve_token(a, amount_in)
            tx = await self.swap_router.functions.exactInput(params).build_transaction({
                'from': self.account.address,
                'nonce': await self.w3.eth.get_transaction_count(self.account.address),
                'gas': 300000,
                'gasPrice': await self.w3.eth.gas_price
            })
            signed_tx = self.w3.eth.account.sign_transaction(tx, self.account.key)
            tx_hash = await self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
            receipt = await self.w3.eth.wait_for_transaction_receipt(tx_hash)
            execution_time = time.perf_counter() - start_time
            metrics.record_order_execution_time(execution_time)
            if receipt['status'] == 1:
                amount_out = int(receipt['logs'][0]['data'], 16) / (10 ** 18)
                order_id = tx_hash.hex()
                store_order('Uniswap', order_id, f"{a}_{b}", 'buy', amount_in, min_out)
                execution_order = await self.determine_execution_order('Uniswap', order_id)
                store_order_execution('Uniswap', order_id, execution_order)
                return {'success': True, 'amount_out': amount_out}
            return {'success': False, 'error': 'Transaction failed'}
        except Exception as e:
            metrics.record_order_execution_time(time.perf_counter() - start_time)
            return {'success': False, 'error': str(e)}

    async def get_fee(self, pool: Dict) -> float:
        fee = get_latest_fee('Uniswap')
        if fee and not metrics.need_fee_update():
            recent_fees = get_recent_implied_fees('Uniswap')
            if recent_fees:
                avg_fee = statistics.mean(recent_fees)
                if abs(avg_fee - fee) / fee < CONFIG['FEE_DISCREPANCY_THRESHOLD']:
                    return avg_fee
        fee = float(pool.get('feeTier', CONFIG['UNISWAP_FEE_TIER'])) / 1_000_000
        store_fee('Uniswap', fee)
        return fee

    async def determine_execution_order(self, exchange: str, order_id: str) -> str:
        execution_order = get_order_execution(exchange, order_id)
        if execution_order:
            return execution_order
        test_amount = 0.0001
        test_pair = 'weth_usdc'
        test_rate = 1.0
        order_ids = []
        timestamps = []
        for i in range(3):
            token_contract = self.w3.eth.contract(address=TOKEN_ADDRESSES['weth'], abi=ERC20_ABI)
            amount_wei = int(test_amount * (10 ** await token_contract.functions.decimals().call()))
            tx = await token_contract.functions.approve(self.swap_router_address, amount_wei).build_transaction({
                'from': self.account.address,
                'nonce': await self.w3.eth.get_transaction_count(self.account.address),
                'gas': 100000,
                'gasPrice': await self.w3.eth.gas_price
            })
            signed_tx = self.w3.eth.account.sign_transaction(tx, self.account.key)
            try:
                tx_hash = await self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
                await self.w3.eth.wait_for_transaction_receipt(tx_hash)
                path_bytes = bytes.fromhex(TOKEN_ADDRESSES['weth'][2:]) + int(3000).to_bytes(3, 'big') + bytes.fromhex(TOKEN_ADDRESSES['usdc'][2:])
                params = {
                    'path': path_bytes,
                    'recipient': self.account.address,
                    'deadline': int(time.time()) + 1200,
                    'amountIn': amount_wei,
                    'amountOutMinimum': 0
                }
                swap_tx = await self.swap_router.functions.exactInput(params).build_transaction({
                    'from': self.account.address,
                    'nonce': await self.w3.eth.get_transaction_count(self.account.address),
                    'gas': 300000,
                    'gasPrice': await self.w3.eth.gas_price
                })
                signed_swap_tx = self.w3.eth.account.sign_transaction(swap_tx, self.account.key)
                swap_tx_hash = await self.w3.eth.send_raw_transaction(signed_swap_tx.rawTransaction)
                order_ids.append(swap_tx_hash.hex())
                timestamps.append(int(datetime.now().timestamp()))
                await asyncio.sleep(0.1)
            except Exception:
                continue
        
        fifo_count = 0
        filo_count = 0
        for order_id in order_ids:
            try:
                receipt = await self.w3.eth.wait_for_transaction_receipt(order_id)
                if receipt['status'] == 1:
                    index = order_ids.index(order_id)
                    if index == 0:
                        fifo_count += 1
                    elif index == len(order_ids) - 1:
                        filo_count += 1
            except Exception:
                continue
        
        if fifo_count >= 2:
            execution_order = 'FIFO'
        elif filo_count >= 2:
            execution_order = 'FILO'
        else:
            execution_order = 'MIXED'
        
        return execution_order

    def fetch_orderbook(self, symbol: str):
        # Stub: return dummy bids/asks
        return {
            "bids": [(100.0, 1.0), (99.5, 2.0)],
            "asks": [(101.0, 1.5), (101.5, 2.5)]
        }

    def place_order(self, symbol, side, qty, price=None):
        return {"status": "stub", "symbol": symbol, "side": side, "qty": qty, "price": price}

