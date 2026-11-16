#!/bin/bash

# Script to complete yobitrageswap setup, clean up old structure, and implement refactored code
# Run this from ~/_1-Projects/a/
# Assumes Termux environment

set -e  # Exit on error

echo "Starting yobitrageswap setup and refactor (fixscript-3.sh)..."

# Step 1: Clean up old and duplicated folders
echo "Cleaning up old and duplicated folders..."
if [ -d "_1-Projects/a/yobitrageswap" ]; then
    rm -rf "_1-Projects/a/yobitrageswap"
fi
if [ -d "_1-Projects/a/_1-Projects" ]; then
    rm -rf "_1-Projects/a/_1-Projects"
fi
if [ -d "yobitrageswap" ]; then
    rm -rf "yobitrageswap"
fi

# Step 2: Create clean directory structure
echo "Creating directory structure..."
mkdir -p yobitrageswap/{config,database,metrics,volatility,api,strategies/arbitrage,strategies/grid_trading,ui,constants}

# Step 3: Create __init__.py files
echo "Creating __init__.py files..."
touch yobitrageswap/__init__.py
touch yobitrageswap/config/__init__.py
touch yobitrageswap/database/__init__.py
touch yobitrageswap/metrics/__init__.py
touch yobitrageswap/volatility/__init__.py
touch yobitrageswap/api/__init__.py
touch yobitrageswap/strategies/__init__.py
touch yobitrageswap/strategies/arbitrage/__init__.py
touch yobitrageswap/strategies/grid_trading/__init__.py
touch yobitrageswap/ui/__init__.py
touch yobitrageswap/constants/__init__.py

# Step 4: Update requirements.txt
echo "Updating requirements.txt..."
cat > requirements.txt << EOF
aiohttp==3.10.10
pycoingecko==3.2.0
psutil==6.1.0
matplotlib==3.9.2
numpy==2.1.2
web3==7.3.0
textual==0.84.0
python-dotenv==1.0.1
EOF

# Step 5: Update .env (placeholder; user to fill in)
echo "Updating .env..."
cat > .env << EOF
API_KEY=your_yobit_api_key
SECRET_KEY=your_yobit_secret_key
ETH_PRIVATE_KEY=your_ethereum_private_key
ETHEREUM_RPC_URL=your_ethereum_rpc_url
CMC_API_KEY=your_coinmarketcap_api_key
EOF

# Step 6: Create and write code files
echo "Creating and writing code files..."

# yobitrageswap/main.py
cat > yobitrageswap/main.py << EOF
import asyncio
import argparse
import logging
from config.config import load_config
from database.database import init_db
from metrics.metrics import Metrics
from volatility.volatility import select_base_currency, visualize_weighting_curves
from api.yobit_api import AsyncYobitAPI
from api.uniswap_api import AsyncUniswapAPI
from strategies.arbitrage.triangular import analyze_yobit as analyze_yobit_tri, analyze_uniswap as analyze_uniswap_tri
from strategies.arbitrage.bellman_ford import analyze_yobit as analyze_yobit_bf, analyze_uniswap as analyze_uniswap_bf
from ui.ui import ArbitrageApp

CONFIG = load_config()
metrics = Metrics()

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s',
                    handlers=[logging.FileHandler(CONFIG['LOG_FILE']), logging.StreamHandler()])
logger = logging.getLogger(__name__)

async def run_analysis(exchange: str, method: str, live: bool, ui: bool) -> list[dict]:
    init_db()
    visualize_weighting_curves()
    metrics.cycle_count += 1
    cycle_start = time.perf_counter()
    base = await select_base_currency()
    batch_size = metrics.get_dynamic_batch_size() if metrics.cycle_count % CONFIG['BATCH_ADJUST_INTERVAL'] == 0 else CONFIG['BATCH_SIZE_INIT']
    opps = []
    async with AsyncYobitAPI(CONFIG['API_KEY'], CONFIG['SECRET_KEY']) as y_client, \
               AsyncUniswapAPI(CONFIG['ETHEREUM_RPC_URL'], CONFIG['ETH_PRIVATE_KEY']) as u_client:
        if method == 'triangular':
            if exchange in ['yobit', 'both']:
                y_opps = await analyze_yobit_tri(y_client, base, batch_size, live)
                opps.extend(y_opps)
            if exchange in ['uniswap', 'both']:
                u_opps = await analyze_uniswap_tri(u_client, base, batch_size, live)
                opps.extend(u_opps)
        elif method == 'bellman-ford':
            if exchange in ['yobit', 'both']:
                y_opps = await analyze_yobit_bf(y_client, base, batch_size, live)
                opps.extend(y_opps)
            if exchange in ['uniswap', 'both']:
                u_opps = await analyze_uniswap_bf(u_client, base, batch_size, live)
                opps.extend(u_opps)
    metrics.record_time('cycle', time.perf_counter() - cycle_start)
    if ui:
        app = ArbitrageApp(opps)
        await app.run_async()
    return opps

def main():
    parser = argparse.ArgumentParser(description="Yobit & Uniswap Arbitrage Bot")
    parser.add_argument('--exchange', choices=['yobit', 'uniswap', 'both'], default='both')
    parser.add_argument('--method', choices=['triangular', 'bellman-ford'], default='triangular')
    parser.add_argument('--live', action='store_true', help='Execute real trades')
    parser.add_argument('--ui', action='store_true', help='Show Textual UI')
    args = parser.parse_args()
    if args.live:
        logger.warning("LIVE TRADING ENABLED. Ensure funds and keys are secure.")
    asyncio.run(run_analysis(args.exchange, args.method, args.live, args.ui))

if __name__ == "__main__":
    main()
EOF

# yobitrageswap/config/config.py
cat > yobitrageswap/config/config.py << EOF
import os
import json
from dotenv import load_dotenv

CONFIG_DEFAULTS = {
    'API_KEY': '', 'SECRET_KEY': '', 'ETH_PRIVATE_KEY': '', 'ETHEREUM_RPC_URL': '',
    'CMC_API_KEY': '', 'INITIAL_INVESTMENT': 100.0, 'TRADING_FEE': 0.002,
    'YOBIT_FEE': 0.002, 'UNISWAP_FEE_TIER': 3000, 'LOG_FILE': 'arbitrage.log',
    'REQUEST_TIMEOUT': 10, 'RETRY_ATTEMPTS': 3, 'RETRY_DELAY': 5,
    'BATCH_SIZE_MIN': 10, 'BATCH_SIZE_MAX': 100, 'BATCH_SIZE_INIT': 40,
    'CYCLE_DELAY': 15, 'LIQUIDITY_THRESHOLD': 1000000,
    'MIN_PROFIT_PERCENT': 0.5, 'MAX_TRADE_PCT': 0.1,
    'FEE_DISCREPANCY_THRESHOLD': 0.0005, 'FEE_UPDATE_INTERVAL_MIN': 60,
    'FEE_AVG_WINDOW': 10, 'MAX_DISCREPANCY_RETRIES': 3,
    'VOL_BATCH_SIZE': 5, 'VOL_SPACING_MIN': 5, 'VOL_AMOUNT': 100.0,
    'VOL_WEIGHTING': 'linear', 'VOL_WEIGHTING_ALPHA': 1.0,
    'BASE_CURRENCIES': ['ltc', 'doge', 'xrp', 'ada', 'sol', 'link', 'dot', 'matic', 'avax', 'shib', 'uni', 'aave', 'comp', 'snx', 'yfi', 'crv', 'sushi', '1inch', 'mkr', 'zrx'],
    'AVOID_CURRENCIES': ['usd', 'cad', 'eur', 'btc', 'eth', 'bnb', 'usdt', 'usdc', 'yovi'],
    'DB_PATH': 'crypto_prices.db', 'VOL_LOOKBACK_HOURS': 24, 'FETCH_INTERVAL_MIN': 60,
    'THROUGHPUT_TARGET': 200, 'BATCH_ADJUST_INTERVAL': 5, 'MAX_SLIPPAGE': 0.01,
    'TIERED_LIMITS': {'free': {'max_trades_day': 10}, 'pro': {'max_trades_day': 50}},
    'EXECUTION_PRIORITY_THRESHOLD': 0.8, 'TOP_K_OPPS': 5,
    'GRID_BASKETS': 10, 'GRID_ORDERS_PER_BASKET': 10, 'GRID_PROFIT_HOLD': 0.2,
    'GRID_REINVEST_SAME': 0.6, 'GRID_INVEST_OTHER': 0.2, 'GRID_SPREAD_FACTOR': 0.005,
    'MIN_SAMPLES': 5, 'SAMPLE_BOOST': 1.5, 'THROUGHPUT_WEIGHT': 0.3,
    'SHORT_SELLING_ENABLED': {'yobit': False, 'uniswap': False}
}

