import asyncio
import time
import logging
import math
from typing import List, Dict, Optional
from ...config.config import load_config
from ...metrics.metrics import Metrics
from ...database.database import store_trade, store_path_stats, store_coin_stats
from ...volatility.volatility import weight_score

CONFIG = load_config()
metrics = Metrics()
logger = logging.getLogger(__name__)

async def analyze_yobit(client: 'AsyncYobitAPI', base: str, batch_size: int, live: bool) -> List[Dict]:
    start_time = time.perf_counter()
    try:
        pairs_data = await client.get_info()
        if not pairs_data or 'pairs' not in pairs_data:
            return []
        pairs = [p for p in pairs_data['pairs'] if base.lower() in p.lower() and 'yovi' not in p.lower()]
        pairs = pairs[:batch_size]
        metrics.record_throughput(len(pairs), time.perf_counter() - start_time)
        depth_data = await client.get_depth(pairs)
        if not depth_data:
            return []
        graph = []
        coins = set()
        for pair in pairs:
            c1, c2 = pair.split('_')
            coins.add(c1.lower())
            coins.add(c2.lower())
            if depth_data.get(pair, {}).get('asks'):
                graph.append((c1.lower(), c2.lower(), -math.log(depth_data[pair]['asks'][0][0] * (1 - await client.get_fee()))))
            if depth_data.get(pair, {}).get('bids'):
                graph.append((c2.lower(), c1.lower(), -math.log(1 / depth_data[pair]['bids'][0][0] * (1 - await client.get_fee()))))
        coins = list(coins)
        if base.lower() not in coins:
            return []
        dist = {coin: float('inf') for coin in coins}
        dist[base.lower()] = 0
        pred = {coin: None for coin in coins}
        # BOLT OPTIMIZATION: Bellman-Ford Early Termination & Local Variable Caching
        # Adding an `updated` flag short-circuits the O(V*E) loop as soon as shortest paths
        # converge (saving up to ~95% of iteration cycles). Caching dist[u] avoids dict lookups.
        num_coins = len(coins)
        for _ in range(num_coins - 1):
            updated = False
            for u, v, w in graph:
                dist_u = dist[u]
                if dist_u + w < dist[v]:
                    dist[v] = dist_u + w
                    pred[v] = u
                    updated = True
            if not updated:
                break
        opps = []
        for u, v, w in graph:
            if dist[u] + w < dist[v]:
                cycle = [v]
                curr = u
                while curr != v and curr is not None:
                    cycle.append(curr)
                    curr = pred[curr]
                cycle.append(v)
                cycle.reverse()
                if cycle[0] != base.lower():
                    continue
                path = []
                for i in range(len(cycle) - 1):
                    for pair in pairs:
                        c1, c2 = pair.split('_')
                        if (c1.lower() == cycle[i] and c2.lower() == cycle[i+1]) or (c2.lower() == cycle[i] and c1.lower() == cycle[i+1]):
                            path.append(pair)
                            break
                start_amount = CONFIG['INITIAL_INVESTMENT']
                amount = start_amount
                slippage = 0.0
                for pair in path:
                    depth = depth_data.get(pair, {})
                    if not depth.get('asks') or not depth.get('bids'):
                        amount = 0
                        break
                    side = 'asks' if cycle[path.index(pair)] == pair.split('_')[0].lower() else 'bids'
                    price = depth[side][0][0]
                    available = depth[side][0][1]
                    amount = min(amount / price, available) if side == 'asks' else amount * price
                    slippage += CONFIG['MAX_SLIPPAGE'] / len(path)
                if amount == 0:
                    continue
                fee = await client.get_fee()
                amount_out = amount * (1 - fee) ** len(path)
                profit_percent = ((amount_out - start_amount) / start_amount) * 100
                if profit_percent >= CONFIG['MIN_PROFIT_PERCENT']:
                    cpu_load, memory_usage, network_latency = metrics.get_system_metrics()
                    score = metrics.score_opportunity(
                        {'profit_percent': f"{profit_percent:.2f}%"},
                        slippage, cpu_load, memory_usage, network_latency, 0.01, time.perf_counter() - start_time
                    )
                    if score > CONFIG['EXECUTION_PRIORITY_THRESHOLD']:
                        opp = {
                            'exchange': 'Yobit',
                            'path': '->'.join(path),
                            'profit_percent': f"{profit_percent:.2f}%",
                            'amount_in': start_amount,
                            'amount_out': amount_out,
                            'score': score
                        }
                        if live:
                            success = False
                            error = ''
                            expected_fee = fee
                            start_trade = time.perf_counter()
                            try:
                                for pair in path:
                                    side = 'buy' if cycle[path.index(pair)] == pair.split('_')[0].lower() else 'sell'
                                    price = depth_data[pair][side][0][0]
                                    amount_to_trade = min(start_amount, depth_data[pair][side][0][1])
                                    result = await client.place_order(pair, side, amount_to_trade, price)
                                    if not result or 'error' in result:
                                        error = result.get('error', 'Trade failed')
                                        break
                                    else:
                                        success = True
                                        metrics.increment_trades()
                            except Exception as e:
                                error = str(e)
                            trade_time = time.perf_counter() - start_trade
                            metrics.record_time('trade', trade_time)
                            implied_fee = fee if success else 0
                            store_trade('Yobit', '->'.join(path), profit_percent, start_amount, amount_out,
                                        expected_fee, implied_fee, slippage, cpu_load, memory_usage, network_latency,
                                        success, error)
                            for coin in set(c for p in path for c in p.split('_')):
                                if coin.lower() != base.lower():
                                    store_coin_stats(coin, 'Yobit', profit_percent)
                        opps.append(opp)
                        store_path_stats('->'.join(path), 'Yobit', 0.01, amount_out, 1)
        metrics.record_time('calc', time.perf_counter() - start_time)
        return sorted(opps, key=lambda x: x['score'], reverse=True)[:CONFIG['TOP_K_OPPS']]
    except Exception as e:
        logger.error(f"Yobit Bellman-Ford analysis failed: {str(e)}")
        return []

