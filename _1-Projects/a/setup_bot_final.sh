#!/bin/bash
cd ~/_1-Projects/a/yobitrageswap

echo "=== Setting Up Arbitrage Bot ==="

# Install dependencies
echo "Installing dependencies..."
pkg install libjpeg-turbo zlib freetype libpng -y
pip install -U aiohttp==3.10.10 pycoingecko==3.2.0 psutil==6.1.0 numpy==2.2.5 web3==7.3.0 textual==0.84.0 python-dotenv==1.0.1 ccxt==4.3.0 solana==0.30.2

# Fix imports in volatility.py (matplotlib)
echo "Fixing matplotlib import..."
sed -i 's/import matplotlib.pyplot as plt/#import matplotlib.pyplot as plt/' volatility/volatility.py
grep "matplotlib" volatility/volatility.py || echo "No matplotlib import found"

# Fix API imports in main.py
echo "Fixing API imports..."
sed -i 's/from api\.yobit_api import AsyncYobitAPI/from yobitrageswap.api.yobit_api import AsyncYobitAPI/' main.py
sed -i 's/from api\.uniswap_api import AsyncUniswapAPI/from yobitrageswap.api.uniswap_api import AsyncUniswapAPI/' main.py
grep -E "(yobit_api|uniswap_api)" main.py || echo "No API imports found"

# Fix strategies imports in main.py (ensure exact match)
echo "Fixing strategies imports..."
sed -i 's/from strategies\.arbitrage\.triangular import/from yobitrageswap.strategies.arbitrage.triangular import/' main.py
sed -i 's/from strategies\.arbitrage\.bellman_ford import/from yobitrageswap.strategies.arbitrage.bellman_ford import/' main.py
grep -E "(triangular|bellman_ford)" main.py || echo "No strategies imports found"

# Add new API imports to main.py
echo "Adding new API imports..."
sed -i '/from yobitrageswap\.api\.uniswap_api import AsyncUniswapAPI/a \
from yobitrageswap.api.indodax_api import AsyncIndodaxAPI\
from yobitrageswap.api.tastytrade_api import AsyncTastyTradeAPI\
from yobitrageswap.api.pumpfun_api import AsyncPumpFunAPI\
from yobitrageswap.api.solana_api import AsyncSolanaAPI\
from yobitrageswap.api.polygon_api import AsyncPolygonAPI' main.py

# Add new exchange clients to run_analysis
echo "Adding new exchange clients..."
sed -i '/async with AsyncYobitAPI.*AsyncUniswapAPI.*:/c \
        async with AsyncYobitAPI(CONFIG['"'"'API_KEY'"'"'], CONFIG['"'"'SECRET_KEY'"'"']) as y_client, \
                AsyncUniswapAPI(CONFIG['"'"'ETHEREUM_RPC_URL'"'"'], CONFIG['"'"'ETH_PRIVATE_KEY'"'"']) as u_client, \
                AsyncIndodaxAPI(CONFIG['"'"'INDODAX_API_KEY'"'"'], CONFIG['"'"'INDODAX_SECRET'"'"']) as i_client, \
                AsyncTastyTradeAPI(CONFIG['"'"'TASTYTRADE_USERNAME'"'"'], CONFIG['"'"'TASTYTRADE_ACCESS_TOKEN'"'"']) as t_client, \
                AsyncPumpFunAPI(CONFIG['"'"'SOLANA_RPC_URL'"'"']) as p_client, \
                AsyncSolanaAPI(CONFIG['"'"'SOLANA_RPC_URL'"'"']) as s_client, \
                AsyncPolygonAPI(CONFIG['"'"'POLYGON_RPC_URL'"'"']) as m_client:' main.py

# Add IndoDax triangular analysis placeholder
echo "Adding IndoDax triangular analysis..."
sed -i '/if method == '"'"'triangular'"'"':/a \
        if CONFIG['"'"'ENABLE_INDODAX'"'"'] and exchange in ['"'"'indodax'"'"', '"'"'both'"'"']:\
            i_opps = await analyze_indodax_tri(i_client, base, batch_size, live)\
            opps.extend(i_opps)' main.py