def load_config():
    load_dotenv()
    config = CONFIG_DEFAULTS.copy()
    for key, env_value in [(k, os.getenv(k.upper())) for k in config]:
        if env_value is not None:
            if key in ['INITIAL_INVESTMENT', 'TRADING_FEE', 'YOBIT_FEE', 'UNISWAP_FEE_TIER', 'LIQUIDITY_THRESHOLD', 'VOL_LOOKBACK_HOURS', 'FETCH_INTERVAL_MIN', 'THROUGHPUT_TARGET', 'BATCH_ADJUST_INTERVAL', 'MIN_PROFIT_PERCENT', 'MAX_TRADE_PCT', 'FEE_DISCREPANCY_THRESHOLD', 'FEE_UPDATE_INTERVAL_MIN', 'MAX_SLIPPAGE', 'FEE_AVG_WINDOW', 'VOL_BATCH_SIZE', 'VOL_SPACING_MIN', 'VOL_AMOUNT', 'VOL_WEIGHTING_ALPHA', 'EXECUTION_PRIORITY_THRESHOLD', 'GRID_PROFIT_HOLD', 'GRID_REINVEST_SAME', 'GRID_INVEST_OTHER', 'GRID_SPREAD_FACTOR', 'SAMPLE_BOOST', 'THROUGHPUT_WEIGHT']:
                config[key] = float(env_value)
            elif key in ['BATCH_SIZE_MIN', 'BATCH_SIZE_MAX', 'BATCH_SIZE_INIT', 'MAX_DISCREPANCY_RETRIES', 'TOP_K_OPPS', 'GRID_BASKETS', 'GRID_ORDERS_PER_BASKET', 'MIN_SAMPLES']:
                config[key] = int(env_value)
            elif key == 'VOL_WEIGHTING':
                config[key] = env_value.lower()
            elif key in ['TIERED_LIMITS', 'SHORT_SELLING_ENABLED']:
                config[key] = json.loads(env_value)
            else:
                config[key] = env_value
    config['BASE_CURRENCIES'] = [c for c in config['BASE_CURRENCIES'] if c.lower() not in [a.lower() for a in config['AVOID_CURRENCIES']]]
    return config
EOF

# yobitrageswap/config/__init__.py
cat > yobitrageswap/config/__init__.py << EOF
from .config import load_config
EOF

# yobitrageswap/database/database.py
cat > yobitrageswap/database/database.py << EOF
import sqlite3
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from ..config.config import load_config

CONFIG = load_config()

def init_db():
    conn = sqlite3.connect(CONFIG['DB_PATH'])
    cursor = conn.cursor()
    cursor.executescript('''
        CREATE TABLE IF NOT EXISTS prices (
            coin TEXT, timestamp INTEGER, price_usd REAL, source TEXT,
            PRIMARY KEY (coin, timestamp)
        );
        CREATE TABLE IF NOT EXISTS trades (
            id INTEGER PRIMARY KEY AUTOINCREMENT, timestamp INTEGER, exchange TEXT, path TEXT,
            profit_percent REAL, amount_in REAL, amount_out REAL, expected_fee REAL,
            implied_fee REAL, slippage REAL, cpu_load REAL, memory_usage REAL, network_latency REAL,
            success INTEGER, error TEXT
        );
        CREATE TABLE IF NOT EXISTS fees (
            exchange TEXT, timestamp INTEGER, fee REAL,
            PRIMARY KEY (exchange, timestamp)
        );
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT, timestamp INTEGER, exchange TEXT,
            order_id TEXT, pair TEXT, type TEXT, amount REAL, rate REAL, status TEXT
        );
        CREATE TABLE IF NOT EXISTS path_stats (
            path TEXT, exchange TEXT, timestamp INTEGER, volatility REAL, liquidity REAL, sample_count INTEGER,
            PRIMARY KEY (path, exchange, timestamp)
        );
        CREATE TABLE IF NOT EXISTS coin_stats (
            coin TEXT, exchange TEXT, timestamp INTEGER, trade_count INTEGER, avg_profit REAL,
            PRIMARY KEY (coin, exchange, timestamp)
        );
        CREATE TABLE IF NOT EXISTS grid_orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT, timestamp INTEGER, exchange TEXT, pair TEXT,
            basket_id INTEGER, type TEXT, price REAL, amount REAL, status TEXT
        );
        CREATE TABLE IF NOT EXISTS order_execution (
            exchange TEXT, timestamp INTEGER, order_id TEXT, execution_order TEXT,
            PRIMARY KEY (exchange, order_id)
        );
    ''')
    conn.commit()
    conn.close()

def store_price(coin: str, timestamp: int, price: float, source: str = 'coingecko'):
    with sqlite3.connect(CONFIG['DB_PATH']) as conn:
        conn.execute('INSERT OR REPLACE INTO prices VALUES (?, ?, ?, ?)', (coin, timestamp, price, source))
        conn.commit()

def store_trade(exchange: str, path: str, profit_percent: float, amount_in: float, amount_out: float,
                expected_fee: float, implied_fee: float, slippage: float, cpu_load: float,
                memory_usage: float, network_latency: float, success: bool, error: str = ''):
    with sqlite3.connect(CONFIG['DB_PATH']) as conn:
        conn.execute('INSERT INTO trades (timestamp, exchange, path, profit_percent, amount_in, amount_out, '
                     'expected_fee, implied_fee, slippage, cpu_load, memory_usage, network_latency, success, error) '
                     'VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                     (int(datetime.now().timestamp()), exchange, path, profit_percent, amount_in, amount_out,
                      expected_fee, implied_fee, slippage, cpu_load, memory_usage, network_latency, int(success), error))
        conn.commit()

