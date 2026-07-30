import asyncio
import time
import logging
from typing import Dict, List
from ...config.config import load_config
from ...metrics.metrics import Metrics
from ...database.database import store_grid_order, store_trade
from ...volatility.volatility import create_grid_baskets

CONFIG = load_config()
metrics = Metrics()
logger = logging.getLogger(__name__)

async def run_grid_trading(client: 'AsyncYobitAPI|AsyncUniswapAPI', pair: str, exchange: str, budget: float) -> List[Dict]:
    start_time = time.perf_counter()
    try:
        if exchange == 'Yobit':
            depth = await client.get_depth([pair])
            if not depth or pair not in depth:
                return []
            bid, ask = depth[pair]['bids'][0][0], depth[pair]['asks'][0][0]
        else:
            pools = await client.get_top_pools(1)
            if not pools or 'pools' not in pools:
                return []
            pool = next((p for p in pools['pools'] if
                         (p['token0']['symbol'].lower(), p['token1']['symbol'].lower()) == tuple(pair.lower().split('_')) or
                         (p['token1']['symbol'].lower(), p['token0']['symbol'].lower()) == tuple(pair.lower().split('_'))), None)
            if not pool:
                return []
            bid = float(pool['token0Price']) if pool['token0']['symbol'].lower() == pair.split('_')[0].lower() else 1 / float(pool['token1Price'])
            ask = bid * (1 + CONFIG['GRID_SPREAD_FACTOR'])
        current_price = (bid + ask) / 2
        baskets = create_grid_baskets(pair, exchange, current_price, bid, ask, budget)
        results = []
        for basket in baskets:
            for order in basket['buy_orders'] + basket['sell_orders']:
                if exchange == 'Yobit':
                    result = await client.place_order(
                        pair, 'buy' if order in basket['buy_orders'] else 'sell',
                        order['amount'], order['price']
                    )
                    if result and 'return' in result and 'order_id' in result['return']:
                        order['status'] = 'placed'
                        store_grid_order(exchange, pair, basket['basket_id'],
                                        'buy' if order in basket['buy_orders'] else 'sell',
                                        order['price'], order['amount'], 'placed')
                elif exchange == 'Uniswap' and order in basket['buy_orders']:
                    amount_out = order['amount'] * order['price']
                    result = await client.swap(
                        [pair.split('_')[0].upper(), pair.split('_')[1].upper(), pair.split('_')[0].upper()],
                        order['amount'], amount_out * (1 - CONFIG['MAX_SLIPPAGE'])
                    )
                    if result['success']:
                        order['status'] = 'placed'
                        store_grid_order(exchange, pair, basket['basket_id'], 'buy',
                                        order['price'], order['amount'], 'placed')
            results.append({
                'exchange': exchange,
                'pair': pair,
                'basket_id': basket['basket_id'],
                'center_price': basket['center_price'],
                'status': 'active'
            })
        metrics.record_time('trade', time.perf_counter() - start_time)
        return results
    except Exception as e:
        logger.error(f"Grid trading failed for {exchange}: {str(e)}")
        return []
