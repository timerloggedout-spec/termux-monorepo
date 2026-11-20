#!/bin/bash

# Script to fix folder structure, move files, and implement refactored code for yobitrageswap
# Run this from ~/_1-Projects/a/
# Assumes you are in ~/ _1-Projects/a/

set -e  # Exit on error

echo "Starting yobitrageswap setup and refactor..."

# Step 1: Clean up duplicated folders
echo "Cleaning up duplicated folders..."
if [ -d "_1-Projects/a/_1-Projects/a/yobitrageswap" ]; then
    rm -rf "_1-Projects/a/_1-Projects/a/yobitrageswap"
fi
if [ -d "_1-Projects/a/_1-Projects" ]; then
    rm -rf "_1-Projects/a/_1-Projects"
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
cat > requirements.txt << 'EOF'
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
cat > .env << 'EOF'
API_KEY=your_yobit_api_key
SECRET_KEY=your_yobit_secret_key
ETH_PRIVATE_KEY=your_ethereum_private_key
ETHEREUM_RPC_URL=your_ethereum_rpc_url
CMC_API_KEY=your_coinmarketcap_api_key
EOF

# Step 6: Create and write code files
echo "Creating and writing code files..."

# yobitrageswap/main.py
cat > yobitrageswap/main.py << 'EOF'
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
from strategies.grid_trading.grid_trading import manage_grid_orders
from ui.ui import ArbitrageApp

CONFIG = load_config()
metrics = Metrics()

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s',
                    handlers=[logging.FileHandler(CONFIG['LOG_FILE']), logging.StreamHandler()])
logger = logging.getLogger(__name__)

async def run_analysis(exchange: str, method: str, live: bool, ui: bool) -> List[Dict]:
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
cat > yobitrageswap/config/config.py << 'EOF'
import os
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
            elif key == 'TIERED_LIMITS':
                config[key] = json.loads(env_value)
            elif key == 'SHORT_SELLING_ENABLED':
                config[key] = json.loads(env_value)
            else:
                config[key] = env_value
    config['BASE_CURRENCIES'] = [c for c in config['BASE_CURRENCIES'] if c.lower() not in [a.lower() for a in config['AVOID_CURRENCIES']]]
    return config
EOF

# yobitrageswap/database/database.py
cat > yobitrageswap/database/database.py << 'EOF'
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
        cursor = conn.execute('SELECT path, volatility
