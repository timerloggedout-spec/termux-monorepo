import os
import json
from dotenv import load_dotenv
import logging
logging.basicConfig(filename='arbitrage.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

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
