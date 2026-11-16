# Test live session export with the working token
python3 -c "
import sys, json
sys.path.insert(0, '/data/data/com.termux/files/home/cli-synthegration')
from conv_explorer import export_session_live

# The function signature from conv_explorer.py: export_session_live(session_id, output_dir)
# We'll check if it exists or add it
"