async def analyze_uniswap(client: 'AsyncUniswapAPI', base: str, batch_size: int, live: bool) -> List[Dict]:
    start_time = time.perf_counter()
    try:
        pools = await client.get_top_pools(batch_size)
        if not pools or 'pools' not in pools:
            return []
        metrics.record_throughput(len(pools['pools']), time.perf_counter() - start_time)
        graph = []
        coins = set()
        for pool in pools['pools']:
            c1, c2 = pool['token0']['symbol'].lower(), pool['token1']['symbol'].lower()
            if 'yovi' in [c1, c2]:
                continue
            coins.add(c1)
            coins.add(c2)
            if float(pool['liquidity']) < CONFIG['LIQUIDITY_THRESHOLD']:
                continue
            fee = await client.get_fee(pool)
            if c1 == base.lower():
                graph.append((c1, c2, -math.log(float(pool['token0Price']) * (1 - fee))))
            elif c2 == base.lower():
                graph.append((c2, c1, -math.log(float(pool['token1Price']) * (1 - fee))))
            else:
                graph.append((c1, c2, -math.log(float(pool['token0Price']) * (1 - fee))))
                graph.append((c2, c1, -math.log(float(pool['token1Price']) * (1 - fee))))
        coins = list(coins)
        if base.lower() not in coins:
            return []
        dist = {coin: float('inf') for coin in coins}
        dist[base.lower()] = 0
        pred = {coin: None for coin in coins}
        # BOLT OPTIMIZATION: Bellman-Ford Early Termination & Local Variable Caching
        # Adding an `updated` flag short-circuits the O(V*E) loop as soon as shortest paths
        # converge (saving up to ~95% of iteration cycles). Caching dist[u] avoids dict lookups.
        num_coins = len(coins)
        for _ in range(num_coins - 1):
            updated = False
            for u, v, w in graph:
                dist_u = dist[u]
                if dist_u + w < dist[v]:
                    dist[v] = dist_u + w
                    pred[v] = u
                    updated = True
            if not updated:
                break
        opps = []
        for u, v, w in graph:
            if dist[u] + w < dist[v]:
                cycle = [v]
                curr = u
                while curr != v and curr is not None:
                    cycle.append(curr)
                    curr = pred[curr]
                cycle.append(v)
                cycle.reverse()
                if cycle[0] != base.lower():
                    continue
                path = []
                for i in range(len(cycle) - 1):
                    for pool in pools['pools']:
                        c1, c2 = pool['token0']['symbol'].lower(), pool['token1']['symbol'].lower()
                        if (c1 == cycle[i] and c2 == cycle[i+1]) or (c2 == cycle[i] and c1 == cycle[i+1]):
                            path.append((c1, c2))
                            break
                start_amount = CONFIG['INITIAL_INVESTMENT']
                amount = start_amount
                slippage = 0.0
                for p in path:
                    for pool in pools['pools']:
                        if (pool['token0']['symbol'].lower(), pool['token1']['symbol'].lower()) == p or                            (pool['token1']['symbol'].lower(), pool['token0']['symbol'].lower()) == p:
                            price = float(pool['token0Price']) if p[0] == base.lower() else 1 / float(pool['token1Price'])
                            liquidity = float(pool['liquidity'])
                            if liquidity < CONFIG['LIQUIDITY_THRESHOLD']:
                                amount = 0
                                break
                            amount = amount / price if p[0] == base.lower() else amount * price
                            slippage += CONFIG['MAX_SLIPPAGE'] / len(path)
                    if amount == 0:
                        break
                if amount == 0:
                    continue
                fee = await client.get_fee(pools['pools'][0])
                amount_out = amount * (1 - fee) ** len(path)
                profit_percent = ((amount_out - start_amount) / start_amount) * 100
                if profit_percent >= CONFIG['MIN_PROFIT_PERCENT']:
                    cpu_load, memory_usage, network_latency = metrics.get_system_metrics()
                    score = metrics.score_opportunity(
                        {'profit_percent': f"{profit_percent:.2f}%"},
                        slippage, cpu_load, memory_usage, network_latency, 0.01, time.perf_counter() - start_time
                    )
                    if score > CONFIG['EXECUTION_PRIORITY_THRESHOLD']:
                        opp = {
                            'exchange': 'Uniswap',
                            'path': '->'.join([f"{p[0]}_{p[1]}" for p in path]),
                            'profit_percent': f"{profit_percent:.2f}%",
                            'amount_in': start_amount,
                            'amount_out': amount_out,
                            'score': score
                        }
                        if live:
                            success = False
                            error = ''
                            expected_fee = fee
                            start_trade = time.perf_counter()
                            try:
                                result = await client.swap([p[0].upper() for p in path], start_amount, amount_out)
                                if result['success']:
                                    success = True
                                    metrics.increment_trades()
                                else:
                                    error = result['error']
                            except Exception as e:
                                error = str(e)
                            trade_time = time.perf_counter() - start_trade
                            metrics.record_time('trade', trade_time)
                            implied_fee = fee if success else 0
                            store_trade('Uniswap', '->'.join([f"{p[0]}_{p[1]}" for p in path]), profit_percent,
                                        start_amount, amount_out, expected_fee, implied_fee, slippage,
                                        cpu_load, memory_usage, network_latency, success, error)
                            for p in path:
                                for coin in p:
                                    if coin.lower() != base.lower():
                                        store_coin_stats(coin, 'Uniswap', profit_percent)
                        opps.append(opp)
                        store_path_stats('->'.join([f"{p[0]}_{p[1]}" for p in path]), 'Uniswap', 0.01, amount_out, 1)
        metrics.record_time('calc', time.perf_counter() - start_time)
        return sorted(opps, key=lambda x: x['score'], reverse=True)[:CONFIG['TOP_K_OPPS']]
    except Exception as e:
        logger.error(f"Uniswap Bellman-Ford analysis failed: {str(e)}")
        return []