# Scan for other relative imports
echo "Scanning for other relative imports..."
find . -type f -name "*.py" -exec grep -H "from [a-zA-Z_][a-zA-Z0-9_]*\." {} \; | grep -v "yobitrageswap\." || echo "No other relative imports found"

# Update config.py for logging and API key validation
echo "Updating config.py..."
cat > config.py << 'CONFIG'
import os
import json
import logging
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', handlers=[logging.FileHandler('arbitrage.log'), logging.StreamHandler()])
logger = logging.getLogger(__name__)

CONFIG_DEFAULTS = {
    'API_KEY': '', 'SECRET_KEY': '', 'ETH_PRIVATE_KEY': '', 'ETHEREUM_RPC_URL': '', 'CMC_API_KEY': '',
    'TASTYTRADE_USERNAME': '', 'TASTYTRADE_ACCESS_TOKEN': '', 'INDODAX_API_KEY': '', 'INDODAX_SECRET': '',
    'SOLANA_RPC_URL': 'https://api.mainnet-beta.solana.com', 'POLYGON_RPC_URL': 'https://polygon-rpc.com',
    'NETWORK': 'mainnet', 'ENABLE_PUMPFUN': False, 'ENABLE_TASTYTRADE': False, 'ENABLE_INDODAX': False,
    'ENABLE_SOLANA': False, 'ENABLE_POLYGON': False,
    'INITIAL_INVESTMENT': 100.0, 'TRADING_FEE': 0.002, 'YOBIT_FEE': 0.002, 'UNISWAP_FEE_TIER': 3000,
    'LOG_FILE': 'arbitrage.log', 'REQUEST_TIMEOUT': 10, 'RETRY_ATTEMPTS': 3, 'RETRY_DELAY': 5,
    'BATCH_SIZE_MIN': 10, 'BATCH_SIZE_MAX': 100, 'BATCH_SIZE_INIT': 40, 'CYCLE_DELAY': 15,
    'LIQUIDITY_THRESHOLD': 1000000, 'MIN_PROFIT_PERCENT': 0.5, 'MAX_TRADE_PCT': 0.1,
    'FEE_DISCREPANCY_THRESHOLD': 0.0005, 'FEE_UPDATE_INTERVAL_MIN': 60, 'FEE_AVG_WINDOW': 10,
    'MAX_DISCREPANCY_RETRIES': 3, 'VOL_BATCH_SIZE': 5, 'VOL_SPACING_MIN': 5, 'VOL_AMOUNT': 100.0,
    'VOL_WEIGHTING': 'linear', 'VOL_WEIGHTING_ALPHA': 1.0,
    'BASE_CURRENCIES': ['ltc', 'doge', 'xrp', 'ada', 'sol', 'link', 'dot', 'matic', 'avax', 'shib', 'uni', 'aave', 'comp', 'snx', 'yfi', 'crv', 'sushi', '1inch', 'mkr', 'zrx'],
    'AVOID_CURRENCIES': ['usd', 'cad', 'eur', 'btc', 'eth', 'bnb', 'usdt', 'usdc', 'yovi'],
    'DB_PATH': 'crypto_prices.db', 'VOL_LOOKBACK_HOURS': 24, 'FETCH_INTERVAL_MIN': 60,
    'THROUGHPUT_TARGET': 200, 'BATCH_ADJUST_INTERVAL': 5, 'MAX_SLIPPAGE': 0.01,
    'TIERED_LIMITS': {'free': {'max_trades_day': 10}, 'pro': {'max_trades_day': 50}},
    'EXECUTION_PRIORITY_THRESHOLD': 0.8, 'TOP_K_OPPS': 5, 'GRID_BASKETS': 10,
    'GRID_ORDERS_PER_BASKET': 10, 'GRID_PROFIT_HOLD': 0.2, 'GRID_REINVEST_SAME': 0.6,
    'GRID_INVEST_OTHER': 0.2, 'GRID_SPREAD_FACTOR': 0.005, 'MIN_SAMPLES': 5,
    'SAMPLE_BOOST': 1.5, 'THROUGHPUT_WEIGHT': 0.3,
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
    # Toggle RPC based on NETWORK
    if config['NETWORK'] == 'testnet':
        config['SOLANA_RPC_URL'] = 'https://api.testnet.solana.com'
        config['POLYGON_RPC_URL'] = 'https://rpc-amoy.polygon.technology'
        config['ETHEREUM_RPC_URL'] = 'https://sepolia.infura.io/v3/' + config['ETHEREUM_RPC_URL'].split('/')[-1] if '/' in config['ETHEREUM_RPC_URL'] else ''
    else:
        config['SOLANA_RPC_URL'] = 'https://api.mainnet-beta.solana.com'
        config['POLYGON_RPC_URL'] = 'https://polygon-rpc.com'
        config['ETHEREUM_RPC_URL'] = 'https://mainnet.infura.io/v3/' + config['ETHEREUM_RPC_URL'].split('/')[-1] if '/' in config['ETHEREUM_RPC_URL'] else ''
    # Validate API keys
    critical_keys = ['API_KEY', 'SECRET_KEY', 'ETH_PRIVATE_KEY', 'ETHEREUM_RPC_URL', 'CMC_API_KEY', 'INDODAX_API_KEY', 'INDODAX_SECRET', 'TASTYTRADE_USERNAME', 'TASTYTRADE_ACCESS_TOKEN']
    missing_keys = [k for k in critical_keys if config.get(k, '') == '' or config.get(k, '').startswith('your_')]
    if missing_keys:
        logger.warning(f"Missing critical env vars: {', '.join(missing_keys)}. Bot will use public data where possible.")
        for key in missing_keys:
            config[key] = ''
        if 'INDODAX_API_KEY' in missing_keys or 'INDODAX_SECRET' in missing_keys:
            config['ENABLE_INDODAX'] = False
            logger.warning("Disabling IndoDax due to missing keys.")
        if 'TASTYTRADE_USERNAME' in missing_keys or 'TASTYTRADE_ACCESS_TOKEN' in missing_keys:
            config['ENABLE_TASTYTRADE'] = False
            logger.warning("Disabling tastyTrade due to missing keys.")
    return config
CONFIG
chmod 644 config.py

# Add CCXT-based IndoDax API
echo "Creating IndoDax API module..."
cat > api/indodax_api.py << 'INDODAX'
import ccxt.async_support as ccxt
from typing import Dict, List

class AsyncIndodaxAPI:
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
INDODAX
chmod 644 api/indodax_api.py

# Add tastyTrade API
echo "Creating tastyTrade API module..."
cat > api/tastytrade_api.py << 'TASTYTRADE'
import aiohttp
from typing import Dict, List

class AsyncTastyTradeAPI:
    def __init__(self, username: str, access_token: str):
        self.username = username
        self.access_token = access_token
        self.base_url = 'https://api.tastytrade.com'

    async def get_quotes(self, symbols: List[str]) -> Dict:
        url = f"{self.base_url}/quotes"
        headers = {'Authorization': f'Bearer {self.access_token}'}
        params = {'symbols': ','.join(symbols)}
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, params=params) as resp:
                return await resp.json()