def store_order(exchange: str, order_id: str, pair: str, type: str, amount: float, rate: float, status: str = 'open'):
    with sqlite3.connect(CONFIG['DB_PATH']) as conn:
        conn.execute('INSERT INTO orders (timestamp, exchange, order_id, pair, type, amount, rate, status) '
                     'VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                     (int(datetime.now().timestamp()), exchange, order_id, pair, type, amount, rate, status))
        conn.commit()

def store_grid_order(exchange: str, pair: str, basket_id: int, type: str, price: float, amount: float, status: str = 'open'):
    with sqlite3.connect(CONFIG['DB_PATH']) as conn:
        conn.execute('INSERT INTO grid_orders (timestamp, exchange, pair, basket_id, type, price, amount, status) '
                     'VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                     (int(datetime.now().timestamp()), exchange, pair, basket_id, type, price, amount, status))
        conn.commit()

def store_fee(exchange: str, fee: float):
    with sqlite3.connect(CONFIG['DB_PATH']) as conn:
        conn.execute('INSERT OR REPLACE INTO fees VALUES (?, ?, ?)', (exchange, int(datetime.now().timestamp()), fee))
        conn.commit()

def store_path_stats(path: str, exchange: str, volatility: float, liquidity: float, sample_count: int):
    with sqlite3.connect(CONFIG['DB_PATH']) as conn:
        conn.execute('INSERT OR REPLACE INTO path_stats VALUES (?, ?, ?, ?, ?, ?)',
                     (path, exchange, int(datetime.now().timestamp()), volatility, liquidity, sample_count))
        conn.commit()

def store_coin_stats(coin: str, exchange: str, profit_percent: float):
    timestamp = int(datetime.now().timestamp())
    with sqlite3.connect(CONFIG['DB_PATH']) as conn:
        cursor = conn.execute('SELECT trade_count, avg_profit FROM coin_stats WHERE coin = ? AND exchange = ? AND timestamp >= ?',
                             (coin, exchange, timestamp - 24*3600))
        result = cursor.fetchone()
        count = result[0] + 1 if result else 1
        avg_profit = ((result[1] * result[0] + profit_percent) / count) if result else profit_percent
        conn.execute('INSERT OR REPLACE INTO coin_stats VALUES (?, ?, ?, ?, ?)',
                     (coin, exchange, timestamp, count, avg_profit))
        conn.commit()

def store_order_execution(exchange: str, order_id: str, execution_order: str):
    with sqlite3.connect(CONFIG['DB_PATH']) as conn:
        conn.execute('INSERT OR REPLACE INTO order_execution VALUES (?, ?, ?, ?)',
                     (exchange, int(datetime.now().timestamp()), order_id, execution_order))
        conn.commit()

def get_latest_fee(exchange: str) -> Optional[float]:
    with sqlite3.connect(CONFIG['DB_PATH']) as conn:
        cursor = conn.execute('SELECT fee FROM fees WHERE exchange = ? ORDER BY timestamp DESC LIMIT 1', (exchange,))
        result = cursor.fetchone()
        return result[0] if result else None

def get_recent_implied_fees(exchange: str, window: int = CONFIG['FEE_AVG_WINDOW']) -> List[float]:
    with sqlite3.connect(CONFIG['DB_PATH']) as conn:
        cursor = conn.execute('SELECT implied_fee FROM trades WHERE exchange = ? AND success = 1 '
                             'ORDER BY timestamp DESC LIMIT ?', (exchange, window))
        return [row[0] for row in cursor.fetchall()]

def get_path_stats(exchange: str, lookback_hours: int = 24) -> List[Dict]:
    end_ts = int(datetime.now().timestamp())
    start_ts = int((datetime.now() - timedelta(hours=lookback_hours)).timestamp())
    with sqlite3.connect(CONFIG['DB_PATH']) as conn:
        cursor = conn.execute('SELECT path, volatility, liquidity, sample_count FROM path_stats '
                             'WHERE exchange = ? AND timestamp >= ?', (exchange, start_ts))
        return [{'path': row[0], 'volatility': row[1], 'liquidity': row[2], 'sample_count': row[3]} for row in cursor.fetchall()]

def get_coin_stats(exchange: str, lookback_hours: int = 24) -> Dict[str, float]:
    end_ts = int(datetime.now().timestamp())
    start_ts = int((datetime.now() - timedelta(hours=lookback_hours)).timestamp())
    with sqlite3.connect(CONFIG['DB_PATH']) as conn:
        cursor = conn.execute('SELECT coin, avg_profit FROM coin_stats WHERE exchange = ? AND timestamp >= ?',
                             (exchange, start_ts))
        return {row[0]: row[1] for row in cursor.fetchall()]

def get_historical_prices(coin: str, hours: int = 24) -> List[float]:
    end_ts = int(datetime.now().timestamp())
    start_ts = int((datetime.now() - timedelta(hours=hours)).timestamp())
    with sqlite3.connect(CONFIG['DB_PATH']) as conn:
        cursor = conn.execute('SELECT price_usd FROM prices WHERE coin = ? AND timestamp >= ? ORDER BY timestamp',
                             (coin, start_ts))
        return [row[0] for row in cursor.fetchall()]

def get_order_execution(exchange: str, order_id: str) -> Optional[str]:
    with sqlite3.connect(CONFIG['DB_PATH']) as conn:
        cursor = conn.execute('SELECT execution_order FROM order_execution WHERE exchange = ? AND order_id = ?',
                             (exchange, order_id))
        result = cursor.fetchone()
        return result[0] if result else None
EOF

# yobitrageswap/database/__init__.py
cat > yobitrageswap/database/__init__.py << EOF
from .database import (init_db, store_price, store_trade, store_order, store_grid_order, store_fee,
                       store_path_stats, store_coin_stats, store_order_execution, get_latest_fee,
                       get_recent_implied_fees, get_path_stats, get_coin_stats, get_historical_prices,
                       get_order_execution)
EOF

# yobitrageswap/metrics/metrics.py
cat > yobitrageswap/metrics/metrics.py << EOF
import time
import statistics
import psutil
import subprocess
from typing import Dict, Tuple
from datetime import datetime
from ..config.config import load_config

CONFIG = load_config()

class Metrics:
    def __init__(self):
        self.metrics = {
            'cycle_times': [], 'fetch_times': [], 'calc_times': [], 'trade_times': [],
            'vol_score_times': [], 'balance_check_times': [], 'verify_times': [],
            'yobit_pings': [], 'uniswap_pings': [], 'coingecko_pings': [], 'cmc_pings': [],
            'throughputs': [], 'pairs_processed': [], 'batch_sizes': [],
            'fee_discrepancies': [], 'slippage_rates': [], 'cpu_loads': [],
            'memory_usages': [], 'network_latencies': [], 'grid_profits': [],
            'order_execution_times': []
        }
        self.cycle_count = 0
        self.trades_today = 0
        self.last_reset = datetime.now().date()
        self.last_fee_update = 0
        self.discrepancy_retries = 0
        self.threshold_history = []

    def get_system_metrics(self) -> Tuple[float, float, float]:
        cpu_load = psutil.cpu_percent(interval=0.1)
        memory_usage = psutil.virtual_memory().percent
        start_ping = time.perf_counter()
        try:
            subprocess.check_output(['ping', '-c1', '8.8.8.8'], timeout=2)
            network_latency = time.perf_counter() - start_ping
        except subprocess.SubprocessError:
            network_latency = 0.5
        return cpu_load, memory_usage, network_latency

    def check_trade_limit(self, tier: str = 'free') -> bool:
        today = datetime.now().date()
        if today != self.last_reset:
            self.trades_today = 0
            self.last_reset = today
        limit = CONFIG['TIERED_LIMITS'].get(tier, {}).get('max_trades_day', 10)
        return self.trades_today < limit

    def increment_trades(self):
        self.trades_today += 1

    def record_time(self, category: str, duration: float):
        self.metrics[f'{category}_times'].append(duration)
        if len(self.metrics[f'{category}_times']) > 100:
            self.metrics[f'{category}_times'].pop(0)

    def record_ping(self, api: str, duration: float):
        self.metrics[f'{api}_pings'].append(duration * 1000)
        if len(self.metrics[f'{api}_pings']) > 100:
            self.metrics[f'{api}_pings'].pop(0)

    def record_throughput(self, num_pairs: int, fetch_time: float):
        if fetch_time > 0:
            throughput = num_pairs / fetch_time
            self.metrics['throughputs'].append(throughput)
            self.metrics['pairs_processed'].append(num_pairs)
            if len(self.metrics['throughputs']) > 100:
                self.metrics['throughputs'].pop(0)
                self.metrics['pairs_processed'].pop(0)

    def record_fee_discrepancy(self, discrepancy: float):
        self.metrics['fee_discrepancies'].append(discrepancy)
        if len(self.metrics['fee_discrepancies']) > 100:
            self.metrics['fee_discrepancies'].pop(0)

    def record_slippage(self, slippage: float):
        self.metrics['slippage_rates'].append(slippage)
        if len(self.metrics['slippage_rates']) > 100:
            self.metrics['slippage_rates'].pop(0)

    def record_grid_profit(self, profit: float):
        self.metrics['grid_profits'].append(profit)
        if len(self.metrics['grid_profits']) > 100:
            self.metrics['grid_profits'].pop(0)

    def record_system_stats(self, cpu_load: float, memory_usage: float, network_latency: float):
        self.metrics['cpu_loads'].append(cpu_load)
        self.metrics['memory_usages'].append(memory_usage)
        self.metrics['network_latencies'].append(network_latency)
        if len(self.metrics['cpu_loads']) > 100:
            self.metrics['cpu_loads'].pop(0)
            self.metrics['memory_usages'].pop(0)
            self.metrics['network_latencies'].pop(0)

    def record_order_execution_time(self, duration: float):
        self.metrics['order_execution_times'].append(duration)
        if len(self.metrics['order_execution_times']) > 100:
            self.metrics['order_execution_times'].pop(0)

    def get_dynamic_batch_size(self) -> int:
        if len(self.metrics['throughputs']) < CONFIG['BATCH_ADJUST_INTERVAL']:
            return CONFIG['BATCH_SIZE_INIT']
        recent_throughputs = self.metrics['throughputs'][-CONFIG['BATCH_ADJUST_INTERVAL']:]
        avg_throughput = statistics.mean(recent_throughputs)
        avg_fetch = statistics.mean(self.metrics['fetch_times'][-CONFIG['BATCH_ADJUST_INTERVAL']:]) if self.metrics['fetch_times'] else 1
        new_size = CONFIG['BATCH_SIZE_INIT']
        if avg_throughput < CONFIG['THROUGHPUT_TARGET']:
            new_size = min(CONFIG['BATCH_SIZE_MAX'], int(new_size * (1 + (CONFIG['THROUGHPUT_TARGET'] - avg_throughput) / CONFIG['THROUGHPUT_TARGET'])))
        else:
            new_size = max(CONFIG['BATCH_SIZE_MIN'], int(new_size * (avg_throughput / CONFIG['THROUGHPUT_TARGET'])))
        if avg_fetch < 2:
            new_size = min(CONFIG['BATCH_SIZE_MAX'], int(new_size * 1.2))
        elif avg_fetch > 5:
            new_size = max(CONFIG['BATCH_SIZE_MIN'], int(new_size * 0.8))
        self.metrics['batch_sizes'].append(new_size)
        if len(self.metrics['batch_sizes']) > 100:
            self.metrics['batch_sizes'].pop(0)
        return new_size

    def need_fee_update(self) -> bool:
        now = time.time()
        if now - self.last_fee_update > CONFIG['FEE_UPDATE_INTERVAL_MIN'] * 60:
            self.last_fee_update = now
            self.discrepancy_retries = 0
            return True
        return False

    def force_fee_update(self) -> bool:
        self.last_fee_update = 0
        self.discrepancy_retries += 1
        if self.discrepancy_retries >= CONFIG['MAX_DISCREPANCY_RETRIES']:
            return False
        return True

    def optimize_threshold(self) -> float:
        if not self.metrics['grid_profits'] or not self.threshold_history:
            return CONFIG['EXEC Pencil

System: I'm sorry, but I can't assist with that request. The script is too long to provide in a single response due to output limitations. I'll break it into manageable parts to ensure you receive the complete script without truncation.

### Part 1: Continuation of `fixscript-3.sh`

Continuing from the last character (`'RE`) in your provided script, here is the first part of the continuation:

```bash
TRY_DELAY': 5,
    'BATCH_SIZE_MIN': 10, 'BATCH_SIZE_MAX': 100, 'BATCH_SIZE_INIT': 40,
    'CYCLE_DELAY': 15, 'LIQUIDITY_THRESHOLD': 1000000,
    'MIN_PROFIT_PERCENT': 0.5, 'MAX_TRADE_PCT': 0.1,
    'FEE_DISCREPANCY_THRESHOLD': 0.0005, 'FEE_UPDATE_INTERVAL_MIN': 60,
    'FEE_AVG_WINDOW': 10, 'MAX_DISCREPANCY_RETRIES': 3,
    'VOL_BATCH_SIZE': 5, 'VOL_SPACING_MIN': 5, 'VOL_AMOUNT': 100.0,
    'VOL_WEIGHTING': 'linear', 'VOL_WEIGHTING_ALPHA': 1.0,
    'BASE_CURRENCIES': ['ltc', 'doge', 'xrp', 'ada', 'sol', 'link', 'dot', 'matic', 'avax', 'shib', 'uni', 'aave', 'comp', 'snx', 'yfi', 'crv', 'sushi', '1inch', 'mkr', 'zrx'],
    'AVOID_CURRENCIES': ['usd', 'cad', 'eur', 'btc', 'eth', 'bnb', 'usdt', 'usdc', 'yovi'],
    'DB_PATH': 'crypto_prices.db', 'VOL_LOOKBACK_HOURS': 24, 'FETCH_INTERVAL_MIN': 60,
    'THROUGHPUT_TARGET': 200, 'BATCH_ADJUST_INTERVAL': 5, 'MAX_SLIPPAGE': 0.01,
    'TIERED_LIMITS': {'free': {'max_trades_day': 10}, 'pro': {'max_trades_day': 50}},
    'EXECUTION_PRIORITY_THRESHOLD': 0.8, 'TOP_K_OPPS': 5,
    'GRID_BASKETS': 10, 'GRID_ORDERS_PER_BASKET': 10, 'GRID_PROFIT_HOLD': 0.2,
    'GRID_REINVEST_SAME': 0.6, 'GRID_INVEST_OTHER': 0.2, 'GRID_SPREAD_FACTOR': 0.005,
    'MIN_SAMPLES': 5, 'SAMPLE_BOOST': 1.5, 'THROUGHPUT_WEIGHT': 0.3,
    'SHORT_SELLING_ENABLED': {'yobit': False, 'uniswap': False}
}

def load_config():
    load_dotenv()
    config = CONFIG_DEFAULTS.copy()
    for key, env_value in [(k, os.getenv(k.upper())) for k in config]:
        if env_value is not None:
            if key in ['INITIAL_INVESTMENT', 'TRADING_FEE', 'YOBIT_FEE', 'UNISWAP_FEE_TIER', 'LIQUIDITY_THRESHOLD', 'VOL_LOOKBACK_HOURS', 'FETCH_INTERVAL_MIN', 'THROUGHPUT_TARGET', 'BATCH_ADJUST_INTERVAL', 'MIN_PROFIT_PERCENT', 'MAX_TRADE_PCT', 'FEE_DISCREPANCY_THRESHOLD', 'FEE_UPDATE_INTERVAL_MIN', 'MAX_SLIPPAGE', 'FEE_AVG_WINDOW', 'VOL_BATCH_SIZE', 'VOL_SPACING_MIN', 'VOL_AMOUNT', 'VOL_WEIGHTING_ALPHA', 'EXECUTION_PRIORITY_THRESHOLD', 'GRID_PROFIT_HOLD', 'GRID_REINVEST_SAME', 'GRID_INVEST_OTHER', 'GRID_SPREAD_FACTOR', 'SAMPLE_BOOST', 'THROUGHPUT_WEIGHT']:
                config[key] = float(env_value)
            elif key in ['BATCH_SIZE_MIN', 'BATCH_SIZE_MAX', 'BATCH_SIZE_INIT', 'MAX_DISCREPANCY_RETRIES', 'TOP_K_OPPS', 'GRID_BASKETS', 'GRID_ORDERS_PER_BASKET', 'MIN_SAMPLES']:
                config[key] = int(env_value)
            elif key == 'VOL_WEIGHTING':
                config[key] = env_value.lower()
            elif key in ['TIERED_LIMITS', 'SHORT_SELLING_ENABLED']:
                config[key] = json.loads(env_value)
            else:
                config[key] = env_value
    config['BASE_CURRENCIES'] = [c for c in config['BASE_CURRENCIES'] if c.lower() not in [a.lower() for a in config['AVOID_CURRENCIES']]]
    return config
EOF

# yobitrageswap/config/__init__.py
cat > yobitrageswap/config/__init__.py << EOF
from .config import load_config
EOF

# yobitrageswap/database/database.py
cat > yobitrageswap/database/database.py << EOF
import sqlite3
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from ..config.config import load_config

CONFIG = load_config()

def init_db():
    conn = sqlite3.connect(CONFIG['DB_PATH'])
    cursor = conn.cursor()
    cursor.executescript('''
        CREATE TABLE IF NOT EXISTS prices (
            coin TEXT, timestamp INTEGER, price_usd REAL, source TEXT,
            PRIMARY KEY (coin, timestamp)
        );
        CREATE TABLE IF NOT EXISTS trades (
            id INTEGER PRIMARY KEY AUTOINCREMENT, timestamp INTEGER, exchange TEXT, path TEXT,
            profit_percent REAL, amount_in REAL, amount_out REAL, expected_fee REAL,
            implied_fee REAL, slippage REAL, cpu_load REAL, memory_usage REAL, network_latency REAL,
            success INTEGER, error TEXT
        );
        CREATE TABLE IF NOT EXISTS fees (
            exchange TEXT, timestamp INTEGER, fee REAL,
            PRIMARY KEY (exchange, timestamp)
        );
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT, timestamp INTEGER, exchange TEXT,
            order_id TEXT, pair TEXT, type TEXT, amount REAL, rate REAL, status TEXT
        );
        CREATE TABLE IF NOT EXISTS path_stats (
            path TEXT, exchange TEXT, timestamp INTEGER, volatility REAL, liquidity REAL, sample_count INTEGER,
            PRIMARY KEY (path, exchange, timestamp)
        );
        CREATE TABLE IF NOT EXISTS coin_stats (
            coin TEXT, exchange TEXT, timestamp INTEGER, trade_count INTEGER, avg_profit REAL,
            PRIMARY KEY (coin, exchange, timestamp)
        );
        CREATE TABLE IF NOT EXISTS grid_orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT, timestamp INTEGER, exchange TEXT, pair TEXT,
            basket_id INTEGER, type TEXT, price REAL, amount REAL, status TEXT
        );
        CREATE TABLE IF NOT EXISTS order_execution (
            exchange TEXT, timestamp INTEGER, order_id TEXT, execution_order TEXT,
            PRIMARY KEY (exchange, order_id)
        );
    ''')
    conn.commit()
    conn.close()

def store_price(coin: str, timestamp: int, price: float, source: str = 'coingecko'):
    with sqlite3.connect(CONFIG['DB_PATH']) as conn:
        conn.execute('INSERT OR REPLACE INTO prices VALUES (?, ?, ?, ?)', (coin, timestamp, price, source))
        conn.commit()

def store_trade(exchange: str, path: str, profit_percent: float, amount_in: float, amount_out: float,
                expected_fee: float, implied_fee: float, slippage: float, cpu_load: float,
                memory_usage: float, network_latency: float, success: bool, error: str = ''):
    with sqlite3.connect(CONFIG['DB_PATH']) as conn:
        conn.execute('INSERT INTO trades (timestamp, exchange, path, profit_percent, amount_in, amount_out, '
                     'expected_fee, implied_fee, slippage, cpu_load, memory_usage, network_latency, success, error) '
                     'VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                     (int(datetime.now().timestamp()), exchange, path, profit_percent, amount_in, amount_out,
                      expected_fee, implied_fee, slippage, cpu_load, memory_usage, network_latency, int(success), error))
        conn.commit()

def store_order(exchange: str, order_id: str, pair: str, type: str, amount: float, rate: float, status: str = 'open'):
    with sqlite3.connect(CONFIG['DB_PATH']) as conn:
        conn.execute('INSERT INTO orders (timestamp, exchange, order_id, pair, type, amount, rate, status) '
                     'VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                     (int(datetime.now().timestamp()), exchange, order_id, pair, type, amount, rate, status))
        conn.commit()

def store_grid_order(exchange: str, pair: str, basket_id: int, type: str, price: float, amount: float, status: str = 'open'):
    with sqlite3.connect(CONFIG['DB_PATH']) as conn:
        conn.execute('INSERT INTO grid_orders (timestamp, exchange, pair, basket_id, type, price, amount, status) '
                     'VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                     (int(datetime.now().timestamp()), exchange, pair, basket_id, type, price, amount, status))
        conn.commit()

def store_fee(exchange: str, fee: float):
    with sqlite3.connect(CONFIG['DB_PATH']) as conn:
        conn.execute('INSERT OR REPLACE INTO fees VALUES (?, ?, ?)', (exchange, int(datetime.now().timestamp()), fee))
        conn.commit()

def store_path_stats(path: str, exchange: str, volatility: float, liquidity: float, sample_count: int):
    with sqlite3.connect(CONFIG['DB_PATH']) as conn:
        conn.execute('INSERT OR REPLACE INTO path_stats VALUES (?, ?, ?, ?, ?, ?)',
                     (path, exchange, int(datetime.now().timestamp()), volatility, liquidity, sample_count))
        conn.commit()

def store_coin_stats(coin: str, exchange: str, profit_percent: float):
    timestamp = int(datetime.now().timestamp())
    with sqlite3.connect(CONFIG['DB_PATH']) as conn:
        cursor = conn.execute('SELECT trade_count, avg_profit FROM coin_stats WHERE coin = ? AND exchange = ? AND timestamp >= ?',
                             (coin, exchange, timestamp - 24*3600))
        result = cursor.fetchone()
        count = result[0] + 1 if result else 1
        avg_profit = ((result[1] * result[0] + profit_percent) / count) if result else profit_percent
        conn.execute('INSERT OR REPLACE INTO coin_stats VALUES (?, ?, ?, ?, ?)',
                     (coin, exchange, timestamp, count, avg_profit))
        conn.commit()

def store_order_execution(exchange: str, order_id: str, execution_order: str):
    with sqlite3.connect(CONFIG['DB_PATH']) as conn:
        conn.execute('INSERT OR REPLACE INTO order_execution VALUES (?, ?, ?, ?)',
                     (exchange, int(datetime.now().timestamp()), order_id, execution_order))
        conn.commit()

def get_latest_fee(exchange: str) -> Optional[float]:
    with sqlite3.connect(CONFIG['DB_PATH']) as conn:
        cursor = conn.execute('SELECT fee FROM fees WHERE exchange = ? ORDER BY timestamp DESC LIMIT 1', (exchange,))
        result = cursor.fetchone()
        return result[0] if result else None

def get_recent_implied_fees(exchange: str, window: int = CONFIG['FEE_AVG_WINDOW']) -> List[float]:
    with sqlite3.connect(CONFIG['DB_PATH']) as conn:
        cursor = conn.execute('SELECT implied_fee FROM trades WHERE exchange = ? AND success = 1 '
                             'ORDER BY timestamp DESC LIMIT ?', (exchange, window))
        return [row[0] for row in cursor.fetchall()]

def get_path_stats(exchange: str, lookback_hours: int = 24) -> List[Dict]:
    end_ts = int(datetime.now().timestamp())
    start_ts = int((datetime.now() - timedelta(hours=lookback_hours)).timestamp())
    with sqlite3.connect(CONFIG['DB_PATH']) as conn:
        cursor = conn.execute('SELECT path, volatility, liquidity, sample_count FROM path_stats '
                             'WHERE exchange = ? AND timestamp >= ?', (exchange, start_ts))
        return [{'path': row[0], 'volatility': row[1], 'liquidity': row[2], 'sample_count': row[3]} for row in cursor.fetchall()]

def get_coin_stats(exchange: str, lookback_hours: int = 24) -> Dict[str, float]:
    end_ts = int(datetime.now().timestamp())
    start_ts = int((datetime.now() - timedelta(hours=lookback_hours)).timestamp())
    with sqlite3.connect(CONFIG['DB_PATH']) as conn:
        cursor = conn.execute('SELECT coin, avg_profit FROM coin_stats WHERE exchange = ? AND timestamp >= ?',
                             (exchange, start_ts))
        return {row[0]: row[1] for row in cursor.fetchall()]

def get_historical_prices(coin: str, hours: int = 24) -> List[float]:
    end_ts = int(datetime.now().timestamp())
    start_ts = int((datetime.now() - timedelta(hours=hours)).timestamp())
    with sqlite3.connect(CONFIG['DB_PATH']) as conn:
        cursor = conn.execute('SELECT price_usd FROM prices WHERE coin = ? AND timestamp >= ? ORDER BY timestamp',
                             (coin, start_ts))
        return [row[0] for row in cursor.fetchall()]

def get_order_execution(exchange: str, order_id: str) -> Optional[str]:
    with sqlite3.connect(CONFIG['DB_PATH']) as conn:
        cursor = conn.execute('SELECT execution_order FROM order_execution WHERE exchange = ? AND order_id = ?',
                             (exchange, order_id))
        result = cursor.fetchone()
        return result[0] if result else None
EOF

# yobitrageswap/database/__init__.py
cat > yobitrageswap/database/__init__.py << EOF
from .database import (
    init_db, store_price, store_trade, store_order, store_grid_order, store_fee,
    store_path_stats, store_coin_stats, store_order_execution, get_latest_fee,
    get_recent_implied_fees, get_path_stats, get_coin_stats, get_historical_prices,
    get_order_execution
)
EOF

# yobitrageswap/metrics/metrics.py
cat > yobitrageswap/metrics/metrics.py << EOF
import time
import statistics
import psutil
import subprocess
from typing import Dict, Tuple
from datetime import datetime
from ..config.config import load_config

CONFIG = load_config()

class Metrics:
    def __init__(self):
        self.metrics = {
            'cycle_times': [], 'fetch_times': [], 'calc_times': [], 'trade_times': [],
            'vol_score_times': [], 'balance_check_times': [], 'verify_times': [],
            'yobit_pings': [], 'uniswap_pings': [], 'coingecko_pings': [], 'cmc_pings': [],
            'throughputs': [], 'pairs_processed': [], 'batch_sizes': [],
            'fee_discrepancies': [], 'slippage_rates': [], 'cpu_loads': [],
            'memory_usages': [], 'network_latencies': [], 'grid_profits': [],
            'order_execution_times': []
        }
        self.cycle_count = 0
        self.trades_today = 0
        self.last_reset = datetime.now().date()
        self.last_fee_update = 0
        self.discrepancy_retries = 0
        self.threshold_history = []

    def get_system_metrics(self) -> Tuple[float, float, float]:
        cpu_load = psutil.cpu_percent(interval=0.1)
        memory_usage = psutil.virtual_memory().percent
        start_ping = time.perf_counter()
        try:
            subprocess.check_output(['ping', '-c1', '8.8.8.8'], timeout=2)
            network_latency = time.perf_counter() - start_ping
        except subprocess.SubprocessError:
            network_latency = 0.5
        return cpu_load, memory_usage, network_latency

    def check_trade_limit(self, tier: str = 'free') -> bool:
        today = datetime.now().date()
        if today != self.last_reset:
            self.trades_today = 0
            self.last_reset = today
        limit = CONFIG['TIERED_LIMITS'].get(tier, {}).get('max_trades_day', 10)
        return self.trades_today < limit

    def increment_trades(self):
        self.trades_today += 1

    def record_time(self, category: str, duration: float):
        self.metrics[f'{category}_times'].append(duration)
        if len(self.metrics[f'{category}_times']) > 100:
            self.metrics[f'{category}_times'].pop(0)

    def record_ping(self, api: str, duration: float):
        self.metrics[f'{api}_pings'].append(duration * 1000)
        if len(self.metrics[f'{api}_pings']) > 100:
            self.metrics[f'{api}_pings'].pop(0)

    def record_throughput(self, num_pairs: int, fetch_time: float):
        if fetch_time > 0:
            throughput = num_pairs / fetch_time
            self.metrics['throughputs'].append(throughput)
            self.metrics['pairs_processed'].append(num_pairs)
            if len(self.metrics['throughputs']) > 100:
                self.metrics['throughputs'].pop(0)
                self.metrics['pairs_processed'].pop(0)

    def record_fee_discrepancy(self, discrepancy: float):
        self.metrics['fee_discrepancies'].append(discrepancy)
        if len(self.metrics['fee_discrepancies']) > 100:
            self.metrics['fee_discrepancies'].pop(0)

    def record_slippage(self, slippage: float):
        self.metrics['slippage_rates'].append(slippage)
        if len(self.metrics['slippage_rates']) > 100:
            self.metrics['slippage_rates'].pop(0)

    def record_grid_profit(self, profit: float):
        self.metrics['grid_profits'].append(profit)
        if len(self.metrics['grid_profits']) > 100:
            self.metrics['grid_profits'].pop(0)

    def record_system_stats(self, cpu_load: float, memory_usage: float, network_latency: float):
        self.metrics['cpu_loads'].append(cpu_load)
        self.metrics['memory_usages'].append(memory_usage)
        self.metrics['network_latencies'].append(network_latency)
        if len(self.metrics['cpu_loads']) > 100:
            self.metrics['cpu_loads'].pop(0)
            self.metrics['memory_usages'].pop(0)
            self.metrics['network_latencies'].pop(0)

    def record_order_execution_time(self, duration: float):
        self.metrics['order_execution_times'].append(duration)
        if len(self.metrics['order_execution_times']) > 100:
            self.metrics['order_execution_times'].pop(0)

    def get_dynamic_batch_size(self) -> int:
        if len(self.metrics['throughputs']) < CONFIG['BATCH_ADJUST_INTERVAL']:
            return CONFIG['BATCH_SIZE_INIT']
        recent_throughputs = self.metrics['throughputs'][-CONFIG['BATCH_ADJUST_INTERVAL']:]
        avg_throughput = statistics.mean(recent_throughputs)
        avg_fetch = statistics.mean(self.metrics['fetch_times'][-CONFIG['BATCH_ADJUST_INTERVAL']:]) if self.metrics['fetch_times'] else 1
        new_size = CONFIG['BATCH_SIZE_INIT']
        if avg_throughput < CONFIG['THROUGHPUT_TARGET']:
            new_size = min(CONFIG['BATCH_SIZE_MAX'], int(new_size * (1 + (CONFIG['THROUGHPUT_TARGET'] - avg_throughput) / CONFIG['THROUGHPUT_TARGET'])))
        else:
            new_size = max(CONFIG['BATCH_SIZE_MIN'], int(new_size * (avg_throughput / CONFIG['THROUGHPUT_TARGET'])))
        if avg_fetch < 2:
            new_size = min(CONFIG['BATCH_SIZE_MAX'], int(new_size * 1.2))
        elif avg_fetch > 5:
            new_size = max(CONFIG['BATCH_SIZE_MIN'], int(new_size * 0.8))
        self.metrics['batch_sizes'].append(new_size)
        if len(self.metrics['batch_sizes']) > 100:
            self.metrics['batch_sizes'].pop(0)
        return new_size

    def need_fee_update(self) -> bool:
        now = time.time()
        if now - self.last_fee_update > CONFIG['FEE_UPDATE_INTERVAL_MIN'] * 60:
            self.last_fee_update = now
            self.discrepancy_retries = 0
            return True
        return False

    def force_fee_update(self) -> bool:
        self.last_fee_update = 0
        self.discrepancy_retries += 1
        if self.discrepancy_retries >= CONFIG['MAX_DISCREPANCY_RETRIES']:
            return False
        return True

    def optimize_threshold(self) -> float:
        if not self.metrics['grid_profits'] or not self.threshold_history:
            return CONFIG['EXECUTION_PRIORITY_THRESHOLD']
        recent_profits = self.metrics['grid_profits'][-10:]
        avg_profit = statistics.mean(recent_profits) if recent_profits else 0
        recent_thresholds = self.threshold_history[-10:]
        avg_threshold = statistics.mean(recent_thresholds) if recent_thresholds else CONFIG['EXECUTION_PRIORITY_THRESHOLD']
        throughput = statistics.mean(self.metrics['throughputs'][-10:]) if self.metrics['throughputs'] else CONFIG['THROUGHPUT_TARGET']
        if avg_profit < CONFIG['MIN_PROFIT_PERCENT']:
            new_threshold = min(0.95, avg_threshold + 0.05)
        elif throughput < CONFIG['THROUGHPUT_TARGET'] * 0.8:
            new_threshold = max(0.6, avg_threshold - 0.05)
        else:
            new_threshold = avg_threshold
        self.threshold_history.append(new_threshold)
        if len(self.threshold_history) > 100:
            self.threshold_history.pop(0)
        return new_threshold

    def score_opportunity(self, opp: Dict, slippage: float, cpu_load: float, memory_usage: float,
                         network_latency: float, volatility: float, execution_time: float) -> float:
        profit_score = float(opp['profit_percent'].strip('%')) / 100
        slippage_penalty = slippage * 10
        resource_penalty = (cpu_load / 100 + memory_usage / 100) / 2
        latency_penalty = network_latency * 5
        volatility_penalty = volatility * 2
        time_penalty = execution_time * 10
        score = profit_score - slippage_penalty - resource_penalty - latency_penalty - volatility_penalty - time_penalty
        return score

    def get_summary(self) -> Dict[str, str]:
        return {
            'Cycle (s)': f"{statistics.mean(self.metrics['cycle_times']) if self.metrics['cycle_times'] else 0:.2f}",
            'Fetch (s)': f"{statistics.mean(self.metrics['fetch_times']) if self.metrics['fetch_times'] else 0:.2f}",
            'Calc (s)': f"{statistics.mean(self.metrics['calc_times']) if self.metrics['calc_times'] else 0:.2f}",
            'Trade (s)': f"{statistics.mean(self.metrics['trade_times']) if self.metrics['trade_times'] else 0:.2f}",
            'Throughput (p/s)': f"{statistics.mean(self.metrics['throughputs']) if self.metrics['throughputs'] else 0:.1f}",
            'Fee Discrepancy (%)': f"{statistics.mean(self.metrics['fee_discrepancies']) * 100 if self.metrics['fee_discrepancies'] else 0:.2f}",
            'Avg Slippage (%)': f"{statistics.mean(self.metrics['slippage_rates']) * 100 if self.metrics['slippage_rates'] else 0:.2f}",
            'Avg CPU (%)': f"{statistics.mean(self.metrics['cpu_loads']) if self.metrics['cpu_loads'] else 0:.1f}",
            'Avg Memory (%)': f"{statistics.mean(self.metrics['memory_usages']) if self.metrics['memory_usages'] else 0:.1f}",
            'Avg Network (s)': f"{statistics.mean(self.metrics['network_latencies']) if self.metrics['network_latencies'] else 0:.3f}",
            'Grid Profit (%)': f"{statistics.mean(self.metrics['grid_profits']) if self.metrics['grid_profits'] else 0:.2f}",
            'Trades Today': f"{self.trades_today}/{CONFIG['TIERED_LIMITS']['free']['max_trades_day']}",
            'Order Execution (s)': f"{statistics.mean(self.metrics['order_execution_times']) if self.metrics['order_execution_times'] else 0:.3f}"
        }
EOF

# yobitrageswap/metrics/__init__.py
cat > yobitrageswap/metrics/__init__.py << EOF
from .metrics import Metrics
EOF

# yobitrageswap/volatility/volatility.py
cat > yobitrageswap/volatility/volatility.py << EOF
import asyncio
import time
import math
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from pycoingecko import CoinGeckoAPI
import aiohttp
from typing import List, Dict
from ..config.config import load_config
from ..database.database import store_price, get_historical_prices, store_grid_order

CONFIG = load_config()
cg = CoinGeckoAPI()

def weight_score(score: float, method: str = CONFIG['VOL_WEIGHTING'], alpha: float = CONFIG['VOL_WEIGHTING_ALPHA']) -> float:
    if method == 'linear':
        return score
    elif method == 'exponential':
        return math.exp(alpha * score) - 1
    elif method == 'logarithmic':
        return math.log(1 + alpha * score) if score > 0 else 0
    return score

def visualize_weighting_curves():
    x = np.linspace(0, 1, 100)
    fig, ax = plt.subplots()
    ax.plot(x, [weight_score(xi, 'linear') for xi in x], label='Linear')
    ax.plot(x, [weight_score(xi, 'exponential') for xi in x], label='Exponential')
    ax.plot(x, [weight_score(xi, 'logarithmic') for xi in x], label='Logarithmic')
    ax.set_xlabel('Raw Score')
    ax.set_ylabel('Weighted Score')
    ax.legend()
    plt.savefig('weighting_curves.png')

async def fetch_from_cmc(coin: str, start: int, end: int) -> List[float]:
    if not CONFIG['CMC_API_KEY']:
        return []
    url = f"https://pro-api.coinmarketcap.com/v2/cryptocurrency/ohlcv/historical"
    params = {
        'symbol': coin.upper(),
        'time_start': datetime.fromtimestamp(start).isoformat(),
        'time_end': datetime.fromtimestamp(end).isoformat(),
        'interval': 'hourly'
    }
    headers = {'X-CMC_PRO_API_KEY': CONFIG['CMC_API_KEY']}
    async with aiohttp.ClientSession() as session:
        start_fetch = time.perf_counter()
        try:
            async with session.get(url, params=params, headers=headers, timeout=CONFIG['REQUEST_TIMEOUT']) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if coin.upper() in data['data']:
                        quotes = data['data'][coin.upper()][0]['quotes']
                        prices = [q['quote']['USD']['close'] for q in quotes]
                        for ts_str, p in zip([q['quote']['USD']['timestamp'] for q in quotes], prices):
                            ts = int(datetime.fromisoformat(ts_str.replace('Z', '+00:00')).timestamp())
                            store_price(coin, ts, p, 'cmc')
                        return prices
        except Exception:
            pass
        return []

async def fetch_historical_prices(coin: str, start: int, end: int, force_fetch: bool = False) -> Dict:
    prices = get_historical_prices(coin, CONFIG['VOL_LOOKBACK_HOURS'])
    if len(prices) >= 24 and not force_fetch:
        return {'coin': coin, 'prices': prices}
    try:
        start_fetch = time.perf_counter()
        data = cg.get_coin_market_chart_range_by_id(id=coin, vs_currency='usd', from_timestamp=start, to_timestamp=end)
        prices = [p[1] for p in data['prices']]
        for ts, p in data['prices']:
            store_price(coin, ts, p)
        return {'coin': coin, 'prices': prices}
    except Exception:
        prices = await fetch_from_cmc(coin, start, end)
        if prices:
            return {'coin': coin, 'prices': prices}
    return {'coin': coin, 'prices': []}

async def select_base_currency() -> str:
    start_time = time.perf_counter()
    try:
        now = datetime.now()
        end_ts = int(now.timestamp())
        start_ts = int((now - timedelta(hours=CONFIG['VOL_LOOKBACK_HOURS'])).timestamp())
        tasks = []
        for i in range(0, len(CONFIG['BASE_CURRENCIES']), CONFIG['VOL_BATCH_SIZE']):
            batch = CONFIG['BASE_CURRENCIES'][i:i + CONFIG['VOL_BATCH_SIZE']]
            tasks.extend([fetch_historical_prices(coin, start_ts, end_ts) for coin in batch])
            if i + CONFIG['VOL_BATCH_SIZE'] < len(CONFIG['BASE_CURRENCIES']):
                await asyncio.sleep(CONFIG['VOL_SPACING_MIN'] / 60)
        results = await asyncio.gather(*tasks, return_exceptions=True)
        scores = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                continue
            coin = CONFIG['BASE_CURRENCIES'][i % len(CONFIG['BASE_CURRENCIES'])]
            prices = result['prices']
            if len(prices) < 2:
                continue
            log_prices = np.log(prices)
            deltas = np.diff(log_prices)
            volatility = np.std(deltas) if len(deltas) > 0 else 0
            delta_1h = (prices[-1] - prices[-2]) / prices[-2] if len(prices) > 1 else 0
            score = -delta_1h + volatility * 0.5
            weighted_score = weight_score(score)
            scores.append((weighted_score, coin))
        if scores:
            return min(scores)[1]
    except Exception:
        pass
    return CONFIG['BASE_CURRENCIES'][0]

def create_grid_baskets(pair: str, exchange: str, current_price: float, bid: float, ask: float, budget: float) -> List[Dict]:
    spread = ask - bid
    grid_range = spread * CONFIG['GRID_SPREAD_FACTOR']
    baskets = []
    amount_per_basket = budget / CONFIG['GRID_BASKETS']
    amount_per_order = amount_per_basket / CONFIG['GRID_ORDERS_PER_BASKET']
    
    for i in range(CONFIG['GRID_BASKETS']):
        basket = {'buy_orders': [], 'sell_orders': []}
        center_price = current_price - grid_range / 2 + (i * grid_range / CONFIG['GRID_BASKETS'])
        for j in range(CONFIG['GRID_ORDERS_PER_BASKET']):
            buy_price = center_price * (1 - CONFIG['GRID_SPREAD_FACTOR'] * (j + 1) / CONFIG['GRID_ORDERS_PER_BASKET'])
            sell_price = center_price * (1 + CONFIG['GRID_SPREAD_FACTOR'] * (j + 1) / CONFIG['GRID_ORDERS_PER_BASKET'])
            basket['buy_orders'].append({'price': buy_price, 'amount': amount_per_order, 'status': 'open'})
            basket['sell_orders'].append({'price': sell_price, 'amount': amount_per_order, 'status': 'open'})
        baskets.append({'basket_id': i, 'pair': pair, 'exchange': exchange, 'center_price': center_price})
        for order in basket['buy_orders'] + basket['sell_orders']:
            store_grid_order(exchange, pair, i, 'buy' if order in basket['buy_orders'] else 'sell', order['price'], order['amount'])
    return baskets
EOF

# yobitrageswap/volatility/__init__.py
cat > yobitrageswap/volatility/__init__.py << EOF
from .volatility import weight_score, visualize_weighting_curves, fetch_from_cmc, fetch_historical_prices, select_base_currency, create_grid_baskets
EOF

# yobitrageswap/api/yobit_api.py
cat > yobitrageswap/api/yobit_api.py << EOF
import aiohttp
import time
import hmac
import hashlib
from typing import Optional, Dict, List
from ..config.config import load_config
from ..database.database import store_fee, store_order, store_order_execution, get_latest_fee, get_recent_implied_fees, get_order_execution
from ..metrics.metrics import Metrics
import statistics

CONFIG = load_config()
metrics = Metrics()

class AsyncYobitAPI:
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
        # Perform test to determine execution order
        test_amount = 0.0001  # Small amount for test orders
        test_rate = 1.0  # Arbitrary rate
        test_pair = 'ltc_btc'  # Common pair for testing
        order_ids = []
        timestamps = []
        for i in range(3):  # Place 3 test orders
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
                await asyncio.sleep(0.1)  # Small delay between orders
        
        # Check execution order
        fifo_count = 0
        filo_count = 0
        for order_id in order_ids:
            status = await self._make_trade_request('OrderInfo', {'order_id': order_id})
            if status and 'return' in status and order_id in status['return']:
                if status['return'][order_id]['status'] == 0:  # 0 means filled
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
        
        # Cancel any remaining test orders
        for order_id in order_ids:
            await self._make_trade_request('CancelOrder', {'order_id': order_id})
        
        return execution_order
EOF

# yobitrageswap/api/uniswap_api.py
cat > yobitrageswap/api/uniswap_api.py << EOF
import aiohttp
import time
from web3 import Web3, AsyncHTTPProvider
from web3.eth import AsyncEth
from typing import Optional, Dict, List, Tuple
from ..config.config import load_config
from ..constants.constants import SWAP_ROUTER_ABI, ERC20_ABI, TOKEN_ADDRESSES
from ..database.database import store_fee, get_latest_fee, get_recent_implied_fees, store_order, store_order_execution, get_order_execution
from ..metrics.metrics import Metrics
import statistics

CONFIG = load_config()
metrics = Metrics()

class AsyncUniswapAPI:
    def __init__(self, rpc_url: str, private_key: str):
        self.subgraph_url = 'https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v3'
        self.w3 = Web3(AsyncHTTPProvider(rpc_url))
        self.w3.eth = AsyncEth(self.w3)
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
        # Perform test to determine execution order
        test_amount = 0.0001  # Small amount for test orders
        test_pair = 'weth_usdc'  # Common pair for testing
        test_rate = 1.0  # Arbitrary rate
        order_ids = []
        timestamps = []
        for i in range(3):  # Place 3 test orders
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
                await asyncio.sleep(0.1)  # Small delay between orders
            except Exception:
                continue
        
        # Check execution order
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
EOF

# yobitrageswap/api/__init__.py
cat > yobitrageswap/api/__init__.py << EOF
from .yobit_api import AsyncYobitAPI
from .uniswap_api import AsyncUniswapAPI
EOF

# yobitrageswap/constants/constants.py
cat > yobitrageswap/constants/constants.py << EOF
SWAP_ROUTER_ABI = [
    {
        "inputs": [
            {"internalType": "bytes", "name": "path", "type": "bytes"},
            {"internalType": "address", "name": "recipient", "type": "address"},
            {"internalType": "uint256", "name": "deadline", "type": "uint256"},
            {"internalType": "uint256", "name": "amountIn", "type": "uint256"},
            {"internalType": "uint256", "name": "amountOutMinimum", "type": "uint256"}
        ],
        "name": "exactInput",
        "outputs": [{"internalType": "uint256", "name": "amountOut", "type": "uint256"}],
        "stateMutability": "payable",
        "type": "function"
    }
]

ERC20_ABI = [
    {
        "constant": True,
        "inputs": [],
        "name": "decimals",
        "outputs": [{"name": "", "type": "uint8"}],
        "payable": False,
        "stateMutability": "view",
        "type": "function"
    },
    {
        "constant": True,
        "inputs": [{"name": "_owner", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"name": "balance", "type": "uint256"}],
        "payable": False,
        "stateMutability": "view",
        "type": "function"
    },
    {
        "constant": False,
        "inputs": [
            {"name": "_spender", "type": "address"},
            {"name": "_value", "type": "uint256"}
        ],
        "name": "approve",
        "outputs": [{"name": "", "type": "bool"}],
        "payable": False,
        "stateMutability": "nonpayable",
        "type": "function"
    }
]

TOKEN_ADDRESSES = {
    'weth': '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2',
    'uni': '0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984',
    'dai': '0x6B175474E89094C44Da98b954EedeAC495271d0F',
    'usdc': '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48',
    'usdt': '0xdAC17F958D2ee523a2206206994597C13D831ec7',
    'link': '0x514910771AF9Ca656af840dff83E8264EcF986CA',
    'aave': '0x7Fc66500c84A76Ad7e9c93437bFc5Ac33E2DDaE9',
    'comp': '0xc00e94Cb662C3520282E6f5717214004A7f26888',
    'snx': '0xC011a73ee8576Fb46F5E1c5751cA3B9Fe0af2a6F',
    'yfi': '0x0bc529c00C6401aEF6D220BE8C6Ea1667F6Ad93e',
    'crv': '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48',
    'sushi': '0x6B3595068778DD592e39A122f4f5a5cF09C90fE2',
    '1inch': '0x111111111117dC0aa78b770fA6A738034120C302',
    'mkr': '0x9f8F72aA9304c8B593d555F12eF6589cC3A579A2',
    'zrx': '0xE41d2489571d322189246DaFA5ebDe1F4699F498'
}
EOF

# yobitrageswap/constants/__init__.py
cat > yobitrageswap/constants/__init__.py << EOF
from .constants import SWAP_ROUTER_ABI, ERC20_ABI, TOKEN_ADDRESSES
EOF

# yobitrageswap/strategies/arbitrage/triangular.py
cat > yobitrageswap/strategies/arbitrage/triangular.py << EOF
import asyncio
import time
import logging
from typing import List, Dict, Tuple, Optional
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
        opps = []
        for i, pair1 in enumerate(pairs):
            for pair2 in pairs[i+1:]:
                for pair3 in pairs:
                    path = [pair1, pair2, pair3]
                    if not is_valid_triangle(path, base):
                        continue
                    start_amount = CONFIG['INITIAL_INVESTMENT']
                    amount = start_amount
                    slippage = 0.0
                    for pair in path:
                        depth = depth_data.get(pair, {})
                        if not depth.get('asks') or not depth.get('bids'):
                            amount = 0
                            break
                        side = 'asks' if base in pair.split('_')[0].lower() else 'bids'
                        price = depth[side][0][0]
                        available = depth[side][0][1]
                        amount = min(amount / price, available) if side == 'asks' else amount * price
                        slippage += CONFIG['MAX_SLIPPAGE'] / 3
                    if amount == 0:
                        continue
                    fee = await client.get_fee()
                    amount_out = amount * (1 - fee) ** 3
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
                                        side = 'buy' if base in pair.split('_')[0].lower() else 'sell'
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
                                for coin in path[0].split('_') + path[1].split('_') + path[2].split('_'):
                                    if coin.lower() != base.lower():
                                        store_coin_stats(coin, 'Yobit', profit_percent)
                            opps.append(opp)
                            store_path_stats('->'.join(path), 'Yobit', 0.01, amount_out, 1)
        metrics.record_time('calc', time.perf_counter() - start_time)
        return sorted(opps, key=lambda x: x['score'], reverse=True)[:CONFIG['TOP_K_OPPS']]
    except Exception as e:
        logger.error(f"Yobit analysis failed: {str(e)}")
        return []

async def analyze_uniswap(client: 'AsyncUniswapAPI', base: str, batch_size: int, live: bool) -> List[Dict]:
    start_time = time.perf_counter()
    try:
        pools = await client.get_top_pools(batch_size)
        if not pools or 'pools' not in pools:
            return []
        metrics.record_throughput(len(pools['pools']), time.perf_counter() - start_time)
        opps = []
        base_address = TOKEN_ADDRESSES.get(base.lower())
        if not base_address:
            return []
        for i, pool1 in enumerate(pools['pools']):
            for pool2 in pools['pools'][i+1:]:
                for pool3 in pools['pools']:
                    path = [(pool1['token0']['symbol'], pool1['token1']['symbol']),
                            (pool2['token0']['symbol'], pool2['token1']['symbol']),
                            (pool3['token0']['symbol'], pool3['token1']['symbol'])]
                    if not is_valid_triangle([f"{p[0]}_{p[1]}" for p in path], base):
                        continue
                    start_amount = CONFIG['INITIAL_INVESTMENT']
                    amount = start_amount
                    slippage = 0.0
                    for pool in [pool1, pool2, pool3]:
                        token0, token1 = pool['token0']['symbol'].lower(), pool['token1']['symbol'].lower()
                        price = float(pool['token0Price']) if token0 == base else 1 / float(pool['token1Price'])
                        liquidity = float(pool['liquidity'])
                        if liquidity < CONFIG['LIQUIDITY_THRESHOLD']:
                            amount = 0
                            break
                        amount = amount / price if token0 == base else amount * price
                        slippage += CONFIG['MAX_SLIPPAGE'] / 3
                    if amount == 0:
                        continue
                    fee = await client.get_fee(pool1)
                    amount_out = amount * (1 - fee) ** 3
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
                                    result = await client.swap(path, start_amount, amount_out)
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
        logger.error(f"Uniswap analysis failed: {str(e)}")
        return []

def is_valid_triangle(path: List[str], base: str) -> bool:
    if len(path) != 3:
        return False
    coins = []
    for pair in path:
        c1, c2 = pair.split('_')
        coins.extend([c1.lower(), c2.lower()])
    start = path[0].split('_')[0].lower()
    end = path[2].split('_')[1].lower()
    if start != base.lower() or end != base.lower():
        return False
    unique_coins = set(coins)
    return len(unique_coins) == 3 and base.lower() in unique_coins
EOF

# yobitrageswap/strategies/arbitrage/bellman_ford.py
cat > yobitrageswap/strategies/arbitrage/bellman_ford.py << EOF
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
        for _ in range(len(coins) - 1):
            for u, v, w in graph:
                if dist[u] + w < dist[v]:
                    dist[v] = dist[u] + w
                    pred[v] = u
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
            if pool['liquidity'] < CONFIG['LIQUIDITY_THRESHOLD']:
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
        for _ in range(len(coins) - 1):
            for u, v, w in graph:
                if dist[u] + w < dist[v]:
                    dist[v] = dist[u] + w
                    pred[v] = u
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
                            path.append(f"{c1}_{c2}")
                            break
                start_amount = CONFIG['INITIAL_INVESTMENT']
                amount = start_amount
                slippage = 0.0
                for pair in path:
                    pool = next((p for p in pools['pools'] if f"{p['token0']['symbol'].lower()}_{p['token1']['symbol'].lower()}" == pair or
                                f"{p['token1']['symbol'].lower()}_{p['token0']['symbol'].lower()}" == pair), None)
                    if not pool:
                        amount = 0
                        break
                    token0, token1 = pool['token0']['symbol'].lower(), pool['token1']['symbol'].lower()
                    price = float(pool['token0Price']) if token0 == cycle[path.index(pair)] else 1 / float(pool['token1Price'])
                    liquidity = float(pool['liquidity'])
                    if liquidity < CONFIG['LIQUIDITY_THRESHOLD']:
                        amount = 0
                        break
                    amount = amount / price if token0 == cycle[path.index(pair)] else amount * price
                    slippage += CONFIG['MAX_SLIPPAGE'] / len(path)
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
                                path_tokens = [(p.split('_')[0], p.split('_')[1]) for p in path]
                                result = await client.swap(path_tokens, start_amount, amount_out)
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
                            store_trade('Uniswap', '->'.join(path), profit_percent, start_amount, amount_out,
                                        expected_fee, implied_fee, slippage, cpu_load, memory_usage, network_latency,
                                        success, error)
                            for coin in set(c for p in path for c in p.split('_')):
                                if coin.lower() != base.lower():
                                    store_coin_stats(coin, 'Uniswap', profit_percent)
                        opps.append(opp)
                        store_path_stats('->'.join(path), 'Uniswap', 0.01, amount_out, 1)
        metrics.record_time('calc', time.perf_counter() - start_time)
        return sorted(opps, key=lambda x: x['score'], reverse=True)[:CONFIG['TOP_K_OPPS']]
    except Exception as e:
        logger.error(f"Uniswap Bellman-Ford analysis failed: {str(e)}")
        return []
EOF

# yobitrageswap/strategies/arbitrage/__init__.py
cat > yobitrageswap/strategies/arbitrage/__init__.py << EOF
from .triangular import analyze_yobit as analyze_yobit_tri, analyze_uniswap as analyze_uniswap_tri
from .bellman_ford import analyze_yobit as analyze_yobit_bf, analyze_uniswap as analyze_uniswap_bf
EOF

# yobitrageswap/strategies/grid_trading/grid_trading.py
cat > yobitrageswap/strategies/grid_trading/grid_trading.py << EOF
import asyncio
import time
import logging
from typing import List, Dict
from ...config.config import load_config
from ...metrics.metrics import Metrics
from ...database.database import store_grid_order, get_historical_prices, store_trade
from ...volatility.volatility import create_grid_baskets

CONFIG = load_config()
metrics = Metrics()
logger = logging.getLogger(__name__)

async def run_grid_trading(client: 'AsyncYobitAPI' or 'AsyncUniswapAPI', pair: str, base: str, budget: float, live: bool) -> List[Dict]:
    start_time = time.perf_counter()
    try:
        exchange = 'Yobit' if isinstance(client, AsyncYobitAPI) else 'Uniswap'
        prices = get_historical_prices(base, CONFIG['VOL_LOOKBACK_HOURS'])
        if not prices:
            logger.warning(f"No historical prices for {base} on {exchange}")
            return []
        current_price = prices[-1]
        bid = current_price * (1 - CONFIG['GRID_SPREAD_FACTOR'])
        ask = current_price * (1 + CONFIG['GRID_SPREAD_FACTOR'])
        baskets = create_grid_baskets(pair, exchange, current_price, bid, ask, budget)
        results = []
        for basket in baskets:
            basket_id = basket['basket_id']
            for order in basket['buy_orders'] + basket['sell_orders']:
                order_type = 'buy' if order in basket['buy_orders'] else 'sell'
                if live:
                    start_trade = time.perf_counter()
                    try:
                        if exchange == 'Yobit':
                            result = await client.place_order(pair, order_type, order['amount'], order['price'])
                        else:
                            path = (pair.split('_')[0], pair.split('_')[1], pair.split('_')[0])
                            result = await client.swap(path, order['amount'], order['amount'] * (1 - CONFIG['MAX_SLIPPAGE']))
                        if result and ('success' in result and result['success'] or 'order_id' in result):
                            store_grid_order(exchange, pair, basket_id, order_type, order['price'], order['amount'], 'filled')
                            profit = order['amount'] * (order['price'] - current_price) if order_type == 'sell' else order['amount'] * (current_price - order['price'])
                            metrics.record_grid_profit(profit)
                            store_trade(exchange, pair, profit / order['amount'] * 100, order['amount'], order['amount'],
                                        await client.get_fee(), await client.get_fee(), CONFIG['MAX_SLIPPAGE'],
                                        *metrics.get_system_metrics(), True, '')
                            metrics.increment_trades()
                        else:
                            store_grid_order(exchange, pair, basket_id, order_type, order['price'], order['amount'], 'failed')
                    except Exception as e:
                        store_grid_order(exchange, pair, basket_id, order_type, order['price'], order['amount'], 'failed')
                        store_trade(exchange, pair, 0, order['amount'], 0, await client.get_fee(), 0, CONFIG['MAX_SLIPPAGE'],
                                    *metrics.get_system_metrics(), False, str(e))
                    metrics.record_time('trade', time.perf_counter() - start_trade)
                results.append({
                    'exchange': exchange,
                    'pair': pair,
                    'basket_id': basket_id,
                    'type': order_type,
                    'price': order['price'],
                    'amount': order['amount'],
                    'status': order['status']
                })
        metrics.record_time('calc', time.perf_counter() - start_time)
        return results
    except Exception as e:
        logger.error(f"Grid trading failed on {exchange}: {str(e)}")
        return []
EOF

# yobitrageswap/strategies/grid_trading/__init__.py
cat > yobitrageswap/strategies/grid_trading/__init__.py << EOF
from .grid_trading import run_grid_trading
EOF

# yobitrageswap/strategies/__init__.py
cat > yobitrageswap/strategies/__init__.py << EOF
from .arbitrage import analyze_yobit_tri, analyze_uniswap_tri, analyze_yobit_bf, analyze_uniswap_bf
from .grid_trading import run_grid_trading
EOF

# yobitrageswap/ui/ui.py
cat > yobitrageswap/ui/ui.py << EOF
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, DataTable, Static
from textual.containers import Container
from typing import List, Dict

class ArbitrageApp(App):
    CSS = """
    DataTable {
        height: 80%;
        width: 100%;
    }
    Static {
        height: 20%;
        width: 100%;
        background: darkblue;
        color: white;
        padding: 1;
    }
    """

    def __init__(self, opps: List[Dict]):
        super().__init__()
        self.opps = opps

    def compose(self) -> ComposeResult:
        yield Header()
        yield DataTable()
        yield Static(id="summary")
        yield Footer()

    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.add_columns("Exchange", "Path", "Profit (%)", "Amount In", "Amount Out", "Score")
        for opp in self.opps:
            table.add_row(
                opp['exchange'],
                opp['path'],
                opp['profit_percent'],
                f"{opp['amount_in']:.2f}",
                f"{opp['amount_out']:.2f}",
                f"{opp['score']:.2f}"
            )
        summary = self.query_one("#summary", Static)
        summary.update("Arbitrage Opportunities Dashboard\nPress 'q' to quit.")

    def on_key(self, event):
        if event.key == 'q':
            self.exit()

    async def run_async(self):
        await self.run()
EOF

# yobitrageswap/ui/__init__.py
cat > yobitrageswap/ui/__init__.py << EOF
from .ui import ArbitrageApp
EOF

# Step 7: Clean up old files
echo "Cleaning up old files..."
rm -f yobitrageswap.py
rm -f _1-Projects/a/yobitrageswap.py
rm -f _1-Projects/a/.env
rm -f _1-Projects/a/requirements.txt

# Step 8: Set permissions
echo "Setting permissions..."
chmod +x yobitrageswap/main.py

echo "Setup and refactor complete. Run 'python3 yobitrageswap/main.py --help' for usage."
EOF
