#!/bin/bash
cd ~/_1-Projects/a/yobitrageswap

echo "=== Fixing Imports in yobitrageswap ==="

# Fix matplotlib in volatility.py
sed -i 's/import matplotlib.pyplot as plt/#import matplotlib.pyplot as plt/' volatility/volatility.py
echo "Fixed matplotlib import."

# Fix API imports in main.py
sed -i 's/from api.yobit_api import AsyncYobitAPI/from yobitrageswap.api.yobit_api import AsyncYobitAPI/' main.py
sed -i 's/from api.uniswap_api import AsyncUniswapAPI/from yobitrageswap.api.uniswap_api import AsyncUniswapAPI/' main.py
echo "Fixed API imports."

# Fix strategies imports in main.py
sed -i 's/from strategies.arbitrage.triangular import/from yobitrageswap.strategies.arbitrage.triangular import/' main.py
sed -i 's/from strategies.arbitrage.bellman_ford import/from yobitrageswap.strategies.arbitrage.bellman_ford import/' main.py
echo "Fixed strategies imports."

# Scan for other potential relative imports (e.g., from module... without yobitrageswap.)
echo "Scanning for other relative imports..."
find . -type f -name "*.py" -exec grep -H "from [a-zA-Z_][a-zA-Z0-9_]*\." {} \; | grep -v "yobitrageswap\." || echo "No other relative imports found."

echo "=== Fixes Complete. Run 'python -m yobitrageswap.main --exchange both --method triangular' to test. ==="