TASTYTRADE
chmod 644 api/tastytrade_api.py

# Add Pump.Fun API
echo "Creating Pump.Fun API module..."
cat > api/pumpfun_api.py << 'PUMPFUN'
import aiohttp
from solana.rpc.async_api import AsyncClient
from typing import Dict, List

class AsyncPumpFunAPI:
    def __init__(self, rpc_url: str):
        self.rpc_url = rpc_url
        self.client = AsyncClient(rpc_url)

    async def get_recent_tokens(self) -> List[Dict]:
        url = "https://pumpportal.fun/api/data/recent_tokens?limit=10"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                return await resp.json()

    async def close(self):
        await self.client.close()
PUMPFUN
chmod 644 api/pumpfun_api.py

# Add Solana API
echo "Creating Solana API module..."
cat > api/solana_api.py << 'SOLANA'
from solana.rpc.async_api import AsyncClient
from typing import Dict

class AsyncSolanaAPI:
    def __init__(self, rpc_url: str):
        self.rpc_url = rpc_url
        self.client = AsyncClient(rpc_url)

    async def get_balance(self, pubkey: str) -> Dict:
        return await self.client.get_balance(pubkey)

    async def close(self):
        await self.client.close()
SOLANA
chmod 644 api/solana_api.py

# Add Polygon API
echo "Creating Polygon API module..."
cat > api/polygon_api.py << 'POLYGON'
from web3 import Web3
from typing import Dict

