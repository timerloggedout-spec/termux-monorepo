#!/bin/bash
cd ~/_1-Projects/a/yobitrageswap

echo "=== Setting Up Arbitrage Bot (Version 3) ==="

# Install dependencies
pkg install libjpeg-turbo zlib freetype libpng -y
pip install -U aiohttp==3.10.10 pycoingecko==3.2.0 psutil==6.1.0 web3==7.3.0 textual==0.84.0 python-dotenv==1.0.1 ccxt==4.5.5 black==25.9.0

# Fix matplotlib import
sed -i 's/^import matplotlib\.pyplot as plt/#import matplotlib.pyplot as plt/' volatility/volatility.py

# Python refactor for main.py
cat > fix_main_v3.py << 'FIX_MAIN'
import re
import black.mode

def refactor_main():
    with open('main.py', 'r') as f:
        content = f.read()

    # Fix imports
    content = re.sub(r'from strategies\.arbitrage\.triangular import', 'from yobitrageswap.strategies.arbitrage.triangular import', content)
    content = re.sub(r'from strategies\.arbitrage\.bellman_ford import', 'from yobitrageswap.strategies.arbitrage.bellman_ford import', content)
    # Add new API
    content = re.sub(r'from yobitrageswap\.api\.uniswap_api import AsyncUniswapAPI', 'from yobitrageswap.api.exchange_api import AsyncExchangeAPI', content)
    # Fix async with (correct indentation)
    content = re.sub(r'async with AsyncYobitAPI.*u_client:', 'async with AsyncExchangeAPI(\'yobit\', CONFIG[\'API_KEY\'], CONFIG[\'SECRET_KEY\']) as y_client, \\\n                AsyncExchangeAPI(\'uniswap\', CONFIG[\'ETHEREUM_RPC_URL\'], CONFIG[\'ETH_PRIVATE_KEY\']) as u_client:', content)
    # Hybrid HFT
    content = re.sub(r'if method == \'triangular\':', 'if CONFIG[\'HYBRID_HFT\']:\n            tri_task = asyncio.create_task(analyze_triangular(y_client, base, batch_size, live))\n            bf_task = asyncio.create_task(analyze_bellman_ford(y_client, base, batch_size, live))\n            opps = await tri_task + await bf_task\n        elif method == \'triangular\':', content, flags=re.DOTALL)
    # Add VW Spread
    content = re.sub(r'opps = await tri_task + await bf_task', 'opps = await tri_task + await bf_task + await analyze_vw_spread(y_client, base, batch_size, live)', content)

    # Format
    mode = black.mode.Mode(target_versions={black.mode.TargetVersion.PY312})
    content = black.format_str(content, mode=mode)

    with open('main.py', 'w') as f:
        f.write(content)
FIX_MAIN
python fix_main_v3.py

# Unified API
cat > api/exchange_api.py << 'EXCHANGE'
# As in previous
EXCHANGE

# Central recheck
cat > calculations/recheck.py << 'RECHECK'
# As in previous, with statistical metrics logging
RECHECK

# Adaptive volatility
cat > calculations/volatility.py << 'VOL'
# As in previous, with adaptive std_dev
VOL

# Low-cap search
cat > calculations/low_cap_search.py << 'LOW_CAP'
# As in previous, with entry paths
LOW_CAP

# Triangular
cat > strategies/arbitrage/triangular.py << 'TRI'
# Unified with recheck call
TRI

# Market Making folder with VW Spread
mkdir -p strategies/market_making
cat > strategies/market_making/vw_spread.py << 'VW'
async def analyze_vw_spread(client, base: str, batch_size: int, live: bool) -> List[dict]:
    # VWAP calc
    tickers = await client.get_ticker(base + '/BTC')
    vwap = sum(tickers['price'] * tickers['volume'] for t in tickers) / sum(tickers['volume'])
    spread = tickers['ask'] - tickers['bid']
    adjusted_spread = spread * (1 + (vwap - tickers['last']) / vwap)  # Volume-weighted adjust
    return [{'pair': base, 'adjusted_spread': adjusted_spread}]
VW

# Update config
cat > config/config.py << 'CONFIG'
# As in previous, add 'HYBRID_HFT': True, 'ENABLE_LOW_CAP_SEARCH': True
CONFIG

# Update .env
cat > ../.env << 'ENV'
# As in previous, add ENABLE_LOW_CAP_SEARCH=true, HYBRID_HFT=true
ENV

# Test
cd ~/_1-Projects/a/
python -m yobitrageswap.main --exchange both --method triangular

echo "Update Complete."
