# 2. Rebuild correlation with the fresh export
python3 ~/archwiz/rebuild_correlation.py   # (same script as before)

# 3. Test the archaeologist
python3 ~/workspace/llm_map/archaeologist.py archwiz/live_view.py --full | head -20