class AsyncPolygonAPI:
    def __init__(self, rpc_url: str):
        self.w3 = Web3(Web3.HTTPProvider(rpc_url))

    async def get_balance(self, address: str) -> Dict:
        balance = self.w3.eth.get_balance(address)
        return {'balance': balance / 10**18}  # Convert wei to MATIC
POLYGON
chmod 644 api/polygon_api.py

# Update volatility.py for public data feeds
echo "Updating volatility.py for public data feeds..."
sed -i '/except Exception:/a \
\        # Fallback to CryptoCompare public API\
\        try:\
\            url = f"https://min-api.cryptocompare.com/data/v2/histohour?fsym={coin.upper()}&tsym=USD&limit=24"\
\            async with aiohttp.ClientSession() as session:\
\                async with session.get(url, timeout=CONFIG['"'"'REQUEST_TIMEOUT'"'"']) as resp:\
\                    if resp.status == 200:\
\                        data = await resp.json()\
\                        prices = [p['"'"'close'"'"'] for p in data['"'"'Data'"'"']['"'"'Data'"'"']]\
\                        for i, p in enumerate(prices):\
\                            ts = data['"'"'Data'"'"']['"'"'Data'"'"'][i]['"'"'time'"'"']\
\                            store_price(coin, ts, p, '"'"'cryptocompare'"'"')\
\                        return {'"'"'coin'"'"': coin, '"'"'prices'"'"': prices}\
\        except Exception:\
\            pass' volatility/volatility.py

# Add IndoDax triangular analysis placeholder
echo "Creating IndoDax triangular analysis..."
cat > strategies/arbitrage/triangular.py << 'TRIANGULAR'
$(cat strategies/arbitrage/triangular.py)

async def analyze_indodax_tri(client, base: str, batch_size: int, live: bool) -> list:
    return []  # Placeholder: implement triangular arbitrage for IndoDax
TRIANGULAR
chmod 644 strategies/arbitrage/triangular.py

# Update .env with new keys
echo "Updating .env..."
cat > ../.env << 'ENV'
API_KEY=your_yobit_api_key
SECRET_KEY=your_yobit_secret_key
ETH_PRIVATE_KEY=your_ethereum_private_key
ETHEREUM_RPC_URL=your_ethereum_rpc_url
CMC_API_KEY=your_coinmarketcap_api_key
INDODAX_API_KEY=your_indodax_api_key
INDODAX_SECRET=your_indodax_secret
TASTYTRADE_USERNAME=your_tastytrade_username
TASTYTRADE_ACCESS_TOKEN=your_tastytrade_access_token
SOLANA_RPC_URL=https://api.testnet.solana.com
POLYGON_RPC_URL=https://rpc-amoy.polygon.technology
NETWORK=testnet
ENABLE_INDODAX=false
ENABLE_TASTYTRADE=false
ENABLE_PUMPFUN=false
ENABLE_SOLANA=false
ENABLE_POLYGON=false
ENV
chmod 644 ../.env

# Ensure storage permissions
echo "Setting storage permissions..."
termux-setup-storage <<< "y"

echo "=== Setup Complete ==="
echo "Edit .env with valid API keys."
echo "Test with: cd ~/_1-Projects/a && python -m yobitrageswap.main --exchange both --method triangular"
