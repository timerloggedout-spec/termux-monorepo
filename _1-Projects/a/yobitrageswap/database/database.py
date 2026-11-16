import sqlite3
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from yobitrageswap.config.config import load_config

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
        return {row[0]: row[1] for row in cursor.fetchall()}

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
