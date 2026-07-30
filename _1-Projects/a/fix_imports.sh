#!/bin/bash

# fix_imports.sh
# Script to fix import paths in yobitrageswap/ Python files using sed

# Ensure working directory is correct
cd ~/_1-Projects/a || { echo "Error: Directory ~/_1-Projects/a not found"; exit 1; }

# Fix imports in all Python files
echo "Fixing imports in yobitrageswap/..."

# Replace config imports
find yobitrageswap -type f -name "*.py" -exec sed -i 's/from config.config import load_config/from yobitrageswap.config.config import load_config/g' {} \;
find yobitrageswap -type f -name "*.py" -exec sed -i 's/from ..config.config import load_config/from yobitrageswap.config.config import load_config/g' {} \;

# Replace database imports
find yobitrageswap -type f -name "*.py" -exec sed -i 's/from database.database import /from yobitrageswap.database.database import /g' {} \;
find yobitrageswap -type f -name "*.py" -exec sed -i 's/from ..database.database import /from yobitrageswap.database.database import /g' {} \;

# Replace metrics imports
find yobitrageswap -type f -name "*.py" -exec sed -i 's/from metrics.metrics import /from yobitrageswap.metrics.metrics import /g' {} \;
find yobitrageswap -type f -name "*.py" -exec sed -i 's/from ..metrics.metrics import /from yobitrageswap.metrics.metrics import /g' {} \;

# Replace volatility imports
find yobitrageswap -type f -name "*.py" -exec sed -i 's/from volatility.volatility import /from yobitrageswap.volatility.volatility import /g' {} \;
find yobitrageswap -type f -name "*.py" -exec sed -i 's/from ..volatility.volatility import /from yobitrageswap.volatility.volatility import /g' {} \;

# Replace constants imports
find yobitrageswap -type f -name "*.py" -exec sed -i 's/from constants.constants import /from yobitrageswap.constants.constants import /g' {} \;
find yobitrageswap -type f -name "*.py" -exec sed -i 's/from ..constants.constants import /from yobitrageswap.constants.constants import /g' {} \;

# Verify changes in key files
echo "Verifying import fixes..."
echo "Checking yobitrageswap/main.py:"
grep "load_config" yobitrageswap/main.py || echo "No load_config import found in main.py"
echo "Checking yobitrageswap/database/database.py:"
grep "load_config" yobitrageswap/database/database.py || echo "No load_config import found in database.py"

# Ensure .env file exists
echo "Ensuring .env file exists..."
touch .env
echo "Please populate .env with valid API keys:"
echo "API_KEY=your_yobit_api_key"
echo "SECRET_KEY=your_yobit_secret_key"
echo "ETH_PRIVATE_KEY=your_ethereum_private_key"
echo "ETHEREUM_RPC_URL=your_ethereum_rpc_url"
echo "CMC_API_KEY=your_coinmarketcap_api_key"

# Check directory structure
echo "Verifying directory structure..."
ls -la yobitrageswap/config/ || echo "Error: yobitrageswap/config/ directory not found"

echo "Import fixes complete. Run 'python -m yobitrageswap.main --exchange both --method triangular' to test."
